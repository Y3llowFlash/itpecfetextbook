"""Synthetic exact-payload, native editorial transfer and existing approval regressions."""
import copy
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
from test_academic_qa import h,qa,record,review,decision
from test_private_student_preview import fixture
import approval_editorial as editorial
import approval_candidates as candidates


def repairs_fixture():
    records=[];reviews={};repairs=[]
    for qid,page in editorial.SCOPE.items():
        r=record(page);r['id']=qid;v=review(r,True);v['extraction']=decision(r)['extraction']
        before={key:copy.deepcopy(v['extraction'][key]) for key in ['imageDescription','optionText']}
        after=copy.deepcopy(before);after['imageDescription']='Complete neutral original-diagram connections'
        if page==28:after['optionText']['d']='B AND (A OR B)'
        repairs.append({'questionId':qid,'pdfPage':page,'contentSha256':r['contentSha256'],'reviewSha256':qa.object_hash(v),
            'imageSha256':r['images'][0]['sha256'],'before':before,'after':after,'status':'source-validated',
            'sourceDiagramEvidence':{'connections':['checked']},'validationMethod':'visual-comparison-with-original-pdf-and-pixel-matched-crop'})
        records.append(r);reviews[qid]=v
    other=record(100);records.append(other);reviews[other['id']]=review(other,True)
    return records,reviews,repairs


