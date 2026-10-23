"""Owner metadata normalization/reconciliation, without private question text."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from test_academic_qa import h,qa
from test_owner_adjudication import fixture
import historical_metadata as m
import metadata_integration as integration
import pilot_readiness as readiness
import json
from types import SimpleNamespace


class HistoricalMetadataTests(unittest.TestCase):
    def baseline(self):
        records,reviews,package=fixture()
        reviews,_=qa.merge_owner_decisions(records,reviews,package,'request')
        policy={'scope':[r['id'] for r in records],'examType':'FE','paper':'AM','subject':'A',
            'instructionsSha256':'request','sourceSha256':'source','publicationApprovalGranted':False}
        return records,reviews,policy
    def test_333_metadata_updates_preserve_all_nonmetadata_evidence_and_source_fields(self):
        records,reviews,policy=self.baseline();before=copy.deepcopy((records,reviews))
        updated,changes=m.merge_metadata(records,reviews,policy)
        self.assertEqual(len(changes),333);self.assertEqual((records,reviews),before)
        for r in records:
            old=reviews[r['id']];new=updated[r['id']]
            self.assertEqual({k:v for k,v in old.items() if k!='metadata'},{k:v for k,v in new.items() if k!='metadata'})
            self.assertEqual((new['metadata']['examType'],new['metadata']['paper'],new['metadata']['subject']),('FE','AM','A'))
            self.assertEqual(new['metadata']['evidence'][0]['kind'],'owner-confirmation')
            self.assertEqual(new['metadata']['history'][0],old['metadata'])
        self.assertEqual(sum(h.valid_verification(r,updated[r['id']]) for r in records),326)
        self.assertEqual(sum(h.valid_adjudication(r,updated[r['id']]) for r in records),7)
        self.assertFalse(any(h.valid_approval(r,updated[r['id']]) for r in records))
    def test_deterministic_and_idempotent_metadata_merge_without_duplicate_history(self):
        records,reviews,policy=self.baseline()
        first,_=m.merge_metadata(records,reviews,policy)
        self.assertEqual(first,m.merge_metadata(records,reviews,policy)[0])
        again,changes=m.merge_metadata(records,first,policy)
        self.assertEqual(again,first);self.assertEqual(changes,[])
    def test_exact_scope_stale_content_and_source_rejected(self):
        records,reviews,policy=self.baseline()
        for key,value in [('scope',policy['scope'][:-1]),('publicationApprovalGranted',True),('paper','B')]:
            with self.subTest(key=key),self.assertRaises(ValueError):m.merge_metadata(records,reviews,{**policy,key:value})
        reviews[records[0]['id']]['contentSha256']='stale'
        self.assertRaisesRegex(ValueError,'Stale',m.merge_metadata,records,reviews,policy)
    def test_spring_autumn_independent_from_morning_subject(self):
        records,reviews,policy=self.baseline();records[0]['season']='S';records[1]['season']='A'
        updated,_=m.merge_metadata(records,reviews,policy)
        for r in records[:2]:self.assertEqual(updated[r['id']]['metadata']['paper'],'AM');self.assertEqual(updated[r['id']]['metadata']['subject'],'A')
        self.assertEqual([r['season'] for r in records[:2]],['S','A'])
    def test_explicit_evening_subject_b_retained_on_repeated_normalization(self):
        meta=m.normalize_metadata(subject='B')
        self.assertEqual((meta['paper'],meta['subject']),('B','B'))
        self.assertEqual(m.normalize_metadata(meta),meta)
        self.assertEqual(m.normalize_metadata(meta,subject='B'),meta)
        self.assertEqual(meta['evidence'][0]['basis'],'explicit-owner-declaration')
        self.assertRaisesRegex(ValueError,'conflict',m.normalize_metadata,meta,subject='A')
    def test_source_specific_values_not_overwritten_by_defaults_or_scope_confirmation(self):
        specific={'examType':'FE','status':'verified','paper':'B','subject':'B','evidence':[{'kind':'source-specific-evidence','reference':'explicit source instruction'}]}
        self.assertEqual(m.normalize_metadata(specific),specific)
        records,reviews,policy=self.baseline();reviews[records[0]['id']]['metadata']=specific
        self.assertRaisesRegex(ValueError,'conflict',m.merge_metadata,records,reviews,policy)
    def test_default_and_source_specific_provenance_are_distinct(self):
        default=m.normalize_metadata();self.assertEqual(default['evidence'][0]['basis'],'owner-default')
        explicit=m.normalize_metadata(subject='B',evidence={'kind':'source-specific-evidence','reference':'original examination cover'})
        self.assertEqual(explicit['evidence'][0]['kind'],'source-specific-evidence')
        self.assertEqual(m.normalize_metadata(default),default)
    def test_inconsistent_source_specific_pairs_and_non_fe_are_flagged(self):
        for args in [{'subject':'B','paper':'Morning'},{'subject':'A','paper':'Evening'}]:
            with self.assertRaises(ValueError):m.normalize_metadata(**args)
        self.assertRaises(ValueError,m.normalize_metadata,{'examType':'AP'})
        self.assertRaises(ValueError,m.normalize_metadata,{'paper':'AM','subject':'B'})
    def test_future_import_review_defaults_do_not_change_literal_source_records(self):
        records,_,_=self.baseline();before=copy.deepcopy(records)
        self.assertEqual(len(m.initial_reviews(records)),333)
        self.assertTrue(all(v['metadata']['subject']=='A' for v in m.initial_reviews(records).values()))
        self.assertTrue(all(v['metadata']['subject']=='B' for v in m.initial_reviews(records,subject='B').values()))
        self.assertEqual(records,before)
        explicit=copy.deepcopy(records[:1]);explicit[0].update(examType='FE',paper='B',subject='B')
        meta=m.initial_reviews(explicit)[explicit[0]['id']]['metadata']
        self.assertEqual((meta['paper'],meta['subject']),('B','B'))
        self.assertEqual(meta['evidence'][0]['kind'],'source-specific-evidence')
        self.assertRaises(ValueError,m.initial_reviews,explicit,subject='A')
    def test_scoped_confirmation_cannot_override_explicit_original_source_b(self):
        records,reviews,policy=self.baseline();records[0]['subject']='B'
        self.assertRaisesRegex(ValueError,'original source metadata conflicts',m.merge_metadata,records,reviews,policy)
    def test_missing_approval_cannot_be_carried_across_metadata_reconciliation(self):
        records,reviews,policy=self.baseline();reviews[records[0]['id']]['approval']['status']='approved'
        self.assertRaisesRegex(ValueError,'publication authority',m.merge_metadata,records,reviews,policy)
    def test_stale_snapshot_or_changed_applied_inputs_rejected(self):
        with tempfile.TemporaryDirectory() as directory,patch.object(h,'WORK',Path(directory)/'live'):
            folder=Path(directory)/'metadata'
            for root in [h.WORK,folder/'before']:
                for name in ['questions','reviews','manifest']:h.write_json(root/f'{name}.json',{})
            policy={'baselineSnapshot':qa.snapshot_hashes(folder/'before')};binding={'engineSha256':'engine'}
            self.assertIsNone(integration.validate_snapshot(folder,policy,binding))
            h.write_json(h.WORK/'reviews.json',{'changed':True})
            self.assertRaisesRegex(ValueError,'Stale',integration.validate_snapshot,folder,policy,binding)
            state={'snapshot':qa.snapshot_hashes(h.WORK),'inputs':binding};h.write_json(folder/'applied-state.json',state)
            self.assertEqual(integration.validate_snapshot(folder,policy,binding),state)
            self.assertRaisesRegex(ValueError,'Stale',integration.validate_snapshot,folder,policy,{'engineSha256':'changed'})
    def test_seven_qualifications_including_page119_remain_unpublishable(self):
        records,reviews,policy=self.baseline();updated,_=m.merge_metadata(records,reviews,policy)
        for page,(qid,_) in qa.OWNER_SCOPE.items():
            r=next(r for r in records if r['id']==qid);v=updated[qid]
            self.assertEqual(v['ownerAdjudication'],reviews[qid]['ownerAdjudication'])
            self.assertTrue(any('grading remains blocked' in e for e in h.approval_errors(r,v)))
            self.assertFalse(h.valid_approval(r,v))
            if page==119:self.assertEqual(v['ownerAdjudication']['gradingEligibility']['acceptedOptions'],['a','d'])
    def test_publication_dry_run_preserves_real_files_and_rejects_writes_or_approval(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            with patch.object(h,'ROOT',root),patch.object(h,'WORK',root/'catalog'),patch.object(integration,'FOLDER',root/'metadata'),patch.object(readiness.p,'WORK',root/'preview'):
                path=h.WORK/'reviews.json';h.write_json(path,{'approval':{'status':'unapproved'}})
                output={'dryRun':True,'approvedInputs':0,'additions':[],'updates':[],'conflicts':[]}
                before=readiness.protected_snapshot()
                with patch.object(readiness.subprocess,'run',return_value=SimpleNamespace(stdout=json.dumps(output))) as runner:
                    self.assertEqual(readiness.publication_dry_run(),output)
                    self.assertIn('--dry-run',runner.call_args.args[0])
                self.assertEqual(readiness.protected_snapshot(),before)
                with patch.object(readiness.subprocess,'run',return_value=SimpleNamespace(stdout=json.dumps({**output,'approvedInputs':1}))):
                    self.assertRaisesRegex(ValueError,'zero approvals',readiness.publication_dry_run)
                def mutate(*args,**kwargs):
                    h.write_json(path,{'approval':{'status':'approved'}})
                    return SimpleNamespace(stdout=json.dumps(output))
                with patch.object(readiness.subprocess,'run',side_effect=mutate):
                    self.assertRaisesRegex(ValueError,'changed protected',readiness.publication_dry_run)


if __name__=='__main__':unittest.main()
