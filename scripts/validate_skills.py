"""Validate a portable research skill suite without changing it."""

import argparse
import codecs
import importlib.util
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

import yaml


NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", re.S)
INLINE_LINK = re.compile(r"!?\[[^\]\n]*\]\(\s*(?:<([^>\n]+)>|([^\s()]+))\s*\)")
REFERENCE_DEFINITION = re.compile(
    r"^ {0,3}\[([^\]\n]+)\]:\s*(?:<([^>\n]+)>|(\S+))", re.M
)


def read_manifest(root: Path) -> list[str]:
    try:
        data = json.loads((root / "skills-manifest.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError(f"Cannot read skill manifest: {exc}") from exc
    if not isinstance(data, dict) or data.get("version") != 1:
        raise ValueError("Manifest must be an object with version 1")
    if "runtime_profile" in data and data["runtime_profile"] not in ("magpie", "codex-native"):
        raise ValueError("Manifest runtime_profile must be magpie or codex-native")
    names = data.get("skills")
    if not isinstance(names, list) or not names:
        raise ValueError("Manifest skills must be a nonempty list")
    if any(not isinstance(name, str) or not NAME.fullmatch(name) or len(name) > 64
           for name in names):
        raise ValueError("Manifest contains an invalid skill name")
    if len(names) != len(set(names)):
        raise ValueError("Manifest contains duplicate skill names")
    return names


def is_link(path: Path) -> bool:
    return path.is_symlink() or path.is_junction()


def markdown_links(text: str) -> list[str]:
    """Return inline and reference-style targets, excluding fenced code."""
    active = []
    fence = None
    for line in text.splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token[0]
                active.append("")
                continue
            if token[0] == fence:
                fence = None
                active.append("")
                continue
        active.append("" if fence is not None else line)
    visible = "\n".join(active)
    links = [angle or plain for angle, plain in INLINE_LINK.findall(visible)]
    links.extend(angle or plain for _, angle, plain in REFERENCE_DEFINITION.findall(visible))
    return links


def local_reference(document: Path, source: Path, href: str) -> tuple[Path | None, bool]:
    """Resolve local targets; reject local paths that escape the bundle."""
    href = href.strip()
    parsed = urlsplit(href)
    is_file_url = parsed.scheme.lower() == "file"
    is_windows_path = re.match(r"^[A-Za-z]:[\\/]", href) is not None
    is_absolute = href.startswith(("/", "\\"))
    if parsed.scheme and not is_file_url and not is_windows_path:
        return None, False
    if parsed.netloc and not is_file_url:
        return None, False
    if is_file_url:
        path_text = unquote(parsed.path)
        if re.match(r"^/[A-Za-z]:/", path_text):
            path_text = path_text[1:]
        target = Path(path_text)
    elif is_windows_path or is_absolute:
        target = Path(unquote(href))
    else:
        path_text = unquote(parsed.path)
        if not path_text:
            raise ValueError(f"reference has no local file target: {href}")
        target = document.parent / path_text
    target = target.resolve()
    if not target.is_relative_to(source):
        return target, True
    return target, False


def yaml_mapping(text: str, label: str) -> dict:
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ValueError(f"{label}: invalid YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{label}: expected a YAML mapping")
    return data


def validate_bundle(root: Path, skills_dir: Path | None = None) -> list[str]:
    bundle = Path(root).expanduser()
    root = bundle.resolve()
    errors = []
    try:
        names = read_manifest(root)
    except ValueError as exc:
        return [str(exc)]
    unresolved_source = Path(skills_dir).expanduser() if skills_dir is not None else bundle / "skills"
    if is_link(unresolved_source):
        return [f"Skill directory cannot be a symlink or junction: {unresolved_source}"]
    source = unresolved_source.resolve()
    if skills_dir is None and not source.is_relative_to(root):
        return [f"Skill directory escapes the bundle: {unresolved_source}"]
    if not source.is_dir():
        return [f"Skill directory does not exist: {source}"]
    release_path = source / "research-navigate/references/workflow-release.json"
    manifest = json.loads((root / "skills-manifest.json").read_text(encoding="utf-8"))
    release = None
    if release_path.is_file():
        try:
            release = json.loads(release_path.read_text(encoding="utf-8"))
            if not isinstance(release, dict):
                raise ValueError("Release metadata must be an object")
            if ("runtime_profile" in release
                    and release["runtime_profile"] != manifest.get("runtime_profile")):
                errors.append("Release runtime_profile differs from the suite manifest")
        except (OSError, ValueError, TypeError):
            errors.append("Release metadata cannot be read for runtime_profile validation")
    if "research-navigate" in names or "runtime_profile" in manifest or release is not None:
        try:
            # Use the trusted bundled checker, never execute code from the inspected suite.
            helper = Path(__file__).resolve().parents[1] / "skills/research-navigate/scripts/workflow_release.py"
            spec = importlib.util.spec_from_file_location("bundle_runtime_profile", helper)
            runtime = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(runtime)
            expected = manifest.get("runtime_profile")
            if release is not None:
                if "runtime_profile" not in release:
                    # The only unprofiled exception must be the actual original metadata.
                    runtime._validate_metadata(release, source)
                expected = runtime._release_profile(release)
            runtime.validate_runtime_profile(source, expected, legacy_release=release,
                                             manifest_path=root / "skills-manifest.json")
        except (OSError, ValueError, TypeError) as exc:
            errors.append(f"runtime_profile routing validation: {exc}")
    if skills_dir is None:
        extra = sorted(p.name for p in source.iterdir()
                       if p.is_dir() and p.name not in names)
        if extra:
            errors.append(f"Unlisted skill directories: {', '.join(extra)}")

    for name in names:
        folder = source / name
        if is_link(folder) or not folder.resolve().is_relative_to(source):
            errors.append(f"{name}: linked/outside skill directory is not portable")
            continue
        if not folder.is_dir():
            errors.append(f"{name}: missing skill directory")
            continue
        entries = list(folder.rglob("*"))
        unsafe = [p for p in entries if is_link(p)
                  or not p.resolve().is_relative_to(folder.resolve())]
        if unsafe:
            errors.append(f"{name}: linked/outside resources are not supported")
            continue
        try:
            skill_text = (folder / "SKILL.md").read_text(encoding="utf-8")
            match = FRONTMATTER.match(skill_text)
            if match is None:
                raise ValueError(f"{name}: missing YAML frontmatter")
            metadata = yaml_mapping(match.group(1), name)
            if metadata.get("name") != name:
                errors.append(f"{name}: frontmatter name does not match directory")
            description = metadata.get("description")
            if not isinstance(description, str) or not description.strip() or len(description) > 1024:
                errors.append(f"{name}: description must contain 1-1024 characters")
            if not skill_text[match.end():].strip():
                errors.append(f"{name}: empty skill instructions")
            ui_data = yaml_mapping(
                (folder / "agents" / "openai.yaml").read_text(encoding="utf-8"), name
            )
            interface = ui_data.get("interface")
            if not isinstance(interface, dict):
                raise ValueError(f"{name}: missing UI interface mapping")
            for key in ("display_name", "short_description", "default_prompt"):
                if not isinstance(interface.get(key), str) or not interface[key].strip():
                    errors.append(f"{name}: missing UI {key}")
            short = interface.get("short_description", "")
            if not isinstance(short, str) or not 25 <= len(short) <= 64:
                errors.append(f"{name}: UI short_description must be 25-64 characters")
            prompt = interface.get("default_prompt", "")
            if not isinstance(prompt, str) or not re.search(
                rf"\${re.escape(name)}(?![a-z0-9-])", prompt
            ):
                errors.append(f"{name}: UI prompt does not invoke this skill")
            policy = ui_data.get("policy", {})
            if not isinstance(policy, dict) or policy.get("allow_implicit_invocation", True) is not True:
                errors.append(f"{name}: automatic discovery must remain enabled")
        except (OSError, UnicodeError, ValueError) as exc:
            errors.append(f"{name}: {exc}")
            continue

        for document in (p for p in entries if p.is_file() and p.suffix == ".md"):
            try:
                text = document.read_text(encoding="utf-8")
                for href in markdown_links(text):
                    target, escapes = local_reference(document, source, href)
                    if target is None:
                        continue
                    if escapes:
                        errors.append(f"{name}: reference leaves installed suite: {href}")
                        continue
                    relative = target.relative_to(source)
                    if not relative.parts:
                        errors.append(f"{name}: reference must name a packaged file: {href}")
                    elif relative.parts[0] not in names:
                        errors.append(f"{name}: reference depends on an unshipped skill: {href}")
                    elif not target.is_file():
                        errors.append(f"{name}: missing reference: {href}")
            except (OSError, UnicodeError, ValueError) as exc:
                errors.append(f"{document}: {exc}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--skills-dir", type=Path, help="Validate an installed copy using the source manifest")
    args = parser.parse_args()
    errors = validate_bundle(args.root, args.skills_dir)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"Validated {len(read_manifest(args.root))} skills: metadata and packaged references are complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
