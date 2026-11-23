"""Check that relative Markdown links in README.md and docs/ point to files in the repository.

validate_skills.py checks links inside skills/; this covers the rest. External
URLs and in-page anchors are not fetched.
"""
from pathlib import Path
import re
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\)")


def broken_links(root=ROOT):
    problems = []
    files = [root / "README.md"] + sorted((root / "docs").rglob("*.md"))
    for path in files:
        if not path.is_file():
            continue
        text = re.sub(r"```.*?```", "", path.read_text(encoding="utf-8"), flags=re.S)
        for target in LINK.findall(text):
            if re.match(r"[a-z]+:", target) or target.startswith("#"):
                continue
            target = unquote(target.split("#", 1)[0])
            if target and not (path.parent / target).exists():
                problems.append(f"{path.relative_to(root)}: {target}")
    return problems


if __name__ == "__main__":
    found = broken_links()
    print("\n".join(found) if found else "All relative links in README.md and docs/ resolve.")
    sys.exit(1 if found else 0)
