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
            # A public-only catalog snapshot must remain blocked after activation.
            entry["availability"] = "pending-local-access"
            entry["dispatch_block_reason"] = "Current host does not expose this model"
            self.assertEqual(entry["quota_pool"], "codex")
            packet = {"id": "new-model", "stage": "research-design",
                      "requested_model" if native else "model": name}
            result = guard.check(packet, registry)
            self.assertEqual(result["status"], "blocked")
            self.assertTrue(any("re-verification" in e for e in result["errors"]))

    def test_verified_new_models_admit_only_covered_authorized_work(self):
        from test_dispatch_guard import packet
        registry = json.loads(guard.REGISTRY.read_text(encoding="utf-8"))
        native = registry["runtime_profile"] == "codex-native"
        for suffix in ("gpt-6.2-astra", "gpt-6.2-sol"):
            name = suffix if native else "codex/" + suffix
            entry = next(m for m in registry["models"] if m["id"] == name)
            self.assertEqual(entry["live_call_status"], "passed-20261121")
            self.assertFalse(entry.get("dispatch_block_reason"))
            p = packet()
            if native:
                p.update(requested_model=name, authorized_models=[name], host_available_models=[name])
            else:
                p.update(model=name, free_only=False, cost_authorization="existing subscription",
                         allowance_coverage="confirmed", allowance_record="fresh account snapshot")
            self.assertEqual(guard.check(p)["status"], "ready-for-dispatch")
            p["budget_state"] = "unknown"
            self.assertEqual(guard.check(p)["status"], "blocked")

    def test_native_catalog_is_not_current_subagent_allowlist(self):
        from test_dispatch_guard import packet
        registry = json.loads(guard.REGISTRY.read_text(encoding="utf-8"))
        if registry["runtime_profile"] != "codex-native":
            return
        p = packet()
        p.update(requested_model="gpt-6.2-sol", authorized_models=["gpt-6.2-sol"])
        p.pop("host_available_models", None)
        self.assertEqual(guard.check(p)["status"], "blocked")
        p["host_available_models"] = ["gpt-6.1-sol"]
        self.assertEqual(guard.check(p)["status"], "blocked")

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
