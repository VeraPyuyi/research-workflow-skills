from decimal import Decimal
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills/research-navigate/scripts'
sys.path.insert(0, str(SCRIPTS))
from reviewer_panel import REGISTRY, reviewer_errors  # noqa: E402

_spec = importlib.util.spec_from_file_location('check_score', ROOT / 'skills/research-review/scripts/check_score.py')
check_score = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_score)


def model(name):
    prefix = '' if json.loads(REGISTRY.read_text())['runtime_profile'] == 'codex-native' else 'codex/'
    return prefix + name


ASTRA, ASTRA_NEW, SOL = model('gpt-6-astra'), model('gpt-6.2-astra'), model('gpt-6.2-sol')
GROK_A, GROK_B = 'cursor/grok-4.5', 'cursor/grok-4.6'
MIMO, GLM, LONGCAT = 'opencode-zen/mimo-v2.6-flash-free', 'opencode-zen/glm-5.3-flash-free', \
    'opencode-zen/longcat-2.5-preview-free'
DEEPSEEK = 'opencode-zen/deepseek-v4.1-flash-free'


def receipt(agent, actual, rnd, revision='v1', **extra):
    return dict(review_round=rnd, agent_id=agent, manuscript_revision=revision, actual_model=actual,
                served_model_evidence='fixture-host-receipt', **extra)


class LineageTests(unittest.TestCase):
    def setUp(self):
        self.plan = dict(review_round=2, producer_models=[DEEPSEEK],
                         reviewer_history=[receipt('m4', MIMO, 1)], reserved_review_models=[])

    def test_versions_and_products_of_one_vendor_share_a_lineage(self):
        self.plan['reviewer_history'] = [receipt('m4', ASTRA, 1)]
        self.assertTrue(reviewer_errors(self.plan, ASTRA_NEW))
        self.assertTrue(reviewer_errors(self.plan, SOL))
        self.plan['reviewer_history'] = [receipt('m4', GROK_A, 1)]
        self.assertTrue(reviewer_errors(self.plan, GROK_B))
        self.assertFalse(reviewer_errors(self.plan, GLM))

    def test_producer_lineage_and_unknown_lineage_are_rejected(self):
        self.assertTrue(reviewer_errors(self.plan, 'workbuddy-ai/deepseek-v4.1-flash'))
        self.assertTrue(reviewer_errors(self.plan, 'opencode-zen/space-bunny-free'))
        self.assertTrue(reviewer_errors(self.plan, 'unknown'))

    def test_reservations_block_the_same_lineage(self):
        self.plan['reserved_review_models'] = [GLM]
        self.assertTrue(reviewer_errors(self.plan, 'opencode-zen/glm-5.3-flash-free'))
        self.assertFalse(reviewer_errors(self.plan, LONGCAT))

    def test_incomplete_or_pending(self):
        self.assertTrue(reviewer_errors({}, MIMO))
        self.assertTrue(reviewer_errors(self.plan))
        self.plan['reviewer_history'] = []
        self.assertTrue(reviewer_errors(self.plan, GLM))


class RegisteredPanelTests(unittest.TestCase):
    def setUp(self):
        self.plan = dict(review_round=2, producer_models=[DEEPSEEK], manuscript_revision='v2',
                         panel={'lineages': ['zhipu-glm', 'meituan-longcat', 'openai-gpt'],
                                'registered_at': '2026-11-23T10:00Z'},
                         reviewer_history=[receipt('m4', MIMO, 1)], reserved_review_models=[])

    def test_only_registered_lineages_review_round_two(self):
        self.assertFalse(reviewer_errors(self.plan, GLM))
        self.assertTrue(reviewer_errors(self.plan, 'opencode-zen/nemotron-3-ultra-free'))

    def test_revision_reuses_the_same_panel_with_new_agents(self):
        self.plan['reviewer_history'] += [receipt('a', GLM, 2, 'v2'), receipt('b', LONGCAT, 2, 'v2'),
                                          receipt('c', SOL, 2, 'v2')]
        self.plan['manuscript_revision'] = 'v3'
        self.assertFalse(reviewer_errors(self.plan, GLM))
        self.plan['manuscript_revision'] = 'v2'
        self.assertTrue(reviewer_errors(self.plan, GLM))
        self.plan['reviewer_history'].append(receipt('a', GLM, 2, 'v3'))
        self.assertTrue(reviewer_errors(self.plan))

    def test_delivery_needs_full_panel_on_final_revision(self):
        self.plan['reviewer_history'] += [receipt('a', GLM, 2, 'v2'), receipt('b', LONGCAT, 2, 'v2')]
        self.plan['final_revision'] = 'v2'
        self.assertTrue(reviewer_errors(self.plan))
        self.plan['reviewer_history'].append(receipt('c', ASTRA_NEW, 2, 'v2'))
        self.assertFalse(reviewer_errors(self.plan))
        del self.plan['panel']
        self.assertTrue(reviewer_errors(self.plan))

    def test_panel_must_be_distinct_and_exclude_producers(self):
        self.plan['panel']['lineages'] = ['zhipu-glm', 'zhipu-glm']
        self.assertTrue(reviewer_errors(self.plan, GLM))
        self.plan['panel']['lineages'] = ['zhipu-glm', 'deepseek']
        self.assertTrue(reviewer_errors(self.plan, GLM))
        self.plan['panel']['lineages'] = ['zhipu-glm']
        self.assertTrue(reviewer_errors(self.plan, GLM))


