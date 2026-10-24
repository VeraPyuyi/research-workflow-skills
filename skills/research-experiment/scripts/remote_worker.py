"""Portable shared-host job controller. Run through the SSH adapter."""

import argparse
from contextlib import contextmanager
import hashlib
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time
import uuid


ACTIVE = {"reserved", "running", "cancel_requested", "unknown"}
TERMINAL = {"completed", "failed", "timed_out", "cancelled"}
IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")
PROC = Path("/proc")
CONTROLLER_PROTOCOL = 2


def identifier(value):
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise ValueError("Invalid project or job identifier")
    return value


def positive(value, label):
    if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
        raise ValueError("Invalid positive resource: " + label)
    return value


def safe_path(root, *parts):
    root = Path(root).absolute()
    target = root.joinpath(*parts)
    for path in (target, *target.parents):
        if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
            raise ValueError("Linked paths are not permitted")
    try:
        target.resolve().relative_to(root.resolve())
    except ValueError:
        raise ValueError("Path escapes the server workspace")
    return target


def atomic_json(path, value):
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        with temporary.open("x", encoding="utf-8") as stream:
            json.dump(value, stream, indent=2, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(str(temporary), str(path))
    finally:
        if temporary.exists():
            temporary.unlink()


@contextmanager
def queue_lock(root, wait_seconds=0):
    root = safe_path(root)
    root.mkdir(parents=True, exist_ok=True)
    path = safe_path(root, ".queue.lock")
    token = uuid.uuid4().hex
    deadline = time.monotonic() + wait_seconds
    while True:
        try:
            descriptor = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            break
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise ValueError("Another coordinator holds the queue lock; reconcile before retry")
            time.sleep(0.05)
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(token)
        yield
    finally:
        if path.exists() and path.read_text() == token:
            path.unlink()


def validate_packet(packet):
    if not isinstance(packet, dict):
        raise ValueError("Job must be an object")
    for field in ("project", "id"):
        identifier(packet.get(field))
    for field in ("authority", "budget_id"):
        if not isinstance(packet.get(field), str) or not packet[field].strip():
            raise ValueError("Missing " + field)
    versions = packet.get("versions")
    if not isinstance(versions, dict) or any(
        not isinstance(versions.get(k), str) or not versions[k]
        for k in ("workflow", "protocol", "code")
    ):
        raise ValueError("Workflow, protocol and code versions are required")
    argv = packet.get("argv")
    if not isinstance(argv, list) or not argv or any(
        not isinstance(arg, str) or "\0" in arg for arg in argv
    ) or not argv[0]:
        raise ValueError("Command must be a nonempty argv list")
    positive(packet.get("timeout_seconds"), "timeout")
    positive(packet.get("budget_run_seconds"), "project run-seconds budget")
    resources = packet.get("resources")
    if not isinstance(resources, dict):
        raise ValueError("Resource request is required")
    if type(resources.get("cpu")) is not int:
        raise ValueError("CPU request must be a positive integer")
    positive(resources["cpu"], "cpu")
    positive(resources.get("memory_mb"), "memory")
    gpus = resources.get("gpus")
    if not isinstance(gpus, list):
        raise ValueError("GPU request must be an explicit list")
    seen = set()
    for gpu in gpus:
        if not isinstance(gpu, dict) or type(gpu.get("index")) is not int or gpu["index"] < 0:
            raise ValueError("Invalid GPU index")
        if gpu["index"] in seen:
            raise ValueError("Duplicate GPU request")
        seen.add(gpu["index"])
        positive(gpu.get("memory_mb"), "GPU memory")
    outputs = packet.get("outputs", [])
    if not isinstance(outputs, list):
        raise ValueError("Output manifest must be a list")
    for name in outputs:
        if (not isinstance(name, str) or not name or "\\" in name
                or Path(name).is_absolute() or ".." in Path(name).parts):
            raise ValueError("Output must be relative to its run directory")
    return packet


def inventory():
    memory = None
    try:
        fields = dict(line.split(":", 1) for line in Path("/proc/meminfo").read_text().splitlines())
        memory = int(fields["MemAvailable"].split()[0]) // 1024
    except (OSError, KeyError, ValueError):
        pass
    gpus = []
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=index,memory.total,memory.free,utilization.gpu",
             "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=5,
            check=True,
        )
        for row in result.stdout.strip().splitlines():
            index, total, free, utilization = [int(item.strip()) for item in row.split(",")]
            gpus.append({"index": index, "total_memory_mb": total,
                         "free_memory_mb": free, "utilization_percent": utilization})
    except (OSError, ValueError, subprocess.SubprocessError):
        pass
    return {"cpu": os.cpu_count(), "available_memory_mb": memory, "gpus": gpus,
            "python": sys.version.split()[0], "observed_at": time.time()}


