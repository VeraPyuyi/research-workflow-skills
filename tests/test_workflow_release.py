"""Portable release/adoption behavior; all runtime fixtures are disposable."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "skills/research-navigate/scripts/workflow_release.py"
METADATA = "research-navigate/references/workflow-release.json"
ROUTING = "research-navigate/references/model-routing.json"


def routing_fixture(profile):
    if profile == "magpie":
        return {"runtime_profile": profile, "models": [
            {"id": "codex/gpt-6.1-sol", "kind": "generative"}],
            "stages": {"research-navigate": {"integrator": "codex/gpt-6.1-sol"}}}
    return {"runtime_profile": profile, "models": [
        {"id": name, "model_family": name, "kind": "generative", "quota_pool": "codex"}
        for name in ("gpt-6.1-sol", "gpt-6-astra", "gpt-6-luna")],
        "native_tools": {name: {"name": "multi_agent_v1." + name, "arguments": arguments}
                         for name, arguments in (
                             ("spawn_agent", ["model", "reasoning_effort", "message", "fork_context"]),
                             ("wait_agent", ["targets", "timeout_ms"]),
                             ("send_input", ["target", "message", "interrupt"]))},
        "task_roles": {"integration": "gpt-6.1-sol"},
        "stages": {"research-navigate": {"integrator": "gpt-6.1-sol"}}}


LEGACY_ID = "research-20261024-jev-autonomy-v1"
LEGACY_DIGEST = "sha256:ae6c9e10217a8dd14b4aab2c736366340ea568f533f47ff59671732c5d121d63"

class WorkflowReleaseTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(SCRIPT.is_file(), "The portable release helper is not implemented")
        spec = importlib.util.spec_from_file_location("workflow_release_under_test", SCRIPT)
        self.api = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.api)
        self.temp = tempfile.TemporaryDirectory(prefix="workflow-release-", dir=SCRIPT.parents[3] / ".build")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skills = self.root / "suite"
        self.project = self.root / "project"
        self.project.mkdir()
        self.put(self.skills / "research-navigate/SKILL.md", b"navigator v1\n")
        self.put(self.skills / "research-navigate/references/workflow-contract.md", b"contract v1\n")
        self.put(self.skills / "research-experiment/SKILL.md", b"experiment v1\n")
        self.json_put(self.skills / ROUTING, routing_fixture("magpie"))
        self.state = self.project / "project-state.json"

    @staticmethod
    def put(path, content):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

    def json_put(self, path, content):
        self.put(path, (json.dumps(content) + "\n").encode())

    def read_state(self):
        return json.loads(self.state.read_text(encoding="utf-8"))

    def seed_state(self, authority=True):
        record = {
            "goal": {"id": "goal-7", "completion": "paper"},
            "delegation": {"reference": "startup-approval-2"},
            "milestone": "M3",
            "jobs": [{"id": "run-9", "status": "running", "workflow_release": "old", "code": "abc"}],
            "protocol": {"revision": "frozen-1"},
            "unknown": {"keep": [1, 2, 3]},
            "workflow": {"custom": "keep", "running_job_pins": {"run-9": "old"}},
        }
        if authority:
            record["workflow"]["automatic_update_authority"] = {
                "enabled": True, "reference": "user:approved-workflow-updates"
            }
        self.json_put(self.state, record)
        return record

    def build(self, release_id="r1", contract_version="1.0"):
        return self.api.build_release(self.skills, release_id, contract_version,
                                      runtime_profile="magpie", apply=True)["release"]

    def receipt(self, release, name="receipt.json", **changes):
        value = {"schema_version": 1, "receipt_id": name,
                 "bundle_digest": release["bundle_digest"], "scope": "workflow-release",
                 "status": "passed", "evidence_refs": ["checks:targeted-release-and-adoption"]}
        value.update(changes)
        path = self.root / name
        self.json_put(path, value)
        return path

    def adopt(self, receipt, **kwargs):
        return self.api.adopt_project(self.project, self.skills,
                                      validation_receipts=[receipt], **kwargs)

    def profiled_release(self, profile, release_id="r1", version="1.0"):
        self.json_put(self.skills / ROUTING, routing_fixture(profile))
        return self.api.build_release(self.skills, release_id, version,
                                      runtime_profile=profile, apply=True)["release"]

    def test_build_rejects_mixed_registry_profiles_before_writing_metadata(self):
        original = self.build()
        before = (self.skills / METADATA).read_bytes()
        for declared, actual in (("magpie", "codex-native"), ("codex-native", "magpie")):
            with self.subTest(declared=declared):
                self.json_put(self.skills / ROUTING, routing_fixture(actual))
                for apply in (False, True):
                    with self.assertRaisesRegex(ValueError, "runtime_profile"):
                        self.api.build_release(self.skills, "mixed", "1.1",
                                               runtime_profile=declared, apply=apply)
                    self.assertEqual((self.skills / METADATA).read_bytes(), before)
        self.assertEqual(original["runtime_profile"], "magpie")

    def test_native_relabeling_cannot_hide_external_models_tools_or_stage_routes(self):
        mutations = [
            lambda r: r["models"].append({"id": "google-vertex/gemini", "kind": "generative"}),
            lambda r: r["models"][0].update(id="codex/gpt-6.1-sol"),
            lambda r: r["models"][0].update(endpoint="https://external.example/generate"),
            lambda r: r["native_tools"]["spawn_agent"].update(name="magpie.spawn"),
            lambda r: r["stages"]["research-navigate"].update(integrator="workbuddy-ai/hy3"),
            lambda r: r["task_roles"].update(integration="typesafe/jev-latest"),
            lambda r: r["models"].append({"id": "typesafe/jev-latest", "kind": "structured_decision"}),
            lambda r: r.update(magpie_config="settings.json"),
            lambda r: r.update(generative_routes={"fallback": "workbuddy-ai/hy3"}),
        ]
        for index, mutate in enumerate(mutations):
            with self.subTest(case=index):
                routing = routing_fixture("codex-native")
                mutate(routing)
                self.json_put(self.skills / ROUTING, routing)
                with self.assertRaises(ValueError):
                    self.api.build_release(self.skills, "bad-native", "1.0", runtime_profile="codex-native")

    def test_inspect_rejects_rehashed_mislabeled_registry_even_with_matching_receipt(self):
        self.seed_state()
        release = self.build()
        self.json_put(self.skills / ROUTING, routing_fixture("codex-native"))
        release["files"][ROUTING] = hashlib.sha256((self.skills / ROUTING).read_bytes()).hexdigest()
        self.write_release(release)
        receipt = self.receipt(release)
        before = self.state.read_bytes()
        with self.assertRaisesRegex(ValueError, "runtime_profile"):
            self.api.inspect_release(self.skills, [receipt])
        with self.assertRaises(ValueError):
            self.adopt(receipt, apply=True)
        self.assertEqual(self.state.read_bytes(), before)

    def test_routing_marker_is_required_and_unknown_profiles_are_rejected(self):
        for value in (None, "arbitrary", True):
            with self.subTest(value=value):
                routing = routing_fixture("magpie")
                if value is None:
                    del routing["runtime_profile"]
                else:
                    routing["runtime_profile"] = value
                self.json_put(self.skills / ROUTING, routing)
                with self.assertRaises(ValueError):
                    self.api.build_release(self.skills, "r1", "1.0", runtime_profile="magpie")

    def test_native_standalone_jev_is_separate_and_cannot_be_a_generative_route(self):
        routing = routing_fixture("codex-native")
        routing["decision_services"] = {"jev": {
            "kind": "structured_decision", "optional": True,
            "adapter": "scripts/jev_decide.py", "default_model": "jev-latest",
            "runtime_models": ["jev-latest"], "credential_env": "TYPESAFE_API_KEY",
            "explicit_config_fields": ["api_key_env", "models"],
            "endpoint": "https://api.typesafe.ai/v1/systemone",
            "quota_pool": "jev", "max_concurrency": 1,
            "generative_worker": False, "review_eligible": False,
            "primitive_types": ["choice", "score", "noul"],
            "fallback": "native-evidence-comparison",
        }}
        routing["stages"]["research-navigate"]["decision_services"] = ["jev"]
        self.json_put(self.skills / ROUTING, routing)
        release = self.api.build_release(self.skills, "native-jev", "1.0",
                                         runtime_profile="codex-native", apply=True)["release"]
        self.assertEqual(self.api.inspect_release(self.skills, [self.receipt(release)])["status"], "verified")
        for changes in ({"kind": "generative"}, {"id": "opencode-zen/jev-1.13-free"},
                        {"magpie_config": "settings.json"}, {"transport": "magpie"},
                        {"config_path": ".magpie/config.json"}, {"review_eligible": True},
                        {"generative_worker": True}, {"max_concurrency": 2},
                        {"endpoint": "https://other.example/api"},
                        {"runtime_models": ["other-model"]}, {"credential_env": "inline key"}):
            with self.subTest(changes=changes):
                bad = routing_fixture("codex-native")
                bad["decision_services"] = {"jev": dict(routing["decision_services"]["jev"], **changes)}
                self.json_put(self.skills / ROUTING, bad)
                with self.assertRaises(ValueError):
                    self.api.build_release(self.skills, "bad-jev", "1.0", runtime_profile="codex-native")
        routing["task_roles"]["integration"] = "jev"
        self.json_put(self.skills / ROUTING, routing)
        with self.assertRaises(ValueError):
            self.api.build_release(self.skills, "bad-role", "1.0", runtime_profile="codex-native")

    def test_builder_checks_available_manifest_and_installed_inspection_needs_no_manifest(self):
        self.build()
        self.json_put(self.root / "skills-manifest.json", {"version": 1, "runtime_profile": "codex-native"})
        with self.assertRaisesRegex(ValueError, "runtime_profile"):
            self.build()
        (self.root / "skills-manifest.json").unlink()
        self.assertEqual(self.api.inspect_release(self.skills)["runtime_profile"], "magpie")

    def write_release(self, release):
        payload = {key: value for key, value in release.items() if key != "bundle_digest"}
        release["bundle_digest"] = "sha256:" + hashlib.sha256(json.dumps(
            payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
            allow_nan=False).encode("ascii")).hexdigest()
        self.json_put(self.skills / METADATA, release)

    def test_build_requires_explicit_valid_profile_and_digest_binds_it(self):
        for profile in (None, "", "native", True, [], {}):
            with self.subTest(profile=profile):
                with self.assertRaises(ValueError):
                    self.api.build_release(self.skills, "r1", "1.0", runtime_profile=profile)
        releases = []
        for profile in ("magpie", "codex-native"):
            self.json_put(self.skills / ROUTING, routing_fixture(profile))
            release = self.api.build_release(
                self.skills, "r1", "1.0", runtime_profile=profile, apply=True)["release"]
            self.assertEqual(release["runtime_profile"], profile)
            report = self.api.inspect_release(self.skills, [self.receipt(release)])
            self.assertEqual(report["runtime_profile"], profile)
            self.assertTrue(report["validation"]["accepted"])
            releases.append(release)
        self.assertNotEqual(releases[0]["bundle_digest"], releases[1]["bundle_digest"])
        with self.assertRaises(ValueError):
            self.api.inspect_release(self.skills, [self.receipt(releases[0])])

    def test_invalid_or_unknown_unprofiled_metadata_cannot_authorize_adoption(self):
        self.seed_state()
        release = self.build()
        release.pop("runtime_profile", None)
        before = self.state.read_bytes()
        for profile in (None, "native", True, [], {}):
            with self.subTest(profile=profile):
                if profile is None:
                    release.pop("runtime_profile", None)
                else:
                    release["runtime_profile"] = profile
                self.write_release(release)
                with self.assertRaises(ValueError):
                    self.adopt(self.receipt(release), apply=True)
                self.assertEqual(self.state.read_bytes(), before)

    def test_automatic_updates_never_cross_profiles_in_either_direction(self):
        for source, target in (("magpie", "codex-native"), ("codex-native", "magpie")):
            with self.subTest(source=source):
                self.seed_state()
                self.adopt(self.receipt(self.profiled_release(source)), apply=True)
                receipt = self.receipt(self.profiled_release(target, "r2", "1.1"))
                before = self.state.read_bytes()
                report = self.adopt(receipt, apply=True)
                self.assertEqual(report["status"], "decision-needed")
                self.assertIn("runtime-profile-switch", report["decisions"])
                self.assertEqual(self.state.read_bytes(), before)

    def test_same_profile_upgrade_records_profile_history_and_keeps_job_pins(self):
        for profile in ("magpie", "codex-native"):
            with self.subTest(profile=profile):
                original = self.seed_state()
                self.adopt(self.receipt(self.profiled_release(profile)), apply=True)
                receipt = self.receipt(self.profiled_release(profile, "r2", "1.1"))
                self.assertEqual(self.adopt(receipt, apply=True)["status"], "adopted")
                workflow = self.read_state()["workflow"]
                self.assertEqual(workflow["runtime_profile"], profile)
                self.assertEqual(workflow["previous_release"]["runtime_profile"], profile)
                entry = workflow["upgrade_history"][-1]
                self.assertEqual(entry["from_runtime_profile"], profile)
                self.assertEqual(entry["runtime_profile"], profile)
                self.assertEqual(entry["to_runtime_profile"], profile)
                self.assertEqual(workflow["running_job_pins"], original["workflow"]["running_job_pins"])

    def test_explicit_switch_requires_target_and_authority_and_supports_dry_run(self):
        self.seed_state()
        self.adopt(self.receipt(self.profiled_release("magpie")), apply=True)
        receipt = self.receipt(self.profiled_release("codex-native", "r2", "1.1"))
        before = self.state.read_bytes()
        for kwargs in ({"switch_runtime_profile": "codex-native"},
                       {"switch_authority_ref": "user:switch-runtime"}):
            with self.subTest(kwargs=kwargs):
                report = self.adopt(receipt, apply=True, **kwargs)
                self.assertEqual(report["status"], "decision-needed")
                self.assertEqual(self.state.read_bytes(), before)
        switch = {"switch_runtime_profile": "codex-native",
                  "switch_authority_ref": "user:switch-runtime"}
        self.assertEqual(self.adopt(receipt, **switch)["status"], "ready")
        self.assertEqual(self.state.read_bytes(), before)
        self.assertEqual(self.adopt(receipt, apply=True, **switch)["status"], "adopted")
        workflow = self.read_state()["workflow"]
        self.assertEqual(workflow["runtime_profile"], "codex-native")
        entry = workflow["upgrade_history"][-1]
        self.assertEqual(entry["authority_ref"], "user:switch-runtime")
        self.assertEqual(entry["runtime_profile_switch"], {
            "from_runtime_profile": "magpie", "to_runtime_profile": "codex-native",
            "bundle_digest": workflow["adopted_release"]["bundle_digest"],
            "authority_ref": "user:switch-runtime"})
        after = self.state.read_bytes()
        self.assertEqual(self.adopt(receipt, apply=True)["status"], "already-adopted")
        self.assertEqual(self.state.read_bytes(), after)

    def test_recorded_switch_authority_is_scoped_consumed_and_independent_of_auto_updates(self):
        record = self.seed_state()
        self.adopt(self.receipt(self.profiled_release("magpie")), apply=True)
        record = self.read_state()
        record["workflow"]["automatic_update_authority"]["enabled"] = False
        release = self.profiled_release("codex-native", "r2", "1.1")
        receipt = self.receipt(release)
        switch = {"from_runtime_profile": "magpie", "to_runtime_profile": "codex-native",
                  "bundle_digest": release["bundle_digest"], "authority_ref": "user:recorded-switch"}
        for field, wrong in (("from_runtime_profile", "codex-native"),
                             ("to_runtime_profile", "magpie"),
                             ("bundle_digest", "sha256:" + "0" * 64), ("authority_ref", "")):
            with self.subTest(field=field):
                record["workflow"]["runtime_profile_switch"] = dict(switch, **{field: wrong})
                self.json_put(self.state, record)
                before = self.state.read_bytes()
                self.assertEqual(self.adopt(receipt, apply=True)["status"], "decision-needed")
                self.assertEqual(self.state.read_bytes(), before)
        record["workflow"]["runtime_profile_switch"] = switch
        self.json_put(self.state, record)
        self.assertEqual(self.adopt(receipt, apply=True)["status"], "adopted")
        workflow = self.read_state()["workflow"]
        self.assertNotIn("runtime_profile_switch", workflow)
        self.assertEqual(workflow["upgrade_history"][-1]["runtime_profile_switch"], switch)
        self.assertEqual(workflow["running_job_pins"], {"run-9": "old"})

    def test_switch_cannot_bypass_validation_customizations_or_contract_compatibility(self):
        self.seed_state()
        self.adopt(self.receipt(self.profiled_release("magpie")), apply=True)
        release = self.profiled_release("codex-native", "r2", "1.1")
        switch = {"switch_runtime_profile": "codex-native", "switch_authority_ref": "user:switch"}
        before = self.state.read_bytes()
        self.assertEqual(self.api.adopt_project(self.project, self.skills, apply=True, **switch)["status"],
                         "validation-needed")
        with self.assertRaises(ValueError):
            self.adopt(self.receipt(release, status=True), apply=True, **switch)
        local = self.project / ".agents/skills/research-experiment/SKILL.md"
        self.put(local, b"customized instructions")
        receipt = self.receipt(release)
        self.assertEqual(self.adopt(receipt, apply=True, **switch)["status"], "conflict")
        self.assertEqual(local.read_bytes(), b"customized instructions")
        local.write_bytes(b"experiment v1\n")
        release = self.profiled_release("codex-native", "r3", "2.0")
        report = self.adopt(self.receipt(release), apply=True, **switch)
        self.assertIn("incompatible-contract", report["decisions"])
        self.assertEqual(report["status"], "decision-needed")
        self.assertEqual(self.state.read_bytes(), before)

    def test_project_profile_binding_prevents_cross_profile_initial_adoption(self):
        record = self.seed_state()
        record["workflow"]["runtime_profile"] = "magpie"
        self.json_put(self.state, record)
        receipt = self.receipt(self.profiled_release("codex-native"))
        before = self.state.read_bytes()
        self.assertEqual(self.adopt(receipt, apply=True)["status"], "decision-needed")
        self.assertEqual(self.state.read_bytes(), before)

    def test_project_profile_must_agree_with_adopted_metadata(self):
        self.seed_state()
        self.adopt(self.receipt(self.profiled_release("magpie")), apply=True)
        record = self.read_state()
        record["workflow"]["runtime_profile"] = "codex-native"
        self.json_put(self.state, record)
        receipt = self.receipt(self.profiled_release("codex-native", "r2"))
        before = self.state.read_bytes()
        with self.assertRaises(ValueError):
            self.adopt(receipt, apply=True)
        self.assertEqual(self.state.read_bytes(), before)

    def test_exact_legacy_release_migrates_to_magpie_without_rewriting_its_digest(self):
        fixture_path = os.environ.get("RESEARCH_LEGACY_RELEASE_FIXTURE")
        if not fixture_path or not Path(fixture_path).is_file():
            self.skipTest("Exact original metadata requires RESEARCH_LEGACY_RELEASE_FIXTURE")
        legacy_release = json.loads(Path(fixture_path).read_text(encoding="utf-8"))
        self.assertEqual(legacy_release["release_id"], LEGACY_ID)
        self.assertEqual(legacy_release["bundle_digest"], LEGACY_DIGEST)
        record = self.seed_state()
        record["workflow"]["adopted_release"] = legacy_release
        record["workflow"]["upgrade_history"] = [{"legacy": "preserve"}]
        self.json_put(self.state, record)
        native = self.profiled_release("codex-native", "native-r2", "1.2")
        before = self.state.read_bytes()
        report = self.adopt(self.receipt(native), apply=True)
        self.assertEqual(report["status"], "decision-needed")
        self.assertIn("runtime-profile-switch", report["decisions"])
        self.assertEqual(self.state.read_bytes(), before)
        magpie = self.profiled_release("magpie", "magpie-r2", "1.2")
        self.assertEqual(self.adopt(self.receipt(magpie), apply=True)["status"], "adopted")
        workflow = self.read_state()["workflow"]
        self.assertEqual(workflow["runtime_profile"], "magpie")
        self.assertEqual(workflow["previous_release"], legacy_release)
        self.assertEqual(workflow["upgrade_history"][0], {"legacy": "preserve"})
        self.assertEqual(workflow["upgrade_history"][-1]["from_runtime_profile"], "magpie")

    def test_exact_legacy_classification_never_bypasses_metadata_digest_validation(self):
        identity = {"release_id": LEGACY_ID, "bundle_digest": LEGACY_DIGEST}
        self.assertEqual(self.api._release_profile(identity), "magpie")
        for changed in ({"release_id": "another-release"},
                        {"bundle_digest": "sha256:" + "0" * 64}):
            with self.subTest(changed=changed):
                with self.assertRaises(ValueError):
                    self.api._release_profile(dict(identity, **changed))
        forged = self.build(LEGACY_ID, "1.1")
        forged.pop("runtime_profile")
        forged["bundle_digest"] = LEGACY_DIGEST
        self.json_put(self.skills / METADATA, forged)
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            self.api.inspect_release(self.skills)

    def test_legacy_name_or_digest_alone_never_infers_a_profile(self):
        release = self.build("research-20261024-jev-autonomy-v1", "1.1")
        release.pop("runtime_profile", None)
        self.write_release(release)
        record = self.seed_state()
        record["workflow"]["adopted_release"] = release
        # A top-level assertion must not launder unknown unprofiled metadata.
        record["workflow"]["runtime_profile"] = "magpie"
        self.json_put(self.state, record)
        receipt = self.receipt(self.profiled_release("magpie", "r2", "1.2"))
        before = self.state.read_bytes()
        with self.assertRaises(ValueError):
            self.adopt(receipt, apply=True)
        self.assertEqual(self.state.read_bytes(), before)
        record["workflow"]["adopted_release"] = dict(release, release_id="renamed", bundle_digest=LEGACY_DIGEST)
        self.json_put(self.state, record)
        with self.assertRaises(ValueError):
            self.adopt(receipt, apply=True)

    def test_switch_arguments_are_validated_and_do_not_silently_select_another_target(self):
        self.seed_state()
        self.adopt(self.receipt(self.profiled_release("magpie")), apply=True)
        receipt = self.receipt(self.profiled_release("codex-native", "r2", "1.1"))
        before = self.state.read_bytes()
        for target, authority in (("native", "user:switch"), (True, "user:switch"),
                                  ("codex-native", ""), ("codex-native", "\n")):
            with self.subTest(target=target, authority=authority):
                with self.assertRaises(ValueError):
                    self.adopt(receipt, apply=True, switch_runtime_profile=target,
                               switch_authority_ref=authority)
                self.assertEqual(self.state.read_bytes(), before)
        report = self.adopt(receipt, apply=True, switch_runtime_profile="magpie",
                            switch_authority_ref="user:switch")
        self.assertEqual(report["status"], "decision-needed")
        self.assertEqual(self.state.read_bytes(), before)

    def test_cli_profile_build_and_explicit_switch_use_real_adoption_gates(self):
        self.seed_state()
        self.adopt(self.receipt(self.profiled_release("magpie")), apply=True)
        self.json_put(self.skills / ROUTING, routing_fixture("codex-native"))
        args = [sys.executable, "-B", str(SCRIPT), "build-release", "--skills-dir", str(self.skills),
                "--release-id", "native-r2", "--contract-version", "1.1"]
        result = subprocess.run(args, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        result = subprocess.run([*args, "--runtime-profile", "codex-native", "--apply"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        release = json.loads(result.stdout)["release"]
        self.assertEqual(release["runtime_profile"], "codex-native")
        receipt = self.receipt(release)
        args = [sys.executable, "-B", str(SCRIPT), "adopt-project", "--project", str(self.project),
                "--skills-dir", str(self.skills), "--validation", str(receipt), "--apply"]
        before = self.state.read_bytes()
        result = subprocess.run(args, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "decision-needed")
        self.assertEqual(self.state.read_bytes(), before)
        result = subprocess.run([*args, "--switch-runtime-profile", "codex-native",
                                 "--switch-authority-ref", "user:cli-switch"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "adopted")

    def test_candidate_hashes_all_files_excludes_self_and_cache_and_dry_run(self):
        self.put(self.skills / "research-navigate/__pycache__/ignored.pyc", b"cache")
        result = self.api.build_release(self.skills, "r1", "1.0", runtime_profile="magpie",
                                        validation_receipts=["checks:release"])
        self.assertEqual(result["status"], "candidate")
        self.assertFalse(result["applied"])
        self.assertFalse((self.skills / METADATA).exists())
        release = result["release"]
        self.assertEqual(release["files"], {
            "research-navigate/SKILL.md": hashlib.sha256(b"navigator v1\n").hexdigest(),
            "research-navigate/references/workflow-contract.md": hashlib.sha256(b"contract v1\n").hexdigest(),
            "research-experiment/SKILL.md": hashlib.sha256(b"experiment v1\n").hexdigest(),
            ROUTING: hashlib.sha256((self.skills / ROUTING).read_bytes()).hexdigest(),
        })
        payload = {key: value for key, value in release.items() if key != "bundle_digest"}
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()
        self.assertEqual(release["bundle_digest"], "sha256:" + digest)
        self.assertEqual(release["validation_receipts"], ["checks:release"])
        self.build()
        self.assertNotIn(METADATA, self.api.inspect_release(self.skills)["release"]["files"])

    def test_build_is_reproducible_and_never_self_validates(self):
        first = self.build()
        second = self.build()
        self.assertEqual(first, second)
        report = self.api.inspect_release(self.skills)
        self.assertEqual(report["status"], "candidate")
        self.assertFalse(report["validation"]["accepted"])

    def test_personal_installation_may_include_unrelated_skills(self):
        release = self.build()
        receipt = self.receipt(release)
        self.put(self.skills / "user-other/SKILL.md", b"user customized workflow")
        report = self.api.inspect_release(self.skills, [receipt])
        self.assertEqual(report["status"], "verified")
        self.assertEqual((self.skills / "user-other/SKILL.md").read_bytes(), b"user customized workflow")

    def test_modified_missing_and_added_release_files_are_rejected(self):
        release = self.build()
        receipt = self.receipt(release)
        self.seed_state()
        path = self.skills / "research-experiment/SKILL.md"
        for mode in ("modified", "missing", "added"):
            with self.subTest(mode=mode):
                if mode == "modified":
                    path.write_bytes(b"modified")
                elif mode == "missing":
                    path.unlink()
                else:
                    path.write_bytes(b"experiment v1\n")
                    self.put(self.skills / "research-experiment/extra.txt", b"extra")
                with self.assertRaises(ValueError):
                    self.adopt(receipt, apply=True)
        self.assertNotIn("adopted_release", self.read_state()["workflow"])

    def test_tampered_metadata_digest_and_identity_are_rejected(self):
        release = self.build()
        receipt = self.receipt(release)
        self.seed_state()
        release["release_id"] = "forged"
        self.json_put(self.skills / METADATA, release)
        with self.assertRaises(ValueError):
            self.adopt(receipt, apply=True)

    def test_validation_needs_matching_passed_scope_and_evidence_not_boolean(self):
        release = self.build()
        self.seed_state()
        report = self.api.adopt_project(self.project, self.skills, apply=True)
        self.assertEqual(report["status"], "validation-needed")
        for changes in ({"bundle_digest": "sha256:" + "0" * 64}, {"scope": "unit-tests"},
                        {"status": True}, {"status": "failed"}, {"evidence_refs": []},
                        {"schema_version": True}):
            with self.subTest(changes=changes):
                receipt = self.receipt(release, **changes)
                with self.assertRaises(ValueError):
                    self.adopt(receipt, apply=True)
        self.json_put(self.root / "boolean.json", {"validated": True})
        with self.assertRaises(ValueError):
            self.adopt(self.root / "boolean.json", apply=True)
        self.assertNotIn("adopted_release", self.read_state()["workflow"])

    def test_dry_run_then_apply_preserves_records_and_running_pins(self):
        original = self.seed_state()
        release = self.build()
        receipt = self.receipt(release)
        before = self.state.read_bytes()
        report = self.adopt(receipt)
        self.assertEqual(report["status"], "ready")
        self.assertFalse(report["applied"])
        self.assertEqual(self.state.read_bytes(), before)
        applied = self.adopt(receipt, apply=True)
        self.assertEqual(applied["status"], "adopted")
        stored = self.read_state()
        for key in original:
            if key != "workflow":
                self.assertEqual(stored[key], original[key])
        self.assertEqual(stored["workflow"]["custom"], "keep")
        self.assertEqual(stored["workflow"]["running_job_pins"], {"run-9": "old"})
        self.assertEqual(stored["workflow"]["adopted_release"]["release_id"], "r1")
        self.assertEqual(stored["workflow"]["upgrade_history"][0]["authority_ref"], "user:approved-workflow-updates")
        self.assertIn("declaration", applied["validation"]["trust"])

    def test_compatible_upgrade_keeps_previous_and_history_and_is_idempotent(self):
        self.seed_state()
        first = self.build()
        self.adopt(self.receipt(first), apply=True)
        self.put(self.skills / "research-experiment/SKILL.md", b"experiment v2\n")
        second = self.build("r2", "1.1")
        receipt = self.receipt(second, "r2-receipt.json")
        self.assertEqual(self.adopt(receipt, apply=True)["status"], "adopted")
        stored = self.read_state()
        self.assertEqual(stored["workflow"]["previous_release"]["release_id"], "r1")
        self.assertEqual(len(stored["workflow"]["upgrade_history"]), 2)
        before = self.state.read_bytes()
        self.assertEqual(self.adopt(receipt, apply=True)["status"], "already-adopted")
        self.assertEqual(self.state.read_bytes(), before)

    def test_incompatible_and_downgrade_contracts_need_decision(self):
        self.seed_state()
        self.adopt(self.receipt(self.build("r1", "1.1")), apply=True)
        before = self.state.read_bytes()
        for version in ("2.0", "1.0"):
            with self.subTest(version=version):
                report = self.adopt(self.receipt(self.build("r2", version)), apply=True)
                self.assertEqual(report["status"], "decision-needed")
                self.assertIn("incompatible-contract", report["decisions"])
                self.assertEqual(self.state.read_bytes(), before)

    def test_missing_automatic_authority_does_not_mutate(self):
        self.seed_state(authority=False)
        report = self.adopt(self.receipt(self.build()), apply=True)
        self.assertEqual(report["status"], "decision-needed")
        self.assertIn("automatic-update-authority", report["decisions"])
        self.assertNotIn("adopted_release", self.read_state()["workflow"])

    def test_reusing_release_identity_for_different_bytes_needs_decision(self):
        self.seed_state()
        self.adopt(self.receipt(self.build()), apply=True)
        before = self.state.read_bytes()
        self.put(self.skills / "research-experiment/SKILL.md", b"new bytes same id")
        report = self.adopt(self.receipt(self.build()), apply=True)
        self.assertEqual(report["status"], "decision-needed")
        self.assertIn("release-id-reused", report["decisions"])
        self.assertEqual(self.state.read_bytes(), before)

    def test_state_inside_digested_suite_cannot_be_adopted(self):
        self.seed_state()
        packaged_state = self.skills / "project-state.json"
        self.json_put(packaged_state, self.read_state())
        release = self.build()
        before = packaged_state.read_bytes()
        with self.assertRaises(ValueError):
            self.api.inspect_project(self.skills, self.skills,
                                     validation_receipts=[self.receipt(release)])
        with self.assertRaises(ValueError):
            self.api.adopt_project(self.skills, self.skills,
                                   validation_receipts=[self.receipt(release)], apply=True)
        self.assertEqual(packaged_state.read_bytes(), before)

    def test_local_copied_skill_is_compared_to_previous_preserving_customization(self):
        self.seed_state()
        first = self.build()
        self.adopt(self.receipt(first), apply=True)
        local = self.project / ".agents/skills/research-experiment/SKILL.md"
        self.put(local, b"experiment v1\n")
        self.put(self.skills / "research-experiment/SKILL.md", b"experiment v2\n")
        receipt = self.receipt(self.build("r2", "1.1"))
        pristine = self.adopt(receipt)
        self.assertEqual(pristine["conflicts"], [])
        self.assertEqual(pristine["local_copies"][0]["status"], "matches-previous")
        local.write_bytes(b"independent custom instructions")
        before = self.state.read_bytes()
        report = self.adopt(receipt, apply=True)
        self.assertEqual(report["status"], "conflict")
        self.assertTrue(report["conflicts"])
        self.assertEqual(local.read_bytes(), b"independent custom instructions")
        self.assertEqual(self.state.read_bytes(), before)

    def test_unknown_extra_and_missing_local_files_are_conflicts(self):
        self.seed_state()
        receipt = self.receipt(self.build())
        local = self.project / "skills/research-experiment"
        self.put(local / "custom.txt", b"extra")
        report = self.adopt(receipt, apply=True)
        self.assertEqual(report["status"], "conflict")

    def test_retained_pristine_copy_stays_recognizable_across_multiple_adoptions(self):
        self.seed_state()
        self.adopt(self.receipt(self.build()), apply=True)
        local = self.project / ".agents/skills/research-experiment/SKILL.md"
        self.put(local, b"experiment v1\n")
        for number in (2, 3):
            self.put(self.skills / "research-experiment/SKILL.md", f"experiment v{number}\n".encode())
            receipt = self.receipt(self.build(f"r{number}", f"1.{number}"))
            self.assertEqual(self.adopt(receipt, apply=True)["status"], "adopted")
            before = self.state.read_bytes()
            self.assertEqual(self.adopt(receipt, apply=True)["status"], "already-adopted")
            self.assertEqual(self.state.read_bytes(), before)
        local.write_bytes(b"custom after third adoption")
        self.assertEqual(self.adopt(receipt, apply=True)["status"], "conflict")

    def test_running_versions_are_captured_without_repinning_or_touching_science(self):
        record = self.seed_state()
        del record["workflow"]["running_job_pins"]
        record["jobs"][0]["config_version"] = "config-1"
        self.json_put(self.state, record)
        science = {}
        for name in ("protocol.md", "data/raw.csv", "manuscript.tex", "jobs/run-9.json"):
            path = self.project / name
            self.put(path, b"scientific artifact must remain byte identical\n")
            science[path] = path.read_bytes()
        self.adopt(self.receipt(self.build()), apply=True)
        self.assertEqual(self.read_state()["workflow"]["running_job_pins"], {
            "run-9": {"workflow_release": "old", "code": "abc", "config_version": "config-1"}
        })
        self.assertEqual({path: path.read_bytes() for path in science}, science)

    def test_reparse_ancestor_detection_rejects_before_any_write(self):
        self.seed_state()
        receipt = self.receipt(self.build())
        suspect = self.project / "linked"
        suspect.mkdir()
        original_lstat = Path.lstat
        before = self.state.read_bytes()

        def lstat(path, *args, **kwargs):
            if path == suspect:
                return SimpleNamespace(st_mode=0o40755, st_file_attributes=0x400)
            return original_lstat(path, *args, **kwargs)

        with mock.patch.object(Path, "lstat", lstat):
            with self.assertRaises(ValueError):
                self.adopt(receipt, state="linked/state.json", apply=True)
        self.assertEqual(self.state.read_bytes(), before)

    def test_parent_traversal_in_root_paths_is_rejected_before_normalization(self):
        release = self.build()
        receipt = self.receipt(release)
        self.seed_state()
        root_alias = self.project / "unused/../.." / self.project.name
        with self.assertRaises(ValueError):
            self.api.adopt_project(root_alias, self.skills, validation_receipts=[receipt], apply=True)

    def test_build_replace_failure_preserves_old_release_and_cleans_up(self):
        self.build()
        before = (self.skills / METADATA).read_bytes()
        with mock.patch.object(self.api.os, "replace", side_effect=OSError("injected build failure")):
            with self.assertRaises(OSError):
                self.build("r2", "1.1")
        self.assertEqual((self.skills / METADATA).read_bytes(), before)
        self.assertEqual(list(self.skills.rglob("*.tmp")), [])
        self.assertEqual(list(self.root.glob("*.lock")), [])

    def test_designated_state_wins_over_fallback_and_explicit_missing_fails(self):
        self.seed_state()
        fallback = self.project / ".research/workflow.json"
        self.json_put(fallback, {"sentinel": "leave untouched"})
        receipt = self.receipt(self.build())
        report = self.adopt(receipt, apply=True)
        self.assertEqual(Path(report["state_path"]), self.state)
        self.assertEqual(json.loads(fallback.read_text()), {"sentinel": "leave untouched"})
        with self.assertRaises(ValueError):
            self.adopt(receipt, state="designated-missing.json", apply=True)

    def test_explicit_state_and_ambiguous_discovery(self):
        self.seed_state()
        other = self.project / ".research/project.json"
        self.json_put(other, {"other": True})
        receipt = self.receipt(self.build())
        with self.assertRaises(ValueError):
            self.adopt(receipt, apply=True)
        report = self.adopt(receipt, state="project-state.json", apply=True)
        self.assertEqual(report["status"], "adopted")
        self.assertEqual(json.loads(other.read_text()), {"other": True})

    def test_fallback_dry_run_creates_nothing_then_uses_recorded_authority(self):
        receipt = self.receipt(self.build())
        report = self.adopt(receipt)
        self.assertEqual(report["state_source"], "fallback")
        self.assertFalse((self.project / ".research").exists())
        fallback = self.project / ".research/workflow.json"
        self.json_put(fallback, {"workflow": {"automatic_update_authority": {
            "enabled": True, "reference": "user:existing-authority"}}})
        self.assertEqual(self.adopt(receipt, apply=True)["status"], "adopted")

    def test_lock_blocks_concurrent_adoption_and_keeps_state_unchanged(self):
        self.seed_state()
        receipt = self.receipt(self.build())
        before = self.state.read_bytes()
        with self.api.exclusive_lock(self.state):
            with self.assertRaises(self.api.LockError):
                self.adopt(receipt, apply=True)
        self.assertEqual(self.state.read_bytes(), before)
        self.assertEqual(self.adopt(receipt, apply=True)["status"], "adopted")

    def test_parallel_adoption_writes_one_history_entry(self):
        self.seed_state()
        receipt = self.receipt(self.build())
        barrier = threading.Barrier(2)
        outcomes = []
        errors = []

        def worker():
            barrier.wait(timeout=5)
            try:
                outcomes.append(self.adopt(receipt, apply=True)["status"])
            except self.api.LockError:
                outcomes.append("locked")
            except Exception as exc:
                errors.append(repr(exc))

        threads = [threading.Thread(target=worker) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)
        self.assertEqual(errors, [])
        self.assertFalse(any(thread.is_alive() for thread in threads))
        self.assertEqual(outcomes.count("adopted"), 1)
        self.assertEqual(len(self.read_state()["workflow"]["upgrade_history"]), 1)

    def test_atomic_replace_failure_keeps_original_and_releases_lock_for_retry(self):
        self.seed_state()
        receipt = self.receipt(self.build())
        before = self.state.read_bytes()
        with mock.patch.object(self.api.os, "replace", side_effect=OSError("injected replace failure")):
            with self.assertRaises(OSError):
                self.adopt(receipt, apply=True)
        self.assertEqual(self.state.read_bytes(), before)
        self.assertEqual(list(self.project.glob("*.tmp")), [])
        self.assertFalse(Path(str(self.state) + ".lock").exists())
        self.assertEqual(self.adopt(receipt, apply=True)["status"], "adopted")

    def test_traversal_absolute_external_and_windows_alias_paths_are_rejected(self):
        self.seed_state()
        receipt = self.receipt(self.build())
        for state in ("../outside.json", self.root / "outside.json", "a/../project-state.json",
                      "C:/outside.json", "folder\\..\\state.json", "file.json:stream"):
            with self.subTest(state=str(state)):
                with self.assertRaises(ValueError):
                    self.adopt(receipt, state=state, apply=True)
        for name in ("../escape", "", "bad\nname"):
            with self.assertRaises(ValueError):
                self.api.build_release(self.skills, name, "1.0", runtime_profile="magpie", apply=True)

    def test_release_inventory_path_escape_is_rejected(self):
        release = self.build()
        release["files"]["../outside"] = "0" * 64
        self.json_put(self.skills / METADATA, release)
        with self.assertRaises(ValueError):
            self.api.inspect_release(self.skills)

    def test_symlink_and_junction_inputs_are_rejected_without_following(self):
        self.seed_state()
        receipt = self.receipt(self.build())
        outside = self.root / "outside"
        outside.mkdir()
        link = self.project / "linked"
        if os.name == "nt":
            completed = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(outside)],
                                       capture_output=True, text=True)
            if completed.returncode:
                self.skipTest("Junction creation unavailable: " + completed.stderr)
            self.addCleanup(lambda: os.rmdir(link) if link.exists() else None)
        else:
            link.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.adopt(receipt, state="linked/state.json", apply=True)
        linked_suite = self.skills / "research-experiment/linked"
        if os.name == "nt":
            completed = subprocess.run(["cmd", "/c", "mklink", "/J", str(linked_suite), str(outside)],
                                       capture_output=True, text=True)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.addCleanup(lambda: os.rmdir(linked_suite) if linked_suite.exists() else None)
        else:
            linked_suite.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.api.build_release(self.skills, "r2", "1.1", runtime_profile="magpie", apply=True)

    def test_malformed_state_and_unknown_workflow_shape_are_not_replaced(self):
        receipt = self.receipt(self.build())
        for record in ([], {"workflow": "opaque"}, {"workflow": {"upgrade_history": "opaque"}}):
            with self.subTest(record=record):
                self.json_put(self.state, record)
                before = self.state.read_bytes()
                with self.assertRaises(ValueError):
                    self.adopt(receipt, apply=True)
                self.assertEqual(self.state.read_bytes(), before)

    def test_cli_build_inspect_adopt_json_and_apply_opt_in(self):
        self.seed_state()

        def cli(*args):
            result = subprocess.run([sys.executable, "-B", str(SCRIPT), *map(str, args)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)

        result = cli("build-release", "--skills-dir", self.skills, "--release-id", "r1", "--contract-version", "1.0",
                     "--runtime-profile", "magpie")
        self.assertFalse(result["applied"])
        release = cli("build-release", "--skills-dir", self.skills, "--release-id", "r1", "--contract-version", "1.0",
                      "--runtime-profile", "magpie", "--apply")["release"]
        receipt = self.receipt(release)
        before = self.state.read_bytes()
        args = ("--project", self.project, "--skills-dir", self.skills, "--validation", receipt)
        self.assertEqual(cli("inspect-project", *args)["status"], "ready")
        self.assertEqual(cli("adopt-project", *args)["status"], "ready")
        self.assertEqual(self.state.read_bytes(), before)
        self.assertEqual(cli("adopt-project", *args, "--apply")["status"], "adopted")

    def test_cli_pending_and_invalid_receipt_exit_codes_and_json(self):
        self.seed_state()
        release = self.build()
        args = [sys.executable, "-B", str(SCRIPT), "adopt-project", "--project",
                str(self.project), "--skills-dir", str(self.skills), "--apply"]
        result = subprocess.run(args, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["status"], "validation-needed")
        self.assertEqual(result.stderr, "")
        bad = self.receipt(release, status=True)
        result = subprocess.run([*args, "--validation", str(bad)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stderr)["status"], "error")
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
