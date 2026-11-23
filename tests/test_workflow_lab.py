import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
_spec = importlib.util.spec_from_file_location("workflow_lab", ROOT / "scripts/workflow_lab.py")
lab = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lab)


def event(project, stage, *weaknesses):
    return {"project": project, "stage": stage, "round": "R1", "revision": "v1", "strengths": [],
            "weaknesses": [dict(text=t, tag=g, **({"trace_ref": r} if r else {})) for t, g, r in weaknesses]}


def summary(rates, runs=3):
    scenarios = {k: {"with_skill": {"runs": runs, "passed": round(v * runs), "pass_rate": v}}
                 for k, v in rates.items()}
    return {"scenarios": scenarios, "ungraded_tasks": 0}


class AggregateTests(unittest.TestCase):
    def test_recurring_and_replayable_signals(self):
        events = [event("p1", "research-survey", ("unresolved refs", "literature-citation", None)),
                  event("p2", "research-survey", ("cited from memory", "literature-citation", None)),
                  event("p1", "research-experiment", ("filled missing seed", "evaluation-integrity", "runs/r3.log")),
                  event("p1", "research-write", ("wordy", "writing-claims", None)),
                  event("p2", "research-write", ("odd tag", "mystery", None))]
        result = lab.aggregate(events)
        keys = {(s["stage"], s["tag"]): s["basis"] for s in result["signals"]}
        self.assertEqual(keys[("research-survey", "literature-citation")], "recurring")
        self.assertEqual(keys[("research-experiment", "evaluation-integrity")], "replayable-trace")
        self.assertNotIn(("research-write", "writing-claims"), keys)
        self.assertEqual(result["unknown_tags"], ["mystery"])

    def test_event_files_are_validated(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "p1/research/optimizer/events.jsonl"
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps(event("p1", "research-survey")) + "\nnot json\n{}\n")
            events, problems = lab.read_events([tmp])
            self.assertEqual(len(events), 1)
            self.assertEqual(len(problems), 2)


class CompareTests(unittest.TestCase):
    BASE = {"core/navigate": 0.67, "core/scope": 0.33, "integrity/missing-data": 0.67}

    def test_improvement_without_regression_is_eligible(self):
        result = lab.compare(summary(self.BASE), summary(dict(self.BASE, **{"core/scope": 1.0})))
        self.assertTrue(result["eligible"], result["problems"])
        self.assertTrue(result["optimizer_fields"]["strengths"]["integrity-preserved"]["preserved"])

    def test_protected_regression_blocks_even_with_net_gain(self):
        cand = {"core/navigate": 1.0, "core/scope": 1.0, "integrity/missing-data": 0.33}
        result = lab.compare(summary(self.BASE), summary(cand))
        self.assertFalse(result["eligible"])
        self.assertFalse(result["optimizer_fields"]["strengths"]["integrity-preserved"]["preserved"])

    def test_too_few_runs_or_no_gain_blocks(self):
        self.assertFalse(lab.compare(summary(self.BASE, runs=1), summary(self.BASE, runs=1))["eligible"])
        self.assertFalse(lab.compare(summary(self.BASE), summary(self.BASE))["eligible"])

    def test_tolerance_applies_only_to_unprotected_scenarios(self):
        cand = {"core/navigate": 0.6, "core/scope": 1.0, "integrity/missing-data": 0.67}
        self.assertFalse(lab.compare(summary(self.BASE), summary(cand))["eligible"])
        self.assertTrue(lab.compare(summary(self.BASE), summary(cand), tolerance=0.1)["eligible"])


class PrepareTests(unittest.TestCase):
    def test_prepare_exports_both_suites_and_plans_with_skill_tasks(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "L1"
            result = lab.prepare("L1", "HEAD", "WORKTREE", out, runs=3, suites={"integrity"})
            for side in ("baseline", "candidate"):
                self.assertTrue((out / side / "skills/research-navigate/SKILL.md").is_file())
                tasks = [json.loads(l) for l in (out / side / "tasks.jsonl").read_text().splitlines()]
                self.assertEqual(len(tasks), result[side]["tasks"])
                self.assertTrue(all(t["condition"] == "with_skill" for t in tasks))
                self.assertTrue(all(str(out / side / "skills") in t["skills"][0] for t in tasks))
            with self.assertRaises(ValueError):
                lab.prepare("L1", "HEAD", "WORKTREE", out)


if __name__ == "__main__":
    unittest.main()
