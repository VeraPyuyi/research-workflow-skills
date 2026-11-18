import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class OptimizerTests(unittest.TestCase):
    def setUp(self):
        (ROOT / ".build").mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / ".build")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        script = ROOT / "skills/research-optimize/scripts/optimize_workflow.py"
        self.assertTrue(script.exists(), "Optimizer runtime is missing")
        spec = importlib.util.spec_from_file_location("optimizer", script)
        self.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.m)
        self.write("baseline/skill.txt", "baseline")
        self.write("candidate/skill.txt", "improved")
        self.write("usage.json", {"model": {"spent": 0, "reserved": 0},
                                 "time": {"spent": 0, "reserved": 0}})
        self.write("criteria.json", {
            "cases": [{"id": "core", "held_out": False}, {"id": "held", "held_out": True}],
            "strengths": ["preserve-negative-results"],
            "metrics": [{"id": "duplicate-searches", "direction": "lower",
                         "source": "task-outcome"}],
        })
        self.contract = {
            "project": "test", "goal": "deliver paper", "authority_ref": "user-plan",
            "baseline": "baseline", "criteria": "criteria.json", "project_usage": "usage.json",
            "budgets": {"model": {"limit": 100, "unit": "units"},
                        "time": {"limit": 1000, "unit": "seconds"}},
        }
        self.write("contract.json", self.contract)
        self.state = self.root / "optimizer.json"
        self.m.operate(self.root, self.state, "init", {"contract": "contract.json"}, apply=True)

    def write(self, path, value):
        dest = self.root / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(value) if isinstance(value, (dict, list)) else value)
        return dest

    def op(self, action, packet):
        return self.m.operate(self.root, self.state, action, packet, apply=True)

    def reserve(self, cid="c1", cost=2, milestone="M1"):
        return self.op("candidate", {"id": cid, "milestone": milestone,
                                    "path": "candidate", "author_model": "gpt-6.1-sol",
                                    "author_context": "author-1",
                                    "cost": {"model": cost, "time": 5}})

    def settle(self, cid="c1", cost=2):
        result = self.op("settle", {"id": cid, "milestone": "M1",
                                   "actual_cost": {"model": cost, "time": 5}})
        self.op("freeze", {"id": cid, "milestone": "M1"})
        return result

    def validation(self):
        state = json.loads(self.state.read_text())
        candidate = state["milestones"]["M1"]["candidates"]["c1"]
        self.write("evidence/run.json", {"actual": "synthetic observed output"})
        artifact = {"path": "evidence/run.json",
                    "sha256": self.m.content_hash(self.root / "evidence/run.json")}
        report = {
            "baseline_sha256": state["baseline_sha256"],
            "criteria_sha256": state["criteria_sha256"],
            "candidate_sha256": candidate["sha256"],
            "cases": {x: {"passed": True, "artifact": artifact} for x in ("core", "held")},
            "strengths": {"preserve-negative-results": {"preserved": True, "artifact": artifact}},
            "measurements": {"duplicate-searches": {"baseline": 3, "candidate": 1, "artifact": artifact}},
            "review": {"reviewer_model": "gpt-6-astra", "context_id": "reviewer-2",
                       "findings_resolved": True, "artifact": artifact},
            "cost_evidence": artifact,
        }
        self.write("validation.json", report)
        return report

    def test_event_deduplication_and_self_recursion(self):
        event = {"stage": "research-survey", "round": "R2", "revision": "S3",
                 "strengths": ["theorem mapping"], "weaknesses": ["duplicate search"],
                 "artifact_refs": ["survey:S3"], "coverage": "supplied artifacts",
                 "actual_cost": {"model": 1, "time": 3}}
        self.op("event", event)
        before = self.state.read_bytes()
        self.op("event", event)
        self.assertEqual(before, self.state.read_bytes())
        event["stage"] = "research-optimize"
        self.op("event", event)
        self.assertEqual(before, self.state.read_bytes())

    def test_twenty_percent_counts_spent_and_reserved(self):
        self.reserve("c1", 7)
        self.settle(cost=7)
        self.reserve("c2", 11)
        with self.assertRaises(ValueError):
            self.reserve("c3", 3)
        self.reserve("c3", 2)

    def test_whole_project_budget_is_also_respected(self):
        self.write("usage.json", {"model": {"spent": 99, "reserved": 0},
                                 "time": {"spent": 0, "reserved": 0}})
        with self.assertRaises(ValueError):
            self.reserve(cost=2)

    def test_numbers_are_strict_and_unknown_budget_cannot_spend(self):
        for n in (True, "2", -1, float("nan")):
            with self.subTest(n=n), self.assertRaises(ValueError):
                self.reserve(cost=n)
        self.contract["budgets"]["model"]["limit"] = None
        self.write("unknown-contract.json", self.contract)
        state = self.root / "unknown-state.json"
        self.m.operate(self.root, state, "init", {"contract": "unknown-contract.json"}, apply=True)
        with self.assertRaises(ValueError):
            self.m.operate(self.root, state, "candidate",
                          {"id": "c", "milestone": "M1", "path": "candidate",
                           "author_model": "gpt-6.1-sol", "author_context": "a",
                           "cost": {"model": 1, "time": 1}}, apply=True)

    def test_frozen_contract_and_criteria_cannot_be_relaxed(self):
        self.contract["budgets"]["model"]["limit"] = 1000
        self.write("contract.json", self.contract)
        with self.assertRaises(ValueError):
            self.reserve()

    def test_three_candidates_and_one_revision(self):
        for cid in ("c1", "c2", "c3"):
            self.reserve(cid, 1)
        with self.assertRaises(ValueError):
            self.reserve("c4", 1)
        self.settle(cost=1)
        self.op("revise", {"id": "c1", "milestone": "M1", "cost": {"model": 1, "time": 1}})
        self.write("candidate/skill.txt", "revised")
        self.settle(cost=1)
        with self.assertRaises(ValueError):
            self.op("revise", {"id": "c1", "milestone": "M1", "cost": {"model": 1, "time": 1}})

    def test_actual_overrun_is_recorded_and_blocks_more_work(self):
        self.reserve(cost=1)
        self.settle(cost=21)
        self.assertEqual(json.loads(self.state.read_text())["spent"]["model"], 21)
        with self.assertRaises(ValueError):
            self.reserve("c2", 1)

    def test_small_consumed_cost_is_not_rounded_out_of_budget(self):
        self.reserve("c1", 1e-100)
        self.settle("c1", 1e-100)
        self.reserve("c2", 1)
        self.settle("c2", 20)
        with self.assertRaises(ValueError):
            self.reserve("c3", 0)

    def test_publication_requires_artifacts_holdout_and_independence(self):
        self.reserve()
        self.settle()
        report = self.validation()
        for edit in ("same-model", "holdout", "artifact"):
            bad = json.loads(json.dumps(report))
            if edit == "same-model":
                bad["review"]["reviewer_model"] = "gpt-6.1-sol"
            elif edit == "holdout":
                del bad["cases"]["held"]
            else:
                bad["cost_evidence"]["sha256"] = "0" * 64
            self.write("validation.json", bad)
            with self.subTest(edit=edit), self.assertRaises(ValueError):
                self.op("validate", {"id": "c1", "milestone": "M1", "report": "validation.json"})

    def test_same_native_model_is_not_independent_review(self):
        self.op("candidate", {"id": "c1", "milestone": "M1", "path": "candidate",
                             "author_model": "gpt-6-astra",
                             "author_context": "a", "cost": {"model": 1, "time": 1}})
        self.settle(cost=1)
        report = self.validation()
        report["review"]["reviewer_model"] = "gpt-6-astra"
        self.write("validation.json", report)
        with self.assertRaises(ValueError):
            self.op("validate", {"id": "c1", "milestone": "M1", "report": "validation.json"})

    def test_unregistered_model_cannot_be_the_publication_reviewer(self):
        self.reserve()
        self.settle()
        report = self.validation()
        report["review"]["reviewer_model"] = "unregistered-reviewer"
        self.write("validation.json", report)
        with self.assertRaises(ValueError):
            self.op("validate", {"id": "c1", "milestone": "M1", "report": "validation.json"})

    def check_versioned_review(self, author, reviewer, independent):
        # Synthetic offline records exercise validation, not host model availability.
        self.op("candidate", {"id": "c1", "milestone": "M1", "path": "candidate",
                             "author_model": author, "author_context": "author-1",
                             "cost": {"model": 2, "time": 5}})
        self.settle()
        report = self.validation()
        report["review"]["reviewer_model"] = reviewer
        self.write("validation.json", report)
        before = self.state.read_bytes()
        if independent:
            result = self.op("validate", {"id": "c1", "milestone": "M1", "report": "validation.json"})
            self.assertEqual(result["status"], "validation-recorded")
            result = self.op("publish", {"id": "c1", "milestone": "M1"})
            self.assertEqual(result["status"], "publication-recorded")
            self.assertFalse(result["deployed"])
        else:
            with self.assertRaisesRegex(ValueError, "Independent reviewer must differ"):
                self.op("validate", {"id": "c1", "milestone": "M1", "report": "validation.json"})
            self.assertEqual(self.state.read_bytes(), before)
            with self.assertRaises(ValueError):
                self.op("publish", {"id": "c1", "milestone": "M1"})

    def test_new_astra_reviewer_can_validate_sol_offline_records(self):
        self.check_versioned_review('gpt-6.1-sol', 'gpt-6.2-astra', True)

    def test_new_sol_reviewer_can_validate_astra_offline_records(self):
        self.check_versioned_review('gpt-6-astra', 'gpt-6.2-sol', True)

    def test_old_astra_author_new_astra_reviewer_not_independent(self):
        self.check_versioned_review('gpt-6-astra', 'gpt-6.2-astra', False)

    def test_new_astra_author_old_astra_reviewer_not_independent(self):
        self.check_versioned_review('gpt-6.2-astra', 'gpt-6-astra', False)

    def test_old_sol_author_new_sol_reviewer_not_independent(self):
        self.check_versioned_review('gpt-6.1-sol', 'gpt-6.2-sol', False)

    def test_new_sol_author_old_sol_reviewer_not_independent(self):
        self.check_versioned_review('gpt-6.2-sol', 'gpt-6.1-sol', False)

    def test_jev_confidence_cannot_be_a_frozen_improvement_measure(self):
        criteria={"cases":[{"id":"core","held_out":False},{"id":"held","held_out":True}],
                  "strengths":["preserve-negative-results"],
                  "metrics":[{"id":"jev-confidence","direction":"higher","source":"task-outcome"}]}
        self.write('criteria.json',criteria)
        with self.assertRaises(ValueError):
            self.m.criteria_for(self.root,self.contract)
    def test_luna_extraction_cannot_satisfy_publication_review(self):
        self.reserve(); self.settle(); report=self.validation()
        report['review']['reviewer_model']='gpt-6-luna'
        self.write('validation.json',report)
        with self.assertRaises(ValueError):
            self.op('validate',{'id':'c1','milestone':'M1','report':'validation.json'})
        with self.assertRaises(ValueError):
            self.op('publish',{'id':'c1','milestone':'M1'})
    def test_reserve_then_develop_then_freeze_with_one_real_revision(self):
        self.reserve()
        self.write("candidate/skill.txt", "actual initial development")
        self.settle()
        self.validation()
        self.op("validate", {"id": "c1", "milestone": "M1", "report": "validation.json"})
        self.op("revise", {"id": "c1", "milestone": "M1", "cost": {"model": 1, "time": 1}})
        self.write("candidate/skill.txt", "actual repaired implementation")
        self.settle(cost=1)
        self.validation()
        self.op("validate", {"id": "c1", "milestone": "M1", "report": "validation.json"})
        self.assertEqual(self.op("publish", {"id": "c1", "milestone": "M1"})["status"],
                         "publication-recorded")

    def test_publish_once_no_install_and_rechecks_candidate(self):
        self.reserve()
        self.settle()
        self.validation()
        self.op("validate", {"id": "c1", "milestone": "M1", "report": "validation.json"})
        self.write("candidate/skill.txt", "changed after validation")
        with self.assertRaises(ValueError):
            self.op("publish", {"id": "c1", "milestone": "M1"})
        self.write("candidate/skill.txt", "improved")
        result = self.op("publish", {"id": "c1", "milestone": "M1"})
        self.assertFalse(result["deployed"])
        with self.assertRaises(ValueError):
            self.op("publish", {"id": "c1", "milestone": "M1"})
        self.assertEqual((self.root / "baseline/skill.txt").read_text(), "baseline")

    def test_no_measured_gain_does_not_publish(self):
        self.reserve()
        self.settle()
        report = self.validation()
        report["measurements"]["duplicate-searches"]["candidate"] = 3
        self.write("validation.json", report)
        with self.assertRaises(ValueError):
            self.op("validate", {"id": "c1", "milestone": "M1", "report": "validation.json"})

    def test_dry_run_and_lock_preserve_state(self):
        before = self.state.read_bytes()
        self.m.operate(self.root, self.state, "status", {}, apply=False)
        self.assertEqual(before, self.state.read_bytes())
        self.state.with_suffix(".json.lock").write_text("another writer")
        with self.assertRaises(ValueError):
            self.reserve()
        self.assertEqual(before, self.state.read_bytes())

    def test_paths_cannot_escape_workspace(self):
        with self.assertRaises(ValueError):
            self.m.contained(self.root, "../escape")


if __name__ == "__main__":
    unittest.main()
