"""Inspect/resume one explicitly authorized blocked native Goal through app-server.

No database writes, thread turns, model requests, budget changes or automatic
retries. A successful status change is not evidence of a later automatic turn.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import queue
import subprocess
import threading
import time


def project(result):
    goal = result.get("goal") if isinstance(result, dict) else None
    if not isinstance(goal, dict) or not isinstance(goal.get("objective"), str):
        return {"goal": None}
    return {
        "goal": {key: goal.get(key) for key in (
            "threadId", "status", "tokenBudget", "tokensUsed",
            "timeUsedSeconds", "createdAt", "updatedAt")},
        "objective_sha256": hashlib.sha256(goal["objective"].encode()).hexdigest(),
    }


def recover(request, thread_id, *, resume=False, authority=None):
    record = {
        "schema_version": 1, "checked_at": datetime.now(timezone.utc).isoformat(),
        "transport": "official app-server", "resume_requested": resume,
        "authority_ref": authority, "inference_requested": False,
        "thread_turn_requested": False, "automatic_continuation_observed": False,
    }
    if resume and (not isinstance(authority, str) or not authority.strip()):
        return dict(record, status="authorization_required")
    try:
        before = request("thread/goal/get", {"threadId": thread_id})
    except Exception:
        return dict(record, status="read_unavailable")
    record["before"] = project(before)
    goal = before.get("goal") if isinstance(before, dict) else None
    if not isinstance(goal, dict) or not isinstance(goal.get("objective"), str):
        return dict(record, status="goal_unavailable")
    if not resume:
        return dict(record, status="read_only")
    if goal.get("status") != "blocked":
        return dict(record, status="not_blocked")
    mutation = None
    mutation_unknown = False
    try:
        mutation = request("thread/goal/set", {
            "threadId": thread_id, "status": "active", "origin": "user"})
    except Exception:
        # A transport failure cannot establish whether the server applied the write.
        mutation_unknown = True
    error = mutation.get("error") if isinstance(mutation, dict) else None
    if isinstance(error, dict):
        record["rpc_error_code"] = error.get("code")
        busy = "active writer" in str(error.get("message", "")).lower()
    else:
        busy = False
    record["mutation_response_observed"] = mutation is not None
    try:
        after = request("thread/goal/get", {"threadId": thread_id})
    except Exception:
        return dict(record, status="mutation_unconfirmed")
    record["after"] = project(after)
    new = after.get("goal") if isinstance(after, dict) else None
    if not isinstance(new, dict):
        return dict(record, status="mutation_unconfirmed")
    record["preserved_objective_and_budget"] = all(
        new.get(key) == goal.get(key) for key in ("objective", "createdAt", "tokenBudget"))
    record["usage_not_reset"] = all(
        isinstance(new.get(key), (int, float))
        and isinstance(goal.get(key), (int, float))
        and new[key] >= goal[key] for key in ("tokensUsed", "timeUsedSeconds"))
    if not record["preserved_objective_and_budget"] or not record["usage_not_reset"]:
        return dict(record, status="state_conflict")
    if busy:
        return dict(record, status="wait_for_writer")
    if new.get("status") == "active":
        return dict(record, status="active_observed",
                    mutation_response_missing=mutation_unknown)
    return dict(record, status="mutation_unconfirmed" if mutation_unknown else "resume_rejected")


class AppServer:
    def __init__(self, binary):
        self.process = subprocess.Popen(
            [str(binary), "app-server", "--stdio"], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
            encoding="utf-8", errors="replace",
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        self.messages = queue.Queue()
        self.serial = 0
        threading.Thread(target=self._read, daemon=True).start()

    def _read(self):
        for line in self.process.stdout:
            try:
                self.messages.put(json.loads(line))
            except ValueError:
                continue

    def request(self, method, params):
        self.serial += 1
        self.process.stdin.write(json.dumps({
            "jsonrpc": "2.0", "id": self.serial, "method": method, "params": params}) + "\n")
        self.process.stdin.flush()
        deadline = time.monotonic() + 35
        while time.monotonic() < deadline:
            try:
                message = self.messages.get(timeout=min(1, max(.01, deadline-time.monotonic())))
            except queue.Empty:
                if self.process.poll() is not None:
                    raise RuntimeError("app_server_exited")
                continue
            if message.get("id") == self.serial:
                return message if "error" in message else message.get("result")
        raise TimeoutError("response_unobserved")

    def initialize(self):
        response = self.request("initialize", {
            "clientInfo": {"name": "research_goal_recovery", "version": "1"},
            "capabilities": {"experimentalApi": True}})
        if not isinstance(response, dict) or "error" in response:
            raise RuntimeError("initialization_unavailable")
        self.process.stdin.write('{"jsonrpc":"2.0","method":"initialized"}\n')
        self.process.stdin.flush()

    def close(self):
        if self.process.poll() is None:
            self.process.stdin.close()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.terminate()
                self.process.wait(timeout=5)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--thread", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--authority")
    args = parser.parse_args()
    if args.resume and not args.authority:
        parser.error("--resume requires the actual explicit user request reference")
    if not args.binary.is_file():
        parser.error("The supplied host binary is unavailable")
    # Reserve the receipt first: a failed exclusive open must precede any mutation.
    with args.output.open("x", encoding="utf-8") as stream:
        server = None
        try:
            server = AppServer(args.binary)
            server.initialize()
            record = recover(server.request, args.thread, resume=args.resume, authority=args.authority)
        except Exception:
            record = {"status": "transport_unavailable", "automatic_continuation_observed": False}
        finally:
            if server is not None:
                server.close()
        stream.write(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))
    return 0 if record["status"] in ("read_only", "active_observed", "not_blocked") else 2


if __name__ == "__main__":
    raise SystemExit(main())