class ScoreFromReportsTests(unittest.TestCase):
    DIGEST = 'a' * 64

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.ledger = dict(final_revision='v2', final_manuscript_sha256=self.DIGEST, venue_profile='V1',
                           panel={'lineages': ['zhipu-glm', 'meituan-longcat'], 'registered_at': 't'},
                           reviewer_history=[])
        for agent, actual, score in (('a', GLM, '8.5'), ('b', LONGCAT, '9')):
            self.add(agent, actual, score)
        self.calibration = {'venue_profile': 'V1', 'lineages': {
            lineage: {'accepted_scores': [8, 7.5], 'rejected_scores': [5, 6]}
            for lineage in ('zhipu-glm', 'meituan-longcat')}}
        self.audit = {'manuscript_sha256': self.DIGEST, 'passed': True}

    def tearDown(self):
        self.tmp.cleanup()

    def add(self, agent, actual, score, digest=None, recorded=None):
        text = f'Findings...\nManuscript SHA-256: {digest or self.DIGEST}\nOverall score: {score}/10\n'
        path = self.root / f'{agent}.md'
        path.write_text(text, encoding='utf-8')
        self.ledger['reviewer_history'].append(receipt(
            agent, actual, 2, 'v2', report_path=f'{agent}.md', score=recorded or score,
            report_sha256=hashlib.sha256(path.read_bytes()).hexdigest()))

    def run_check(self, **overrides):
        kwargs = dict(calibration=self.calibration, claim_audit=self.audit, refs=self.audit)
        kwargs.update(overrides)
        return check_score.check(self.ledger, self.root, **kwargs)

    def test_met_only_with_reports_calibration_and_audits(self):
        self.assertEqual(self.run_check()['status'], 'met', self.run_check()['problems'])
        self.assertEqual(self.run_check(calibration=None)['status'], 'outstanding')
        self.assertEqual(self.run_check(claim_audit=None)['status'], 'outstanding')
        self.assertEqual(self.run_check(refs={'manuscript_sha256': 'b' * 64, 'passed': True})['status'],
                         'outstanding')

    def test_recorded_score_must_match_report_and_reach_threshold(self):
        self.ledger['reviewer_history'][0]['score'] = '9'
        self.assertEqual(self.run_check()['status'], 'outstanding')
        self.ledger['reviewer_history'] = []
        self.add('a', GLM, '7.999')
        self.add('b', LONGCAT, '9')
        result = self.run_check()
        self.assertEqual(result['status'], 'outstanding')
        self.assertEqual([r['report_score'] for r in result['reviews']], ['7.999', '9'])

    def test_tampered_report_or_wrong_manuscript_fails(self):
        (self.root / 'a.md').write_text('Overall score: 10/10\n', encoding='utf-8')
        self.assertEqual(self.run_check()['status'], 'outstanding')
        self.ledger['reviewer_history'] = []
        self.add('a', GLM, '9', digest='c' * 64)
        self.add('b', LONGCAT, '9')
        self.assertEqual(self.run_check()['status'], 'outstanding')

    def test_non_discriminating_reviewer_is_not_credited(self):
        self.calibration['lineages']['zhipu-glm'] = {'accepted_scores': [8, 8], 'rejected_scores': [7.5, 7.8]}
        self.assertEqual(self.run_check()['status'], 'outstanding')
        status, separation = check_score.calibration_status(self.calibration, 'zhipu-glm', 'V1')
        self.assertEqual(status, 'not-discriminating')
        self.assertLess(Decimal(separation), Decimal(1))

    def test_missing_panel_member_fails(self):
        self.ledger['panel']['lineages'].append('openai-gpt')
        self.assertIn('openai-gpt', ' '.join(self.run_check()['problems']))


if __name__ == '__main__':
    unittest.main()
