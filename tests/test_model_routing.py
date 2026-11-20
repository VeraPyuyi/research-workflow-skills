"""Consume the native registry through the guard; preserve scientific reuse checks."""
import importlib.util
import json
from pathlib import Path
import unittest
from unittest import mock
from test_dispatch_guard import packet, guard
ROOT = Path(__file__).resolve().parents[1]
ROUTING = ROOT / 'skills/research-navigate/references/model-routing.json'

class NativeRoutingTests(unittest.TestCase):
    def test_stage_allocations_are_dispatchable_and_cover_all_seventeen_skills(self):
        registry = json.loads(ROUTING.read_text())
        manifest = json.loads((ROOT / 'skills-manifest.json').read_text())
        self.assertEqual(set(registry['stages']), set(manifest['skills']))
        for stage, allocation in registry['stages'].items():
            p = packet(); p.update(stage=stage, requested_model=allocation['default_executor'],
                                  authorized_models=list(guard.MODELS), host_available_models=list(guard.MODELS))
            if stage == 'research-review':
                p.update(author_models=['gpt-6.1-sol'], author_evidence='actual author record',
                         new_agent=True, prior_agent_ids=[], prior_review_agent_ids=[])
            self.assertEqual(guard.check(p)['status'], 'ready-for-dispatch', stage)
            self.assertEqual(allocation['integrator'], 'gpt-6.2-sol')
    def test_task_roles_select_exact_requested_models(self):
        registry = json.loads(ROUTING.read_text())
        expectations = {'integration':'gpt-6.2-sol', 'engineering':'gpt-6.2-sol',
                        'experiment_control':'gpt-6.2-sol', 'writing':'gpt-6.2-sol',
                        'hard_math':'gpt-6.2-astra', 'causality':'gpt-6.2-astra',
                        'scientific_review':'gpt-6.2-astra', 'contribution_review':'gpt-6.2-astra',
                        'bounded_extraction':'gpt-6-luna'}
        for role, expected in expectations.items():
            p = packet(); p.update(requested_model=registry['task_roles'][role],
                                   authorized_models=list(guard.MODELS), host_available_models=list(guard.MODELS))
            self.assertEqual(guard.check(p)['spawn_request']['arguments']['model'], expected)
    def test_relabelled_external_registry_is_not_native_authority(self):
        registry = json.loads(ROUTING.read_text())
        registry['models'][0]['quota_pool'] = 'different'
        self.assertEqual(guard.check(packet(), registry)['status'], 'blocked')
    def test_reuse_audit_preserves_scientific_decisions(self):
        content = (ROOT/'skills/research-navigate/references/reuse-and-simplification.md').read_text().lower()
        for phrase in ('direct reuse', 'needs argument', 'analogy only', 'contribution affected',
                       'experiment removal', 'implementation replacement', 'preserve citations', 'proof status'):
            self.assertIn(phrase, content)
    def test_optimizer_rejects_model_identity_outside_native_registry(self):
        script = ROOT/'skills/research-optimize/scripts/optimize_workflow.py'
        spec = importlib.util.spec_from_file_location('native_optimizer', script)
        optimizer = importlib.util.module_from_spec(spec); spec.loader.exec_module(optimizer)
        for invalid in ('unknown', 'external/author', 'codex/gpt-6.1-sol', 'jev-latest'):
            with self.subTest(model=invalid), self.assertRaises(ValueError):
                optimizer.model_identity(invalid)
        # Family identity is version-independent; exact IDs remain dispatch identities.
        for model, family in (('gpt-6-astra', 'gpt-astra'), ('gpt-6.2-astra', 'gpt-astra'),
                              ('gpt-6.1-sol', 'gpt-sol'), ('gpt-6.2-sol', 'gpt-sol'),
                              ('gpt-6-luna', 'gpt-luna')):
            with self.subTest(model=model):
                self.assertEqual(optimizer.model_identity(model), family)
        registry = json.loads(ROUTING.read_text())
        registry['models'].append(dict(id='gpt-9-arbitrary', kind='generative',
                                       model_family='gpt-arbitrary', quota_pool='codex'))
        with mock.patch.object(optimizer, 'read', return_value=registry):
            with self.assertRaises(ValueError):
                optimizer.model_identity('gpt-9-arbitrary')
        for item in registry['models']:
            item['model_family'] = item['id']
        with mock.patch.object(optimizer, 'read', return_value=registry):
            self.assertEqual(optimizer.model_identity('gpt-6-astra'),
                             optimizer.model_identity('gpt-6.2-astra'))
            self.assertEqual(optimizer.model_identity('gpt-6.1-sol'),
                             optimizer.model_identity('gpt-6.2-sol'))

if __name__ == '__main__': unittest.main()
