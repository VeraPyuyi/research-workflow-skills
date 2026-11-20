"""Activated subscription routes preserve custom group intent and old fallbacks."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from scripts.magpie_routing import build_target_group, preserve_custom_group, INTENTS

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "skills/research-navigate/references/model-routing.json"


class ActivationTests(unittest.TestCase):
    def test_stage_free_branches_do_not_select_removed_catalog_entries(self):
        registry = json.loads(REGISTRY.read_text("utf-8"))
        models = {m["id"]: m for m in registry["models"]}
        for stage in registry["stages"].values():
            self.assertTrue(stage["free_executors"])
            for model in stage["free_executors"]:
                self.assertTrue(models[model]["free"])
                self.assertFalse(models[model].get("dispatch_block_reason"), model)

    def group(self, blocked=False):
        registry = json.loads(REGISTRY.read_text("utf-8"))
        for item in registry["models"]:
            if "6.2" in item["id"]:
                item["group_eligible"] = True
                item["dispatch_block_reason"] = "no access" if blocked else ""
        levels = {model: ["high", "max"] for model in
                  ("codex/gpt-6-astra", "codex/gpt-6.1-sol",
                   "codex/gpt-6.2-astra", "codex/gpt-6.2-sol")}
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            path = Path(directory) / "routing.json"
            path.write_text(json.dumps(registry), encoding="utf-8")
            return registry, build_target_group(path, {"levels": levels})

    def test_verified_preferences_and_old_fallbacks(self):
        _, group = self.group()
        self.assertIn("codex/gpt-6.2-astra:high", group["members"])
        self.assertIn("codex/gpt-6-astra:high", group["members"])
        rules = {r["intent"]: r["use"] for r in group["rules"]}
        self.assertEqual(rules[INTENTS["hard"]], "codex/gpt-6.2-astra:high")
        self.assertEqual(rules[INTENTS["experiment"]], "codex/gpt-6.2-sol:high")

    def test_blocked_preferences_keep_the_working_routes(self):
        _, group = self.group(True)
        self.assertFalse(any("6.2" in m for m in group["members"]))
        rules = {r["intent"]: r["use"] for r in group["rules"]}
        self.assertEqual(rules[INTENTS["hard"]], "codex/gpt-6-astra:high")

    def test_custom_and_paused_rules_are_not_rewritten(self):
        registry, group = self.group()
        before = dict(id="smart-split-api", members=["openai/gpt-6-astra:xhigh",
                         "codex/gpt-6-astra:max", "codex/gpt-6.1-sol:max"],
                      rules=[{"use": "openai/gpt-6-astra:xhigh", "intent": "User's API choice"},
                             {"use": "codex/gpt-6-astra:max", "intent": INTENTS["hard"]},
                             {"use": "codex/gpt-6.1-sol:max", "intent": INTENTS["experiment"], "pause": True}])
        snapshot = copy.deepcopy(before)
        after = preserve_custom_group(before, group, registry)
        self.assertEqual(before, snapshot)
        self.assertEqual(after["members"][0], before["members"][0])
        self.assertEqual(after["rules"][0], before["rules"][0])
        self.assertEqual(after["rules"][1]["use"], "codex/gpt-6.2-astra:high")
        self.assertEqual(after["rules"][2], before["rules"][2])
        self.assertIn("codex/gpt-6-astra:max", after["members"])