class ApprovalCandidateTests(unittest.TestCase):
    def test_missing_expanded_or_stale_publication_package_is_rejected(self):
        ids=[f'SYNTHETIC-{i}' for i in range(36)];context={'questionIds':ids,'conceptCounts':{'logic-gates':36}}
        with tempfile.TemporaryDirectory() as directory,patch.object(editorial,'folder',return_value=Path(directory)),patch.object(editorial,'inputs',return_value=context):
            self.assertRaisesRegex(ValueError,'Missing',candidates.check,True)
            base={'schema':'itpec-final-approval-candidates-v1','questionIds':ids,'conceptCounts':context['conceptCounts'],
                'candidates':[{}]*36,'privateOnly':True,'readOnly':True,'publicationApprovalGranted':False}
            for key,value in [('questionIds',ids+['EXTRA']),('conceptCounts',{}),('candidates',[{}]*35),('publicationApprovalGranted',True)]:
                h.write_json(Path(directory)/'manifest.json',{**base,key:value})
                with self.subTest(field=key),self.assertRaisesRegex(ValueError,'scope'):candidates.check(True)
            h.write_json(Path(directory)/'manifest.json',base)
            self.assertRaisesRegex(ValueError,'Stale candidate implementation',candidates.check,True)
    def test_native_transfer_changes_only_two_accessible_reviews_with_provenance(self):
        records,reviews,repairs=repairs_fixture();before=copy.deepcopy((records,reviews,repairs))
        updated=editorial.merge_native(records,reviews,repairs)
        self.assertEqual((records,reviews,repairs),before)
        for qid,old in reviews.items():
            new=updated[qid]
            if qid not in editorial.SCOPE:self.assertEqual(new,old);continue
            self.assertEqual({k:v for k,v in old.items() if k!='extraction'},{k:v for k,v in new.items() if k!='extraction'})
            repair=next(r for r in repairs if r['questionId']==qid)
            for key in ['imageDescription','optionText']:self.assertEqual(new['extraction'][key],repair['after'][key])
            self.assertEqual(new['extraction']['editorialProvenance']['overlaySha256'],qa.object_hash(repair))
            self.assertEqual(new['approval']['status'],'unapproved')
        self.assertEqual(updated,editorial.merge_native(records,reviews,repairs))
    def test_missing_duplicate_stale_unvalidated_or_wrong_option_overlay_rejected(self):
        records,reviews,repairs=repairs_fixture()
        for changed in [repairs[:1],[repairs[0]]*2]:
            self.assertRaises(ValueError,editorial.merge_native,records,reviews,changed)
        for field in ['contentSha256','reviewSha256','imageSha256','pdfPage','status','before']:
            changed=copy.deepcopy(repairs);changed[0][field]='stale'
            with self.subTest(field=field),self.assertRaises(ValueError):editorial.merge_native(records,reviews,changed)
        changed=copy.deepcopy(repairs);changed[1]['after']['optionText']['a']='Changed other option'
        self.assertRaises(ValueError,editorial.merge_native,records,reviews,changed)
    def test_owner_cases_or_approval_cannot_enter_native_transfer(self):
        records,reviews,repairs=repairs_fixture()
        for value in ['owner','approved']:
            changed=copy.deepcopy(reviews)
            if value=='owner':changed[records[0]['id']]['ownerAdjudication']={'selectedAnswer':'b'}
            else:changed[records[0]['id']]['approval']['status']='approved'
            rebased=copy.deepcopy(repairs);rebased[0]['reviewSha256']=qa.object_hash(changed[records[0]['id']])
            self.assertRaisesRegex(ValueError,'owner cases or publication authority',editorial.merge_native,records,changed,rebased)
    def candidate_fixture(self):
        records,reviews,inventory,_=fixture();selected=inventory[:36]
        for r in records:
            reviews[r['id']]['mapping'].update(chapterId='fe-v1-ch01',evidence=['bound synthetic source passage'])
        concepts=[{'id':cid} for cid in candidates.pilot.COUNTS]
        for q in selected:q['reviewSha256']=qa.object_hash(reviews[q['id']])
        with patch.object(candidates.pilot,'association',side_effect=lambda q,c:{'questionId':q['id']}):
            bank,answers,_,associations=candidates.pilot.project(selected,records,reviews,concepts)
        return records,reviews,[r['id'] for r in records],associations,bank,answers
    def test_exact_36_native_candidates_equal_preview_and_remain_unapproved(self):
        args=self.candidate_fixture();before=copy.deepcopy(args)
        entries=candidates.build_entries(*args)
        self.assertEqual(len(entries),36);self.assertEqual(args,before)
        self.assertEqual(entries,candidates.build_entries(*args))
        for entry in entries:
            self.assertEqual(entry['review']['approval']['status'],'unapproved')
            self.assertTrue(entry['technicalEligibility']);self.assertFalse(entry['publicationApprovalGranted'])
            self.assertEqual(entry['publicationFingerprint'],h.publication_fingerprint(entry['record'],entry['review']))
    def test_extra_or_duplicate_candidates_and_changed_preview_content_rejected(self):
        args=list(self.candidate_fixture())
        for ids in [args[2][:-1],args[2]+[args[2][0]],[args[2][0]]*36]:
            changed=copy.deepcopy(args);changed[2]=ids
            self.assertRaises(ValueError,candidates.build_entries,*changed)
        for field in ['imageDescription','optionText','summary','steps','takeaway']:
            changed=copy.deepcopy(args);changed[5][0][field]='Altered'
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,'differs from validated'):candidates.build_entries(*changed)
    def test_unapproved_candidate_has_no_valid_publication_authority(self):
        args=self.candidate_fixture();entries=candidates.build_entries(*args)
        self.assertFalse(any(h.valid_approval(e['record'],e['review']) for e in entries))
        args[1][args[2][0]]['approval']['status']='approved'
        self.assertRaisesRegex(ValueError,'unapproved',candidates.build_entries,*args)
    def test_existing_approval_fingerprint_invalidates_all_student_content_changes(self):
        e=candidates.build_entries(*self.candidate_fixture())[0];r=e['record'];v=e['review']
        v['approval']={'status':'approved','reviewer':'synthetic test only','fingerprint':e['publicationFingerprint']}
        self.assertTrue(h.valid_approval(r,v))
        for dimension,field,value in [('explanation','summary','Changed'),('extraction','imageDescription','Changed'),
            ('extraction','optionText',{'a':'new'}),('mapping','conceptId','other'),('metadata','paper','B'),('verification','independentAnswer','d')]:
            changed=copy.deepcopy(v);changed[dimension][field]=value
            with self.subTest(field=field):self.assertFalse(h.valid_approval(r,changed))
        changed=copy.deepcopy(r);changed['rawText']='Different original question'
        self.assertFalse(h.valid_approval(changed,v))


if __name__=='__main__':unittest.main()
