"""Fetch the paper-presentation study data into .build/paper-presentation-study.

The study data (reading records, behaviour comparison, renders) lives on the
data-only branch ``paper-presentation-study-data`` of this repository, pinned
below by commit and by a content manifest. This script fetches that commit
with git (or copies from a local checkout given with --source), verifies the
manifest for this branch's runtime profile and writes the files to
``.build/paper-presentation-study`` for scripts/validate_presentation_study.py.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
REMOTE = "https://github.com/VeraPyuyi/research-workflow-skills.git"
DATA_COMMIT = "81261ddcdd05fbee53a728ebdb8618f6bc5ce7bc"
MANIFESTS = {
    "magpie": "356400fadd9ae3e3bd3a4ac9ef619e70058db70245a8db3861441b6ccbd0d065",
    "codex-native": "148e80ccfdfcc74977703bbe022686298ad738dfa333333b86d493918ddf3f60",
}
TARGET = ROOT / ".build" / "paper-presentation-study"


def manifest_digest(base):
    rows = sorted(f"{p.relative_to(base).as_posix()}\0{hashlib.sha256(p.read_bytes()).hexdigest()}"
                  for p in Path(base).rglob("*") if p.is_file())
    return hashlib.sha256("\n".join(rows).encode()).hexdigest()


def profile():
    return json.loads((ROOT / "skills-manifest.json").read_text(encoding="utf-8"))["runtime_profile"]


def fetch(remote, checkout):
    subprocess.run(["git", "init", "-q", str(checkout)], check=True)
    # Keep the pinned bytes: no line-ending conversion (Windows defaults to autocrlf).
    for key, value in (("core.autocrlf", "false"), ("core.eol", "lf")):
        subprocess.run(["git", "-C", str(checkout), "config", key, value], check=True)
    subprocess.run(["git", "-C", str(checkout), "fetch", "-q", "--depth", "1", remote, DATA_COMMIT], check=True)
    subprocess.run(["git", "-C", str(checkout), "checkout", "-q", "FETCH_HEAD"], check=True)
    head = subprocess.run(["git", "-C", str(checkout), "rev-parse", "HEAD"], capture_output=True,
                          text=True, check=True).stdout.strip()
    if head != DATA_COMMIT:
        raise ValueError("Fetched commit differs from the pinned data commit")


def install(source_root, name, target=TARGET):
    source = Path(source_root) / name / "paper-presentation-study"
    if not source.is_dir():
        raise ValueError(f"No study data for profile {name} in {source_root}")
    digest = manifest_digest(source)
    if digest != MANIFESTS[name]:
        raise ValueError(f"Study data manifest mismatch for {name}: {digest}")
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target)
    return digest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", type=Path, help="Local checkout of the data branch (skips git fetch)")
    parser.add_argument("--remote", default=REMOTE)
    args = parser.parse_args(argv)
    name = profile()
    try:
        if args.source:
            digest = install(args.source, name)
        else:
            with tempfile.TemporaryDirectory() as tmp:
                fetch(args.remote, Path(tmp) / "data")
                digest = install(Path(tmp) / "data", name)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(json.dumps({"status": "error", "detail": str(exc)}))
        return 1
    print(json.dumps({"status": "installed", "profile": name, "target": str(TARGET.relative_to(ROOT)),
                      "commit": DATA_COMMIT, "manifest_sha256": digest}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
