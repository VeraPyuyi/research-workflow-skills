"""Native guard behavior, using real packets without live inference."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/research-navigate/scripts/check_dispatch.py'
spec = importlib.util.spec_from_file_location('native_dispatch', SCRIPT)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


def packet():
    return dict(id='branch-1', stage='research-implement', runtime_profile='codex-native',
                authorized_profiles=['codex-native'],
                authorized_models=['gpt-6.1-sol', 'gpt-6-astra', 'gpt-6-luna'],
                requested_model='gpt-6.1-sol', reasoning_effort='high', supported_efforts=['high'],
                actual_model='unknown', dispatch_tool='multi_agent_v1.spawn_agent',
                available_tools=['multi_agent_v1.spawn_agent', 'multi_agent_v1.wait_agent',
                                 'multi_agent_v1.send_input'],
                capability_record='host tools and effort inspected',
                resource_authorization='approved research envelope', budget_state='within',
                data_allowed=True, tools_allowed=True, contains_images=False,
                message='Implement the approved evaluator.', fork_context=False,
                write_paths=['/work/branch-1'], active=[], decision_active=[], confirmed_pools=['codex'])


def active(task_id='a', model='gpt-6-astra', **extra):
    r = dict(id=task_id, requested_model=model, runtime_profile='codex-native',
             status='running', write_paths=['/work/' + task_id]); r.update(extra); return r


DEFAULT_SUBMISSION_ROOT = None

def blind(number=1, submission_root=None):
    p = packet(); p.pop('message')
    p.update(stage='research-review', requested_model='gpt-6-astra', review_mode='venue_blind',
             review_round=number, new_agent=True, fork_context=False,
             submission_root=str(submission_root or DEFAULT_SUBMISSION_ROOT),
             author_models=['gpt-6.1-sol'], author_evidence='observed author model record',
             manuscript_revision='paper-v' + str(number), venue_profile='criteria-v1',
             prior_agent_ids=['author-agent'], prior_review_agent_ids=[],
             allowed_inputs=[dict(kind='manuscript', ref='review-bundle/paper.pdf', revision='paper-v' + str(number)),
                             dict(kind='venue_criteria', ref='review-bundle/criteria.txt', revision='criteria-v1')])
    if number == 2: p.update(prior_review_agent_ids=['reviewer-round-1'], previous_round_completed=True)
    return p


class NativeDispatchTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(dir=ROOT)
        self.addCleanup(temp.cleanup)
        self.bundle = Path(temp.name) / 'submission'
        files = self.bundle / 'review-bundle'
        files.mkdir(parents=True)
        (files / 'paper.pdf').write_bytes(b'synthetic frozen submission')
        (files / 'criteria.txt').write_text('Synthetic verified criteria', encoding='utf-8')
        patch = mock.patch(__name__ + '.DEFAULT_SUBMISSION_ROOT', self.bundle.resolve().as_posix())
        patch.start(); self.addCleanup(patch.stop)
    def dispatched(self, p, agent_id='worker'):
        admission = self.ready(p)
        return guard.record_dispatch(admission, {'agent_id':agent_id},
                                     spawn_evidence='synthetic actual spawn-response record')
    def receipt(self, dispatch, **extra):
        r=dict(task_id=dispatch['task_id'], request_digest=dispatch['request_digest'],
               agent_id=dispatch['spawn_returned_agent_id'], status='completed',
               actual_model='gpt-6.1-sol', model_evidence='observed model', artifact_refs=['result-v1'])
        r.update(extra); return r
    def ready(self, p):
        r = guard.check(p); self.assertEqual(r['status'], 'ready-for-dispatch', r); return r
    def blocked(self, p, phrase=None):
        r = guard.check(p); self.assertEqual(r['status'], 'blocked', r)
        if phrase: self.assertIn(phrase, ' '.join(r['errors']).lower())
        return r
    def test_native_request_exact_signature_and_no_inferred_execution(self):
        p = packet(); before = copy.deepcopy(p); r = self.ready(p)
        self.assertEqual(r['spawn_request'], dict(tool='multi_agent_v1.spawn_agent', arguments=dict(
            model='gpt-6.1-sol', reasoning_effort='high', message=p['message'], fork_context=False)))
        self.assertEqual(r['requested_model'], 'gpt-6.1-sol'); self.assertEqual(r['actual_model'], 'unknown')
        self.assertFalse(r['executed']); self.assertFalse(r['reserved']); self.assertEqual(p, before)
    def test_all_three_models_dispatch_exactly(self):
        for model in ('gpt-6.1-sol', 'gpt-6-astra', 'gpt-6-luna'):
            p = packet(); p['requested_model'] = model
            self.assertEqual(self.ready(p)['spawn_request']['arguments']['model'], model)
    def test_profile_model_authorization_fail_closed(self):
        for key, value in [('runtime_profile', 'external'), ('runtime_profile', None),
                           ('authorized_profiles', []), ('authorized_models', ['gpt-6-astra']),
                           ('requested_model', 'codex/gpt-6.1-sol'), ('requested_model', 'gpt-6-sol'),
                           ('requested_model', 'auto'), ('requested_model', ['gpt-6.1-sol'])]:
            with self.subTest(key=key, value=value):
                p = packet(); p[key] = value; self.blocked(p)
    def test_gateway_claim_cannot_replace_native_capability_and_authority(self):
        for key, value in [('dispatch_tool', 'gateway'), ('available_tools', []),
                           ('capability_record', ''), ('supported_efforts', []),
                           ('resource_authorization', ''), ('budget_state', 'unknown'),
                           ('budget_state', 'exhausted'), ('data_allowed', 1),
                           ('tools_allowed', 'true'), ('fork_context', None)]:
            p = packet(); p[key] = value; self.blocked(p)
    def test_external_routing_fields_cannot_be_smuggled(self):
        for field, value in [('provider_fallback', ['other']), ('provider', 'other'), ('free_only', True),
                             ('adapter', 'external.py'), ('call_type', 'structured_decision'), ('model', 'auto'),
                             ('service', 'jev'), ('api_key_env', 'TYPESAFE_API_KEY')]:
            p = packet(); p[field] = value; self.blocked(p)
    def test_preflight_does_not_accept_claimed_actual_model(self):
        p = packet(); p['actual_model'] = 'gpt-6.1-sol'; self.blocked(p)
    def test_images_require_native_modality_evidence(self):
        p = packet(); p['contains_images'] = True; self.blocked(p)
        p['native_vision_record'] = 'host image capability checked'; self.ready(p)
    def test_confirmed_shared_pool_admits_second_blocks_third(self):
        p = packet(); p['active'] = [active()]; self.ready(p)
        p['active'].append(active('b', 'gpt-6-luna')); self.blocked(p, 'pool capacity')
    def test_unknown_pool_is_serial_across_all_models(self):
        p = packet(); p['confirmed_pools'] = []; self.ready(p)
        p['active'] = [active(model='gpt-6-luna')]; self.blocked(p, 'pool capacity')
    def test_reservations_count_unknown_completion_blocks_expansion(self):
        p = packet(); p['active'] = [active(status='reserved')]; self.ready(p)
        for status in ('unknown', 'completed', 'timed_out', 'cancel_requested', 'failed'):
            p['active'] = [active(status=status)]; self.blocked(p, 'reconcile')
    def test_global_six_and_malformed_inventory(self):
        p = packet(); p['active'] = [active(str(i)) for i in range(6)]
        self.blocked(p, 'global worker capacity')
        for item in (None, {}, active(model='unregistered'), active(runtime_profile='external')):
            p['active'] = [item]; self.blocked(p)
    def test_duplicate_ids_and_missing_write_inventory(self):
        p = packet(); p['active'] = [active('branch-1')]; self.blocked(p)
        p['active'] = [active(), active()]; self.blocked(p)
        p['active'] = [active()]; p['active'][0].pop('write_paths'); self.blocked(p)
    def test_write_overlap_windows_posix_and_invalid_paths(self):
        for first, second in [('/work/shared', '/work/shared/paper.md'),
                              ('D:/work/shared', 'd:\\WORK\\shared\\paper.md')]:
            p = packet(); p['write_paths'] = [first]
            p['active'] = [active(write_paths=[second])]; self.blocked(p, 'overlap')
        p['write_paths'] = ['D:/work/different']; self.ready(p)
        for paths in (['relative'], ['/work/../shared'], 'all', [None]):
            p = packet(); p['write_paths'] = paths; self.blocked(p)
    def test_review_needs_author_provenance_and_fresh_context(self):
        for key, value in [('author_models', []), ('author_evidence', ''),
                           ('author_models', ['unknown']), ('fork_context', True), ('new_agent', False)]:
            p = blind(); p[key] = value; self.blocked(p)
    def test_same_model_bias_is_never_an_independent_gate(self):
        p = blind(); p['author_models'] = ['gpt-6-astra']; self.blocked(p, 'same-model')
        p.update(allow_same_model_review=True, same_model_bias_record='Shared model bias; provisional only')
        r = self.ready(p); self.assertFalse(r['model_independent']); self.assertFalse(r['independent_gate_eligible'])
    def test_blind_prompt_excludes_coordinator_history(self):
        for number in (1, 2):
            r = self.ready(blind(number)); prompt = r['spawn_request']['arguments']['message']
            self.assertIn('review-bundle/paper.pdf', prompt); self.assertNotIn('author-agent', prompt)
            self.assertNotIn('reviewer-round-1', prompt); self.assertFalse(r['spawn_request']['arguments']['fork_context'])
        p = blind(); p['message'] = 'Round one says reject'; self.blocked(p)
    def test_round_two_requires_prior_identity_and_completion(self):
        for key, value in [('prior_review_agent_ids', []), ('previous_round_completed', False)]:
            p = blind(2); p[key] = value; self.blocked(p)
    def test_blind_manifest_rejects_internal_material_and_bad_versions(self):
        for kind in ('prior_review', 'response_letter', 'internal_logs', 'optimizer', 'project_history'):
            p = blind(2); p['allowed_inputs'].append(dict(kind=kind, ref='private', revision='v1')); self.blocked(p)
        for key, value in [('review_round', True), ('review_round', 3), ('allowed_inputs', []),
                           ('venue_profile', ''), ('review_mode', 'almost-blind')]:
            p = blind(); p[key] = value; self.blocked(p)
        p = blind(); p['allowed_inputs'][0]['revision'] = 'old'; self.blocked(p)
        p = blind(); p['allowed_inputs'][0]['ref'] = '../history'; self.blocked(p)
    def test_unknown_completion_is_not_success_or_free_capacity(self):
        for receipt in ({}, {'status': 'timeout'}, {'status': 'completed'},
                        {'status': 'completed', 'agent_id': 'worker', 'actual_model': 'unknown'}):
            r = guard.check_completion(packet(), receipt)
            self.assertFalse(r['completed']); self.assertFalse(r['release_capacity']); self.assertFalse(r['independent_gate_eligible'])
    def test_completion_records_actual_separately_and_rejects_mismatch(self):
        receipt = dict(status='completed', agent_id='worker', actual_model='gpt-6.1-sol',
                       model_evidence='host identity', artifact_refs=['evaluator-v1'])
        p=packet(); dispatch=self.dispatched(p)
        receipt.update(task_id=dispatch['task_id'],request_digest=dispatch['request_digest'])
        r = guard.check_completion(p, receipt, dispatch); self.assertTrue(r['completed'], r)
        self.assertTrue(r['release_capacity']); self.assertEqual(r['actual_model'], 'gpt-6.1-sol')
        receipt['actual_model'] = 'gpt-6-astra'; r = guard.check_completion(p, receipt, dispatch)
        self.assertFalse(r['completed']); self.assertEqual(r['actual_model'], 'gpt-6-astra')
    def test_review_receipt_verifies_new_agent_context_and_manifest(self):
        p = blind(2)
        receipt = dict(status='completed', agent_id='new-reviewer', actual_model='gpt-6-astra',
                       model_evidence='host identity', artifact_refs=['review-2'], fork_context=False,
                       input_manifest=p['allowed_inputs'], isolation_record='dedicated bundle; instruction-only',
                       input_audit_record='actual inputs inspected; no prior reports')
        dispatch=self.dispatched(p,'new-reviewer')
        receipt.update(task_id=dispatch['task_id'],request_digest=dispatch['request_digest'])
        self.assertTrue(guard.check_completion(p, receipt, dispatch)['independent_gate_eligible'])
        for key, value in [('agent_id', 'reviewer-round-1'), ('agent_id', 'author-agent'),
                           ('fork_context', True), ('input_manifest', []), ('isolation_record', ''), ('input_audit_record', '')]:
            bad = copy.deepcopy(receipt); bad[key] = value
            self.assertFalse(guard.check_completion(p, bad, dispatch)['completed'])
    def test_malformed_fields_always_return_blocked_without_crashing(self):
        for key, value in [('stage', []), ('authorized_profiles', None), ('confirmed_pools', None),
                           ('active', {}), ('requested_model', {}), ('reasoning_effort', []),
                           ('write_paths', [dict(path='all')])]:
            with self.subTest(key=key):
                p = packet(); p[key] = value; self.blocked(p)
        for value in (1, {}, ['gpt-6.1-sol', []]):
            p = blind(); p['author_models'] = value; self.blocked(p)
        p = packet(); p['active'] = [active(model=[])]; self.blocked(p)
        p = blind(); p['allowed_inputs'][0]['kind'] = []; self.blocked(p)
    def test_extraction_model_cannot_replace_scientific_reviewer(self):
        p = blind(); p['requested_model'] = 'gpt-6-luna'; self.blocked(p)
    def test_cross_model_authorization_does_not_authorize_external_runtime(self):
        p = packet(); p['authorized_models'].append('unregistered-model'); self.blocked(p)
    def test_submission_root_and_each_ref_identify_existing_regular_files(self):
        for root in (None, 'relative', str(self.bundle / '..'), self.bundle.as_posix() + '/.',
                     self.bundle.as_posix() + '/review-bundle/paper.pdf'):
            p=blind(); p['submission_root']=root; self.blocked(p)
        for ref in ('.', 'review-bundle', 'review-bundle/CON.pdf', 'review-bundle/paper.pdf ',
                    'review-bundle/paper.pdf.', 'review-bundle/a\nfile.pdf',
                    'review-bundle/./paper.pdf', 'review-bundle//paper.pdf',
                    'review-bundle/../paper.pdf', 'review-bundle/NUL.txt', 'review-bundle/missing.pdf'):
            p=blind(); p['allowed_inputs'][0]['ref']=ref; self.blocked(p)
    def test_generated_review_prompt_uses_absolute_exact_allowlist(self):
        p=blind(); first=self.ready(p)
        other=self.bundle.parent/'other'; (other/'review-bundle').mkdir(parents=True)
        (other/'review-bundle/paper.pdf').write_bytes(b'a different paper')
        (other/'review-bundle/criteria.txt').write_bytes(b'other criteria')
        q=blind(submission_root=other.resolve().as_posix()); second=self.ready(q)
        self.assertIn((self.bundle/'review-bundle/paper.pdf').resolve().as_posix(), first['spawn_request']['arguments']['message'])
        self.assertIn((other/'review-bundle/paper.pdf').resolve().as_posix(), second['spawn_request']['arguments']['message'])
        self.assertNotEqual(first['request_digest'],second['request_digest'])
    def test_root_alias_and_symlink_escape_are_rejected(self):
        outside=self.bundle.parent/'outside.pdf'; outside.write_bytes(b'not submitted')
        link=self.bundle/'review-bundle/linked.pdf'
        try: link.symlink_to(outside)
        except OSError:
            self.skipTest('Symlink creation unavailable; junction and reparse-marker checks are separate')
        p=blind(); p['allowed_inputs'][0]['ref']='review-bundle/linked.pdf'; self.blocked(p)
        root_alias=self.bundle.parent/'root-alias'; root_alias.symlink_to(self.bundle,target_is_directory=True)
        p=blind(submission_root=root_alias.as_posix()); self.blocked(p)
    def test_reparse_directory_escape_is_rejected(self):
        if sys.platform!='win32': return
        outside=self.bundle.parent/'outside'; outside.mkdir()
        (outside/'paper.pdf').write_bytes(b'outside')
        junction=self.bundle/'linked'
        r=subprocess.run(['cmd','/c','mklink','/J',str(junction),str(outside)],capture_output=True,text=True)
        if r.returncode: self.skipTest('Junction creation unavailable')
        self.addCleanup(lambda: junction.rmdir() if junction.exists() else None)
        p=blind(); p['allowed_inputs'][0]['ref']='linked/paper.pdf'; self.blocked(p)
    def test_reparse_marker_is_rejected_before_file_resolution(self):
        original=Path.lstat
        target=self.bundle/'review-bundle/paper.pdf'
        def observe(path):
            value=original(path)
            if path==target:
                class Reparse:
                    st_mode=value.st_mode
                    st_file_attributes=1024
                return Reparse()
            return value
        with mock.patch.object(Path,'lstat',observe):
            self.blocked(blind())
    def test_receipt_cannot_replay_across_task_request_or_spawned_agent(self):
        p=packet(); dispatch=self.dispatched(p); receipt=self.receipt(dispatch)
        self.assertTrue(guard.check_completion(p,receipt,dispatch)['completed'])
        q=packet(); q.update(id='different-task',message='Different work',write_paths=['/work/other'])
        other=self.dispatched(q,'other-worker')
        for plan, record, value in ((q,other,receipt), (p,dispatch,dict(receipt,task_id='wrong')),
                                    (p,dispatch,dict(receipt,agent_id='other-worker')),
                                    (p,dispatch,dict(receipt,request_digest='0'*64)),
                                    (p,None,receipt)):
            r=guard.check_completion(plan,value,record)
            self.assertFalse(r['completed']); self.assertFalse(r['release_capacity'])
            self.assertFalse(r['independent_gate_eligible'])
        p['message']='Changed after admission'
        self.assertFalse(guard.check_completion(p,receipt,dispatch)['completed'])
    def test_spawn_binding_is_created_separately_and_inventory_is_not_readmitted(self):
        p=packet(); admission=self.ready(p)
        self.assertEqual(guard.record_dispatch(admission,{},spawn_evidence='missing')['status'],'blocked')
        dispatch=self.dispatched(p,'spawn-returned-worker'); receipt=self.receipt(dispatch)
        p['active']=[active('branch-1','gpt-6.1-sol')]
        self.assertTrue(guard.check_completion(p,receipt,dispatch)['completed'])
    def test_changed_submission_bytes_invalidate_the_admitted_request(self):
        p=blind(); dispatch=self.dispatched(p,'new-reviewer')
        receipt=self.receipt(dispatch,actual_model='gpt-6-astra',fork_context=False,
                             input_manifest=p['allowed_inputs'],isolation_record='bundle',input_audit_record='inspected')
        (self.bundle/'review-bundle/paper.pdf').write_bytes(b'changed frozen manuscript')
        r=guard.check_completion(p,receipt,dispatch)
        self.assertFalse(r['completed']); self.assertFalse(r['release_capacity'])
    def test_decision_inventory_cannot_be_omitted_after_service_is_available(self):
        p=packet(); p.pop('decision_active'); self.blocked(p)
    def test_cli_records_observed_spawn_and_binds_completion_without_overwrite(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            directory=Path(directory); plan=packet()
            packet_file=directory/'packet.json'; packet_file.write_text(json.dumps(plan),encoding='utf-8')
            spawn=directory/'observed.json'; spawn.write_text(json.dumps({'agent_id':'observed-worker'}),encoding='utf-8')
            binding=directory/'dispatch.json'
            args=[sys.executable,'-B',str(SCRIPT),str(packet_file),'--spawn-result',str(spawn),
                  '--spawn-evidence','synthetic-spawn-log','--dispatch-record',str(binding)]
            r=subprocess.run(args,capture_output=True,text=True); self.assertEqual(r.returncode,0,r.stdout+r.stderr)
            record=json.loads(binding.read_text()); self.assertEqual(record['spawn_returned_agent_id'],'observed-worker')
            before=binding.read_bytes(); r=subprocess.run(args,capture_output=True,text=True)
            self.assertEqual(r.returncode,1); self.assertEqual(binding.read_bytes(),before)
            receipt=self.receipt(record); receipt_file=directory/'completion.json'
            receipt_file.write_text(json.dumps(receipt),encoding='utf-8')
            args=[sys.executable,'-B',str(SCRIPT),str(packet_file),'--completion',str(receipt_file),'--dispatch-record',str(binding)]
            r=subprocess.run(args,capture_output=True,text=True); self.assertEqual(r.returncode,0,r.stdout+r.stderr)
            receipt['task_id']='different-task'; receipt_file.write_text(json.dumps(receipt),encoding='utf-8')
            r=subprocess.run(args,capture_output=True,text=True); self.assertEqual(r.returncode,1)
            self.assertFalse(json.loads(r.stdout)['release_capacity'])
    def test_cli_native_admission_and_invalid_packet(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            file = Path(directory) / 'packet.json'; file.write_text(json.dumps(packet()), encoding='utf-8')
            r = subprocess.run([sys.executable, '-B', str(SCRIPT), str(file)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr); self.assertFalse(json.loads(r.stdout)['executed'])
            file.write_text('[]', encoding='utf-8')
            r = subprocess.run([sys.executable, '-B', str(SCRIPT), str(file)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 1); self.assertEqual(json.loads(r.stdout)['status'], 'blocked')

if __name__ == '__main__': unittest.main()
