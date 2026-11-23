"""List manuscript numbers that cannot be traced to recorded results.

Collects reportable numbers from the manuscript (decimals and percentages in
prose and tables; integers, years, references, labels and equations are
skipped) and looks each one up among the recorded values:

* ``values`` of every claim in ``analysis/claims.jsonl``;
* every numeric cell of the CSV tables given with ``--table`` (for example the
  ``table.csv`` written by render_evidence.py).

A number matches when a recorded value rounds to it at the precision printed
in the paper, directly or as a percentage (0.183 -> 18.3%). Unmatched numbers
are candidates for review, not proof of fabrication: a number may come from a
cited source, a hyperparameter or a derived quantity, in which case add it to a
claim's ``values`` or pass ``--allow`` with a reason in the handoff.

Exit status: 0 when every number is traced, 1 otherwise.
"""
import argparse
import csv
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import hashlib
import json
from pathlib import Path
import re
import sys

NUMBER = re.compile(r"(?<![\w.\\])(\d+(?:\.\d+)?\s*\\?%|(?:(?<=[\s(=])-)?\d+\.\d+)(?!\w|\.\d)")
SKIP_SPANS = re.compile(
    r"\\(?:cite[a-zA-Z]*|ref|eqref|label|url|href|includegraphics|input|include|bibliography)"
    r"\*?(?:\[[^\]]*\])*\{[^}]*\}|\$\$.*?\$\$|\\\[.*?\\\]|\\begin\{(equation|align)\*?\}.*?\\end\{\1\*?\}|"
    r"^%.*?$|(?<!\\)%[^\n]*$|https?://\S+|\(\s*\d{4}[a-z]?\s*\)|\bv\d+(?:\.\d+)+\b|"
    r"\b(?:Section|Sec\.|Table|Figure|Fig\.|Eq\.|Appendix|Algorithm)\s+[A-Z]?\d+(?:\.\d+)*|"
    r"\b\d+(?:\.\d+)?\s*\\?%\s*(?:CI|confidence|credible|prediction)\b",
    re.S | re.M)


def manuscript_numbers(text):
    masked = SKIP_SPANS.sub(lambda m: " " * len(m.group(0)), text)
    found = []
    for match in NUMBER.finditer(masked):
        raw = match.group(1)
        line = text.count("\n", 0, match.start()) + 1
        found.append({"text": raw.replace(" ", ""), "line": line})
    return found


def _decimal(value):
    try:
        number = Decimal(str(value).strip().rstrip("%").replace(",", ""))
    except (InvalidOperation, ValueError):
        return None
    return number if number.is_finite() else None


def recorded_values(claims_path=None, tables=()):
    values = []
    if claims_path and Path(claims_path).is_file():
        for line in Path(claims_path).read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            for key, value in (row.get("values") or {}).items():
                number = _decimal(value)
                if number is not None:
                    values.append((number, f"claim {row.get('claim_id')}:{key}"))
            unc = row.get("uncertainty") or {}
            for key in ("low", "high", "half_width", "se", "sd"):
                number = _decimal(unc.get(key)) if key in unc else None
                if number is not None:
                    values.append((number, f"claim {row.get('claim_id')}:uncertainty.{key}"))
    for table in tables:
        with open(table, newline="", encoding="utf-8") as handle:
            for r, row in enumerate(csv.reader(handle)):
                for c, cell in enumerate(row):
                    number = _decimal(cell)
                    if number is not None:
                        values.append((number, f"{Path(table).name}[{r},{c}]"))
    return values


def _matches(printed, value):
    is_percent = printed.endswith("%")
    shown = Decimal(printed.rstrip("%").replace("\\", "").strip())
    places = Decimal(1).scaleb(shown.as_tuple().exponent)
    candidates = [value]
    if is_percent:
        candidates.append(value * 100)
    for candidate in candidates:
        if candidate.quantize(places, rounding=ROUND_HALF_UP) == shown:
            return True
        if abs(candidate - shown) <= places / 2:
            return True
    return False


def audit(manuscripts, claims=None, tables=(), allow=()):
    values = recorded_values(claims, tables)
    allowed = set(allow)
    rows, unmatched = [], []
    for path in manuscripts:
        text = Path(path).read_text(encoding="utf-8", errors="replace")
        for item in manuscript_numbers(text):
            if item["text"] in allowed:
                continue
            source = next((label for value, label in values if _matches(item["text"], value)), None)
            entry = dict(item, file=Path(path).name, source=source)
            rows.append(entry)
            if source is None:
                unmatched.append(entry)
    digest = None
    if len(manuscripts) == 1:
        digest = hashlib.sha256(Path(manuscripts[0]).read_bytes()).hexdigest()
    return {"manuscript_sha256": digest, "numbers_checked": len(rows), "unmatched": unmatched,
            "passed": not unmatched and bool(values)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("manuscript", nargs="+", help="Manuscript source(s); give one file to bind a digest")
    parser.add_argument("--claims", help="analysis/claims.jsonl")
    parser.add_argument("--table", action="append", default=[], help="CSV of reported values (repeatable)")
    parser.add_argument("--allow", action="append", default=[], help="Printed number exempted, e.g. 0.001")
    parser.add_argument("--output", help="Write the JSON report here as well")
    args = parser.parse_args(argv)
    try:
        report = audit(args.manuscript, args.claims, args.table, args.allow)
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 2
    text = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
