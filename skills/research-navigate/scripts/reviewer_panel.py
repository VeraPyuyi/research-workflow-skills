"""Check coordinator-supplied blind reviewer receipts and outstanding reservations."""
import argparse
import json
from pathlib import Path

from model_identity import model_family

REGISTRY = Path(__file__).resolve().parents[1] / 'references/model-routing.json'


def reviewer_errors(plan, candidate=None):
    records = plan.get('reviewer_history')
    pending = plan.get('reserved_review_models')
    if not isinstance(records, list) or not isinstance(pending, list):
        return ['Supply the complete reviewer_history and reserved_review_models lists']
    registered = {row['id']: row for row in json.loads(REGISTRY.read_text(encoding='utf-8'))['models']}
    families, agents, rounds = set(), set(), set()

    def claim(model):
        if not isinstance(model, str) or model not in registered:
            return False
        family = model_family(model, registered[model].get('model_family'))
        if family in families or registered[model].get('kind', 'generative') != 'generative':
            return False
        families.add(family)
        return True

    for row in records:
        if not isinstance(row, dict) or not all(isinstance(row.get(k), str) and row[k].strip()
                for k in ('agent_id', 'served_model_evidence', 'manuscript_revision')):
            return ['Incomplete reviewer receipt']
        if (type(row.get('review_round')) is not int or row['review_round'] not in (1, 2)
                or row['agent_id'] in agents or not claim(row.get('actual_model'))):
            return ['Duplicate or unverified blind reviewer identity in completed history']
        agents.add(row['agent_id'])
        rounds.add(row['review_round'])
    if any(not claim(model) for model in pending):
        return ['Conflicting or unknown reserved reviewer family']
    if candidate is not None:
        if plan.get('review_round') == 2 and 1 not in rounds:
            return ['M5 requires the actual M4 reviewer receipt']
        prior_ids = plan.get('prior_review_agent_ids', [])
        if (not isinstance(prior_ids, list) or any(not isinstance(item, str) for item in prior_ids)
                or not set(prior_ids).issubset(agents)):
            return ['Missing actual identity for a previous reviewer']
        if not claim(candidate):
            return ['Select an unused registered reviewer model family']
    elif pending or rounds != {1, 2}:
        return ['Delivery needs completed M4 and M5 receipts and reconciled reservations']
    return []


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ledger', type=Path)
    args = parser.parse_args()
    try:
        errors = reviewer_errors(json.loads(args.ledger.read_text(encoding='utf-8-sig')))
    except (ValueError, TypeError, AttributeError, OSError) as exc:
        errors = [str(exc)]
    print(json.dumps({'reviewer_identities_valid': not errors, 'errors': errors}))
    raise SystemExit(bool(errors))
