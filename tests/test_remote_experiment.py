import importlib.util
import hashlib
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/research-experiment/scripts"


def load_module(name):
    path = SCRIPTS / (name + ".py")
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def packet(job="job-1"):
    return {
        "project": "test-project", "id": job,
        "argv": ["python3", "-c", "print('done')"],
        "authority": "approved-test", "budget_id": "budget-1",
        "budget_run_seconds": 100, "timeout_seconds": 10,
        "resources": {"cpu": 1, "memory_mb": 64,
                      "gpus": [{"index": 0, "memory_mb": 128}]},
        "versions": {"workflow": "r1", "protocol": "p1", "code": "c1"},
        "outputs": []
    }


def capacity():
    return {"cpu": 4, "available_memory_mb": 1024,
            "gpus": [{"index": 0, "free_memory_mb": 1024}]}


class RemoteWorkerTests(unittest.TestCase):
    def setUp(self):
        self.worker = load_module("remote_worker")
        self.assertIsNotNone(self.worker, "The shared server job controller is missing")

    def test_gpu_and_cpu_can_be_shared(self):
        first = dict(packet(), status="running", elapsed_seconds=0)
        self.worker.admit(packet("job-2"), capacity(), [first])

    def test_active_reservations_count_against_memory(self):
        first = dict(packet(), status="running")
        first["resources"]["gpus"][0]["memory_mb"] = 950
        with self.assertRaises(ValueError):
            self.worker.admit(packet("job-2"), capacity(), [first])

    def test_unknown_jobs_block_expansion(self):
        first = dict(packet(), status="unknown")
        with self.assertRaises(ValueError):
            self.worker.admit(packet("job-2"), capacity(), [first])

    def test_budget_counts_consumed_and_committed(self):
        first = dict(packet(), status="completed", elapsed_seconds=95)
        with self.assertRaises(ValueError):
            self.worker.admit(packet("job-2"), capacity(), [first])

    def test_missing_gpu_is_not_free_gpu(self):
        inventory = capacity()
        inventory["gpus"] = []
        with self.assertRaises(ValueError):
            self.worker.admit(packet(), inventory, [])

    def test_invalid_resources_and_path_ids_fail(self):
        for value in (True, -1, 0, float("nan"), "1"):
            p = packet()
            p["resources"]["cpu"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.worker.validate_packet(p)
        for field in ("project", "id"):
            p = packet()
            p[field] = "../escape"
            with self.assertRaises(ValueError):
                self.worker.validate_packet(p)

    def test_provenance_and_authority_are_required(self):
        for field in ("authority", "versions", "budget_id"):
            p = packet()
            p.pop(field)
            with self.assertRaises(ValueError):
                self.worker.validate_packet(p)

    def test_duplicate_identity_does_not_launch_again(self):
        with tempfile.TemporaryDirectory(dir=ROOT / ".build") as folder:
            launched = []
            def launch(job_file):
                launched.append(str(job_file))
                return {"pid": 99999999, "process_start": "test"}
            first = self.worker.submit(Path(folder), packet(), capacity(), launch=launch)
            again = self.worker.submit(Path(folder), packet(), capacity(), launch=launch)
            self.assertEqual(first["id"], again["id"])
            self.assertEqual(len(launched), 1)
            changed = packet()
            changed["argv"] = ["different"]
            with self.assertRaises(ValueError):
                self.worker.submit(Path(folder), changed, capacity(), launch=launch)

    def test_delimiter_collision_jobs_have_independent_records(self):
        with tempfile.TemporaryDirectory(dir=ROOT / ".build") as folder:
            root = Path(folder)
            first, second = packet("c"), packet("b--c")
            first["project"], second["project"] = "team--b", "team"
            launched = []
            def launch(path):
                launched.append(path)
                return {"pid": 123, "process_start": "fixture"}
            with patch.object(self.worker, "alive", return_value=True):
                self.worker.submit(root, first, capacity(), launch)
                self.worker.submit(root, second, capacity(), launch)
                for p in (first, second):
                    got = self.worker.status(root, p["project"], p["id"])
                    self.assertEqual((got["project"], got["id"]), (p["project"], p["id"]))
            self.assertEqual(len(set(launched)), 2)

    def test_completed_legacy_smoke_jobs_remain_readable_without_resubmission(self):
        with tempfile.TemporaryDirectory(dir=ROOT / ".build") as folder:
            root = Path(folder)
            (root / ".jobs").mkdir()
            for job in ("shared-smoke-a", "shared-smoke-b"):
                p = packet(job)
                p["project"] = "workflow-validation-20261024"
                record = dict(p, status="completed", elapsed_seconds=1,
                              packet_sha256=hashlib.sha256(json.dumps(
                                  p, sort_keys=True, allow_nan=False).encode()).hexdigest())
                path = root / ".jobs" / (p["project"] + "--" + job + ".json")
                path.write_text(json.dumps(record))
                before = path.read_bytes()
                with patch.object(self.worker, "launch_supervisor", side_effect=AssertionError("resubmit")):
                    self.assertEqual(self.worker.status(root, p["project"], job), record)
                    self.assertEqual(self.worker.cancel(root, p["project"], job), record)
                    self.assertEqual(self.worker.submit(root, p, capacity()), record)
                self.assertEqual(path.read_bytes(), before)
            self.assertEqual(len(list((root / ".jobs").glob("*.json"))), 2)

    def test_colliding_legacy_lookup_cannot_read_or_cancel_other_job(self):
        with tempfile.TemporaryDirectory(dir=ROOT / ".build") as folder:
            root = Path(folder)
            (root / ".jobs").mkdir()
            path = root / ".jobs/team--b--c.json"
            path.write_text(json.dumps(dict(packet("c"), project="team--b", status="completed")))
            before = path.read_bytes()
            for operation in (self.worker.status, self.worker.cancel):
                with self.subTest(operation=operation.__name__), self.assertRaises((ValueError, FileNotFoundError)):
                    operation(root, "team", "b--c")
            self.assertEqual(path.read_bytes(), before)

    def test_canonical_record_with_wrong_stored_identity_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=ROOT / ".build") as folder:
            root = Path(folder)
            path = self.worker.record_path(root, "test-project", "job-1")
            path.parent.mkdir()
            path.write_text(json.dumps(dict(packet("other"), status="completed")))
            for operation in (self.worker.status, self.worker.cancel):
                with self.subTest(operation=operation.__name__), self.assertRaises(ValueError):
                    operation(root, "test-project", "job-1")

    def test_live_matching_legacy_record_is_not_renamed_or_relaunched(self):
        with tempfile.TemporaryDirectory(dir=ROOT / ".build") as folder:
            root = Path(folder)
            p = packet()
            path = root / ".jobs/test-project--job-1.json"
            path.parent.mkdir()
            record = dict(p, status="running", pid=123, process_start="fixture",
                          packet_sha256=hashlib.sha256(json.dumps(p, sort_keys=True).encode()).hexdigest())
            path.write_text(json.dumps(record))
            before = path.read_bytes()
            with patch.object(self.worker, "alive", return_value=True), \
                    patch.object(self.worker, "launch_supervisor", side_effect=AssertionError("resubmit")), \
                    patch.object(self.worker.os, "kill", side_effect=AssertionError("unsafe signal")):
                self.assertEqual(self.worker.status(root, "test-project", "job-1"), record)
                self.assertEqual(self.worker.submit(root, p, capacity()), record)
                with self.assertRaisesRegex(ValueError, "Legacy"):
                    self.worker.cancel(root, "test-project", "job-1")
            self.assertEqual(path.read_bytes(), before)
            self.assertFalse(self.worker.record_path(root, "test-project", "job-1").exists())

    def test_duplicate_canonical_and_legacy_records_block_ambiguous_lookup(self):
        with tempfile.TemporaryDirectory(dir=ROOT / ".build") as folder:
            root = Path(folder)
            path = self.worker.record_path(root, "test-project", "job-1")
            path.parent.mkdir()
            record = dict(packet(), status="completed")
            path.write_text(json.dumps(record))
            path.with_name("test-project--job-1.json").write_text(json.dumps(record))
            with self.assertRaises(ValueError):
                self.worker.status(root, "test-project", "job-1")

    def test_launch_failure_retains_unknown_commitment(self):
        with tempfile.TemporaryDirectory(dir=ROOT / ".build") as folder:
            def fail(_):
                raise OSError("simulated transport boundary")
            with self.assertRaises(OSError):
                self.worker.submit(Path(folder), packet(), capacity(), launch=fail)
            record = json.loads(self.worker.record_path(Path(folder), "test-project", "job-1").read_text())
            self.assertEqual(record["status"], "unknown")

    def test_lock_prevents_parallel_admission_race(self):
        with tempfile.TemporaryDirectory(dir=ROOT / ".build") as folder:
            root = Path(folder)
            root.mkdir(exist_ok=True)
            (root / ".queue.lock").write_text("another coordinator")
            with self.assertRaises(ValueError):
                self.worker.submit(root, packet(), capacity(), launch=lambda _: {})


