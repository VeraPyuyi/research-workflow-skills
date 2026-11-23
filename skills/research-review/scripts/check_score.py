"""Check the M5 score condition against the review files themselves.

Reads the coordinator's panel ledger (the same JSON that reviewer_panel.py
checks), then for every round-2 review of ``final_revision``:

* the raw report file exists and its SHA-256 matches ``report_sha256``;
* the report's last ``Overall score: X/10`` line equals the recorded score;
* the report's last ``Manuscript SHA-256: <hex>`` line equals the ledger's
  ``final_manuscript_sha256``.

The score condition is met only when, in addition:

* every registered panel lineage reviewed the final revision;
* each lineage has a calibration record for this venue profile whose accepted
  and rejected calibration papers are separated by at least ``--min-separation``;
* the claim audit and reference check (``--claim-audit``, ``--refs``) passed on
  the same manuscript digest;
* every raw score reaches the threshold (default 8, inclusive, unrounded).

Scores are a necessary signal, never sufficient: the coordinator still checks
unresolved critical/major findings and every other delivery condition, and the
user decides on submission. All scores are reported; none is averaged away.
"""
from decimal import Decimal, InvalidOperation
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'research-navigate/scripts'))
from reviewer_panel import _lineage, _registry  # noqa: E402

SCORE_LINE = re.compile(r'^\s*Overall score:\s*([0-9]+(?:\.[0-9]+)?)\s*/\s*10\s*$', re.M)
DIGEST_LINE = re.compile(r'^\s*Manuscript SHA-256:\s*([0-9a-f]{64})\s*$', re.M)


def qualifying_score(raw, threshold=Decimal(8)):
    """Compare the reviewer's original decimal score without rounding."""
    try:
        score = Decimal(str(raw)) if raw is not None else None
    except (InvalidOperation, TypeError, ValueError):
        return False
    return score is not None and score.is_finite() and threshold <= score <= Decimal(10)


def _inside(root, relative):
    if not isinstance(relative, str) or not relative or '\\' in relative:
        return None
    path = PurePosixPath(relative)
    if path.is_absolute() or '..' in path.parts:
        return None
    return Path(root, *path.parts)


def _mean(values):
    return sum(Decimal(str(v)) for v in values) / len(values)


def calibration_status(calibration, lineage, venue, min_separation=Decimal(1)):
    """A lineage must score known-accepted papers above known-rejected ones."""
    calibration = calibration or {}
    entry = (calibration.get('lineages') or {}).get(lineage)
    if calibration.get('venue_profile') != venue or not isinstance(entry, dict):
        return 'uncalibrated', None
    accepted, rejected = entry.get('accepted_scores'), entry.get('rejected_scores')
    if (not isinstance(accepted, list) or not isinstance(rejected, list)
            or len(accepted) < 2 or len(rejected) < 2):
        return 'uncalibrated', None
    try:
        separation = _mean(accepted) - _mean(rejected)
    except (InvalidOperation, TypeError, ValueError):
        return 'uncalibrated', None
    return ('calibrated' if separation >= min_separation else 'not-discriminating'), str(separation)


def check(ledger, root, threshold=Decimal(8), calibration=None, claim_audit=None, refs=None,
          min_separation=Decimal(1)):
    problems, rows = [], []
    final = ledger.get('final_revision')
    digest = ledger.get('final_manuscript_sha256')
    panel = (ledger.get('panel') or {}).get('lineages') or []
    venue = ledger.get('venue_profile')
    if (not isinstance(final, str) or not isinstance(digest, str)
            or not re.fullmatch(r'[0-9a-f]{64}', digest)):
        return {'status': 'outstanding', 'reviews': [],
                'problems': ['Ledger needs final_revision and final_manuscript_sha256']}
    registry = _registry()
    covered = set()
    for row in ledger.get('reviewer_history') or []:
        if (not isinstance(row, dict) or row.get('review_round') != 2
                or row.get('manuscript_revision') != final):
            continue
        agent = row.get('agent_id')
        lineage = _lineage(row.get('actual_model'), registry)
        entry = {'agent_id': agent, 'lineage': lineage, 'recorded_score': row.get('score'),
                 'report_score': None}
        path = _inside(root, row.get('report_path'))
        if path is None or not path.is_file():
            problems.append(f'{agent}: raw report missing')
        else:
            data = path.read_bytes()
            if hashlib.sha256(data).hexdigest() != row.get('report_sha256'):
                problems.append(f'{agent}: report bytes differ from report_sha256')
            text = data.decode('utf-8', 'replace')
            scores, digests = SCORE_LINE.findall(text), DIGEST_LINE.findall(text)
            entry['report_score'] = scores[-1] if scores else None
            if not scores or str(row.get('score')) != scores[-1]:
                problems.append(f'{agent}: recorded score does not match the report')
            if not digests or digests[-1] != digest:
                problems.append(f'{agent}: report does not name the final manuscript digest')
        status, separation = calibration_status(calibration, lineage, venue, min_separation)
        entry['calibration'], entry['calibration_separation'] = status, separation
        if status != 'calibrated':
            problems.append(f'{agent}: reviewer lineage {lineage} is {status} for {venue}')
        if not qualifying_score(entry['report_score'], threshold):
            problems.append(f'{agent}: score below {threshold} or unreadable')
        if lineage is not None:
            covered.add(lineage)
        rows.append(entry)
    missing = set(panel) - covered
    if not panel or missing:
        problems.append('Registered panel lineages without a final-revision review: '
                        + ', '.join(sorted(missing) or ['<no panel registered>']))
    for label, report in (('claim audit', claim_audit), ('reference check', refs)):
        if not isinstance(report, dict):
            problems.append(f'{label} report missing')
        elif report.get('manuscript_sha256') != digest or report.get('passed') is not True:
            problems.append(f'{label} did not pass on the final manuscript digest')
    return {'status': 'met' if not problems else 'outstanding', 'threshold': str(threshold),
            'final_revision': final, 'reviews': rows, 'problems': problems}


def _load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig')) if path else None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--ledger', required=True, help='Panel ledger JSON (default research/reviews/panel.json)')
    parser.add_argument('--root', default='.', help='Directory that report paths are relative to')
    parser.add_argument('--calibration', help='Reviewer calibration JSON for this venue profile')
    parser.add_argument('--claim-audit', help='claim_audit.py JSON output for the final manuscript')
    parser.add_argument('--refs', help='verify_refs.py JSON output for the final manuscript')
    parser.add_argument('--threshold', default='8')
    parser.add_argument('--min-separation', default='1')
    args = parser.parse_args(argv)
    try:
        result = check(_load(args.ledger), args.root, Decimal(args.threshold), _load(args.calibration),
                       _load(args.claim_audit), _load(args.refs), Decimal(args.min_separation))
    except (OSError, ValueError, InvalidOperation, AttributeError) as exc:
        result = {'status': 'outstanding', 'problems': [str(exc)], 'reviews': []}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result['status'] == 'met' else 1


if __name__ == '__main__':
    raise SystemExit(main())
