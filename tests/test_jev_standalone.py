"""Standalone Jev credential/whitelist and cross-service admission boundaries."""
import copy
import io
import json
import os
from pathlib import Path
import unittest
from unittest import mock
import test_jev_decide as fixtures
from test_dispatch_guard import packet as native_packet, active, guard

class StandaloneJevTests(unittest.TestCase):
    setUp = fixtures.JevTests.setUp
    execute = fixtures.JevTests.execute
    def test_default_env_uses_only_latest_without_reading_any_file(self):
        with mock.patch.dict(os.environ, {'TYPESAFE_API_KEY':'FAKE-DEFAULT-KEY'}), \
             mock.patch.object(Path, 'read_text', side_effect=AssertionError('unexpected config read')):
            key = fixtures.jev.load_credentials(None, 'jev-latest')
        self.assertEqual(key, 'FAKE-DEFAULT-KEY')
    def test_default_env_executes_with_fake_transport_and_no_personal_config(self):
        with mock.patch.dict(os.environ, {'TYPESAFE_API_KEY':'FAKE-DEFAULT-KEY'}), \
             mock.patch.object(Path, 'home', side_effect=AssertionError('personal configuration forbidden')):
            r = fixtures.jev.decide(fixtures.packet(), execute=True, receipt_path=self.receipt,
                transport=lambda *args: fixtures.response())
        self.assertEqual(r['execution_status'], 'completed', r)
        self.assertNotIn('FAKE-', json.dumps(r))
    def test_packet_cannot_expand_default_whitelist_even_in_dryrun(self):
        p = fixtures.packet(); p['request']['model'] = 'jev-preview'
        self.assertEqual(fixtures.jev.decide(p)['execution_status'], 'blocked')
        p['request']['model'] = 'jev-unapproved'; p['account_supported_models'].append('jev-unapproved')
        self.assertEqual(fixtures.jev.decide(p)['execution_status'], 'blocked')
    def test_config_is_explicit_env_reference_and_runtime_whitelist_only(self):
        self.config.write_text(json.dumps({'api_key_env':'JEV_TEST_KEY','models':['jev-preview']}))
        p = fixtures.packet(); p['request']['model']='jev-preview'
        self.assertEqual(self.execute(p)['execution_status'], 'completed')
    def test_config_rejects_inline_keys_endpoints_provider_shapes_and_bad_models(self):
        for cfg in ({'api_key_env':'JEV_TEST_KEY','models':['jev-latest'],'api_key':'FAKE-SECRET'},
                    {'api_key_env':'JEV_TEST_KEY','models':['jev-latest'],'endpoint':'https://evil.invalid'},
                    {'providers':[]}, {'api_key_env':'bad-name','models':['jev-latest']},
                    {'api_key_env':'JEV_TEST_KEY','models':['gpt-6-astra']},
                    {'api_key_env':'JEV_TEST_KEY','models':[]},
                    {'api_key_env':'JEV_TEST_KEY','models':['jev-latest','jev-latest']}):
            self.config.write_text(json.dumps(cfg))
            with self.subTest(config=cfg):
                r=self.execute(); self.assertEqual(r['execution_status'],'blocked')
                self.assertNotIn('FAKE-',json.dumps(r))
    def test_missing_key_or_unknown_credit_never_sends(self):
        with mock.patch.dict(os.environ, {'JEV_TEST_KEY':''}):
            sent=mock.Mock(side_effect=AssertionError('must not send'))
            r=self.execute(transport=sent)
            self.assertEqual(r['execution_status'],'blocked'); sent.assert_not_called()
        p=fixtures.packet(); p['authorization']['existing_credit_coverage']='unknown'
        with mock.patch.object(fixtures.jev,'load_credentials',side_effect=AssertionError('key read')):
            self.assertEqual(self.execute(p)['execution_status'],'blocked')
    def test_whitelist_applies_to_cache_reuse_after_config_change(self):
        self.execute(); self.config.write_text(json.dumps({'api_key_env':'JEV_TEST_KEY','models':['jev-preview']}))
        r=self.execute(verified_model_version='jev-1.13.0',transport=lambda *a:self.fail('cache must not call'))
        self.assertEqual(r['execution_status'],'blocked')
    def test_no_live_execution_without_shared_worker_snapshot(self):
        p=fixtures.packet(); p.pop('dispatch_snapshot')
        sent=mock.Mock(side_effect=AssertionError('must not send'))
        self.assertEqual(self.execute(p,transport=sent)['execution_status'],'blocked'); sent.assert_not_called()
    def test_service_capacity_checked_before_key_or_transport(self):
        p=fixtures.packet(); p['dispatch_snapshot']['decision_active']=[decision_task()]
        with mock.patch.object(fixtures.jev,'load_credentials',side_effect=AssertionError('key read')):
            r=self.execute(p)
        self.assertEqual(r['execution_status'],'blocked')
        self.assertFalse(self.receipt.exists())
    def test_unavailable_service_explicitly_returns_native_fallback_without_research_block(self):
        for mode in ('missing_key', 'unknown_credit', 'timeout'):
            self.receipt=self.base/(mode+'.json'); p=fixtures.packet()
            if mode=='unknown_credit': p['authorization']['existing_credit_coverage']='unknown'
            key='' if mode=='missing_key' else 'FAKE-KEY'
            transport=mock.Mock(side_effect=TimeoutError('FAKE-PRIVATE-ERROR'))
            with mock.patch.dict(os.environ, {'JEV_TEST_KEY':key}):
                r=self.execute(p,transport=transport)
            self.assertEqual(r['fallback'],'native-evidence-comparison')
            self.assertFalse(r['blocks_research'])
            self.assertNotIn('FAKE-',json.dumps(r))
            if mode=='timeout': self.assertEqual(r['commitment_state'],'pending')
    def test_default_runtime_never_honors_environment_endpoint(self):
        with mock.patch.dict(os.environ, {'TYPESAFE_API_KEY':'FAKE-KEY','TYPESAFE_BASE_URL':'https://evil.invalid'}):
            self.assertEqual(fixtures.jev.runtime_config(), {'api_key_env':'TYPESAFE_API_KEY','models':['jev-latest']})
    def test_cli_accepts_config_path_but_never_a_key_or_provider_argument(self):
        source=self.base/'packet.json'; source.write_text(json.dumps(fixtures.packet()))
        out=io.StringIO()
        with mock.patch('sys.stdout',out): code=fixtures.jev.main([str(source),'--config',str(self.config)])
        self.assertEqual(code,0); self.assertEqual(json.loads(out.getvalue())['execution_status'],'dry_run')
        for flag in ('--api-key','--providers','--endpoint'):
            out=io.StringIO(); err=io.StringIO()
            with mock.patch('sys.stdout',out),mock.patch('sys.stderr',err):
                code=fixtures.jev.main([str(source),flag,'FAKE-ARGUMENT-SECRET'])
            self.assertEqual(code,2); self.assertNotIn('FAKE-ARGUMENT-SECRET',out.getvalue()+err.getvalue())


