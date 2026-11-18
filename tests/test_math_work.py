"""Contract and idempotent return handling, not a proof checker."""
import copy
import importlib.util
from pathlib import Path
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "skills/research-navigate/scripts"
sys.path.insert(0, str(SCRIPTS))
import check_dispatch


def math_packet():
    return {
        "original_spec_ref": "brief#problem", "original_spec_revision": "1",
        "active_obligation": "O2", "parent_obligation": "O1",
        "parent_task_id": "P1", "return_to": "theory#O1",
        "continuation_owner": "coordinator", "theorem_uses": ["theory#import1"],
        "established_connection": ["local lemma"], "remaining_connection": ["actual input"],
        "next_discriminating_action": "check actual upstream output",
        "obstacle_id": "hard-core-1"
    }


class MathWorkTests(unittest.TestCase):
    def test_guard_rejects_malformed_optional_math_without_claiming_proof(self):
        # These calls may fail other capability checks, but must explain math errors.
        for value in ([], {}, dict(math_packet(), parent_task_id="child"),
                      dict(math_packet(), continuation_owner=["a", "b"]),
                      dict(math_packet(), theorem_uses="all papers")):
            with self.subTest(value=value):
                result = check_dispatch.check({"id": "child", "math_work": value})
                self.assertTrue(any("math_work" in e for e in result["errors"]))

    def test_returns_are_consumed_once_by_owner_and_keep_running_jobs(self):
        import math_work
        packet = math_packet()
        state = {"id": "P1", "math_work": packet, "consumed_returns": {},
                 "delegations": {"C4": copy.deepcopy(packet)},
                 "tasks": [{"id": "T5", "status": "pending"},
                           {"id": "T6", "status": "running", "revision": "v1"}]}
        event = {"id": "return-C4-v1", "parent_task_id": "P1",
                 "original_spec_ref": "brief#problem", "active_obligation": "O2",
                 "parent_obligation": "O1", "original_spec_revision": "1",
                 "return_to": "theory#O1", "artifact_refs": ["L4@v1"],
                 "connection_review_ref": "integrator#L4-check",
                 "supersedes_pending": ["T5", "T6"],
                 "next_action": "probe-hard-core-1", "child_task_id": "C4"}
        original = copy.deepcopy(state)
        changed, receipt = math_work.consume_return(state, event, "coordinator")
        self.assertEqual(state, original)
        self.assertEqual(changed["tasks"][0]["status"], "superseded")
        self.assertEqual(changed["tasks"][1], original["tasks"][1])
        self.assertEqual(receipt["next_action"], "probe-hard-core-1")
        self.assertFalse(receipt["executed"])
        repeated, receipt = math_work.consume_return(changed, event, "coordinator")
        self.assertEqual(repeated, changed)
        self.assertIsNone(receipt["next_action"])
        for wrong in (dict(event, original_spec_revision="2"),
                      dict(event, original_spec_ref="different-brief"),
                      dict(event, active_obligation="sibling-obligation"),
                      dict(event, child_task_id="never-dispatched"),
                      dict(event, parent_task_id="other"),
                      dict(event, parent_obligation="O9"),
                      dict(event, return_to="other")):
            with self.assertRaises(ValueError):
                math_work.consume_return(state, wrong, "coordinator")
        with self.assertRaises(ValueError):
            math_work.consume_return(state, event, "child")
        with self.assertRaises(ValueError):
            math_work.consume_return(changed, dict(event, next_action="another"), "coordinator")

    def test_parent_reference_not_only_revision_is_bound(self):
        import math_work
        work = math_packet()
        parent = copy.deepcopy(work)
        parent["original_spec_ref"] = "brief#different-problem"
        self.assertTrue(math_work.validate_math_work(
            {"id": "C4", "math_work": work, "parent_binding": parent}))

    def test_no_math_record_for_empirical_work(self):
        import math_work
        self.assertEqual(math_work.validate_math_work({"id": "empirical"}), [])


if __name__ == "__main__":
    unittest.main()
