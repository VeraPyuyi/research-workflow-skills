from decimal import Decimal, InvalidOperation
import argparse


def qualifying_score(raw):
    """Compare the reviewer's original decimal score without rounding."""
    try:
        score = Decimal(raw)
    except (InvalidOperation, TypeError, ValueError):
        return False
    return score.is_finite() and Decimal(8) <= score <= Decimal(10)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check the final panel scores only. The coordinator verifies review coverage and all other delivery conditions.')
    parser.add_argument('scores', nargs='+', help='One original 0-10 score per assigned final reviewer, or missing')
    scores = parser.parse_args().scores
    passed = all(qualifying_score(score) for score in scores)
    print('score requirement met' if passed else 'score requirement outstanding')
    raise SystemExit(0 if passed else 1)