def admit(packet, available, records):
    validate_packet(packet)
    if any(record.get("status") not in ACTIVE | TERMINAL for record in records):
        raise ValueError("Unrecognized existing job status")
    if any(record.get("status") in {"unknown", "cancel_requested"} for record in records):
        raise ValueError("Uncertain commitments must be reconciled before expansion")
    active = [record for record in records if record.get("status") in ACTIVE]
    for record in records:
        if record.get("project") == packet["project"]:
            if (record.get("budget_id") != packet["budget_id"]
                    or record.get("budget_run_seconds") != packet["budget_run_seconds"]):
                raise ValueError("Project budget changed; resolve its approval before submission")
    spent = sum(record.get("elapsed_seconds", 0) for record in records
                if record.get("project") == packet["project"] and record["status"] in TERMINAL)
    committed = sum(record["timeout_seconds"] for record in active
                    if record.get("project") == packet["project"])
    if spent + committed + packet["timeout_seconds"] > packet["budget_run_seconds"]:
        raise ValueError("Project run-seconds budget exhausted including active commitments")
    resources = packet["resources"]
    for key, capacity_key in (("cpu", "cpu"), ("memory_mb", "available_memory_mb")):
        total = available.get(capacity_key)
        positive(total, capacity_key)
        requested = resources[key] + sum(record["resources"][key] for record in active)
        if requested > total:
            raise ValueError("Insufficient shared " + key)
    gpu_capacity = {gpu["index"]: gpu["free_memory_mb"] for gpu in available.get("gpus", [])}
    for gpu in resources["gpus"]:
        reserved = sum(g["memory_mb"] for record in active
                       for g in record["resources"]["gpus"] if g["index"] == gpu["index"])
        if gpu["memory_mb"] + reserved > gpu_capacity.get(gpu["index"], 0):
            raise ValueError("Insufficient shared GPU memory")


def record_path(root, project, job):
    identity = json.dumps([identifier(project), identifier(job)], separators=(",", ":"))
    return safe_path(root, ".jobs", hashlib.sha256(identity.encode("ascii")).hexdigest() + ".json")


def read_record(path, project, job):
    record = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(record, dict) or (record.get("project"), record.get("id")) != (project, job):
        raise ValueError("Stored job identity does not match the requested job")
    return record


def lookup_record(root, project, job):
    """Keep matching legacy records in place; never resolve a delimiter alias."""
    canonical = record_path(root, project, job)
    legacy = safe_path(root, ".jobs", project + "--" + job + ".json")
    found = []
    if canonical.exists():
        read_record(canonical, project, job)
        found.append(canonical)
    if legacy.exists():
        record = json.loads(legacy.read_text(encoding="utf-8"))
        if isinstance(record, dict) and (record.get("project"), record.get("id")) == (project, job):
            found.append(legacy)
    if len(found) > 1:
        raise ValueError("Multiple records for this job; reconcile without resubmitting")
    return found[0] if found else canonical


def process_start(pid):
    try:
        info = process_info(pid)
        return info["start"] if info else None
    except (OSError, ValueError):
        return None


def process_info(pid):
    try:
        fields = (PROC / str(pid) / "stat").read_text().rsplit(")", 1)[1].split()
        return {"pid": pid, "state": fields[0], "ppid": int(fields[1]),
                "group": int(fields[2]), "session": int(fields[3]), "start": fields[19]}
    except FileNotFoundError:
        return None
    except (IndexError, ValueError):
        raise ValueError("Unparseable process identity")


def child_exit(child):
    # WNOWAIT pins the launcher PID even after exit. Never poll/wait/reap it
    # until all group signaling and session reconciliation have finished.
    result = os.waitid(os.P_PID, child.pid, os.WEXITED | os.WNOHANG | os.WNOWAIT)
    if result is None:
        return None
    if result.si_pid != child.pid:
        raise ValueError("Unconfirmed child wait identity")
    return result.si_status if result.si_code == os.CLD_EXITED else -result.si_status


def session_members(anchor):
    current = process_info(anchor["pid"])
    if (not current or any(current[k] != anchor[k] for k in
                           ("pid", "ppid", "start", "group", "session"))
            or current["ppid"] != os.getpid()
            or current["group"] != current["pid"] or current["session"] != current["pid"]):
        raise ValueError("Launcher/session ownership is unconfirmed")
    members = []
    for folder in PROC.iterdir():
        if not folder.name.isdigit():
            continue
        info = process_info(int(folder.name))
        if info and (info["session"] == anchor["session"] or info["group"] == anchor["group"]):
            if info["session"] != anchor["session"]:
                raise ValueError("Process group belongs to another session")
            if info["state"] not in ("Z", "X"):
                members.append(info)
    return members