class RemoteSupervisorTests(unittest.TestCase):
    """Real records and /proc fixtures, with only Linux process/syscall boundaries faked."""

    def setUp(self):
        self.worker = load_module("remote_worker")
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / ".build")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.proc = self.root / "proc"
        self.proc.mkdir()
        self.clock = 0
        self.signals = []
        self.reaped = False
        self.cancel_on_launch = False
        self.on_sleep = lambda: None
        self.handlers = {}
        self.leader, self.descendant, self.outsider = 4100, 4101, 9000
        self.process(self.leader, "Z", os.getpid(), self.leader, self.leader, 100)
        self.process(self.descendant, "S", self.leader, self.leader, self.leader, 101)
        self.process(self.outsider, "S", 1, self.outsider, self.outsider, 200)
        p = packet()
        p["timeout_seconds"] = 0.1
        self.path = self.worker.record_path(self.root, p["project"], p["id"])
        self.path.parent.mkdir()
        run_dir = self.root / p["project"] / "runs" / p["id"]
        run_dir.mkdir(parents=True)
        self.record = dict(p, root=str(self.root), run_dir=str(run_dir),
                           status="reserved", pid=os.getpid(), process_start="supervisor",
                           controller_protocol=2)
        self.worker.atomic_json(self.path, self.record)
        self.child = SimpleNamespace(pid=self.leader, wait=self.reap, poll=self.poll)

    def process(self, pid, state, parent, group, session, start):
        folder = self.proc / str(pid)
        folder.mkdir(exist_ok=True)
        fields = [state, str(parent), str(group), str(session)] + ["0"] * 15 + [str(start)]
        (folder / "stat").write_text(str(pid) + " (worker with ) space) " + " ".join(fields))

    def fields(self, pid):
        return (self.proc / str(pid) / "stat").read_text().rsplit(")", 1)[1].split()

    def zombie(self, pid):
        f = self.fields(pid)
        self.process(pid, "Z", int(f[1]), int(f[2]), int(f[3]), int(f[19]))

    def reap(self, timeout=None):
        self.reaped = True
        (self.proc / str(self.leader) / "stat").unlink()
        return 0

    def poll(self):
        return 0 if self.reaped else None

    def waitid(self, kind, pid, flags):
        if self.reaped:
            raise ChildProcessError("already reaped")
        if self.fields(pid)[0] == "Z":
            return SimpleNamespace(si_pid=pid, si_code=1, si_status=0)
        return None

    def killpg(self, group, sig):
        # Reaping the launcher before signaling would allow its numeric group ID to be reused.
        self.assertFalse(self.reaped)
        self.assertEqual(group, self.leader)
        self.signals.append((group, sig))
        for folder in self.proc.iterdir():
            if (folder / "stat").exists() and int(self.fields(int(folder.name))[2]) == group:
                self.zombie(int(folder.name))

    def sleep(self, duration):
        self.clock += duration
        self.on_sleep()

    def launch(self, *args, **kwargs):
        self.assertTrue(kwargs["start_new_session"])
        if self.cancel_on_launch:
            self.handlers[self.worker.signal.SIGTERM](None, None)
        return self.child

    def run_supervisor(self):
        from contextlib import ExitStack
        with ExitStack() as stack:
            def mocked(obj, name, value):
                return stack.enter_context(patch.object(obj, name, value, create=True))
            mocked(self.worker, "PROC", self.proc)
            mocked(self.worker, "process_start", lambda pid: "supervisor")
            mocked(self.worker.subprocess, "Popen", self.launch)
            mocked(self.worker.signal, "signal", lambda sig, fn: self.handlers.update({sig: fn}))
            mocked(self.worker.signal, "getsignal", lambda sig: self.worker.signal.SIG_DFL)
            mocked(self.worker.signal, "SIGKILL", 9)
            mocked(self.worker.os, "waitid", self.waitid)
            for name, value in (("P_PID", 1), ("WEXITED", 4), ("WNOHANG", 1), ("WNOWAIT", 0x1000000), ("CLD_EXITED", 1)):
                mocked(self.worker.os, name, value)
            mocked(self.worker.os, "killpg", self.killpg)
            mocked(self.worker.os, "kill", lambda *a: self.fail("numeric PID signal"))
            mocked(self.worker.time, "monotonic", lambda: self.clock)
            mocked(self.worker.time, "sleep", self.sleep)
            self.worker.run_job(self.path)
        return json.loads(self.path.read_text())

    def test_exited_launcher_does_not_release_living_descendants(self):
        result = self.run_supervisor()
        self.assertEqual(result["status"], "timed_out")
        self.assertEqual(self.fields(self.descendant)[0], "Z")
        self.assertEqual(self.fields(self.outsider)[0], "S")
        self.assertTrue(self.reaped)

    def test_descendants_finishing_within_deadline_complete_without_signal(self):
        self.on_sleep = lambda: self.zombie(self.descendant)
        result = self.run_supervisor()
        self.assertEqual(result["status"], "completed")
        self.assertGreater(self.clock, 0)
        self.assertEqual(self.signals, [])

    def test_cancel_during_launch_keeps_child_handle_for_group_cleanup(self):
        self.cancel_on_launch = True
        result = self.run_supervisor()
        self.assertEqual(result["status"], "cancelled")
        self.assertEqual(self.fields(self.descendant)[0], "Z")
        self.assertEqual(self.fields(self.outsider)[0], "S")

    def test_other_group_in_owned_session_retains_unknown_without_unsafe_signal(self):
        self.process(self.descendant, "S", self.leader, self.descendant, self.leader, 101)
        result = self.run_supervisor()
        self.assertEqual(result["status"], "unknown")
        self.assertEqual(self.fields(self.descendant)[0], "S")
        self.assertEqual(self.signals, [])

    def test_reused_launcher_identity_is_not_signalled(self):
        self.on_sleep = lambda: self.process(self.leader, "S", 1, self.leader, self.leader, 999)
        result = self.run_supervisor()
        self.assertEqual(result["status"], "unknown")
        self.assertEqual(self.signals, [])

    def test_cancel_before_launch_never_starts_work(self):
        self.record["status"] = "cancel_requested"
        self.worker.atomic_json(self.path, self.record)
        self.launch = lambda *a, **k: self.fail("cancelled job launched")
        result = self.run_supervisor()
        self.assertEqual(result["status"], "cancelled")

    def test_mailbox_cancellation_does_not_signal_a_numeric_supervisor_pid(self):
        with patch.object(self.worker, "alive", return_value=True), \
                patch.object(self.worker.os, "kill", side_effect=AssertionError("PID signal")):
            result = self.worker.cancel(self.root, "test-project", "job-1")
        self.assertEqual(result["status"], "cancel_requested")
        self.assertEqual(json.loads(self.path.read_text())["status"], "cancel_requested")

    def test_mailbox_cancel_with_exited_launcher_terminates_remaining_work(self):
        def request_cancel():
            current = json.loads(self.path.read_text())
            current["status"] = "cancel_requested"
            self.worker.atomic_json(self.path, current)
        self.on_sleep = request_cancel
        result = self.run_supervisor()
        self.assertEqual(result["status"], "cancelled")
        self.assertEqual(self.fields(self.descendant)[0], "Z")
        self.assertEqual(self.fields(self.outsider)[0], "S")

    def test_launcher_exit_at_timeout_still_reconciles_descendants(self):
        self.process(self.leader, "S", os.getpid(), self.leader, self.leader, 100)
        def exit_at_deadline():
            if self.clock >= 0.1:
                self.zombie(self.leader)
        self.on_sleep = exit_at_deadline
        result = self.run_supervisor()
        self.assertEqual(result["status"], "timed_out")
        self.assertEqual(self.fields(self.descendant)[0], "Z")

    def test_unconfirmed_group_termination_keeps_budget_reserved(self):
        self.killpg = lambda group, sig: self.signals.append((group, sig))
        result = self.run_supervisor()
        self.assertEqual(result["status"], "unknown")
        self.assertEqual(self.fields(self.descendant)[0], "S")
        with self.assertRaises(ValueError):
            self.worker.admit(packet("next"), capacity(), [result])
        self.assertLess(self.clock, 5.3)

    def test_incomplete_proc_inventory_retains_unknown_without_signalling(self):
        iterdir = Path.iterdir
        def denied(path):
            if path == self.proc:
                raise PermissionError("incomplete process inventory")
            return iterdir(path)
        with patch.object(Path, "iterdir", denied):
            result = self.run_supervisor()
        self.assertEqual(result["status"], "unknown")
        self.assertEqual(self.signals, [])

    def test_already_reaped_launcher_cannot_authorize_a_group_signal(self):
        def no_child(*args):
            raise ChildProcessError("not our unreaped child")
        self.waitid = no_child
        result = self.run_supervisor()
        self.assertEqual(result["status"], "unknown")
        self.assertEqual(self.signals, [])

    def test_duplicate_supervisor_run_cannot_restart_a_terminal_job(self):
        self.record["status"] = "completed"
        self.worker.atomic_json(self.path, self.record)
        self.launch = lambda *a, **k: self.fail("completed job relaunched")
        with self.assertRaises(ValueError):
            self.run_supervisor()
        self.assertEqual(json.loads(self.path.read_text())["status"], "completed")

    def test_late_observed_worker_cleanup_cannot_be_reported_as_success(self):
        iterdir = Path.iterdir
        scans = []
        def late_worker(path):
            entries = list(iterdir(path))
            if path == self.proc:
                scans.append(1)
                if len(scans) == 1:
                    return iter(p for p in entries if p.name != str(self.descendant))
            return iter(entries)
        with patch.object(Path, "iterdir", late_worker):
            result = self.run_supervisor()
        self.assertNotEqual(result["status"], "completed")
        self.assertEqual(self.fields(self.descendant)[0], "Z")


