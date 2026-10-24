"""Scoped updater integration tests; fixtures stay on the workspace volume."""

from contextlib import redirect_stderr
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
try:
    import update_skills as updater
except ModuleNotFoundError as exc:
    if exc.name != "update_skills":
        raise
    updater = None


def files(folder):
    return {p.relative_to(folder).as_posix(): p.read_bytes()
            for p in folder.rglob("*") if p.is_file()}


def fingerprints(folder):
    return {name: hashlib.sha256(content).hexdigest()
            for name, content in files(folder).items()}


class SkillUpdateTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(updater, "The scoped safe updater is not implemented")
        build = ROOT / ".build" / "jev-autonomy-20261024"
        build.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="skill-update-test-", dir=build)
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.candidate = self.base / "candidate"
        self.target = self.base / "discovery" / "skills"
        self.backup = self.base / "backups" / "update-1"
        self.old = [f"research-stage-{i}" for i in range(16)]
        self.added = "research-stage-16"
        self.names = self.old + [self.added]
        self.target.mkdir(parents=True)
        self.candidate.mkdir()
        for name in self.names:
            folder = self.candidate / "skills" / name
            (folder / "agents").mkdir(parents=True)
            (folder / "SKILL.md").write_text(
                f"---\nname: {name}\ndescription: Use when assessing research evidence.\n"
                "---\n\nAssess evidence and report uncertainty.\n", encoding="utf-8")
            (folder / "agents" / "openai.yaml").write_text(
                "interface:\n  display_name: Research Stage\n"
                "  short_description: Assess the supplied research evidence\n"
                f"  default_prompt: Use ${name} to assess evidence.\n", encoding="utf-8")
            if name in self.old:
                shutil.copytree(folder, self.target / name)
        self.manifest = self.candidate / "skills-manifest.json"
        self.manifest.write_text(json.dumps({"version": 1, "skills": self.names}),
                                 encoding="utf-8")
        self.before = self.base / "before-hashes.json"
        self.before.write_text(json.dumps({n: fingerprints(self.target / n)
                                           for n in self.old}), encoding="utf-8")
        with (self.candidate / "skills" / self.old[0] / "SKILL.md").open("a") as stream:
            stream.write("\nRequire an evidence ledger.\n")
        self.expected = self.base / "candidate-hashes.json"
        self.expected.write_text(json.dumps({n: fingerprints(self.candidate / "skills" / n)
                                             for n in self.names}), encoding="utf-8")
        unrelated = self.target / "my-custom-skill"
        unrelated.mkdir()
        (unrelated / "SKILL.md").write_bytes(b"user content\x00\xff")
        self.original = files(self.target)

    def update(self, apply=True, **changes):
        args = dict(candidate=self.candidate, before_hashes=self.before,
                    candidate_hashes=self.expected, target=self.target,
                    backup=self.backup, apply=apply)
        args.update(changes)
        return updater.update_install(**args)

    def assert_untouched(self):
        self.assertEqual(files(self.target), self.original)
        self.assertFalse(self.backup.exists())

    def test_dry_run_plans_changed_and_new_seventeenth_without_writes(self):
        result = self.update(apply=False)
        self.assertEqual(result["planned"], [self.old[0], self.added])
        self.assertEqual(result["updated"], [])
        self.assert_untouched()

    def test_apply_backs_up_changed_old_and_installs_seventeenth(self):
        result = self.update()
        self.assertEqual(result["updated"], [self.old[0], self.added])
        for name in self.names:
            self.assertEqual(files(self.target / name), files(self.candidate / "skills" / name))
        self.assertEqual(files(self.backup / self.old[0]),
                         {p.split("/", 1)[1]: b for p, b in self.original.items()
                          if p.startswith(self.old[0] + "/")})
        self.assertFalse((self.backup / self.added).exists())
        self.assertEqual((self.target / "my-custom-skill/SKILL.md").read_bytes(),
                         b"user content\x00\xff")
        receipt = json.loads((self.backup / "update-receipt.json").read_text())
        self.assertEqual(receipt["status"], "complete")
        self.assertEqual(receipt["updated"], [self.old[0], self.added])
        self.assertEqual(receipt["candidate_hashes"], json.loads(self.expected.read_text()))

    def test_exact_retry_preserves_bytes_timestamps_and_immutable_receipt(self):
        self.update()
        receipt = self.backup / "update-receipt.json"
        original_receipt = receipt.read_bytes()
        stamps = {p: p.stat().st_mtime_ns for p in self.target.rglob("*")}
        result = self.update()
        self.assertEqual(result["planned"], [])
        self.assertEqual(result["updated"], [])
        self.assertEqual(result["unchanged"], self.names)
        self.assertEqual(receipt.read_bytes(), original_receipt)
        self.assertEqual({p: p.stat().st_mtime_ns for p in self.target.rglob("*")}, stamps)

    def test_new_skill_already_exact_candidate_is_allowed(self):
        shutil.copytree(self.candidate / "skills" / self.added, self.target / self.added)
        result = self.update()
        self.assertEqual(result["updated"], [self.old[0]])
        self.assertIn(self.added, result["unchanged"])

    def test_custom_content_in_old_or_added_folder_refuses_all_writes(self):
        for name in (self.old[-1], self.added):
            with self.subTest(name=name):
                folder = self.target / name
                folder.mkdir(exist_ok=True)
                custom = folder / "custom.txt"
                custom.write_bytes(b"keep my notes")
                snapshot = files(self.target)
                with self.assertRaises(ValueError):
                    self.update()
                self.assertEqual(files(self.target), snapshot)
                self.assertFalse(self.backup.exists())
                custom.unlink()
                if name == self.added:
                    folder.rmdir()

    def test_missing_old_skill_is_not_silently_reinstalled(self):
        folder = self.target / self.old[-1]
        folder.rename(self.base / "missing-old")
        with self.assertRaises(ValueError):
            self.update()
        self.assertFalse(self.backup.exists())
        self.assertFalse((self.target / self.added).exists())

    def test_removed_old_skill_is_refused(self):
        data = json.loads(self.before.read_text())
        data["research-removed"] = data[self.old[0]]
        self.before.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            self.update()
        self.assert_untouched()

    def test_stale_candidate_or_fingerprints_refuse_all_writes(self):
        path = self.candidate / "skills" / self.added / "SKILL.md"
        original = path.read_bytes()
        path.write_bytes(original + b"\nUnsealed edit.\n")
        with self.assertRaises(ValueError):
            self.update()
        self.assert_untouched()

        path.write_bytes(original)
        data = json.loads(self.expected.read_text())
        data[self.added]["SKILL.md"] = "0" * 64
        self.expected.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            self.update()
        self.assert_untouched()

    def test_unfingerprinted_file_at_source_root_is_refused(self):
        (self.candidate / "skills" / "unlisted.txt").write_bytes(b"not fingerprinted")
        with self.assertRaises(ValueError):
            self.update()
        self.assert_untouched()

    def test_malformed_or_escaping_fingerprint_inventory_is_refused(self):
        original = self.before.read_bytes()
        for bad in ({"../escape": {}}, {self.old[0]: {"../outside": "0" * 64}},
                    {self.old[0]: {"SKILL.md": "not-a-digest"}}, []):
            with self.subTest(bad=bad):
                self.before.write_text(json.dumps(bad))
                with self.assertRaises(ValueError):
                    self.update()
                self.assert_untouched()
        self.before.write_bytes(original)

    def test_partial_install_failure_restores_old_and_quarantines_new_folder(self):
        copytree = shutil.copytree

        def partial(source, destination, *args, **kwargs):
            if Path(source).name == self.added:
                Path(destination).mkdir()
                (Path(destination) / "partial.txt").write_bytes(b"partial seventeenth")
                raise OSError("injected copy failure")
            return copytree(source, destination, *args, **kwargs)

        with mock.patch("install_skills.shutil.copytree", side_effect=partial):
            with self.assertRaisesRegex(RuntimeError, "injected copy failure"):
                self.update()
        self.assertEqual(files(self.target), self.original)
        self.assertEqual((self.backup / ".failed-candidate" / self.added /
                          "partial.txt").read_bytes(), b"partial seventeenth")
        self.assertEqual(files(self.backup / ".failed-candidate" / self.old[0]),
                         files(self.candidate / "skills" / self.old[0]))
        receipt = json.loads((self.backup / "update-receipt.json").read_text())
        self.assertEqual(receipt["status"], "rolled-back")

    def test_changes_during_preflight_are_preserved_and_abort_before_backup(self):
        validate = updater.validate_bundle
        for path in (self.target / self.old[-1] / "SKILL.md",
                     self.target / "my-custom-skill/SKILL.md", self.before,
                     self.expected, self.manifest,
                     self.candidate / "skills" / self.added / "SKILL.md"):
            with self.subTest(path=path):
                original = path.read_bytes()

                def change(*args, **kwargs):
                    result = validate(*args, **kwargs)
                    path.write_bytes(original + b"\n ")
                    return result

                with mock.patch.object(updater, "validate_bundle", side_effect=change):
                    with self.assertRaises(ValueError):
                        self.update()
                self.assertFalse(self.backup.exists())
                self.assertEqual(path.read_bytes(), original + b"\n ")
                self.assertFalse((self.target / self.added).exists())
                path.write_bytes(original)

    def test_change_after_backup_before_install_rolls_back_without_losing_edit(self):
        rename = Path.rename
        changed = self.target / "my-custom-skill/SKILL.md"

        def concurrent(path, destination):
            result = rename(path, destination)
            if path == self.target / self.old[0]:
                changed.write_bytes(b"concurrent user edit")
            return result

        with mock.patch.object(Path, "rename", concurrent):
            with self.assertRaises(RuntimeError):
                self.update()
        expected = dict(self.original)
        expected["my-custom-skill/SKILL.md"] = b"concurrent user edit"
        self.assertEqual(files(self.target), expected)

    def test_candidate_change_during_copy_fails_verification_and_rolls_back(self):
        install = updater.install_bundle

        def change(*args, **kwargs):
            path = self.candidate / "skills" / self.added / "SKILL.md"
            path.write_bytes(path.read_bytes() + b"\nlate edit\n")
            return install(*args, **kwargs)

        with mock.patch.object(updater, "install_bundle", side_effect=change):
            with self.assertRaises(RuntimeError):
                self.update()
        self.assertEqual(files(self.target), self.original)

    def test_interrupt_just_after_backup_rename_still_restores_old_directory(self):
        rename = Path.rename

        def interrupted(path, destination):
            result = rename(path, destination)
            if path == self.target / self.old[0]:
                raise KeyboardInterrupt("injected cancellation after rename")
            return result

        with mock.patch.object(Path, "rename", interrupted), redirect_stderr(io.StringIO()):
            with self.assertRaises(KeyboardInterrupt):
                self.update()
        self.assertEqual(files(self.target), self.original)
        self.assertEqual(json.loads((self.backup / "update-receipt.json").read_text())
                         ["status"], "rolled-back")

    def test_special_file_metadata_is_refused_before_opening(self):
        lstat = Path.lstat
        for special in (self.candidate / "skills" / self.added / "SKILL.md",
                        self.target / "my-custom-skill/SKILL.md"):
            with self.subTest(special=special):
                def special_info(path):
                    if path == special:
                        return SimpleNamespace(st_mode=stat.S_IFIFO, st_file_attributes=0)
                    return lstat(path)

                with mock.patch.object(Path, "lstat", special_info):
                    with self.assertRaisesRegex(ValueError, "Special"):
                        self.update()
                self.assert_untouched()

    def test_cross_volume_backup_is_refused(self):
        checked_info = updater.checked_info

        def different_volume(path):
            info = checked_info(path)
            if path == self.base:
                return SimpleNamespace(st_mode=info.st_mode, st_dev=info.st_dev + 1)
            return info

        with mock.patch.object(updater, "checked_info", side_effect=different_volume):
            with self.assertRaisesRegex(ValueError, "volume"):
                self.update()
        self.assert_untouched()

    def test_custom_empty_directory_is_preserved_and_refused(self):
        empty = self.target / self.old[0] / "custom-empty"
        empty.mkdir()
        with self.assertRaises(ValueError):
            self.update()
        self.assertTrue(empty.is_dir())
        self.assert_untouched()

    def test_new_destination_created_during_preflight_is_preserved(self):
        validate = updater.validate_bundle
        custom = self.target / self.added / "custom.txt"

        def change(*args, **kwargs):
            result = validate(*args, **kwargs)
            custom.parent.mkdir()
            custom.write_bytes(b"concurrent new skill")
            return result

        with mock.patch.object(updater, "validate_bundle", side_effect=change):
            with self.assertRaises(ValueError):
                self.update()
        self.assertEqual(custom.read_bytes(), b"concurrent new skill")
        self.assertFalse(self.backup.exists())

    def test_unsafe_or_overlapping_paths_and_existing_backup_are_refused(self):
        self.backup.mkdir(parents=True)
        marker = self.backup / "preserved.txt"
        marker.write_bytes(b"existing backup")
        for changes in ({}, {"backup": self.target / "backup"},
                        {"backup": self.target.parent},
                        {"backup": self.candidate / "backup"},
                        {"target": self.candidate / "skills"},
                        {"backup": Path("relative-backup")}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.update(**changes)
        self.assertEqual(marker.read_bytes(), b"existing backup")
        self.assertEqual(files(self.target), self.original)

    def test_reparse_ancestor_is_rejected(self):
        lstat = Path.lstat

        def reparse(path):
            info = lstat(path)
            if path == self.target.parent:
                return SimpleNamespace(st_mode=info.st_mode,
                                       st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT)
            return info

        with mock.patch.object(Path, "lstat", reparse):
            with self.assertRaisesRegex(ValueError, "reparse"):
                self.update()
        self.assert_untouched()

    def test_incomplete_enumeration_aborts_without_writes(self):
        scandir = os.scandir

        def denied(path):
            if Path(path) == self.target / self.old[-1] / "agents":
                raise PermissionError("injected unreadable subtree")
            return scandir(path)

        with mock.patch.object(updater.os, "scandir", side_effect=denied):
            with self.assertRaises((OSError, ValueError)):
                self.update()
        self.assert_untouched()

    def test_cli_requires_opt_in_and_accepts_parameterized_inputs(self):
        result = subprocess.run(
            [sys.executable, "-B", str(ROOT / "scripts/update_skills.py"),
             "--candidate", str(self.candidate), "--before-hashes", str(self.before),
             "--candidate-hashes", str(self.expected), "--target", str(self.target),
             "--backup", str(self.backup)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["planned"], [self.old[0], self.added])
        self.assert_untouched()


if __name__ == "__main__":
    unittest.main()