def reconcile_child(child, anchor, cleanup_seconds=5):
    """Terminate only the pinned original group; ambiguous groups keep commitments."""
    deadline = time.monotonic() + cleanup_seconds
    signalled = False
    quiet = False
    while True:
        child_exit(child)  # Also establishes that this process is still our unreaped child.
        members = session_members(anchor)
        if not members:
            # A second observation must still show the owned launcher has exited.
            if child_exit(child) is None:
                raise ValueError("Session completion is unconfirmed")
            if not quiet:
                quiet = True
                time.sleep(0.05)
                continue
            child.wait(timeout=5)
            return signalled
        quiet = False
        if any(info["group"] != anchor["group"] for info in members):
            raise ValueError("Live descendant in an unpinned process group; reconcile manually")
        if time.monotonic() >= deadline:
            raise ValueError("Owned process group termination is unconfirmed")
        if not signalled:
            # The unreaped direct child prevents this group ID from being reused.
            # Validate again immediately before signaling; never signal scanned PIDs.
            child_exit(child)
            session_members(anchor)
            os.killpg(anchor["group"], signal.SIGKILL)
            signalled = True
        time.sleep(0.05)


def alive(record):
    pid = record.get("pid")
    return type(pid) is int and record.get("process_start") is not None and (
        process_start(pid) == record["process_start"]
    )


def load_records(root):
    folder = safe_path(root, ".jobs")
    if not folder.exists():
        return []
    records = []
    for path in folder.glob("*.json"):
        safe_path(root, ".jobs", path.name)
        record = json.loads(path.read_text(encoding="utf-8"))
        if record.get("status") in {"running", "reserved"} and not alive(record):
            record["status"] = "unknown"
            record["uncertainty"] = "Supervisor not confirmed; inspect exit record and process identity"
            atomic_json(path, record)
        records.append(record)
    return records


def launch_supervisor(job_file):
    output = Path(job_file).parent / (Path(job_file).stem + ".supervisor.log")
    with output.open("ab") as stream:
        process = subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve()), "run", str(job_file)],
            stdin=subprocess.DEVNULL, stdout=stream, stderr=stream,
            start_new_session=True, close_fds=True,
        )
    return {"pid": process.pid, "process_start": process_start(process.pid)}


def submit(root, packet, available=None, launch=None):
    validate_packet(packet)
    root = safe_path(root)
    digest = hashlib.sha256(json.dumps(packet, sort_keys=True, allow_nan=False).encode()).hexdigest()
    with queue_lock(root):
        path = lookup_record(root, packet["project"], packet["id"])
        path.parent.mkdir(exist_ok=True)
        if path.exists():
            existing = read_record(path, packet["project"], packet["id"])
            if existing.get("packet_sha256") != digest:
                raise ValueError("Job identity already belongs to another packet")
            return existing
        records = load_records(root)
        admit(packet, available or inventory(), records)
        run_dir = safe_path(root, packet["project"], "runs", packet["id"])
        run_dir.mkdir(parents=True, exist_ok=False)
        record = dict(packet, root=str(root), run_dir=str(run_dir), controller_protocol=CONTROLLER_PROTOCOL,
                      packet_sha256=digest, status="reserved", submitted_at=time.time())
        atomic_json(path, record)
        try:
            identity = (launch or launch_supervisor)(path)
            record.update(identity)
            atomic_json(path, record)
        except BaseException:
            record["status"] = "unknown"
            record["uncertainty"] = "Launch boundary interrupted; do not resubmit"
            atomic_json(path, record)
            raise
        return record


def status(root, project, job):
    with queue_lock(root):
        path = lookup_record(root, project, job)
        read_record(path, project, job)
        load_records(root)
        return read_record(path, project, job)


def cancel(root, project, job):
    with queue_lock(root):
        path = lookup_record(root, project, job)
        record = read_record(path, project, job)
        if record["status"] in TERMINAL:
            return record
        if record.get("controller_protocol") != CONTROLLER_PROTOCOL:
            raise ValueError("Legacy active supervisor needs operator reconciliation; no signal sent")
        if not alive(record):
            raise ValueError("Supervisor identity is unknown; no process was signalled")
        # The owning supervisor polls this mailbox. A numeric PID signal has an
        # unavoidable check/kill reuse race on Python 3.7 without pidfd support.
        record["status"] = "cancel_requested"
        atomic_json(path, record)
        return record


class Cancelled(Exception):
    pass


