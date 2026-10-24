"""Safely update fingerprinted skills; dry-run unless --apply is supplied.

Fingerprint JSON maps skill names to {relative POSIX file path: SHA-256}.
Backup must be a fresh directory outside discovery on the target volume.
Receipts are exclusive, read-only audit records, never rewritten on retry.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
from datetime import datetime, timezone

from install_skills import install_bundle
from validate_skills import NAME, read_manifest, validate_bundle


def checked_info(path):
    info = path.lstat()
    if (stat.S_ISLNK(info.st_mode)
            or getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT):
        raise ValueError(f"Linked/reparse deployment resource: {path}")
    if not (stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode)):
        raise ValueError(f"Special deployment resource: {path}")
    return info


def plain_path(path):
    path = Path(path).expanduser()
    if not path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Deployment paths must be absolute without '..': {path}")
    for ancestor in reversed((path, *path.parents)):
        try:
            info = checked_info(ancestor)
        except FileNotFoundError:
            continue
        if ancestor != path and not stat.S_ISDIR(info.st_mode):
            raise ValueError(f"Deployment ancestor is not a directory: {ancestor}")
    if path.resolve() != path:
        raise ValueError(f"Deployment path is not canonical: {path}")
    return path


def child(parent, name):
    path = plain_path(parent / name)
    if path.parent != parent or not path.is_relative_to(parent):
        raise ValueError(f"Unsafe deployment child: {path}")
    return path


def stamp(info):
    identity = (info.st_dev, info.st_ino, info.st_mode)
    if stat.S_ISDIR(info.st_mode):
        return identity
    # Python 3.12 Windows lstat/fstat disagree on ctime (creation vs change).
    times = (info.st_size, info.st_mtime_ns)
    return identity + times + (() if os.name == "nt" else (info.st_ctime_ns,))


def read_file(path):
    plain_path(path)
    before = checked_info(path)
    if not stat.S_ISREG(before.st_mode):
        raise ValueError(f"Expected a regular file: {path}")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    with os.fdopen(os.open(path, flags), "rb") as stream:
        if stamp(os.fstat(stream.fileno())) != stamp(before):
            raise ValueError(f"File changed while opening: {path}")
        content = stream.read()
        if stamp(os.fstat(stream.fileno())) != stamp(before):
            raise ValueError(f"File changed while reading: {path}")
    if stamp(checked_info(path)) != stamp(before):
        raise ValueError(f"File changed after reading: {path}")
    return content, stamp(before)


def scan(folder):
    """Include directories and identities; scandir errors must propagate."""
    folder = plain_path(folder)
    if not stat.S_ISDIR(checked_info(folder).st_mode):
        raise ValueError(f"Expected deployment directory: {folder}")
    inventory = {}
    pending = [folder]
    while pending:
        directory = pending.pop()
        info = checked_info(directory)
        inventory[directory.relative_to(folder).as_posix()] = (None, stamp(info))
        with os.scandir(directory) as entries:
            for entry in entries:
                path = child(directory, entry.name)
                info = checked_info(path)
                if stat.S_ISDIR(info.st_mode):
                    pending.append(path)
                else:
                    content, identity = read_file(path)
                    inventory[path.relative_to(folder).as_posix()] = (
                        hashlib.sha256(content).hexdigest(), identity)
    return inventory


def subtree(inventory, name):
    return {key[len(name) + 1:]: value for key, value in inventory.items()
            if key.startswith(name + "/")}


def matches(inventory, expected):
    files = {key: value[0] for key, value in inventory.items() if value[0] is not None}
    directories = {key for key, value in inventory.items() if value[0] is None and key != "."}
    expected_dirs = {p.as_posix() for key in expected
                     for p in PurePosixPath(key).parents if p.as_posix() != "."}
    return files == expected and directories == expected_dirs


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate fingerprint key: {key}")
        result[key] = value
    return result


def load_hashes(content):
    data = json.loads(content, object_pairs_hook=unique_object)
    if not isinstance(data, dict) or not data:
        raise ValueError("Fingerprint inventory must be a nonempty skill mapping")
    for name, inventory in data.items():
        if not NAME.fullmatch(name) or len(name) > 64 or not isinstance(inventory, dict):
            raise ValueError(f"Invalid fingerprint skill: {name}")
        if not {"SKILL.md", "agents/openai.yaml"}.issubset(inventory):
            raise ValueError(f"Incomplete fingerprint inventory: {name}")
        seen = set()
        for key, digest in inventory.items():
            parts = key.split("/")
            if (any(not part or part in (".", "..") or part.endswith((".", " "))
                    or re.search(r'[<>:"\\|?*\x00-\x1f]', part)
                    or re.fullmatch(r"(?i:con|prn|aux|nul|com[0-9]|lpt[0-9])(?:\..*)?", part)
                    for part in parts)
                    or key.casefold() in seen or not isinstance(digest, str)
                    or not re.fullmatch(r"[a-f0-9]{64}", digest)):
                raise ValueError(f"Invalid fingerprint file: {name}/{key}")
            seen.add(key.casefold())
    return data


def overlap(left, right):
    return left.is_relative_to(right) or right.is_relative_to(left)


def checked_rename(source, destination):
    source, destination = plain_path(source), plain_path(destination)
    if not stat.S_ISDIR(checked_info(source).st_mode):
        raise ValueError(f"Rename source is not a directory: {source}")
    try:
        checked_info(destination)
    except FileNotFoundError:
        pass
    else:
        raise ValueError(f"Rename would overwrite existing content: {destination}")
    if checked_info(source).st_dev != checked_info(destination.parent).st_dev:
        raise ValueError("Backup and target must share a volume for directory renames")
    source.rename(destination)


def write_receipt(backup, result):
    receipt = child(backup, "update-receipt.json")
    with receipt.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    receipt.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)


def update_install(candidate, before_hashes, candidate_hashes, target, backup, apply=False):
    candidate, before_hashes, candidate_hashes, target, backup = map(
        plain_path, (candidate, before_hashes, candidate_hashes, target, backup))
    if overlap(target, backup):
        raise ValueError("Target and backup must not overlap; backup must be outside discovery")
    for protected in (candidate, before_hashes, candidate_hashes):
        if any(overlap(path, protected) for path in (target, backup)):
            raise ValueError("Deployment paths and candidate/fingerprints must not overlap")
    # st_dev also catches mounted volumes whose drive strings happen to agree.
    backup_parent = next(p for p in backup.parents if p.exists())
    if checked_info(target).st_dev != checked_info(backup_parent).st_dev:
        raise ValueError("Backup and target must share a volume for directory renames")
    frozen_files = {p: read_file(p) for p in
                    (before_hashes, candidate_hashes, candidate / "skills-manifest.json")}
    old = load_hashes(frozen_files[before_hashes][0])
    new = load_hashes(frozen_files[candidate_hashes][0])
    names = read_manifest(candidate)
    if not set(old).issubset(names):
        raise ValueError("Removed old skills are refused")
    if set(new) != set(names):
        raise ValueError("Candidate fingerprint skill set differs from manifest")
    source = scan(candidate / "skills")
    if {key.split("/", 1)[0] for key in source if key != "."} != set(names):
        raise ValueError("Source contains unlisted or missing skill resources")
    installed = scan(target)
    planned, unchanged, added = [], [], []
    for name in names:
        if not matches(subtree(source, name), new[name]):
            raise ValueError(f"Candidate differs from fingerprint snapshot: {name}")
        actual = subtree(installed, name)
        if name in installed and matches(actual, new[name]):
            unchanged.append(name)
        elif name in old and name in installed and matches(actual, old[name]):
            planned.append(name)
        elif name not in old and name not in installed:
            planned.append(name)
            added.append(name)
        else:
            raise ValueError(f"Installed skill differs from known revisions or is missing: {name}")
    errors = validate_bundle(candidate)
    if errors:
        raise ValueError("Invalid candidate: " + "; ".join(errors))

    def recheck_inputs():
        for path, frozen in frozen_files.items():
            if read_file(path) != frozen:
                raise ValueError(f"Input changed after preflight: {path}")
        if scan(candidate / "skills") != source:
            raise ValueError("Candidate changed after preflight")

    def recheck_target():
        if scan(target) != installed:
            raise ValueError("Installed content changed after preflight")

    recheck_inputs()
    recheck_target()
    result = {"target": str(target), "backup": str(backup), "candidate": str(candidate),
              "planned": planned, "unchanged": unchanged, "added": added, "updated": [],
              "before_hashes": old, "candidate_hashes": new,
              "input_sha256": {str(p): hashlib.sha256(v[0]).hexdigest()
                               for p, v in frozen_files.items()}}
    if not apply or not planned:
        return result
    if backup.exists():
        raise ValueError(f"Backup destination already exists: {backup}")
    plain_path(backup)
    backup.mkdir(parents=True)
    moved, installing = [], False
    try:
        for name in planned:
            recheck_inputs()
            recheck_target()
            if name in added:
                continue
            destination, saved = child(target, name), child(backup, name)
            # Register intent first so cancellation immediately after rename is recoverable.
            moved.append(name)
            checked_rename(destination, saved)
            installed = {key: value for key, value in installed.items()
                         if key != name and not key.startswith(name + "/")}
            if not matches(scan(saved), old[name]):
                raise ValueError(f"Backup differs from old fingerprint: {name}")
        recheck_inputs()
        recheck_target()
        installing = True
        install_bundle(candidate, target, apply=True)
        recheck_inputs()
        errors = validate_bundle(candidate, target)
        if errors:
            raise ValueError("Installed validation failed: " + "; ".join(errors))
        recheck_inputs()
        final = scan(target)
        unaffected = {key: value for key, value in final.items()
                      if key.split("/", 1)[0] not in planned}
        if unaffected != installed:
            raise ValueError("Unrelated or unchanged installed content changed during installation")
        for name in names:
            if not matches(subtree(final, name), new[name]):
                raise ValueError(f"Installed bytes differ from candidate: {name}")
            # Hashes seal inputs; direct bytes comparison also verifies the copy.
            for relative in new[name]:
                if read_file(target / name / relative)[0] != read_file(
                        candidate / "skills" / name / relative)[0]:
                    raise ValueError(f"Installed byte comparison failed: {name}/{relative}")
        recheck_inputs()
        if scan(target) != final:
            raise ValueError("Installed content changed during final verification")
        result.update(status="complete", updated=list(planned), backed_up=list(moved),
                      timestamp=datetime.now(timezone.utc).isoformat())
        write_receipt(backup, result)
    except BaseException as exc:
        rollback_errors = []
        for name in reversed(moved + added):
            try:
                destination = child(target, name)
                if name in moved:
                    saved = child(backup, name)
                    if not saved.exists():
                        if destination.exists() and matches(scan(destination), old[name]):
                            moved.remove(name)
                            continue
                        raise ValueError(f"Missing old backup: {saved}")
                    if not matches(scan(saved), old[name]):
                        raise ValueError(f"Old backup changed; preserved for recovery: {saved}")
                if destination.exists():
                    if not installing:
                        raise ValueError(f"Concurrent destination preserved in place: {destination}")
                    quarantine = child(backup, ".failed-candidate")
                    quarantine.mkdir(exist_ok=True)
                    checked_rename(destination, child(quarantine, name))
                if name in moved:
                    checked_rename(child(backup, name), destination)
            except BaseException as recovery_exc:
                rollback_errors.append(f"{name}: {recovery_exc}")
        result.update(status="recovery-incomplete" if rollback_errors else "rolled-back",
                      updated=[], backed_up=list(moved), error=str(exc),
                      recovery_errors=rollback_errors,
                      timestamp=datetime.now(timezone.utc).isoformat())
        try:
            write_receipt(backup, result)
        except BaseException as receipt_exc:
            rollback_errors.append(f"Receipt preserved/unavailable: {receipt_exc}")
        message = (f"Update failed: {exc}; recovery errors: {rollback_errors}; "
                   f"backup/quarantined files preserved at {backup}")
        if not isinstance(exc, Exception):
            print(message, file=sys.stderr)
            raise
        raise RuntimeError(message) from exc
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("candidate", "before-hashes", "candidate-hashes", "target", "backup"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--apply", action="store_true", help="Apply the preflighted update")
    try:
        result = update_install(**vars(parser.parse_args()))
    except (OSError, ValueError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
