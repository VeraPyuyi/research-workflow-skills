import json
import os
import shutil
import unittest
from pathlib import Path
from unittest import mock

from scripts.magpie_routing import (
    GROUP_ID,
    apply_plan,
    build_plan,
    build_target_group,
    load_effort_evidence,
    resolve_config_path,
    sanitize_config,
    supported_efforts,
)


ROOT = Path(__file__).resolve().parents[1]
ROUTING = ROOT / "skills" / "research-navigate" / "references" / "model-routing.json"


def sample_config():
    return {
        "providers": [
            {
                "id": "codex",
                "models": ["gpt-6-astra", "gpt-6.1-sol"],
                "apiKey": "sk-test-secret",
            },
            {
                "id": "google-vertex",
                "models": ["gemini-4-argon"],
            },
            {
                "id": "typesafe",
                "models": ["jev-latest"],
            },
            {
                "id": "workbuddy-ai",
                "models": ["hy3", "step-5-preview", "deepseek-v4.1-flash"],
            },
            {
                "id": "opencode-zen",
                "models": [
                    "beam-free",
                    "deepseek-v4.1-flash-free",
                    "glm-5.3-flash-free",
                    "jev-1.13-free",
                    "longcat-2.5-preview-free",
                    "mimo-v2.6-flash-free",
                    "nemotron-3.5-lightning-free",
                    "nemotron-3.5-super-vl-free",
                    "nemotron-3-ultra-free",
                    "space-bunny-free",
                ],
            },
            {
                "id": "cursor",
                "models": ["composer-2.5", "grok-4.6"],
            },
        ],
        "groups": [
            {
                "id": GROUP_ID,
                "name": "科研",
                "members": [
                    "codex/gpt-6-astra:max",
                    "group/auto-step-5-preview",
                    "dot/text",
                ],
                "routing": "order",
                "rules": [
                    {"use": "dot/text", "tokens": 160000},
                    {"use": "group/auto-step-5-preview", "images": True},
                ],
                "classifier": "typesafe/jev-latest",
            },
            {
                "id": "github",
                "name": "Github",
                "members": ["codex/gpt-6.1-sol"],
                "routing": "order",
            },
        ],
    }


