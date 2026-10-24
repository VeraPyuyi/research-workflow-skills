import json
from copy import deepcopy
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
try:
    from install_skills import install_bundle
    from validate_skills import validate_bundle
except ModuleNotFoundError:
    install_bundle = None
    validate_bundle = None


def write_skill(root, name):
    folder = root / "skills" / name
    (folder / "agents").mkdir(parents=True)
    (folder / "SKILL.md").write_text(
        f"---\nname: {name}\n"
        "description: Use when evaluating a supplied research artifact.\n"
        "---\n\n# Research artifact\n\n"
        "Read the supplied evidence and report its limits.\n",
        encoding="utf-8",
    )
    (folder / "agents" / "openai.yaml").write_text(
        'interface:\n  display_name: "Research Artifact"\n'
        '  short_description: "Evaluate a supplied research artifact"\n'
        f'  default_prompt: "Use ${name} to assess this evidence."\n'
        "policy:\n  allow_implicit_invocation: true\n",
        encoding="utf-8",
    )


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(callable(install_bundle), "Installer is not implemented")
        self.assertTrue(callable(validate_bundle), "Validator is not implemented")
        build_root = ROOT / ".build"
        build_root.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=build_root)
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "bundle"
        self.root.mkdir()
        self.names = ["research-one", "research-two"]
        (self.root / "skills-manifest.json").write_text(
            json.dumps({"version": 1, "skills": self.names}), encoding="utf-8"
        )
        for name in self.names:
            write_skill(self.root, name)
        self.target = self.base / "installed"

    def test_valid_portable_bundle(self):
        self.assertEqual(validate_bundle(self.root), [])

    def research_bundle(self, profile):
        # Real routing schemas in a disposable bundle; never edit either release tree.
        write_skill(self.root, "research-navigate")
        self.names.append("research-navigate")
        (self.root / "skills-manifest.json").write_text(json.dumps({
            "version": 1, "skills": self.names, "runtime_profile": profile}), encoding="utf-8")
        routing = {"runtime_profile": "magpie", "models": [
            {"id": "codex/gpt-6.1-sol", "kind": "generative"}],
            "stages": {"research-navigate": {"integrator": "codex/gpt-6.1-sol"}}}
        if profile == "codex-native":
            routing = {"runtime_profile": profile, "models": [
                {"id": name, "model_family": name, "kind": "generative", "quota_pool": "codex"}
                for name in ("gpt-6.1-sol", "gpt-6-astra", "gpt-6-luna")],
                "native_tools": {name: {"name": "multi_agent_v1." + name} for name in
                                 ("spawn_agent", "wait_agent", "send_input")},
                "task_roles": {"integration": "gpt-6.1-sol"},
                "stages": {"research-navigate": {"integrator": "gpt-6.1-sol"}}}
        folder = self.root / "skills/research-navigate/references"
        folder.mkdir()
        path = folder / "model-routing.json"
        path.write_text(json.dumps(routing), encoding="utf-8")
        return path, routing

    def test_registry_must_agree_with_manifest_and_release_in_both_directions(self):
        path, routing = self.research_bundle("magpie")
        release_path = path.with_name("workflow-release.json")
        for label in ("codex-native", "magpie"):
            with self.subTest(label=label):
                manifest_path = self.root / "skills-manifest.json"
                manifest = json.loads(manifest_path.read_text())
                manifest["runtime_profile"] = label
                manifest_path.write_text(json.dumps(manifest))
                release_path.write_text(json.dumps({"runtime_profile": label}))
                routing["runtime_profile"] = "magpie" if label == "codex-native" else "codex-native"
                path.write_text(json.dumps(routing))
                errors = validate_bundle(self.root)
                self.assertTrue(any("runtime_profile" in e for e in errors), errors)

    def test_relabeling_external_content_as_native_is_rejected_by_bundle_validation(self):
        path, routing = self.research_bundle("codex-native")
        self.assertEqual(validate_bundle(self.root), [])
        mutations = [
            lambda r: r["models"].append({"id": "cursor/grok-4.7@256k", "kind": "generative"}),
            lambda r: r["stages"]["research-navigate"].update(default_executor="workbuddy-ai/hy3"),
            lambda r: r["native_tools"]["spawn_agent"].update(name="magpie.spawn"),
            lambda r: r.update(runtime_profile="unknown"),
        ]
        for index, mutate in enumerate(mutations):
            with self.subTest(case=index):
                bad = deepcopy(routing)
                mutate(bad)
                path.write_text(json.dumps(bad))
                self.assertTrue(validate_bundle(self.root))

    def test_native_jev_exception_requires_separate_structured_service_without_magpie(self):
        path, routing = self.research_bundle("codex-native")
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
        path.write_text(json.dumps(routing))
        self.assertEqual(validate_bundle(self.root), [])
        for changes in ({"kind": "generative"}, {"magpie_config": "private.json"}):
            with self.subTest(changes=changes):
                bad = deepcopy(routing)
                bad["decision_services"]["jev"].update(changes)
                path.write_text(json.dumps(bad))
                self.assertTrue(validate_bundle(self.root))

    def test_research_registry_cannot_be_missing_or_unprofiled(self):
        path, routing = self.research_bundle("magpie")
        self.assertEqual(validate_bundle(self.root), [])
        del routing["runtime_profile"]
        path.write_text(json.dumps(routing))
        self.assertTrue(validate_bundle(self.root))
        path.unlink()
        self.assertTrue(validate_bundle(self.root))

    def test_known_legacy_label_cannot_launder_fabricated_metadata(self):
        path, _ = self.research_bundle("magpie")
        path.with_name("workflow-release.json").write_text(json.dumps({
            "release_id": "research-20261024-jev-autonomy-v1",
            "bundle_digest": "sha256:ae6c9e10217a8dd14b4aab2c736366340ea568f533f47ff59671732c5d121d63"
        }), encoding="utf-8")
        self.assertTrue(validate_bundle(self.root))

    def test_runtime_profile_must_be_known_and_match_release(self):
        manifest_path = self.root / "skills-manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["runtime_profile"] = "unknown-runtime"
        manifest_path.write_text(json.dumps(manifest))
        self.assertTrue(validate_bundle(self.root))
        manifest["runtime_profile"] = "codex-native"
        manifest_path.write_text(json.dumps(manifest))
        metadata = self.root / "skills/research-navigate/references/workflow-release.json"
        metadata.parent.mkdir(parents=True)
        metadata.write_text(json.dumps({"runtime_profile": "magpie"}))
        # Isolate this invariant from the extra fixture directory.
        errors = validate_bundle(self.root)
        self.assertTrue(any("runtime_profile" in error for error in errors))

    def test_dry_run_does_not_create_target(self):
        result = install_bundle(self.root, self.target)
        self.assertEqual(result["planned"], ["research-one", "research-two"])
        self.assertEqual(result["installed"], [])
        self.assertFalse(self.target.exists())

    def test_apply_preserves_files_and_unrelated_skills(self):
        unrelated = self.target / "user-skill" / "SKILL.md"
        unrelated.parent.mkdir(parents=True)
        unrelated.write_text("user-owned", encoding="utf-8")
        result = install_bundle(self.root, self.target, apply=True)
        self.assertEqual(result["installed"], ["research-one", "research-two"])
        self.assertEqual(unrelated.read_text(encoding="utf-8"), "user-owned")
        for name in self.names:
            self.assertEqual(
                (self.target / name / "SKILL.md").read_bytes(),
                (self.root / "skills" / name / "SKILL.md").read_bytes(),
            )

    def test_identical_install_is_idempotent(self):
        install_bundle(self.root, self.target, apply=True)
        existing = self.target / "research-one" / "SKILL.md"
        timestamp = existing.stat().st_mtime_ns
        result = install_bundle(self.root, self.target, apply=True)
        self.assertEqual(result["installed"], [])
        self.assertEqual(result["unchanged"], ["research-one", "research-two"])
        self.assertEqual(existing.stat().st_mtime_ns, timestamp)

    def test_one_conflict_prevents_all_writes(self):
        existing = self.target / "research-two" / "SKILL.md"
        existing.parent.mkdir(parents=True)
        existing.write_text("my customized skill", encoding="utf-8")
        with self.assertRaises(ValueError):
            install_bundle(self.root, self.target, apply=True)
        self.assertFalse((self.target / "research-one").exists())
        self.assertEqual(existing.read_text(encoding="utf-8"), "my customized skill")

    def test_dry_run_reports_conflict_without_modifying_files(self):
        self.target.mkdir()
        conflict = self.target / "research-two"
        conflict.write_text("not a directory", encoding="utf-8")
        with self.assertRaises(ValueError):
            install_bundle(self.root, self.target)
        self.assertEqual(conflict.read_text(encoding="utf-8"), "not a directory")

    def test_missing_source_is_rejected_before_install(self):
        missing = self.root / "skills" / "research-two" / "SKILL.md"
        missing.unlink()
        with self.assertRaises(ValueError):
            install_bundle(self.root, self.target, apply=True)
        self.assertFalse(self.target.exists())

    def test_duplicate_manifest_names_are_rejected(self):
        (self.root / "skills-manifest.json").write_text(
            json.dumps({"version": 1, "skills": ["research-one", "research-one"]}),
            encoding="utf-8",
        )
        self.assertTrue(validate_bundle(self.root))
        with self.assertRaises(ValueError):
            install_bundle(self.root, self.target, apply=True)
        self.assertFalse(self.target.exists())

    def test_manifest_cannot_escape_target(self):
        (self.root / "skills-manifest.json").write_text(
            json.dumps({"version": 1, "skills": ["../escaped"]}), encoding="utf-8"
        )
        with self.assertRaises(ValueError):
            install_bundle(self.root, self.target, apply=True)
        self.assertFalse((self.base / "escaped").exists())
        self.assertFalse(self.target.exists())

    def test_source_target_overlap_is_rejected(self):
        for target in (self.root / "skills", self.root / "skills" / "nested", self.root):
            with self.subTest(target=target), self.assertRaises(ValueError):
                install_bundle(self.root, target, apply=True)
        self.assertEqual(validate_bundle(self.root), [])

    def test_malformed_yaml_is_reported(self):
        path = self.root / "skills" / "research-one" / "SKILL.md"
        path.write_text("---\nname: [broken\n---\nBody", encoding="utf-8")
        self.assertTrue(validate_bundle(self.root))

    def test_metadata_cannot_invoke_a_different_skill(self):
        path = self.root / "skills" / "research-one" / "agents" / "openai.yaml"
        path.write_text(
            path.read_text(encoding="utf-8").replace("$research-one", "$wrong-stage"),
            encoding="utf-8",
        )
        self.assertTrue(validate_bundle(self.root))

    def test_missing_shared_reference_is_detected(self):
        path = self.root / "skills" / "research-one" / "SKILL.md"
        with path.open("a", encoding="utf-8") as stream:
            stream.write("\nRead [contract](../research-two/references/contract.md).\n")
        self.assertTrue(validate_bundle(self.root))
        refs = self.root / "skills" / "research-two" / "references"
        refs.mkdir()
        (refs / "contract.md").write_text("# Contract\nActual guidance.\n", encoding="utf-8")
        self.assertEqual(validate_bundle(self.root), [])
        install_bundle(self.root, self.target, apply=True)
        self.assertTrue((self.target / "research-two" / "references" / "contract.md").is_file())

    def test_reference_cannot_depend_on_unshipped_repo_file(self):
        (self.root / "private.md").write_text("not packaged", encoding="utf-8")
        path = self.root / "skills" / "research-one" / "SKILL.md"
        with path.open("a", encoding="utf-8") as stream:
            stream.write("\nRead [private](../../private.md).\n")
        self.assertTrue(validate_bundle(self.root))

    def test_unlisted_skill_is_detected(self):
        write_skill(self.root, "research-forgotten")
        self.assertTrue(validate_bundle(self.root))

    def test_empty_manifest_and_unknown_version_are_rejected(self):
        for data in ({"version": 1, "skills": []}, {"version": 2, "skills": self.names}):
            with self.subTest(data=data):
                (self.root / "skills-manifest.json").write_text(
                    json.dumps(data), encoding="utf-8"
                )
                self.assertTrue(validate_bundle(self.root))

    def test_cli_defaults_to_dry_run(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "install_skills.py"),
             "--root", str(self.root), "--target", str(self.target)],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["installed"], [])
        self.assertFalse(self.target.exists())

    def test_installed_validation_allows_unrelated_user_skills(self):
        install_bundle(self.root, self.target, apply=True)
        unrelated = self.target / "user-only" / "SKILL.md"
        unrelated.parent.mkdir()
        unrelated.write_text("existing unrelated content", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_skills.py"),
             "--root", str(self.root), "--skills-dir", str(self.target)],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_linked_source_root_is_rejected_before_copy(self):
        source = self.root / "skills"
        outside_bundle = self.base / "external-skills"
        self.assertTrue(source.resolve().is_relative_to(self.base.resolve()))
        self.assertTrue(outside_bundle.resolve().is_relative_to(self.base.resolve()))
        source.rename(outside_bundle)
        try:
            source.symlink_to(outside_bundle, target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"Directory links are unavailable in this environment: {exc}")
        self.assertTrue(validate_bundle(self.root))
        with self.assertRaises(ValueError):
            install_bundle(self.root, self.target, apply=True)
        self.assertFalse(self.target.exists())

    def test_reference_style_dependencies_are_validated(self):
        path = self.root / "skills" / "research-one" / "SKILL.md"
        with path.open("a", encoding="utf-8") as stream:
            stream.write("\nRead [shared][contract].\n\n"
                         "[contract]: ../research-two/contract.md\n")
        self.assertTrue(validate_bundle(self.root))
        (self.root / "skills" / "research-two" / "contract.md").write_text(
            "# Shared contract\nEvidence handoff.\n", encoding="utf-8"
        )
        self.assertEqual(validate_bundle(self.root), [])

    def test_absolute_local_references_are_not_remote_urls(self):
        path = self.root / "skills" / "research-one" / "SKILL.md"
        original = path.read_text(encoding="utf-8")
        for address in ("C:/missing-suite-reference/contract.md",
                        r"C:\missing-suite-reference\contract.md",
                        "file:///C:/missing-suite-reference/contract.md"):
            with self.subTest(address=address):
                path.write_text(original + f"\nRead [contract]({address}).\n",
                                encoding="utf-8")
                self.assertTrue(validate_bundle(self.root))

    def test_directory_reference_returns_errors_instead_of_crashing(self):
        path = self.root / "skills" / "research-one" / "SKILL.md"
        with path.open("a", encoding="utf-8") as stream:
            stream.write("\nRead [suite](../).\n")
        self.assertTrue(validate_bundle(self.root))

    def test_angle_wrapped_reference_with_spaces_and_parentheses(self):
        folder = self.root / "skills" / "research-one"
        (folder / "notes (sample).md").write_text("# Notes\nUseful evidence.\n", encoding="utf-8")
        with (folder / "SKILL.md").open("a", encoding="utf-8") as stream:
            stream.write("\nRead [notes](<notes (sample).md>).\n")
        self.assertEqual(validate_bundle(self.root), [])

    def test_link_examples_in_code_are_not_dependencies(self):
        path = self.root / "skills" / "research-one" / "SKILL.md"
        with path.open("a", encoding="utf-8") as stream:
            stream.write("\n```markdown\n[example](not-a-dependency.md)\n```\n")
        self.assertEqual(validate_bundle(self.root), [])

    def test_source_link_probe_without_filesystem_link_privileges(self):
        from unittest import mock

        unresolved = self.root / "skills"
        with mock.patch("validate_skills.is_link", side_effect=lambda path: path == unresolved):
            self.assertTrue(validate_bundle(self.root))


if __name__ == "__main__":
    unittest.main()