class RemoteClientTests(unittest.TestCase):
    def setUp(self):
        self.client = load_module("remote_experiment")
        self.assertIsNotNone(self.client, "The SSH adapter is missing")

    def test_profile_has_no_inline_secret(self):
        profile = {
            "id": "host", "host": "127.0.0.1", "port": 22, "user": "root",
            "root": "/root/research-workspaces",
            "credential_ref": "wincred:research/server",
            "host_key_sha256": "SHA256:abc"
        }
        self.client.validate_profile(profile)
        profile["password"] = "not-allowed"
        with self.assertRaises(ValueError):
            self.client.validate_profile(profile)

    def test_cross_platform_credential_references(self):
        profile = {"id": "host", "host": "127.0.0.1", "port": 22, "user": "root",
                   "root": "/root/research-workspaces", "host_key_sha256": "SHA256:abc"}
        for ref in ("ssh-agent:", "keyfile:~/.ssh/id_ed25519", "wincred:research/server"):
            with self.subTest(ref=ref):
                self.client.validate_profile(dict(profile, credential_ref=ref))
        for ref in ("keyfile:", "agent", "wincred:other/x", "password:abc"):
            with self.subTest(ref=ref), self.assertRaises(ValueError):
                self.client.validate_profile(dict(profile, credential_ref=ref))

    def test_agent_and_keyfile_authentication(self):
        paramiko = MagicMock()
        paramiko.AuthenticationException = type("AuthenticationException", (Exception,), {})
        paramiko.PasswordRequiredException = type("PasswordRequiredException", (Exception,), {})
        rejected, accepted = object(), object()
        paramiko.Agent.return_value.get_keys.return_value = [rejected, accepted]
        transport = MagicMock()
        transport.auth_publickey.side_effect = lambda user, key: (
            (_ for _ in ()).throw(paramiko.AuthenticationException()) if key is rejected else None)
        self.client.authenticate_transport(paramiko, transport, {"user": "u", "credential_ref": "ssh-agent:"})
        self.assertIs(transport.auth_publickey.call_args.args[1], accepted)
        paramiko.Agent.return_value.get_keys.return_value = []
        with self.assertRaises(ValueError):
            self.client.authenticate_transport(paramiko, transport, {"user": "u", "credential_ref": "ssh-agent:"})
        paramiko.PKey.from_path.side_effect = paramiko.PasswordRequiredException()
        with self.assertRaises(ValueError):
            self.client.authenticate_transport(paramiko, MagicMock(),
                                               {"user": "u", "credential_ref": "keyfile:/k"})

    def test_unpinned_host_is_only_probeable(self):
        profile = {
            "id": "host", "host": "127.0.0.1", "port": 22, "user": "root",
            "root": "/root/research-workspaces",
            "credential_ref": "wincred:research/server"
        }
        self.client.validate_profile(profile, require_pin=False)
        with self.assertRaises(ValueError):
            self.client.validate_profile(profile)

    def test_relative_transfers_reject_escape(self):
        for bad in ("../secret", "/root/secret", "a/../../b", "a\\b", ""):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self.client.relative_path(bad)
        self.assertEqual(self.client.relative_path("results/table.json"), "results/table.json")

    def test_upload_uses_writable_exclusive_staging_and_atomic_publish(self):
        from unittest.mock import patch
        sftp = MagicMock()
        sftp.lstat.side_effect = FileNotFoundError
        with patch.object(self.client, "mkdirs"):
            self.client.upload_new(sftp, "/owned/file", b"content")
        staging, mode = sftp.open.call_args.args
        self.assertIn("w", mode)
        self.assertIn("x", mode)
        self.assertNotEqual(staging, "/owned/file")
        sftp.rename.assert_called_once_with(staging, "/owned/file")


if __name__ == "__main__":
    unittest.main()