def run_job(job_file):
    path = Path(job_file).resolve()
    record = json.loads(path.read_text(encoding="utf-8"))
    root = Path(record["root"])
    if lookup_record(root, record["project"], record["id"]) != path:
        raise ValueError("Record path mismatch")
    started = time.monotonic()
    child = None
    anchor = None
    launch_started = False
    interrupted_flag = False
    def interrupted(_signal, _frame):
        nonlocal interrupted_flag
        interrupted_flag = True
    def cancellation_requested():
        return interrupted_flag or read_record(path, record["project"], record["id"])["status"] == "cancel_requested"
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    with queue_lock(root, wait_seconds=5):
        record = read_record(path, record["project"], record["id"])
        if (record["status"] not in ("reserved", "cancel_requested")
                or record.get("pid") != os.getpid()
                or record.get("process_start") != process_start(os.getpid())
                or record.get("controller_protocol") != CONTROLLER_PROTOCOL):
            raise ValueError("Supervisor does not own a pending launch")
        record.update(status="cancel_requested" if cancellation_requested() else "running",
                      started_at=time.time(), pid=os.getpid(),
                      process_start=process_start(os.getpid()))
        atomic_json(path, record)
    try:
        if cancellation_requested():
            raise Cancelled()
        if (not all(hasattr(os, name) for name in ("waitid", "P_PID", "WEXITED", "WNOHANG", "WNOWAIT", "CLD_EXITED"))
                or signal.getsignal(getattr(signal, "SIGCHLD", 17)) != signal.SIG_DFL):
            raise ValueError("Non-reaping Linux child observation is required")
        environment = dict(os.environ)
        environment["OMP_NUM_THREADS"] = str(record["resources"]["cpu"])
        environment["MKL_NUM_THREADS"] = str(record["resources"]["cpu"])
        environment["CUDA_VISIBLE_DEVICES"] = ",".join(
            str(gpu["index"]) for gpu in record["resources"]["gpus"]
        )
        run_dir = safe_path(root, record["project"], "runs", record["id"])
        with (run_dir / "stdout.log").open("wb") as out, (run_dir / "stderr.log").open("wb") as err:
            launch_started = True
            child = subprocess.Popen(record["argv"], cwd=str(run_dir), env=environment,
                                     stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                     start_new_session=True)
            anchor = process_info(child.pid)
            if anchor is None:
                raise ValueError("Launcher ownership was not observed")
            with queue_lock(root, wait_seconds=5):
                current = read_record(path, record["project"], record["id"])
                current["workload_identity"] = anchor
                atomic_json(path, current)
                record["workload_identity"] = anchor
            while True:
                if cancellation_requested():
                    raise Cancelled()
                if time.monotonic() - started >= record["timeout_seconds"]:
                    raise subprocess.TimeoutExpired(record["argv"], record["timeout_seconds"])
                code = child_exit(child)
                members = session_members(anchor)
                if code is not None and not members:
                    break
                time.sleep(0.05)
        missing = [name for name in record.get("outputs", [])
                   if not safe_path(run_dir, name).is_file()]
        record.update(exit_code=code, missing_outputs=missing,
                      status="completed" if code == 0 and not missing else "failed")
    except subprocess.TimeoutExpired:
        record["status"] = "timed_out"
    except Cancelled:
        record["status"] = "cancelled"
    except BaseException as exc:
        record.update(status="failed", error_type=type(exc).__name__)
    finally:
        if child is not None:
            try:
                if anchor is None:
                    raise ValueError("Launcher ownership was not observed")
                terminated_work = reconcile_child(child, anchor)
                if terminated_work and record["status"] == "completed":
                    record.update(status="failed", error_type="LiveWorkObservedDuringFinalization")
            except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired):
                record.update(status="unknown", uncertainty="Owned session termination/identity unconfirmed")
        elif launch_started:
            record.update(status="unknown", uncertainty="Launch interrupted before child identity was captured")
        record.update(elapsed_seconds=time.monotonic() - started, finished_at=time.time())
        with queue_lock(root, wait_seconds=5):
            current = read_record(path, record["project"], record["id"])
            if record["status"] != "unknown" and (interrupted_flag or current["status"] == "cancel_requested"):
                record["status"] = "cancelled"
            atomic_json(path, record)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["probe", "submit", "status", "cancel", "run"])
    parser.add_argument("job_file", nargs="?")
    parser.add_argument("--root")
    parser.add_argument("--project")
    parser.add_argument("--job")
    args = parser.parse_args()
    try:
        if args.action == "run":
            run_job(args.job_file)
            return 0
        if args.action == "probe":
            result = inventory()
        elif args.action == "submit":
            result = submit(Path(args.root), json.load(sys.stdin))
        elif args.action == "status":
            result = status(Path(args.root), args.project, args.job)
        else:
            result = cancel(Path(args.root), args.project, args.job)
        print(json.dumps(result, allow_nan=False))
        return 0
    except (OSError, ValueError, KeyError, TypeError):
        print(json.dumps({"status": "error", "reason": "Invalid request or unresolved server state"}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
