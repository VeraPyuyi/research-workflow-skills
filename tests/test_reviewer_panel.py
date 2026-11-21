from pathlib import Path
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'skills/research-navigate/scripts'
sys.path.insert(0, str(SCRIPTS))
from reviewer_panel import REGISTRY, reviewer_errors
import json


class ReviewerIdentityTests(unittest.TestCase):
    def setUp(self):
        prefix = '' if json.loads(REGISTRY.read_text())['runtime_profile'] == 'codex-native' else 'codex/'
        self.a = prefix + 'gpt-6-astra'
        self.other_version = prefix + 'gpt-6.2-astra'
        self.b = prefix + 'gpt-6.2-sol'
        self.first = dict(review_round=1, agent_id='agent-1', manuscript_revision='v1',
                          actual_model=self.a, served_model_evidence='fixture-host-receipt-1')
        self.plan = dict(review_round=2, reviewer_history=[self.first], reserved_review_models=[])

    def test_rounds_and_panel(self):
        self.assertFalse(reviewer_errors(self.plan, self.b))
        self.assertTrue(reviewer_errors(self.plan, self.other_version))
        self.plan['reserved_review_models'] = [self.b]
        self.assertTrue(reviewer_errors(self.plan, self.b))

    def test_repair_attempt_keeps_old_and_requires_evidence(self):
        self.plan['reviewer_history'].append(dict(self.first, actual_model=self.b, agent_id='agent-2', review_round=2))
        self.assertFalse(reviewer_errors(self.plan))
        self.assertTrue(reviewer_errors(self.plan, self.b))
        self.plan['reviewer_history'][1]['actual_model'] = self.other_version
        self.assertTrue(reviewer_errors(self.plan))
        self.first['actual_model'] = 'unknown'
        self.assertTrue(reviewer_errors(self.plan))

    def test_incomplete_or_pending(self):
        self.assertTrue(reviewer_errors({}, self.a))
        self.assertTrue(reviewer_errors(self.plan))
        self.plan['reviewer_history'] = []
        self.assertTrue(reviewer_errors(self.plan, self.b))


if __name__ == '__main__':
    unittest.main()
