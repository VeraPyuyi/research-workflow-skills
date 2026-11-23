import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


behavior_eval, check_links = load("behavior_eval"), load("check_links")


class BehaviorEvalTests(unittest.TestCase):
    def test_every_integrity_scenario_has_criteria(self):
        items, rubric = behavior_eval.load_suites({"integrity"})["integrity"]
        self.assertGreaterEqual(len(items), 8)
        for item in items:
            criteria, shared = behavior_eval.criteria_for(item, rubric)
            self.assertTrue(criteria, item["id"])
            self.assertIsNone(shared)

    def test_plan_grade_summarize_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            tasks = behavior_eval.plan(out, runs=2, names={"integrity"})
            self.assertEqual(len(tasks), 8 * 2 * 2)
            self.assertTrue(all(t["skills"] == [] for t in tasks if t["condition"] == "without_skill"))
            for task in tasks[:6]:
                (out / "answers" / f"{task['task_id']}.md").write_text("answer", encoding="utf-8")
                ok = task["condition"] == "with_skill"
                (out / "grades" / f"{task['task_id']}.json").write_text(
                    json.dumps({"criteria": [ok, True]}), encoding="utf-8")
            packets, missing = behavior_eval.grade(out)
            self.assertEqual((len(packets), len(missing)), (6, len(tasks) - 6))
            self.assertNotIn("condition", packets[0])
            summary = behavior_eval.summarize(out)
            self.assertEqual(summary["ungraded_tasks"], len(tasks) - 6)
            for cells in summary["scenarios"].values():
                for name, cell in cells.items():
                    if name == "with_skill":
                        self.assertEqual(cell["pass_rate"], 1.0)
                    elif name == "without_skill":
                        self.assertEqual(cell["pass_rate"], 0.0)

    def test_all_suites_load(self):
        suites = behavior_eval.load_suites()
        self.assertIn("core", suites)
        self.assertTrue(all(items for items, _ in suites.values()))


class LinkTests(unittest.TestCase):
    def test_readme_and_docs_links_resolve(self):
        self.assertEqual(check_links.broken_links(), [])


if __name__ == "__main__":
    unittest.main()
