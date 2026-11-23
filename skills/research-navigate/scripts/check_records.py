"""Lock and check the default research records (see references/records.md).

Structural checks only: they show whether the records are complete and
consistent with each other, not whether the science is right.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys

RUN_STATUS = {"completed", "failed", "interrupted", "cancelled", "unknown"}
DATA_KIND = {"measured", "synthetic", "illustrative"}
CLAIM_STATUS = {"supported", "limited", "contradicted", "unresolved"}
READ_DEPTH = {"full", "section", "abstract", "metadata", "none"}
VERIFIED = {"resolved", "title_mismatch", "unresolved", "unchecked"}
MILESTONES = ("M1", "M2", "M3", "M4", "M5")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def contained(root, relative):
    path = PurePosixPath(str(relative).replace("\\", "/"))
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValueError(f"Expected a project-relative path: {relative}")
    return Path(root, *path.parts)


def read_jsonl(path, problems, label):
    rows = []
    if not path.is_file():
        problems.append(f"{label}: missing {path.name}")
        return rows
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except ValueError:
            problems.append(f"{label}: line {number} is not JSON")
            continue
        if not isinstance(row, dict):
            problems.append(f"{label}: line {number} is not an object")
            continue
        rows.append(row)
    return rows


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def lock_protocol(project, protocol, approval):
    source = contained(project, protocol)
    if not source.is_file():
        raise ValueError("Protocol file not found")
    if not approval.strip():
        raise ValueError("Name the approval or delegation that covers this protocol")
    lock = source.with_suffix(".lock")
    record = {"protocol": str(PurePosixPath(protocol)), "sha256": sha256(source),
              "approval": approval, "locked_at": now()}
    if lock.exists():
        old = json.loads(lock.read_text(encoding="utf-8"))
        if old.get("sha256") != record["sha256"]:
            raise ValueError("A different revision is already locked; write a new protocol revision")
        return old
    lock.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


def lock_evaluator(project, files):
    record = {"files": {}, "locked_at": now()}
    for name in files:
        path = contained(project, name)
        if not path.is_file():
            raise ValueError(f"Evaluator file not found: {name}")
        record["files"][str(PurePosixPath(name))] = sha256(path)
    record["digest"] = evaluator_digest(record)
    target = Path(project, "research/protocol/evaluator.lock")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return record


def evaluator_digest(lock):
    return hashlib.sha256(json.dumps(lock.get("files", {}), sort_keys=True).encode()).hexdigest()


def check(project, milestone, cited_ids=()):
    project = Path(project)
    base = project / "research"
    problems = []
    level = MILESTONES.index(milestone) + 1

    state_path = base / "STATE.json"
    if not state_path.is_file():
        problems.append("STATE.json missing")
    else:
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
            for key in ("milestone", "next_action", "coverage"):
                if key not in state:
                    problems.append(f"STATE.json lacks {key}")
        except ValueError:
            problems.append("STATE.json is not JSON")

    if not (base / "brief.md").is_file():
        problems.append("brief.md missing")

    locks = sorted((base / "protocol").glob("P*.lock")) if (base / "protocol").is_dir() else []
    locked = {}
    for lock_path in locks:
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
        try:
            source = contained(project, lock["protocol"])
        except (KeyError, ValueError):
            problems.append(f"{lock_path.name}: invalid protocol path")
            continue
        if not source.is_file() or sha256(source) != lock.get("sha256"):
            problems.append(f"{lock_path.name}: protocol changed after locking")
        locked[lock.get("sha256")] = lock_path.stem
    if not locked:
        problems.append("No locked protocol (run lock-protocol after approval)")

    evaluator = None
    if level >= 2:
        lock_path = base / "protocol/evaluator.lock"
        if not lock_path.is_file():
            problems.append("evaluator.lock missing")
        else:
            evaluator = json.loads(lock_path.read_text(encoding="utf-8"))
            for name, digest in evaluator.get("files", {}).items():
                path = contained(project, name)
                if not path.is_file() or sha256(path) != digest:
                    problems.append(f"Evaluator file changed or missing: {name}")

    if level >= 3:
        runs = read_jsonl(base / "runs/ledger.jsonl", problems, "runs")
        by_id = {}
        for row in runs:
            rid = row.get("attempt_id")
            if not isinstance(rid, str) or rid in by_id:
                problems.append(f"runs: missing or duplicate attempt_id {rid!r}")
                continue
            by_id[rid] = row
            if row.get("status") not in RUN_STATUS:
                problems.append(f"runs: {rid} has invalid status")
            if row.get("data_kind") not in DATA_KIND:
                problems.append(f"runs: {rid} lacks data_kind")
            if row.get("protocol_sha256") not in locked:
                problems.append(f"runs: {rid} does not cite a locked protocol")
            if evaluator is not None and row.get("evaluator_sha256") not in (None, evaluator_digest(evaluator)):
                problems.append(f"runs: {rid} used a different evaluator")
        claims = read_jsonl(base / "analysis/claims.jsonl", problems, "claims")
        for row in claims:
            cid = row.get("claim_id", "?")
            if row.get("status") not in CLAIM_STATUS:
                problems.append(f"claims: {cid} has invalid status")
            if not isinstance(row.get("deviations"), list):
                problems.append(f"claims: {cid} must list deviations (empty if none)")
            if row.get("protocol_sha256") not in locked:
                problems.append(f"claims: {cid} does not cite a locked protocol")
            run_ids = row.get("run_ids")
            if row.get("status") in ("supported", "limited") and not run_ids and not row.get("source_ids"):
                problems.append(f"claims: {cid} is supported without runs or sources")
            for rid in run_ids or []:
                run = by_id.get(rid)
                if run is None:
                    problems.append(f"claims: {cid} cites unknown run {rid}")
                elif run.get("status") != "completed":
                    problems.append(f"claims: {cid} cites run {rid} with status {run.get('status')}")
                elif run.get("data_kind") != "measured" and row.get("data_kind") != run.get("data_kind"):
                    problems.append(f"claims: {cid} rests on {run.get('data_kind')} run {rid} without saying so")

    if level >= 4:
        sources = read_jsonl(base / "literature.jsonl", problems, "literature")
        status = {row.get("id"): row for row in sources}
        for row in sources:
            if row.get("read_depth") not in READ_DEPTH or row.get("verified") not in VERIFIED:
                problems.append(f"literature: {row.get('id')} lacks read_depth or verified")
        for cid in cited_ids:
            row = status.get(cid)
            if row is None:
                problems.append(f"Cited source {cid} is not in literature.jsonl")
            elif row.get("verified") != "resolved":
                problems.append(f"Cited source {cid} is {row.get('verified')}")
    return problems


def cited_keys(paths):
    import re
    keys = []
    pattern = re.compile(r"\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]+)\}")
    for path in paths:
        text = Path(path).read_text(encoding="utf-8", errors="replace")
        for group in pattern.findall(text):
            keys.extend(k.strip() for k in group.split(",") if k.strip())
    return sorted(set(keys))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    lp = commands.add_parser("lock-protocol")
    lp.add_argument("--project", type=Path, required=True)
    lp.add_argument("--protocol", required=True)
    lp.add_argument("--approval", required=True)
    le = commands.add_parser("lock-evaluator")
    le.add_argument("--project", type=Path, required=True)
    le.add_argument("files", nargs="+")
    ck = commands.add_parser("check")
    ck.add_argument("--project", type=Path, required=True)
    ck.add_argument("--milestone", choices=MILESTONES, required=True)
    ck.add_argument("--manuscript", nargs="*", default=[], help="LaTeX sources whose \\cite keys must be resolved")
    args = parser.parse_args(argv)
    try:
        if args.command == "lock-protocol":
            result = lock_protocol(args.project, args.protocol, args.approval)
        elif args.command == "lock-evaluator":
            result = lock_evaluator(args.project, args.files)
        else:
            problems = check(args.project, args.milestone, cited_keys(args.manuscript))
            result = {"milestone": args.milestone, "passed": not problems, "problems": problems}
    except (OSError, ValueError, KeyError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 2
    print(json.dumps(result, indent=2))
    return 0 if args.command != "check" or result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
