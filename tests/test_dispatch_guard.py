"""Exercise the installed offline preflight, not a toy scheduler in the test."""

import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / "skills/research-navigate/scripts/check_dispatch.py"
sys.dont_write_bytecode = True


def packet():
    return {
        "id": "branch-1",
        "stage": "research-survey",
        "model": "workbuddy-ai/hy3",
        "effort": "high",
        "free_only": True,
        "budget_state": "within",
        "capability_record": "catalog/current; tools and data checked",
        "supported_efforts": ["high"],
        "provider_fallback": [],
        "data_allowed": True,
        "contains_images": False,
        "direct_vision": False,
        "vision_endpoint_verified": False,
        "tools_allowed": True,
        "write_paths": ["D:/project/branch-1"],
        "active": [],
        "confirmed_pools": ["codex"],
    }

def blind_packet():
    plan = packet()
    plan.update(
        stage="research-review", model="workbuddy-ai/step-5-preview",
        author_model="workbuddy-ai/deepseek-v4.1-flash",
        author_evidence="runtime author identity",
        review_mode="venue_blind", review_round=1, new_agent=True,
        fork_context=False, manuscript_revision="M4", venue_profile="V1",
        allowed_inputs=[
            {"kind": "manuscript", "ref": "bundle/paper.pdf", "revision": "M4"},
            {"kind": "venue_criteria", "ref": "bundle/criteria.txt", "revision": "V1"},
        ],
    )
    return plan


class DispatchGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if GUARD.exists():
            spec = importlib.util.spec_from_file_location("check_dispatch", GUARD)
            cls.module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.module)
        else:
            cls.module = None

    def check(self, plan):
        self.assertIsNotNone(self.module, "Installed dispatch preflight is missing")
        return self.module.check(plan)

    def test_cursor_plus_rejects_uncovered_effort_and_fast_tier(self):
        plan = packet()
        plan.update(model="cursor/grok-4.6", free_only=False, effort="medium",
                    supported_efforts=["medium", "xhigh", "max"],
                    cost_authorization="included subscription only",
                    allowance_coverage="confirmed", allowance_record="current Plus snapshot")
        self.assertEqual(self.check(plan)["status"], "ready-for-dispatch")
        for field, value in (("effort", "xhigh"), ("effort", "max"),
                             ("service_tier", "priority"), ("service_tier", "fast")):
            changed = copy.deepcopy(plan)
            changed[field] = value
            self.assertEqual(self.check(changed)["status"], "blocked")

    def test_composer_observed_adapter_mismatch_blocks_strict_dispatch(self):
        plan = packet()
        plan.update(model="cursor/composer-2.5", free_only=False, effort="medium",
                    supported_efforts=["medium"], cost_authorization="included only",
                    allowance_coverage="confirmed", allowance_record="current Plus snapshot")
        self.assertEqual(self.check(plan)["status"], "blocked")

    def test_hard_output_budget_cannot_use_unverified_cursor_limit(self):
        plan = packet()
        plan.update(model="cursor/grok-4.6", free_only=False, effort="medium",
                    supported_efforts=["medium"], cost_authorization="included only",
                    allowance_coverage="confirmed", allowance_record="current Plus snapshot",
                    requires_hard_output_cap=True, max_tokens=128)
        self.assertEqual(self.check(plan)["status"], "blocked")

    def test_direct_compatible_free_route_is_admitted(self):
        result = self.check(packet())
        self.assertEqual(result["status"], "ready-for-dispatch")
        self.assertEqual(result["model"], "workbuddy-ai/hy3")
        self.assertFalse(result["executed"])

    def test_free_route_rejects_mixed_group_paid_and_provider_fallback(self):
        for model in ("group/smart-split", "codex/gpt-6-astra",
                      "workbuddy/deepseek-v4.1-flash"):
            plan = packet()
            plan["model"] = model
            self.assertEqual(self.check(plan)["status"], "blocked")
        plan = packet()
        plan["provider_fallback"] = ["codex/gpt-6-astra"]
        self.assertEqual(self.check(plan)["status"], "blocked")

    def test_unknown_capability_or_unsupported_effort_cannot_be_rounded(self):
        for key, value in (("capability_record", ""), ("supported_efforts", []),
                           ("effort", "max"), ("data_allowed", False)):
            plan = packet()
            plan[key] = value
            self.assertEqual(self.check(plan)["status"], "blocked")

    def test_historical_image_cannot_trigger_hidden_vision_route(self):
        plan = packet()
        plan["contains_images"] = True
        self.assertEqual(self.check(plan)["status"], "blocked")
        plan["direct_vision"] = True
        self.assertEqual(self.check(plan)["status"], "blocked")
        plan["vision_endpoint_verified"] = True
        self.assertEqual(self.check(plan)["status"], "ready-for-dispatch")

    def test_billed_dispatch_requires_referenced_authority(self):
        plan = packet()
        plan.update(model="codex/gpt-6.1-sol", effort="max",
                    supported_efforts=["max"], free_only=False)
        self.assertEqual(self.check(plan)["status"], "blocked")
        plan["cost_authorization"] = "decision-7; subscription scope and limit"
        self.assertEqual(self.check(plan)["status"], "blocked")
        plan["allowance_coverage"] = "confirmed"
        plan["allowance_record"] = "account allowance checked for this task"
        self.assertEqual(self.check(plan)["status"], "ready-for-dispatch")

    def test_shared_codex_pool_blocks_third_worker(self):
        plan = packet()
        plan.update(model="codex/gpt-6.1-sol", effort="max",
                    supported_efforts=["max"], free_only=False,
                    cost_authorization="decision-7",
                    allowance_coverage="confirmed", allowance_record="quota snapshot")
        plan["active"] = [
            {"id": "a", "model": "codex/gpt-6-astra", "status": "running"},
            {"id": "b", "model": "codex/gpt-6.1-sol", "status": "running"},
        ]
        self.assertEqual(self.check(plan)["status"], "blocked")
        plan["active"].pop()
        self.assertEqual(self.check(plan)["status"], "ready-for-dispatch")

    def test_unknown_pool_permits_only_one(self):
        plan = packet()
        plan["active"] = [{"id": "a", "model": "workbuddy-ai/step-5-preview",
                           "status": "running"}]
        self.assertEqual(self.check(plan)["status"], "blocked")

    def test_cursor_variants_share_one_unknown_concurrency_pool(self):
        plan = packet()
        plan.update(
            model="cursor/grok-4.6", free_only=False, effort="medium",
            supported_efforts=["medium"], cost_authorization="included subscription only",
            allowance_coverage="confirmed", allowance_record="refreshed Plus snapshot",
            active=[{"id": "cursor-running-1", "model": "cursor/grok-4.5",
                     "status": "running", "write_paths": ["D:/project/branch-2"]}],
        )
        self.assertEqual(self.check(plan)["status"], "blocked")

    def test_unknown_status_exhaustion_and_duplicate_do_not_expand(self):
        for state in ("unknown", "exhausted"):
            plan = packet()
            plan["budget_state"] = state
            self.assertEqual(self.check(plan)["status"], "blocked")
        plan = packet()
        plan["active"] = [{"id": "branch-1", "model": "codex/gpt-6-astra",
                           "status": "unknown"}]
        self.assertEqual(self.check(plan)["status"], "blocked")

    def test_overlapping_windows_writes_are_rejected_case_insensitively(self):
        plan = packet()
        plan["active"] = [{"id": "a", "model": "codex/gpt-6-astra",
                           "status": "running",
                           "write_paths": ["d:\\PROJECT\\branch-1\\paper.md"]}]
        self.assertEqual(self.check(plan)["status"], "blocked")
        plan["write_paths"] = ["D:/project/branch-2"]
        self.assertEqual(self.check(plan)["status"], "ready-for-dispatch")

    def test_review_rejects_same_model_even_on_other_channel(self):
        plan = packet()
        plan.update(model="opencode-zen/deepseek-v4.1-flash-free",
                    effort="max", supported_efforts=["max"],
                    author_model="workbuddy-ai/deepseek-v4.1-flash",
                    author_evidence="actual served identity recorded")
        self.assertEqual(self.check(plan)["status"], "blocked")

    def test_unverified_author_identity_cannot_satisfy_independence(self):
        plan = packet()
        plan.update(model="workbuddy-ai/step-5-preview",
                    author_model="workbuddy-ai/deepseek-v4.1-flash",
                    author_evidence="")
        self.assertEqual(self.check(plan)["status"], "blocked")

    def test_review_requires_explicit_author_provenance(self):
        plan = packet()
        plan.update(stage="research-review",
                    model="workbuddy-ai/step-5-preview",
                    author_model="workbuddy-ai/deepseek-v4.1-flash")
        self.assertEqual(self.check(plan)["status"], "blocked")
        plan["author_evidence"] = "runtime log records the served identity"
        self.assertEqual(self.check(plan)["status"], "ready-for-dispatch")
        plan["stage"] = "research-survey"
        self.assertEqual(self.check(plan)["status"], "ready-for-dispatch")

    def test_disallowed_tools_block_dispatch(self):
        plan = packet()
        plan["tools_allowed"] = False
        self.assertEqual(self.check(plan)["status"], "blocked")

    def test_preflight_does_not_mutate_or_reserve(self):
        plan = packet()
        before = copy.deepcopy(plan)
        self.check(plan)
        self.assertEqual(plan, before)

    def test_posix_server_write_scopes_are_supported(self):
        plan = packet()
        plan["write_paths"] = ["/srv/research/analysis"]
        self.assertEqual(self.check(plan)["status"], "ready-for-dispatch")
        plan["active"] = [{"id": "a", "model": "codex/gpt-6-astra",
                           "status": "running",
                           "write_paths": ["/srv/research/analysis/table.csv"]}]
        self.assertEqual(self.check(plan)["status"], "blocked")

    def test_global_limit_rejects_seventh_worker(self):
        plan = packet()
        plan["active"] = [
            {"id": str(i), "model": "codex/gpt-6-astra", "status": "running"}
            for i in range(6)
        ]
        self.assertEqual(self.check(plan)["status"], "blocked")

    def test_two_blind_rounds_admit_only_fresh_context_declarations(self):
        for round_number in (1, 2):
            plan = blind_packet()
            plan["review_round"] = round_number
            self.assertEqual(self.check(plan)["status"], "ready-for-dispatch")
        for key, value in (("fork_context", True), ("fork_context", None),
                           ("new_agent", False), ("review_round", 3),
                           ("review_round", True), ("manuscript_revision", ""),
                           ("venue_profile", "")):
            with self.subTest(key=key, value=value):
                plan = blind_packet()
                plan[key] = value
                self.assertEqual(self.check(plan)["status"], "blocked")

    def test_blind_review_rejects_internal_history_and_missing_materials(self):
        for kind in ("prior_review", "response_letter", "author_self_assessment",
                     "internal_logs", "project_history"):
            plan = blind_packet()
            plan["allowed_inputs"].append({"kind": kind, "ref": "private", "revision": "v1"})
            self.assertEqual(self.check(plan)["status"], "blocked")
        for inputs in ([], None, "all project files", [{"kind": "manuscript"}]):
            plan = blind_packet()
            plan["allowed_inputs"] = inputs
            self.assertEqual(self.check(plan)["status"], "blocked")
        for remove in (0, 1):
            plan = blind_packet()
            plan["allowed_inputs"].pop(remove)
            self.assertEqual(self.check(plan)["status"], "blocked")

    def test_review_modes_and_blind_versions_are_checked(self):
        plan = blind_packet()
        plan["allowed_inputs"][0]["revision"] = "old-M1"
        self.assertEqual(self.check(plan)["status"], "blocked")
        plan = blind_packet()
        plan["allowed_inputs"][1]["revision"] = "old-V0"
        self.assertEqual(self.check(plan)["status"], "blocked")
        for mode in ("blind-ish", "", []):
            plan = blind_packet()
            plan["review_mode"] = mode
            self.assertEqual(self.check(plan)["status"], "blocked")
        plan = blind_packet()
        plan["stage"] = "research-write"
        self.assertEqual(self.check(plan)["status"], "blocked")

    def test_blind_review_preflight_does_not_claim_execution_or_isolation(self):
        plan = blind_packet()
        before = copy.deepcopy(plan)
        result = self.check(plan)
        self.assertEqual(plan, before)
        self.assertFalse(result["executed"])
        self.assertFalse(result["reserved"])

    def test_numeric_booleans_cannot_bypass_dispatch_evidence(self):
        for field in ("contains_images", "free_only", "tools_allowed"):
            for value in (0, 1, "true"):
                with self.subTest(field=field, value=value):
                    plan = blind_packet()
                    plan[field] = value
                    plan["direct_vision"] = True
                    plan["vision_endpoint_verified"] = False
                    self.assertEqual(self.check(plan)["status"], "blocked")
        for value in (1, "verified"):
            plan = blind_packet()
            plan.update(contains_images=True, direct_vision=True,
                        vision_endpoint_verified=value)
            self.assertEqual(self.check(plan)["status"], "blocked")

    def test_jev_requires_native_typed_service_without_effort(self):
        plan = packet()
        plan.update(model="typesafe/jev-latest", effort=None, supported_efforts=[],
                    call_type="structured_decision", decision_types=["Choice", "Score", "Noul"],
                    adapter="jev_decide.py", free_only=False,
                    cost_authorization="existing authorized allowance",
                    allowance_coverage="confirmed", allowance_record="verified allowance")
        self.assertEqual(self.check(plan)["status"], "ready-for-dispatch")
        for key, value in (("effort", "max"), ("call_type", "generative"),
                           ("decision_types", ["free-text"]), ("adapter", "smart-split"),
                           ("contains_images", True), ("allowance_coverage", "unknown")):
            bad = copy.deepcopy(plan)
            bad[key] = value
            self.assertEqual(self.check(bad)["status"], "blocked")

    def test_free_jev_is_not_an_assumed_generative_or_native_alternative(self):
        plan = packet()
        plan.update(model="opencode-zen/jev-1.13-free", effort=None)
        self.assertEqual(self.check(plan)["status"], "blocked")
        plan.update(call_type="structured_decision", decision_types=["Choice"],
                    adapter="jev_decide.py")
        self.assertEqual(self.check(plan)["status"], "blocked")

    def test_cursor_requires_current_allowance_and_exact_capability(self):
        plan = packet()
        plan.update(model="cursor/grok-4.6", free_only=False, effort="medium",
                    supported_efforts=["medium"], cost_authorization="account-scope",
                    allowance_coverage="confirmed", allowance_record="current covered quota")
        self.assertEqual(self.check(plan)["status"], "ready-for-dispatch")
        plan["effort"] = "max"
        plan["supported_efforts"] = ["medium", "max"]
        self.assertEqual(self.check(plan)["status"], "blocked")

    def test_vertex_generic_allowance_does_not_prove_app_builder_credit(self):
        registry = json.loads(self.module.REGISTRY.read_text(encoding="utf-8"))
        for endpoint in registry["models"]:
            if not endpoint["id"].startswith("google-vertex/"):
                continue
            # A caller declaration or stale registry flag cannot unlock billing.
            endpoint.pop("dispatch_block_reason", None)
            endpoint.update(group_eligible=True, allowance_state="confirmed")
            plan = packet()
            plan.update(model=endpoint["id"], free_only=False, effort="high",
                        supported_efforts=["high"], cost_authorization="existing budget",
                        allowance_coverage="confirmed", allowance_record="billing enabled",
                        promotional_credit="Trial credit for GenAI App Builder")
            with self.subTest(model=endpoint["id"]):
                result = self.module.check(plan, registry)
                self.assertEqual(result["status"], "blocked")
                self.assertTrue(any("GenAI App Builder" in error for error in result["errors"]))



if __name__ == "__main__":
    unittest.main()
