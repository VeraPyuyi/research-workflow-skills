import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
ROUTING = SKILLS / "research-navigate" / "references" / "model-routing.json"
EVIDENCE = ROOT / "tests" / "magpie-evidence-snapshot.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


class ModelRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.routing = load(ROUTING)
        cls.models = {m["id"]: m for m in cls.routing["models"]}

    def test_every_skill_has_free_execution_and_independent_review(self):
        manifest = load(ROOT / "skills-manifest.json")
        stages = self.routing["stages"]
        self.assertEqual(set(stages), set(manifest["skills"]))
        for stage, allocation in stages.items():
            with self.subTest(stage=stage):
                free = allocation["free_executors"]
                reviewers = allocation["reviewers"]
                self.assertTrue(free)
                self.assertTrue(reviewers)
                for model_id in free:
                    self.assertIn(model_id, self.models)
                    self.assertTrue(self.models[model_id]["free"])
                for model_id in reviewers:
                    self.assertIn(model_id, self.models)
                self.assertIn(allocation["integrator"], self.models)

    def test_free_channels_are_explicit(self):
        expected = {
            "workbuddy-ai/hy3",
            "workbuddy-ai/step-5-preview",
            "workbuddy-ai/deepseek-v4.1-flash",
            "opencode-zen/beam-free",
            "opencode-zen/mimo-v2.6-flash-free",
            "opencode-zen/nemotron-3.5-super-vl-free",
            "opencode-zen/nemotron-3.5-lightning-free",
            "opencode-zen/jev-1.13-free",
            "opencode-zen/longcat-2.5-preview-free",
            "opencode-zen/deepseek-v4.1-flash-free",
            "opencode-zen/glm-5.3-flash-free",
            "opencode-zen/space-bunny-free",
            "opencode-zen/nemotron-3-ultra-free",
        }
        actual = {m["id"] for m in self.routing["models"] if m["free"]}
        self.assertEqual(actual, expected)
        self.assertIn("channel", self.models["workbuddy-ai/deepseek-v4.1-flash"]["limitations"][1].lower())
        self.assertNotIn("workbuddy/deepseek-v4.1-flash", self.models)

    def test_access_and_capability_are_not_inferred(self):
        for model in self.routing["models"]:
            self.assertIn("access", model)
            self.assertIn("limitations", model)
            self.assertNotEqual(model["access"].strip(), "")
        self.assertIn("unverified", self.models["opencode-zen/longcat-2.5-preview-free"]["access"].lower())
        self.assertIn("unverified", self.models["opencode-zen/nemotron-3-ultra-free"]["access"].lower())

    def test_shared_codex_pool_is_explicit(self):
        codex = [m for m in self.routing["models"] if m["quota_pool"] == "codex"]
        self.assertEqual({m["id"] for m in codex}, {"codex/gpt-6-astra", "codex/gpt-6.1-sol"})
        policy = self.routing["policy"]
        self.assertEqual(policy["max_concurrency_per_confirmed_pool"], 2)
        self.assertEqual(policy["max_concurrency_unknown_pool"], 1)
        self.assertLessEqual(policy["dot_max_concurrency"], policy["max_active_workers"])

    def test_verified_cursor_is_an_actionable_stage_assignment(self):
        for stage in ("research-ideate", "research-design", "research-analyze",
                      "research-review", "research-implement", "research-product-build"):
            with self.subTest(stage=stage):
                self.assertEqual(
                    self.routing["stages"][stage]["covered_account_executors"][0],
                    "cursor/grok-4.6",
                )
        model = self.models["cursor/grok-4.6"]
        self.assertTrue(model["group_eligible"])
        self.assertTrue(model["automatic_group_intents"])
        self.assertGreaterEqual(len(model["stage_roles"]), 12)
        self.assertEqual(model["fixed_effort"], "medium")
        self.assertEqual(model["quota_pool"], "cursor")
        self.assertFalse(self.models["cursor/composer-2.5"]["group_eligible"])

    def test_unverified_vertex_has_no_default_stage_or_review_assignment(self):
        for endpoint in self.models.values():
            if endpoint["id"].startswith("google-vertex/"):
                self.assertFalse(endpoint.get("group_eligible", True))
                self.assertTrue(endpoint.get("dispatch_block_reason"))
        for stage, allocation in self.routing["stages"].items():
            with self.subTest(stage=stage):
                assigned = [allocation["integrator"]]
                for field in ("free_executors", "reviewers", "covered_account_executors"):
                    assigned += allocation.get(field, [])
                self.assertFalse(any(m.startswith("google-vertex/") for m in assigned))
                self.assertTrue(allocation["reviewers"])
        for assigned in self.routing["review_roles"].values():
            self.assertFalse(any(m.startswith("google-vertex/") for m in assigned))

    def test_effective_concurrency_never_exceeds_cap(self):
        limits = {
            "codex": self.routing["policy"]["max_concurrency_per_confirmed_pool"],
            "opencode-zen-free": self.routing["policy"]["max_concurrency_unknown_pool"],
        }
        tasks = ["codex/gpt-6-astra", "codex/gpt-6.1-sol",
                 "opencode-zen/beam-free", "opencode-zen/glm-5.3-flash-free"]
        active = {pool: 0 for pool in limits}
        admitted = []
        for model_id in tasks:
            pool = self.models[model_id]["quota_pool"]
            if active[pool] < limits[pool]:
                active[pool] += 1
                admitted.append(model_id)
        self.assertEqual(
            admitted,
            [
                "codex/gpt-6-astra",
                "codex/gpt-6.1-sol",
                "opencode-zen/beam-free",
            ],
        )

    def test_free_fallback_cannot_silently_enter_billed_endpoint(self):
        review = self.routing["review_roles"]["scientific_math"]
        self.assertIn("workbuddy-ai/deepseek-v4.1-flash", review)
        self.assertIn("codex/gpt-6.1-sol", review)
        self.assertFalse(self.models["codex/gpt-6.1-sol"]["free"])
        text = (SKILLS / "research-navigate" / "references" / "model-routing.md").read_text(encoding="utf-8")
        self.assertIn("paid escalation requires", text.lower())
        self.assertIn("Do not let a free-model failure fall through to a billed endpoint", text)

    def test_reuse_audit_has_required_decisions(self):
        text = (SKILLS / "research-navigate" / "references" / "reuse-and-simplification.md").read_text(encoding="utf-8").lower()
        for phrase in (
            "direct reuse",
            "needs argument",
            "analogy only",
            "contribution affected",
            "experiment removal",
            "implementation replacement",
        ):
            self.assertIn(phrase.lower(), text)
        self.assertIn("preserve citations", text)
        self.assertIn("proof status", text)

    def test_review_stage_contains_three_gates_and_independence(self):
        review = (SKILLS / "research-review" / "SKILL.md").read_text(encoding="utf-8")
        for phrase in (
            "research/protocol gate",
            "principal-conclusions gate",
            "submission/release gate",
            "independent",
            "actual derivation",
        ):
            self.assertIn(phrase, review)

    def test_default_navigation_invocation_does_not_request_goal_activation(self):
        import yaml
        entry = yaml.safe_load(
            (SKILLS / "research-navigate/agents/openai.yaml").read_text(encoding="utf-8")
        )
        prompt = entry["interface"]["default_prompt"]
        self.assertIn("$research-navigate", prompt)
        self.assertNotIn("in Goal mode", prompt)
        self.assertNotIn("submission-ready paper", prompt)

    def test_every_stage_entrypoint_links_to_routing(self):
        manifest = load(ROOT / "skills-manifest.json")
        for stage in manifest["skills"]:
            text = (SKILLS / stage / "SKILL.md").read_text(encoding="utf-8")
            with self.subTest(stage=stage):
                self.assertIn("model-routing.md", text)

    def test_snapshot_contains_no_credentials(self):
        data = load(EVIDENCE)
        serialized = json.dumps(data).lower()
        data.pop("scope", None)
        for secret in ("api_key", "authorization", "sk-"):
            self.assertNotIn(secret, serialized)
        for item in data.get("configured_exposed_models", []):
            self.assertEqual(set(item), {"provider", "model", "status", "source"})


if __name__ == "__main__":
    unittest.main()