class MagpieRoutingHelperTests(unittest.TestCase):
    def setUp(self):
        # Leave room for timestamped backup names on Windows without long paths.
        test_root = ROOT / ".build" / "magpie-tests"
        self.base = test_root / self.id().split(".")[-1]
        self.assertTrue(self.base.resolve().is_relative_to(ROOT.resolve()))
        self.assertEqual(self.base.resolve().parent, test_root.resolve())
        if self.base.exists():
            shutil.rmtree(self.base)
        self.base.mkdir(parents=True)
        self.config_path = self.base / "providers.json"
        self.settings_path = self.base / "settings.json"
        self.catalog_path = self.base / "models_cache.json"
        self.artifact_dir = self.base / "artifacts"
        self.config_path.write_text(json.dumps(sample_config(), indent=2), encoding="utf-8")
        self.settings_path.write_text(
            json.dumps(
                {
                    "modelEfforts": {
                        "codex/gpt-6-astra": ["high", "xhigh", "max"],
                        "codex/gpt-6.1-sol": ["high", "xhigh", "max"],
                        "google-vertex/gemini-4-argon": ["high"],
                        "typesafe/jev-latest": ["xhigh", "max"],
                        "workbuddy-ai/deepseek-v4.1-flash": ["max"],
                        "workbuddy-ai/step-5-preview": ["high"],
                        "workbuddy-ai/hy3": ["high"],
                        "opencode-zen/beam-free": ["max"],
                        "opencode-zen/glm-5.3-flash-free": ["max"],
                        "opencode-zen/jev-1.13-free": ["max"],
                        "opencode-zen/nemotron-3.5-super-vl-free": ["xhigh"],
                    }
                }
            ),
            encoding="utf-8",
        )
        self.catalog_path.write_text(
            json.dumps(
                {
                    "models": [
                        {"slug": "gpt-6-astra", "default_reasoning_level": "medium", "supported_reasoning_levels": [{"effort": "high"}, {"effort": "xhigh"}, {"effort": "max"}]},
                        {"slug": "gpt-6.1-sol", "default_reasoning_level": "low", "supported_reasoning_levels": [{"effort": "high"}, {"effort": "xhigh"}, {"effort": "max"}]},
                        {"slug": "google-vertex/gemini-4-argon", "default_reasoning_level": "high", "supported_reasoning_levels": [{"effort": "high"}]},
                        {"slug": "workbuddy-ai/hy3", "default_reasoning_level": "high", "supported_reasoning_levels": [{"effort": "high"}]},
                        {"slug": "workbuddy-ai/step-5-preview", "default_reasoning_level": "high", "supported_reasoning_levels": [{"effort": "high"}]},
                        {"slug": "workbuddy-ai/deepseek-v4.1-flash", "default_reasoning_level": "max", "supported_reasoning_levels": [{"effort": "max"}]},
                        {"slug": "opencode-zen/beam-free", "default_reasoning_level": "max", "supported_reasoning_levels": [{"effort": "max"}]},
                        {"slug": "opencode-zen/glm-5.3-flash-free", "default_reasoning_level": "max", "supported_reasoning_levels": [{"effort": "max"}]},
                        {"slug": "opencode-zen/nemotron-3.5-super-vl-free", "default_reasoning_level": "xhigh", "supported_reasoning_levels": [{"effort": "xhigh"}]},
                        {"slug": "opencode-zen/jev-1.13-free", "default_reasoning_level": "max", "supported_reasoning_levels": [{"effort": "max"}]},
                        {"slug": "opencode-zen/deepseek-v4.1-flash-free", "default_reasoning_level": "max", "supported_reasoning_levels": [{"effort": "max"}]},
                        {"slug": "opencode-zen/longcat-2.5-preview-free", "default_reasoning_level": "max", "supported_reasoning_levels": [{"effort": "max"}]},
                        {"slug": "opencode-zen/nemotron-3.5-lightning-free", "default_reasoning_level": "max", "supported_reasoning_levels": [{"effort": "max"}]},
                        {"slug": "opencode-zen/mimo-v2.6-flash-free", "default_reasoning_level": "max", "supported_reasoning_levels": [{"effort": "max"}]},
                        {"slug": "opencode-zen/space-bunny-free", "default_reasoning_level": "max", "supported_reasoning_levels": [{"effort": "max"}]},
                        {"slug": "typesafe/jev-latest", "default_reasoning_level": "max", "supported_reasoning_levels": [{"effort": "max"}]},
                        {"slug": "cursor/composer-2.5", "default_reasoning_level": "high", "supported_reasoning_levels": [{"effort": "high"}]},
                        {"slug": "cursor/grok-4.6", "default_reasoning_level": "medium", "supported_reasoning_levels": [{"effort": "medium"}]},
                    ]
                }
            ),
            encoding="utf-8",
        )

    def test_build_target_group_removes_blanket_and_dot_routes(self):
        evidence = load_effort_evidence(self.catalog_path, {"codex", "google-vertex", "typesafe", "workbuddy-ai", "opencode-zen"})
        group = build_target_group(ROUTING, evidence)
        members = group["members"]
        rules = group["rules"]
        self.assertIn("codex/gpt-6-astra:high", members)
        self.assertIn("codex/gpt-6.1-sol:high", members)
        self.assertFalse(any(m.startswith("google-vertex/") for m in members))
        free_prefixes = {
            "opencode-zen/beam-free",
            "opencode-zen/deepseek-v4.1-flash-free",
            "opencode-zen/mimo-v2.6-flash-free",
            "opencode-zen/nemotron-3.5-super-vl-free",
            "opencode-zen/nemotron-3.5-lightning-free",
        }
        self.assertTrue(free_prefixes.issubset({m.rsplit(":", 1)[0] if m.rsplit(":", 1)[-1] in {"low", "medium", "high", "xhigh", "max"} else m for m in members}))
        self.assertNotIn("dot/text", members)
        self.assertFalse(any(rule.get("tokens") for rule in rules))
        self.assertFalse(any(rule.get("images") for rule in rules))
        self.assertFalse(any(rule.get("compact") for rule in rules))
        self.assertFalse(any(str(rule.get("use", "")).startswith("group/") for rule in rules))
        self.assertEqual(group["classifier"], "typesafe/jev-latest")
        self.assertNotIn("typesafe/jev-latest", members)
        self.assertFalse(any("jev-" in m for m in members))
        self.assertIn("cursor/grok-4.6:medium", members)
        self.assertFalse(any(m.startswith("cursor/composer-2.5") for m in members))
        self.assertLessEqual(max(len(rule["intent"]) for rule in rules), 200)
        intents = " ".join(rule["intent"] for rule in rules)
        self.assertIn("Routine research writing", intents)
        self.assertIn("Final manuscript integration", intents)
        self.assertIn("Experiment and protocol coordination", intents)

    def test_cursor_receives_its_own_intents_not_only_fallback_membership(self):
        evidence = load_effort_evidence(self.catalog_path)
        group = build_target_group(ROUTING, evidence)
        cursor_rules = [rule for rule in group["rules"]
                        if rule["use"] == "cursor/grok-4.6:medium"]
        self.assertGreaterEqual(len(cursor_rules), 2)
        self.assertTrue(any("competing explanations" in rule["intent"].lower()
                            for rule in cursor_rules))
        self.assertTrue(any("engineering" in rule["intent"].lower()
                            for rule in cursor_rules))
        self.assertTrue(all("tokens" not in rule and "images" not in rule
                            for rule in cursor_rules))

    def test_focus_has_an_explicit_free_intent_route(self):
        group = build_target_group(ROUTING, load_effort_evidence(self.catalog_path))
        routes = [rule for rule in group["rules"] if "topic drift" in rule["intent"].lower()]
        self.assertEqual(len(routes), 1)
        self.assertTrue(routes[0]["use"].startswith("opencode-zen/deepseek-v4.1-flash-free"))
        self.assertNotIn("tokens", routes[0])
        self.assertNotIn("images", routes[0])

    def test_subscription_group_member_requires_supported_fixed_effort(self):
        evidence = load_effort_evidence(self.catalog_path)
        evidence["levels"]["cursor/grok-4.6"] = ["high"]
        group = build_target_group(ROUTING, evidence)
        self.assertFalse(any(member.startswith("cursor/") for member in group["members"]))
        self.assertFalse(any(rule["use"].startswith("cursor/") for rule in group["rules"]))

    def test_blocked_endpoint_cannot_reenter_group_through_registry_flag(self):
        routing = json.loads(ROUTING.read_text(encoding="utf-8"))
        endpoint = next(item for item in routing["models"] if item["id"] == "cursor/grok-4.6")
        endpoint["dispatch_block_reason"] = "new adapter mismatch"
        routing_path = self.base / "blocked-routing.json"
        routing_path.write_text(json.dumps(routing), encoding="utf-8")
        group = build_target_group(routing_path, load_effort_evidence(self.catalog_path))
        self.assertFalse(any(member.startswith("cursor/") for member in group["members"]))

    def test_vertex_cannot_reenter_group_with_generic_eligibility_or_free_flag(self):
        routing = json.loads(ROUTING.read_text(encoding="utf-8"))
        for endpoint in routing["models"]:
            if endpoint["id"].startswith("google-vertex/"):
                endpoint.update(group_eligible=True, free=True,
                                allowance_state="confirmed",
                                automatic_group_intents=["Review supplied evidence"])
                endpoint.pop("dispatch_block_reason", None)
        path = self.base / "generic-vertex-approval.json"
        path.write_text(json.dumps(routing), encoding="utf-8")
        group = build_target_group(path, load_effort_evidence(self.catalog_path))
        self.assertFalse(any(m.startswith("google-vertex/") for m in group["members"]))
        self.assertFalse(any(r["use"].startswith("google-vertex/") for r in group["rules"]))
        consistency = next(r for r in group["rules"] if "Long-evidence consistency" in r["intent"])
        self.assertTrue(consistency["use"].startswith("opencode-zen/deepseek-v4.1-flash-free"))
        self.assertIn("cursor/grok-4.6:medium", group["members"])

    def test_unverified_account_candidates_do_not_join_automatic_group(self):
        routing = json.loads(ROUTING.read_text(encoding="utf-8"))
        endpoint = next(item for item in routing["models"] if item["id"] == "cursor/grok-4.6")
        endpoint["group_eligible"] = False
        routing_path = self.base / "direct-only-routing.json"
        routing_path.write_text(json.dumps(routing), encoding="utf-8")
        group = build_target_group(routing_path, load_effort_evidence(self.catalog_path))
        self.assertFalse(any(member.startswith("cursor/") for member in group["members"]))

    def test_build_plan_redacts_credentials_and_preserves_other_groups(self):
        plan = build_plan(self.config_path, ROUTING, self.artifact_dir, self.catalog_path)
        serialized = json.dumps(plan.before_sanitized)
        self.assertNotIn("sk-test-secret", serialized)
        other = next(group for group in plan.after_sanitized["groups"] if group["id"] == "github")
        self.assertEqual(other["members"], ["codex/gpt-6.1-sol"])
        self.assertTrue((self.artifact_dir / "smart-split.diff").exists())
        self.assertTrue((self.artifact_dir / "effort-evidence.json").exists())

    def test_group_exports_use_allowlist_not_arbitrary_fields(self):
        from scripts.magpie_routing import project_group

        group = {
            "id": GROUP_ID,
            "name": "research",
            "members": [],
            "rules": [{"use": "x/y", "intent": "short", "private": "plain-private-value"}],
            "private_extension": {"credential": "plain-private-value"},
        }
        projected = project_group(group)
        self.assertNotIn("private_extension", projected)
        self.assertEqual(projected["rules"], [{"use": "x/y", "intent": "short"}])

    def test_apply_aborts_on_stale_hash(self):
        plan = build_plan(self.config_path, ROUTING, self.artifact_dir, self.catalog_path)
        with self.assertRaisesRegex(ValueError, "config changed"):
            apply_plan(self.config_path, plan, "deadbeef")

    def test_apply_updates_only_target_group_and_keeps_backup(self):
        plan = build_plan(self.config_path, ROUTING, self.artifact_dir, self.catalog_path)
        result = apply_plan(self.config_path, plan, plan.config_hash_before)
        updated = json.loads(self.config_path.read_text(encoding="utf-8"))
        target = next(group for group in updated["groups"] if group["id"] == GROUP_ID)
        other = next(group for group in updated["groups"] if group["id"] == "github")
        self.assertEqual(target["members"], plan.after_group["members"])
        self.assertEqual(other["members"], ["codex/gpt-6.1-sol"])
        self.assertTrue(Path(result["backup"]).exists())
        self.assertEqual(result["group_sha256_after"], plan.after_hash)

    def test_invalid_target_or_effort_is_rejected(self):
        evidence = load_effort_evidence(self.catalog_path, {"codex", "google-vertex", "typesafe", "workbuddy-ai", "opencode-zen", "cursor"})
        from scripts.magpie_routing import provider_models, validate_group_fields, validate_members

        bad = build_target_group(ROUTING, evidence)
        bad["members"].append("cursor/composer-2.5:max")
        with self.assertRaisesRegex(ValueError, "unsupported effort"):
            validate_group_fields(bad)
            validate_members(bad, provider_models(sample_config()), evidence)
        bad["members"].remove("cursor/composer-2.5:max")
        bad["rules"].append({"use": "cursor/composer-2.5", "intent": "bad"})
        with self.assertRaisesRegex(ValueError, "not a group member"):
            validate_group_fields(bad)
            validate_members(bad, provider_models(sample_config()), evidence)

    def test_rule_ordering_is_not_execution_pin(self):
        evidence = load_effort_evidence(self.catalog_path, {"codex", "google-vertex", "typesafe", "workbuddy-ai", "opencode-zen"})
        group = build_target_group(ROUTING, evidence)
        self.assertEqual(group["routing"], "order")
        self.assertNotEqual(group["rules"][0]["use"], "codex/gpt-6-astra:max")
        self.assertIn("codex/gpt-6-astra:high", group["members"])

    def test_custom_api_order_and_pause_survive_retired_endpoint_repair(self):
        from scripts.magpie_routing import preserve_custom_group
        target = build_target_group(ROUTING, load_effort_evidence(self.catalog_path))
        before = {
            "id": "smart-split-api", "name": "Custom API", "routing": "order",
            "members": ["openai/gpt-6-astra:high", "codex/gpt-6-astra:max",
                        "workbuddy-ai/step-5-preview:high"],
            "classifier": "typesafe/jev-latest",
            "rules": [{"use": "codex/gpt-6-astra:max", "agents": ["codex"], "pause": True},
                      {"use": "workbuddy-ai/step-5-preview:high", "intent": "custom prose"}]
        }
        after = preserve_custom_group(before, target, json.loads(ROUTING.read_text(encoding="utf-8")))
        self.assertEqual(after["id"], before["id"])
        self.assertEqual(after["members"][:2], before["members"][:2])
        self.assertEqual(after["rules"][0], before["rules"][0])
        self.assertEqual(after["rules"][1]["use"], "opencode-zen/deepseek-v4.1-flash-free:max")
        self.assertEqual(after["rules"][1]["intent"], "custom prose")
        self.assertFalse(any("workbuddy-ai/" in m or "6.2" in m for m in after["members"]))

    @mock.patch("scripts.magpie_routing._is_reparse_point")
    def test_reparse_ancestor_is_rejected(self, reparse_mock):
        reparse_mock.side_effect = lambda path: path == self.base
        with self.assertRaisesRegex(ValueError, "reparse point"):
            resolve_config_path(self.config_path)

    def test_sanitize_config_uses_allowlist_not_secret_patterns(self):
        config = sample_config()
        config["providers"][0]["apiKey"] = "ordinary-value-not-a-token"
        config["providers"][0]["headers"] = {"x-private": "plain-header-value"}
        config["providers"][0]["cookies"] = "plain-cookie-value"
        config["providers"][0]["base_url"] = "https://private.invalid"
        sanitized = sanitize_config(config)
        serialized = json.dumps(sanitized)
        for value in ("ordinary-value-not-a-token", "plain-header-value", "plain-cookie-value", "private.invalid"):
            self.assertNotIn(value, serialized)
        self.assertEqual(
            set(sanitized["providers"][0]),
            {"id", "models", "fallback_present"},
        )

    def test_recommended_effort_is_not_capability_evidence(self):
        catalog = json.loads(self.catalog_path.read_text(encoding="utf-8"))
        catalog["models"].append(
            {
                "slug": "recommended-only",
                "default_reasoning_level": "high",
                "supported_reasoning_levels": [],
            }
        )
        self.catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
        evidence = load_effort_evidence(self.catalog_path)
        self.assertEqual(supported_efforts("codex/recommended-only", evidence), [])

    def test_bare_catalog_slug_does_not_authorize_other_providers(self):
        self.catalog_path.write_text(
            json.dumps(
                {
                    "models": [
                        {
                            "slug": "hy3",
                            "default_reasoning_level": "high",
                            "supported_reasoning_levels": [{"effort": "high"}],
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        evidence = load_effort_evidence(
            self.catalog_path,
            {"codex", "opencode-zen", "workbuddy-ai", "google-vertex", "cursor"},
        )
        self.assertEqual(supported_efforts("codex/hy3", evidence), ["high"])
        self.assertEqual(supported_efforts("opencode-zen/hy3", evidence), [])
        self.assertEqual(supported_efforts("workbuddy-ai/hy3", evidence), [])

    def test_settings_model_efforts_are_not_capability_evidence(self):
        self.catalog_path.write_text(
            json.dumps(
                {
                    "models": [
                        {
                            "slug": "gpt-6-astra",
                            "default_reasoning_level": "max",
                            "supported_reasoning_levels": [],
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        evidence = load_effort_evidence(self.catalog_path, {"codex"})
        self.assertEqual(supported_efforts("codex/gpt-6-astra", evidence), [])
        self.assertNotIn("settings.json", json.dumps(evidence))

    def test_classifier_omits_unverified_effort(self):
        self.catalog_path.write_text(
            json.dumps(
                {
                    "models": [
                        {
                            "slug": "gpt-6-astra",
                            "supported_reasoning_levels": [{"effort": "max"}],
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        evidence = load_effort_evidence(self.catalog_path, {"codex", "opencode-zen", "typesafe"})
        group = build_target_group(ROUTING, evidence)
        self.assertNotIn("typesafe/jev-latest", group["members"])
        self.assertEqual(group["classifier"], "typesafe/jev-latest")
        self.assertNotIn(":", group["classifier"])
        self.assertNotIn("typesafe/jev-latest", group["members"])
        self.assertTrue(all(len(rule["intent"]) <= 200 for rule in group["rules"]))

    def test_plan_hash_comes_from_parsed_bytes(self):
        from scripts.magpie_routing import read_config_bytes, sha256_bytes

        original = self.config_path.read_bytes()
        calls = {"n": 0}
        real = read_config_bytes

        def diverge(path):
            calls["n"] += 1
            data = real(path)
            if path == self.config_path and calls["n"] > 1:
                return data + b"\n"
            return data

        with mock.patch("scripts.magpie_routing.read_config_bytes", side_effect=diverge):
            plan = build_plan(self.config_path, ROUTING, self.artifact_dir, self.catalog_path)
        self.assertEqual(plan.config_hash_before, sha256_bytes(original))

    def test_apply_aborts_when_expected_hash_matches_but_plan_does_not(self):
        from scripts.magpie_routing import sha256_bytes

        plan = build_plan(self.config_path, ROUTING, self.artifact_dir, self.catalog_path)
        mutated = self.config_path.read_bytes() + b"\n"
        self.config_path.write_bytes(mutated)
        with self.assertRaisesRegex(ValueError, "config changed"):
            apply_plan(self.config_path, plan, sha256_bytes(mutated))
        self.assertEqual(self.config_path.read_bytes(), mutated)

    def test_apply_aborts_when_config_changes_after_backup(self):
        from scripts import magpie_routing

        plan = build_plan(self.config_path, ROUTING, self.artifact_dir, self.catalog_path)
        original = self.config_path.read_bytes()
        concurrent = b'{"groups":[],"concurrent":true}\n'

        def tamper(path):
            path.write_bytes(concurrent)

        with mock.patch("scripts.magpie_routing._before_atomic_replace", side_effect=tamper):
            with self.assertRaisesRegex(ValueError, "config changed"):
                apply_plan(self.config_path, plan, plan.config_hash_before)
        self.assertEqual(self.config_path.read_bytes(), concurrent)
        backups = list(self.base.glob("providers.json.bak.*"))
        self.assertGreaterEqual(len(backups), 1)
        self.assertTrue(any(path.read_bytes() == original for path in backups))
        self.assertFalse(list(self.base.glob("providers.json.tmp")))
        self.assertFalse(list(self.base.glob("*.tmp")))
        self.assertNotIn("apiKey", magpie_routing.__file__)

    def test_failed_read_back_does_not_restore_over_live_file(self):
        plan = build_plan(self.config_path, ROUTING, self.artifact_dir, self.catalog_path)
        original = self.config_path.read_bytes()

        def fail(_path):
            raise OSError("simulated read failure")

        with mock.patch("scripts.magpie_routing._read_back_config_bytes", side_effect=fail):
            with self.assertRaisesRegex(ValueError, "read-back failed"):
                apply_plan(self.config_path, plan, plan.config_hash_before)
        live = self.config_path.read_bytes()
        self.assertNotEqual(live, original)
        self.assertIn(b"smart-split", live)
        backups = list(self.base.glob("providers.json.bak.*"))
        self.assertEqual(backups[0].read_bytes(), original)

    def test_mismatched_read_back_does_not_restore(self):
        plan = build_plan(self.config_path, ROUTING, self.artifact_dir, self.catalog_path)
        original = self.config_path.read_bytes()

        def hijack(_path):
            return b'{"hijacked":true}\n'

        with mock.patch("scripts.magpie_routing._read_back_config_bytes", side_effect=hijack):
            with self.assertRaisesRegex(ValueError, "read-back mismatch"):
                apply_plan(self.config_path, plan, plan.config_hash_before)
        live = self.config_path.read_bytes()
        self.assertNotEqual(live, original)
        self.assertNotIn(b"hijacked", live)
        backups = list(self.base.glob("providers.json.bak.*"))
        self.assertEqual(backups[0].read_bytes(), original)

    def test_helper_does_not_invoke_subprocess_or_network(self):
        source = (ROOT / "scripts" / "magpie_routing.py").read_text(encoding="utf-8")
        tree_ok = "subprocess" not in source and "urllib" not in source and "requests" not in source
        self.assertTrue(tree_ok)
        with mock.patch("subprocess.run", side_effect=AssertionError("subprocess")), mock.patch(
            "socket.socket", side_effect=AssertionError("socket")
        ):
            build_plan(self.config_path, ROUTING, self.artifact_dir, self.catalog_path)


if __name__ == "__main__":
    unittest.main()