def decision_task(task_id='jev-running', **extra):
    r=dict(id=task_id,service='jev',runtime_profile='codex-native',status='running',write_paths=[])
    r.update(extra); return r


def decision_plan():
    return fixtures.packet()['dispatch_snapshot']


class DecisionAdmissionTests(unittest.TestCase):
    def test_jev_is_not_a_native_worker_or_scientific_reviewer(self):
        for field in ('requested_model','model'):
            p=native_packet(); p[field]='jev-latest'
            self.assertEqual(guard.check(p)['status'],'blocked')
    def test_jev_inventory_uses_own_pool_not_codex_pool(self):
        p=native_packet(); p['decision_active']=[decision_task()]; p['active']=[active()]
        self.assertEqual(guard.check(p)['status'],'ready-for-dispatch')
    def test_unknown_or_malformed_service_inventory_blocks_expansion(self):
        for entries in (None, {}, [None], [decision_task(status='unknown')],
                        [decision_task(service='other')], [decision_task(api_key='FAKE')],
                        [decision_task(),decision_task('other')]):
            p=native_packet(); p['decision_active']=entries
            self.assertEqual(guard.check(p)['status'],'blocked')
    def test_service_identity_and_outputs_share_global_collision_checks(self):
        p=native_packet(); p['decision_active']=[decision_task('branch-1')]
        self.assertEqual(guard.check(p)['status'],'blocked')
        p['decision_active']=[decision_task(write_paths=['/work/branch-1/result'])]
        self.assertEqual(guard.check(p)['status'],'blocked')
    def test_service_proposal_admits_one_but_not_second_even_if_marked_confirmed(self):
        p=decision_plan(); self.assertEqual(guard.check_decision(p)['status'],'ready-for-decision')
        p['decision_active']=[decision_task()]
        p['confirmed_pools']=['jev']
        self.assertEqual(guard.check_decision(p)['status'],'blocked')
    def test_all_workers_and_service_tasks_count_toward_global_six(self):
        p=decision_plan(); p['active']=[active(str(i)) for i in range(6)]
        r=guard.check_decision(p); self.assertEqual(r['status'],'blocked')
        self.assertIn('Global worker capacity',' '.join(r['errors']))
        p=native_packet(); p['active']=[active(str(i)) for i in range(5)]
        p['decision_active']=[decision_task()]
        r=guard.check(p); self.assertIn('Global worker capacity',' '.join(r['errors']))
    def test_service_snapshot_keeps_unknown_codex_pool_serial(self):
        p=decision_plan(); p['active']=[active('one'),active('two','gpt-6-luna')]
        self.assertEqual(guard.check_decision(p)['status'],'blocked')
        p['confirmed_pools']=['codex']
        self.assertEqual(guard.check_decision(p)['status'],'ready-for-decision')
    def test_decision_snapshot_does_not_accept_endpoint_or_external_profile(self):
        for key,value in [('runtime_profile','other'),('endpoint','https://evil.invalid'),('api_key','FAKE')]:
            p=decision_plan(); p[key]=value
            self.assertEqual(guard.check_decision(p)['status'],'blocked')

if __name__=='__main__': unittest.main()
