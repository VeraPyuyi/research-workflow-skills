"""Native Goal resume tests use a fake RPC, never a host database."""
import importlib.util
from pathlib import Path
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "skills/research-navigate/scripts/goal_recovery.py"


class GoalRecoveryTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location("goal_recovery", SCRIPT)
        self.api = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.api)
        self.goal = dict(threadId="synthetic-chat", status="blocked",
                         objective="Private objective", tokenBudget=30000,
                         tokensUsed=200, timeUsedSeconds=30, createdAt=10, updatedAt=20)
        self.calls = []

    def rpc(self, method, params):
        self.calls.append((method, params))
        if method == "thread/goal/set":
            self.goal.update(status="active", updatedAt=25)
        return {"goal": dict(self.goal)}

    def recover(self, **kwargs):
        return self.api.recover(self.rpc, "synthetic-chat", **kwargs)

    def test_read_only_default_never_mutates(self):
        result = self.recover()
        self.assertEqual("blocked", result["before"]["goal"]["status"])
        self.assertNotIn("Private objective", str(result))
        self.assertEqual(["thread/goal/get"], [m for m, _ in self.calls])

    def test_resume_requires_explicit_authority_reference(self):
        result = self.recover(resume=True)
        self.assertEqual("authorization_required", result["status"])
        self.assertEqual([], self.calls)

    def test_resume_preserves_objective_and_budget_and_usage(self):
        result = self.recover(resume=True, authority="user-request")
        self.assertEqual("active_observed", result["status"])
        self.assertTrue(result["preserved_objective_and_budget"])
        self.assertFalse(result["automatic_continuation_observed"])
        self.assertEqual({"threadId": "synthetic-chat", "status": "active", "origin": "user"},
                         self.calls[1][1])

    def test_busy_writer_is_deferred_without_retry(self):
        def busy(method, params):
            self.calls.append((method, params))
            if method == "thread/goal/set":
                return {"error": {"code": -32603, "message": "private-path already has an active writer"}}
            return {"goal": dict(self.goal)}
        result = self.api.recover(busy, "synthetic-chat", resume=True, authority="user-request")
        self.assertEqual("wait_for_writer", result["status"])
        self.assertNotIn("private-path", str(result))
        self.assertEqual(1, sum(m == "thread/goal/set" for m, _ in self.calls))

    def test_timeout_reads_status_once_without_duplicate_mutation(self):
        def unknown(method, params):
            if method == "thread/goal/set":
                self.calls.append((method, params))
                raise TimeoutError()
            return self.rpc(method, params)
        result = self.api.recover(unknown, "synthetic-chat", resume=True, authority="user-request")
        self.assertEqual("mutation_unconfirmed", result["status"])
        self.assertEqual(1, sum(m == "thread/goal/set" for m, _ in self.calls))

    def test_does_not_reactivate_paused_complete_or_limited_goals(self):
        for status in ("paused", "complete", "usageLimited", "budgetLimited", "active"):
            with self.subTest(status=status):
                self.goal["status"] = status
                self.calls.clear()
                result = self.recover(resume=True, authority="user-request")
                self.assertEqual("not_blocked", result["status"])
                self.assertEqual(["thread/goal/get"], [m for m, _ in self.calls])

    def test_unexpected_objective_change_is_not_success(self):
        def changed(method, params):
            response = self.rpc(method, params)
            if method == "thread/goal/set":
                self.goal["objective"] = "Changed outside caller"
            return response
        result = self.api.recover(changed, "synthetic-chat", resume=True, authority="user-request")
        self.assertEqual("state_conflict", result["status"])


if __name__ == "__main__":
    unittest.main()
