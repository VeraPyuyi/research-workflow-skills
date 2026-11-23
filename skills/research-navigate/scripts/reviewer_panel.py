"""Check blind-reviewer identities, the registered final panel and reservations.

Independence is judged by registry ``lineage`` (provider/base-model line), not by
product name or version: two GPT products or two Grok versions count once. An
endpoint with an undocumented lineage cannot certify a blind review.

Rounds:
  1  (M4) one fresh reviewer whose lineage differs from every producer.
  2  (M5) a panel registered before any round-2 dispatch: ``panel.lineages``
     lists distinct lineages, none of them a producer. Every revision attempt is
     reviewed by the same registered lineages with new agents, so a failing score
     cannot be escaped by trying further lineages one at a time.

Without a registered panel the legacy rule applies: every review of the paper
uses a distinct lineage. Delivery requires a registered panel.

Single-lineage fallback: when the registry policy sets ``single_lineage_fallback``
and every documented generative model shares one lineage (for example a host
that offers only one vendor's models), product families stand in for lineages.
Such reviews are context-independent only; ``independence_unit()`` reports this
so that results never claim model independence.

The ledger is coordinator-supplied. This script checks consistency, not that
the recorded calls actually happened; scores are checked by check_score.py.
"""
import argparse
import json
from pathlib import Path

from model_identity import model_family, model_lineage

REGISTRY = Path(__file__).resolve().parents[1] / 'references/model-routing.json'
MIN_PANEL = 2


def _registry():
    return {row['id']: row for row in json.loads(REGISTRY.read_text(encoding='utf-8'))['models']}


def independence_unit(registered=None):
    """'lineage', or 'family' under a declared single-lineage fallback."""
    data = json.loads(REGISTRY.read_text(encoding='utf-8'))
    registered = registered if registered is not None else {row['id']: row for row in data['models']}
    lineages = {model_lineage(row) for row in registered.values()} - {None}
    if data.get('policy', {}).get('single_lineage_fallback') is True and len(lineages) == 1:
        return 'family'
    return 'lineage'


def _lineage(model, registered):
    if not isinstance(model, str) or model not in registered:
        return None
    row = registered[model]
    lineage = model_lineage(row)
    if lineage is not None and independence_unit(registered) == 'family':
        return model_family(model, row.get('model_family'))
    return lineage


def reviewer_errors(plan, candidate=None):
    records = plan.get('reviewer_history')
    pending = plan.get('reserved_review_models')
    if not isinstance(records, list) or not isinstance(pending, list):
        return ['Supply the complete reviewer_history and reserved_review_models lists']
    registered = _registry()

    producers = plan.get('producer_models')
    if producers is None:
        producers = [plan['author_model']] if isinstance(plan.get('author_model'), str) else []
    if not isinstance(producers, list) or not all(isinstance(m, str) for m in producers):
        return ['producer_models must be a list of registered model ids']
    producer_lineages = {_lineage(m, registered) for m in producers} - {None}

    panel = plan.get('panel')
    panel_lineages = None
    if panel is not None:
        lineages = panel.get('lineages') if isinstance(panel, dict) else None
        if (not isinstance(lineages, list) or len(lineages) < MIN_PANEL
                or not all(isinstance(x, str) and x for x in lineages)
                or len(set(lineages)) != len(lineages)):
            return [f'Register a final panel of at least {MIN_PANEL} distinct lineages']
        if set(lineages) & producer_lineages:
            return ['A registered panel lineage matches a producer lineage']
        if not isinstance(panel.get('registered_at'), str) or not panel['registered_at'].strip():
            return ['Record when the final panel was registered']
        panel_lineages = set(lineages)

    agents, rounds = set(), set()
    legacy_used = set()
    round2_by_revision = {}
    for row in records:
        if not isinstance(row, dict) or not all(isinstance(row.get(k), str) and row[k].strip()
                for k in ('agent_id', 'served_model_evidence', 'manuscript_revision')):
            return ['Incomplete reviewer receipt']
        if type(row.get('review_round')) is not int or row['review_round'] not in (1, 2):
            return ['Reviewer receipt has an invalid round']
        if row['agent_id'] in agents:
            return ['Duplicate reviewer agent id; every review needs a new agent']
        lineage = _lineage(row.get('actual_model'), registered)
        if lineage is None:
            return ['Unverified blind reviewer identity or undocumented lineage in completed history']
        if lineage in producer_lineages:
            return ['A completed blind review shares a producer lineage']
        if row['review_round'] == 2 and panel_lineages is not None:
            if lineage not in panel_lineages:
                return ['A round-2 review lies outside the registered panel']
            seen = round2_by_revision.setdefault(row['manuscript_revision'], set())
            if lineage in seen:
                return ['A panel lineage reviewed the same revision twice']
            seen.add(lineage)
        else:
            if lineage in legacy_used:
                return ['Duplicate reviewer lineage in completed history']
            legacy_used.add(lineage)
        agents.add(row['agent_id'])
        rounds.add(row['review_round'])

    reserved = []
    for model in pending:
        lineage = _lineage(model, registered)
        if lineage is None or lineage in reserved:
            return ['Conflicting or unknown reserved reviewer lineage']
        reserved.append(lineage)

    if candidate is not None:
        lineage = _lineage(candidate, registered)
        if lineage is None:
            return ['Select a registered reviewer with a documented lineage']
        if lineage in producer_lineages:
            return ['The reviewer shares a lineage with a producer']
        if lineage in reserved:
            return ['That lineage is already reserved for an in-flight review']
        prior_ids = plan.get('prior_review_agent_ids', [])
        if (not isinstance(prior_ids, list) or any(not isinstance(item, str) for item in prior_ids)
                or not set(prior_ids).issubset(agents)):
            return ['Missing actual identity for a previous reviewer']
        if plan.get('review_round') == 2:
            if 1 not in rounds:
                return ['M5 requires the actual M4 reviewer receipt']
            if panel_lineages is not None:
                if lineage not in panel_lineages:
                    return ['Round-2 reviewers must come from the registered panel']
                revision = plan.get('manuscript_revision')
                if lineage in round2_by_revision.get(revision, set()):
                    return ['That panel lineage already reviewed this revision']
                return []
        if lineage in legacy_used:
            return ['Select an unused reviewer lineage']
        return []

    if pending:
        return ['Delivery needs reconciled reservations']
    if rounds != {1, 2}:
        return ['Delivery needs completed M4 and M5 receipts']
    if panel_lineages is None:
        return ['Delivery needs a registered final panel']
    final = plan.get('final_revision')
    if not isinstance(final, str) or final not in round2_by_revision:
        return ['Name the final_revision reviewed in round 2']
    if round2_by_revision[final] != panel_lineages:
        return ['Every registered panel lineage must review the final revision']
    return []


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('ledger', type=Path)
    args = parser.parse_args()
    try:
        errors = reviewer_errors(json.loads(args.ledger.read_text(encoding='utf-8-sig')))
    except (ValueError, TypeError, AttributeError, OSError, KeyError) as exc:
        errors = [str(exc)]
    print(json.dumps({'reviewer_identities_valid': not errors, 'errors': errors}))
    raise SystemExit(bool(errors))
