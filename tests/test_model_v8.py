import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/research-navigate/scripts"
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location("guard_v8", SCRIPTS / "check_dispatch.py")
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class NewRoutingTests(unittest.TestCase):
    def test_public_release_does_not_enable_local_dispatch(self):
        registry = json.loads(guard.REGISTRY.read_text(encoding="utf-8"))
        native = registry["runtime_profile"] == "codex-native"
        self.assertEqual(registry["version"], 2 if native else 8)
        for suffix in ("gpt-6.2-astra", "gpt-6.2-sol"):
            name = suffix if native else "codex/" + suffix
            entry = next((m for m in registry["models"] if m["id"] == name), None)
            self.assertIsNotNone(entry)
            self.assertEqual(entry["availability"], "pending-local-access")
            self.assertTrue(entry["dispatch_block_reason"])
            self.assertEqual(entry["quota_pool"], "codex")
            packet = {"id": "new-model", "stage": "research-design",
                      "requested_model" if native else "model": name}
            result = guard.check(packet)
            self.assertEqual(result["status"], "blocked")
            self.assertTrue(any("re-verification" in e for e in result["errors"]))

    def test_versions_and_channels_cannot_fake_review_independence(self):
        if hasattr(guard, "identity"):
            self.assertEqual(guard.identity("codex/gpt-6.2-astra"),
                             guard.identity("openai/gpt-6-astra"))
            self.assertEqual(guard.identity("gpt-6.2-sol"), guard.identity("gpt-6.1-sol"))
        else:
            from model_identity import model_family
            self.assertEqual(model_family("gpt-6.2-sol"), model_family("gpt-6.1-sol"))

    def test_unknown_model_cannot_join_native_release(self):
        from model_identity import NATIVE_MODELS
        self.assertNotIn("gpt-6.3-astra", NATIVE_MODELS)
        self.assertNotIn("openai/gpt-6.2-astra", NATIVE_MODELS)


if __name__ == "__main__":
    unittest.main()
