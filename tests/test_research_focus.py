"""Integration checks for focus packaging, routing and event-loop boundaries."""

import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def module_at(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ResearchFocusTests(unittest.TestCase):
    def test_focus_is_installed_with_complete_bundle_and_reference(self):
        import tempfile
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        from install_skills import install_bundle, file_inventory
        from validate_skills import validate_bundle

        manifest = json.loads((ROOT / "skills-manifest.json").read_text())
        self.assertEqual(len(manifest["skills"]), 18)
        self.assertIn("research-focus", manifest["skills"])
        self.assertEqual(validate_bundle(ROOT), [])
        (ROOT / ".build").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / ".build") as temporary:
            target = Path(temporary) / "skills"
            install_bundle(ROOT, target, apply=True)
            self.assertEqual(file_inventory(target / "research-focus"),
                             file_inventory(ROOT / "skills/research-focus"))
            self.assertTrue((target / "research-focus/references/thesis-anchor.md").is_file())

    def test_focus_has_profile_appropriate_execution_and_review(self):
        registry = json.loads((ROOT / "skills/research-navigate/references/model-routing.json").read_text())
        self.assertIn("research-focus", registry["stages"])
        stage = registry["stages"]["research-focus"]
        self.assertTrue(stage["reviewers"])
        if registry["runtime_profile"] == "magpie":
            models = {m["id"]: m for m in registry["models"]}
            self.assertTrue(stage["free_executors"])
            self.assertTrue(all(models[m]["free"] for m in stage["free_executors"]))
            self.assertIn("cursor/grok-4.6", stage["covered_account_executors"])
            self.assertIn("research-focus", models["cursor/grok-4.6"]["stage_roles"])
            self.assertIn("typesafe/jev-latest", stage["decision_services"])
        else:
            self.assertEqual(stage["integrator"], "gpt-6.2-sol")
            self.assertIn(stage["default_executor"], ("gpt-6.2-sol", "gpt-6.2-astra"))
            self.assertEqual(stage["bounded_extractor"], "gpt-6-luna")
            self.assertNotIn("free_executors", stage)

    def test_focus_bookkeeping_cannot_restart_optimizer_loop(self):
        optimizer = module_at("focus_optimizer", "skills/research-optimize/scripts/optimize_workflow.py")
        from unittest.mock import patch
        original = {"events": {}, "spent": {"model": 0, "time": 0}, "milestones": {}}
        for stage in ("research-focus", "research-optimize"):
            state = json.loads(json.dumps(original))
            with patch.object(optimizer, "frozen", return_value={}):
                result = optimizer.transition(ROOT, ROOT / "unused-state.json", state,
                                              "event", {"stage": stage})
            self.assertEqual(state, original)
            self.assertIn("suppressed", result)

    def test_focus_decision_packet_is_admitted_without_credentials_or_network(self):
        from unittest.mock import patch
        fixtures = module_at("focus_jev_fixtures", "tests/test_jev_decide.py")
        packet = fixtures.packet()
        packet["stage"] = "research-focus"
        with patch.object(fixtures.jev, "load_credentials", side_effect=AssertionError("key access")), \
                patch.object(fixtures.jev, "post_system_one", side_effect=AssertionError("network")):
            result = fixtures.jev.decide(packet)
        self.assertEqual(result["execution_status"], "dry_run", result)
        self.assertEqual(result["actual_model"], "unknown")
        self.assertEqual(result["attempts"], 0)

    def test_blind_review_cannot_receive_focus_history(self):
        guard = module_at("focus_dispatch", "skills/research-navigate/scripts/check_dispatch.py")
        registry = json.loads((ROOT / "skills/research-navigate/references/model-routing.json").read_text())
        packet = {
            "stage": "research-review", "review_mode": "venue_blind",
            "new_agent": True, "fork_context": False, "review_round": 2,
            "manuscript_revision": "M5", "venue_profile": "V1",
            "allowed_inputs": [
                {"kind": "manuscript", "ref": "paper.pdf", "revision": "M5"},
                {"kind": "venue_criteria", "ref": "criteria.md", "revision": "V1"},
                {"kind": "research_focus", "ref": "internal-focus.json", "revision": "T2"},
            ],
        }
        errors = guard.review_errors(packet)
        if registry["runtime_profile"] == "codex-native":
            errors = errors[0]
            self.assertIn("Internal history, prior reviews and response letters are forbidden", errors)
        else:
            self.assertIn("Internal history, previous reviews and other inputs are not allowed", errors)


if __name__ == "__main__":
    unittest.main()
