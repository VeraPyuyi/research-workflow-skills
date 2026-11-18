"""Regression coverage for the withdrawn Anthropic integration."""

import json
from pathlib import Path
import unittest

from scripts.magpie_routing import build_target_group


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "skills/research-navigate/references/model-routing.json"


class RetiredProviderTests(unittest.TestCase):
    def test_registry_and_all_stage_assignments_exclude_retired_provider(self):
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.assertFalse(any(
            model["id"].startswith("anthropic/") for model in registry["models"]))
        self.assertNotIn("anthropic/", json.dumps(registry["stages"]))
        self.assertNotIn(
            "anthropic", registry["policy"].get("payg_authorized_providers", []))

    def test_group_build_cannot_reintroduce_anthropic_from_cached_capabilities(self):
        evidence = {"levels": {
            f"anthropic/claude-{family}-{version}": ["high", "max"]
            for family, version in (
                ("opus", "5-5"), ("fable", "5-1"),
                ("sonnet", "5-5"), ("haiku", "5-5"))
        }}
        evidence["levels"]["cursor/grok-4.6"] = ["medium"]
        evidence["levels"]["opencode-zen/beam-free"] = ["max"]
        group = build_target_group(REGISTRY, evidence)
        self.assertNotIn("anthropic/", json.dumps(group))
        self.assertEqual(group["classifier"], "typesafe/jev-latest")
        self.assertTrue(any(m.startswith("cursor/") for m in group["members"]))
        self.assertTrue(any("free" in m for m in group["members"]))


if __name__ == "__main__":
    unittest.main()
