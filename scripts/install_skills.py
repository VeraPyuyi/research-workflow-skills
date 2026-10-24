"""Install the complete suite; dry-run by default and never overwrite different files."""

import argparse
import json
import os
from pathlib import Path
import shutil
import sys

from validate_skills import is_link, read_manifest, validate_bundle


def file_inventory(folder: Path) -> dict[str, bytes]:
    inventory = {}
    for path in folder.rglob("*"):
        if is_link(path) or not path.resolve().is_relative_to(folder.resolve()):
            raise ValueError(f"Linked resources are not supported: {path}")
        if path.is_file():
            inventory[path.relative_to(folder).as_posix()] = path.read_bytes()
    return inventory


def install_bundle(root: Path, target: Path, apply: bool = False) -> dict:
    root = Path(root).resolve()
    source = (root / "skills").resolve()
    target = Path(target).expanduser().resolve()
    if target.is_relative_to(source) or source.is_relative_to(target):
        raise ValueError("Source and installation target must not overlap")
    errors = validate_bundle(root)
    if errors:
        raise ValueError("Invalid source bundle:\n" + "\n".join(errors))
    if target.exists() and not target.is_dir():
        raise ValueError(f"Target is not a directory: {target}")
    names = read_manifest(root)
    planned, unchanged = [], []
    for name in names:
        destination = target / name
        if is_link(destination) or not destination.resolve().is_relative_to(target):
            raise ValueError(f"Unsafe destination: {destination}")
        if destination.exists():
            if not destination.is_dir() or file_inventory(destination) != file_inventory(source / name):
                raise ValueError(f"Existing different skill is preserved; resolve conflict before installing: {destination}")
            unchanged.append(name)
        else:
            planned.append(name)
    result = {"target": str(target), "planned": planned, "installed": [], "unchanged": unchanged}
    if apply and planned:
        target.mkdir(parents=True, exist_ok=True)
        for name in planned:
            try:
                shutil.copytree(source / name, target / name)
            except OSError as exc:
                raise ValueError(
                    f"Copy failed for {name}; installed so far: {result['installed']}. "
                    f"Inspect the possibly partial new directory before retrying: {exc}"
                ) from exc
            result["installed"].append(name)
    return result


def main() -> int:
    default_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--target", type=Path, default=default_home / "skills")
    parser.add_argument("--apply", action="store_true", help="Perform the preflighted copy")
    args = parser.parse_args()
    try:
        result = install_bundle(args.root, args.target, args.apply)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
