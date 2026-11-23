"""Check study identities and split/locator integrity, not reading or science."""

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re


def default_data_dir(root):
    """Study data: $STUDY_DATA_DIR, then .build/ (scripts/fetch_study_data.py), then docs/."""
    root = Path(root)
    if os.environ.get("STUDY_DATA_DIR"):
        return Path(os.environ["STUDY_DATA_DIR"])
    fetched = root / ".build/paper-presentation-study"
    return fetched if fetched.is_dir() else root / "docs/paper-presentation-study"


def validate_study(root, data=None):
    root = Path(root)
    library = root / "skills/research-write/references/paper-style-study"
    docs = Path(data) if data else default_data_dir(root)
    errors = []
    try:
        registry = json.loads((library / "sources.json").read_text("utf-8"))
        patterns = json.loads((library / "patterns.json").read_text("utf-8"))
        freeze = json.loads((docs / "pattern-freeze.json").read_text("utf-8"))
        records = []
        for split in ("discovery", "holdout"):
            records.extend(json.loads((docs / f"{split}-readings.json").read_text("utf-8")))
        papers = registry["papers"]
        by_id = {p["id"]: p for p in papers}
        reads = {p["id"]: p for p in records}
        if len(papers) != 90 or len(by_id) != 90 or len(records) != 90 or len(reads) != 90:
            errors.append("Require 90 unique sources and 90 unique reading records.")
        if set(reads) != set(by_id):
            errors.append("Reading/source identity sets differ.")
        if len({p["pdf_sha256"] for p in papers}) != 90:
            errors.append("Duplicate PDF identities in sample.")
        cells = Counter((p["venue"], p["year"], p["role"], p["split"]) for p in papers)
        venue_years = {(p["venue"], p["year"]) for p in papers}
        if len(venue_years) != 15:
            errors.append("Require 15 venue-year cells.")
        for venue, year in venue_years:
            for role, split, expected in (
                ("selected", "discovery", 3), ("selected", "holdout", 1),
                ("control", "discovery", 1), ("control", "holdout", 1),
            ):
                if cells[(venue, year, role, split)] != expected:
                    errors.append(f"Invalid split in {venue}-{year}/{role}/{split}.")
        for paper in papers:
            pid = paper["id"]
            if not re.fullmatch(r"[0-9a-f]{64}", paper["pdf_sha256"]):
                errors.append(f"{pid}: invalid PDF digest.")
            record = reads.get(pid)
            if record is None:
                continue
            for a, b in (("source_pdf_sha256", "pdf_sha256"),
                         ("source_version", "version"), ("category", "category"),
                         ("split", "split")):
                if record.get(a) != paper[b]:
                    errors.append(f"{pid}: {a} disagrees with pinned source.")
            coverage = record["coverage"]
            pages = coverage.get("main_pdf_pages_read", [])
            images = coverage.get("detail_image_pages_viewed", [])
            if not pages or sorted(set(pages)) != list(range(1, max(pages) + 1)):
                errors.append(f"{pid}: main-text coverage is empty or has gaps.")
            if not images:
                errors.append(f"{pid}: no actual detail image recorded.")
            for page in pages + images:
                if not isinstance(page, int) or not 1 <= page <= paper["total_pdf_pages"]:
                    errors.append(f"{pid}: page outside pinned PDF.")
        if patterns.get("status") != "frozen" or not patterns.get("frozen_at"):
            errors.append("Pattern cards must be frozen before holdout evaluation.")
        if (hashlib.sha256((library / "patterns.json").read_bytes()).hexdigest()
                != freeze["patterns_sha256"]):
            errors.append("Pattern content changed after the recorded freeze.")
        if patterns["frozen_at"] != freeze["frozen_at"] or freeze["holdout_read_at_freeze"] != 0:
            errors.append("Pattern freeze chronology is inconsistent.")
        card_ids = {card["id"] for card in patterns["cards"]}
        for record in records:
            if record.get("split") != "holdout":
                continue
            checks = record.get("pattern_checks", [])
            if len(checks) != len(card_ids) or {c["pattern_id"] for c in checks} != card_ids:
                errors.append(f"{record['id']}: incomplete holdout pattern assessment.")
            for check in checks:
                if (check.get("verdict") not in {"fits", "qualified", "not-applicable", "counterexample"}
                        or not check.get("reason") or not check.get("locator")):
                    errors.append(f"{record['id']}: invalid or unexplained holdout assessment.")
        for card in patterns["cards"]:
            cited = set()
            venues = set()
            for source in card["sources"]:
                pid = source["paper_id"]
                paper = by_id.get(pid)
                record = reads.get(pid)
                if paper is None or record is None:
                    errors.append(f"{card['id']}: missing source {pid}.")
                    continue
                if paper["split"] != "discovery":
                    errors.append(f"{card['id']}: holdout used as discovery evidence.")
                cited.add(pid)
                venues.add(paper["venue"])
                read_pages = record["coverage"]["main_pdf_pages_read"]
                if not set(source["pdf_pages"]) <= set(read_pages):
                    errors.append(f"{card['id']}: source locator exceeds main-text reading scope.")
                if re.search(r"\b(?:figure|table)\b", source["locator"], re.IGNORECASE):
                    viewed_pages = record["coverage"]["detail_image_pages_viewed"]
                    if not set(source["pdf_pages"]) & set(viewed_pages):
                        errors.append(
                            f"{card['id']}: visual locator has no matching viewed detail page."
                        )
            if card["evidence_level"] == "repeated-cross-venue-observation":
                if len(cited) < 3 or len(venues) < 2:
                    errors.append(f"{card['id']}: insufficient independent cross-venue support.")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f"Malformed or missing study record: {exc}")
    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--data", type=Path, help="Study data directory (default: fetched .build copy)")
    args = parser.parse_args()
    data = args.data or default_data_dir(args.root)
    if not (data / "discovery-readings.json").is_file():
        print(json.dumps({"status": "data-missing", "data": str(data),
                          "detail": "Run python scripts/fetch_study_data.py first"}, indent=2))
        raise SystemExit(2)
    problems = validate_study(args.root, data)
    print(json.dumps({"status": "failed" if problems else "passed",
                      "errors": problems,
                      "limit": "Record consistency only; not proof of reading or scientific correctness."},
                     indent=2))
    raise SystemExit(bool(problems))
