"""Exact final package, context binding and source-review safeguards; no approval writes."""
from copy import deepcopy
import contextlib
import io
import json
import subprocess
import unittest
from unittest.mock import patch
from test_approval_candidates_batch02 import package_fixture
import approval_candidates as c
import release_3 as release

def released():return (release.FOLDER/'state.json').exists()
def inputs():return release.archived_inputs() if released() else c.batch03_inputs()


def fixture(source_status='source-rechecked',highlight_status='source-validated-pending-owner-editorial-approval'):
    records,reviews,context,concepts,_,_,_,bank,answers,links=package_fixture()
    for v in reviews.values():v['classification']={'status':'source-reviewed','placement':'exact','chapter':1}
    rows=[{'id':i,'status':source_status,'rawTranscriptSha256':next(r['contentSha256'] for r in records if r['id']==i),
        'literalOptionWording':deepcopy(reviews[i]['extraction']['optionText']),'editorialClarifications':['Neutral synthetic layout description only.']} for i in context['questionIds']]
    report=[{'conceptId':'bits','status':highlight_status,'editorialReview':{'status':'source-rechecked','ownerApprovalGranted':False}}]
    def read(path,*args):
        if str(path).endswith('pilot-bank.json'):return deepcopy(bank)
        if str(path).endswith('explanations.json'):return deepcopy(answers)
        raise AssertionError(path)
    with patch.object(c.h,'read_json',side_effect=read),patch.object(c.h,'_PRACTICE_SNAPSHOT',[]):entries=c.batch03_entries(context,records,reviews,concepts,links,rows,report)
    manifest={'schema':'itpec-final-approval-candidates-v1','batch':3,'privateOnly':True,'readOnly':True,'publicationApprovalGranted':False,
        'questionIds':context['questionIds'],'conceptCounts':context['conceptCounts'],'candidates':entries,'conceptDefinitions':concepts,'highlightIntegration':report}
    manifest['candidateSetFingerprint']=c.batch03_fingerprint(context,entries,concepts,report)
    return records,reviews,context,concepts,report,entries,manifest,rows,bank,answers,links


class FinalBatch03Tests(unittest.TestCase):
    def setUp(self):self.records,self.reviews,self.context,self.concepts,self.report,self.entries,self.manifest,self.rows,self.bank,self.answers,self.links=fixture()
    def validate(self,manifest=None):return c.validate_final_package(manifest or self.manifest,self.entries,self.concepts,self.report,self.context,batch=3)

    def test_exact_40_scope_and_original_preview_unchanged(self):
        self.validate();self.assertEqual(len(self.entries),40)
        for e,q,a in zip(self.entries,self.bank,self.answers):
            self.assertEqual(e['studentVisible'],c.preview_visible(q,a));self.assertEqual(e['review'],self.reviews[e['id']])
            self.assertEqual(e['publicationFingerprint'],c.h.publication_fingerprint(e['record'],e['review']))
            self.assertEqual(e['review']['approval']['status'],'unapproved');self.assertFalse(e['publicationApprovalGranted'])

    def test_missing_duplicate_extra_or_reordered_ids_rejected(self):
        for value in [self.context['questionIds'][:-1],self.context['questionIds']+[self.context['questionIds'][0]],self.context['questionIds'][::-1]]:
            with self.subTest(value=value),self.assertRaises(ValueError):self.validate({**self.manifest,'questionIds':value})
        with self.assertRaises(ValueError):self.validate({**self.manifest,'candidates':self.entries[:-1]})

    def test_native_image_answer_accessible_text_metadata_and_mapping_changes_rejected(self):
        for dimension,key,value in [('verification','independentAnswer','d'),('extraction','imageDescription','Altered'),('extraction','optionText',{'a':'Altered'}),('metadata','subject','B'),('mapping','subsectionId','elsewhere'),('explanation','steps',['Altered'])]:
            m=deepcopy(self.manifest);m['candidates'][0]['review'][dimension][key]=value
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,'stale'):self.validate(m)
        m=deepcopy(self.manifest);m['candidates'][0]['record']['images'][0]['sha256']='other'
        self.assertRaisesRegex(ValueError,'stale',self.validate,m)

    def test_new_source_and_literal_wording_are_in_context_fingerprint(self):
        e=self.entries[0];original=e['approvalContextFingerprint']
        for field in ['finalSourceReview','sourceTranscription','finalHighlightReview','textbookSupport']:
            changed=deepcopy(e);changed[field]={'changed':True}
            with self.subTest(field=field):self.assertNotEqual(original,c.approval_context_fingerprint(changed,changed['conceptDefinition']))
        for key in ['title','summary','sourceHighlight']:
            changed=deepcopy(e['conceptDefinition']);changed[key]='Altered'
            self.assertNotEqual(original,c.approval_context_fingerprint(e,changed))

    def test_candidate_set_and_owner_flags_cannot_be_forged(self):
        for key,value in [('candidateSetFingerprint','stale'),('publicationApprovalGranted',True),('readOnly',False),('privateOnly',False),('batch',2)]:
            with self.subTest(key=key),self.assertRaises(ValueError):self.validate({**self.manifest,key:value})

    def test_failed_source_review_blocks_without_changing_academic_content(self):
        _,reviews,_,_,_,entries,_,*_=fixture(source_status='correction-required')
        self.assertTrue(all(not e['technicalEligibility'] and 'source-transcription-correction-required' in e['remainingBlockers'] for e in entries))
        self.assertTrue(all(e['review']==reviews[e['id']] and e['review']['approval']['status']=='unapproved' for e in entries))

    def test_failed_highlight_cannot_be_reclassified_as_approved(self):
        records,reviews,context,concepts,report,entries,manifest,*_=fixture(highlight_status='correction-required')
        self.assertTrue(all(not e['technicalEligibility'] for e in entries));self.assertTrue(all('source-highlight-correction-required' in e['remainingBlockers'] for e in entries))
        self.assertTrue(all(e['highlightIntegration']['ownerEditorialApprovalGranted'] is False for e in entries))
        page=c.render_gallery(manifest,concepts);self.assertIn('correction required; owner editorial approval absent',page)

    def test_prior_approvals_and_all_nonselected_objects_are_immutable(self):
        original=deepcopy(self.reviews);c.validate_live_reviews(self.records,self.reviews,original,self.context['questionIds'])
        other=next(i for i in original if i not in self.context['questionIds']);bad=deepcopy(self.reviews);bad[other]['approval']={'status':'changed'}
        self.assertRaisesRegex(ValueError,'Noncandidate',c.validate_live_reviews,self.records,bad,original,self.context['questionIds'])
        bad=deepcopy(self.reviews);bad[self.context['questionIds'][0]]['approval']={'status':'approved'}
        self.assertRaisesRegex(ValueError,'read-only',c.validate_live_reviews,self.records,bad,original,self.context['questionIds'])

    @unittest.skipUnless((c.batch03_folder()/'manifest.json').exists(),'private final package intentionally absent from Git')
    def test_actual_40_28_14_package_equality_preservation_and_source_bindings(self):
        m=release.validate_package() if released() else c.check_batch03();self.assertEqual(len(m['candidates']),40);self.assertEqual(len(m['conceptDefinitions']),28);self.assertEqual(len(m['highlightIntegration']),14)
        self.assertTrue(all(e['technicalEligibility'] for e in m['candidates']));self.assertTrue(all(e['review']['approval']['status']=='unapproved' for e in m['candidates']))
        context,records,reviews,frozen=inputs();self.assertEqual(reviews,frozen);self.assertEqual(len(context['releasedQuestionIds']),76)
        self.assertEqual(m['sourceSha256'],c.h.digest(c.h.SOURCE.read_bytes()));self.assertEqual(m['textbookSha256'],c.h.digest(c.qa.TEXTBOOK.read_bytes()))
        self.assertEqual(sum(c.h.valid_approval(r,reviews[r['id']]) for r in records),76)
        for r in m['highlightIntegration']:self.assertFalse(r['ownerEditorialApprovalGranted']);self.assertEqual(r['editorialReview']['status'],'source-rechecked')
        source=next(e for e in m['candidates'] if e['record']['regions'][0]['pdfPage']==155)
        self.assertNotIn('XOR',source['sourceTranscription']['literalOptionWording']['a']);self.assertIn('XOR',source['studentVisible']['optionText']['a'])

    @unittest.skipUnless((c.batch03_folder()/'manifest.json').exists(),'private final package intentionally absent from Git')
    def test_actual_review_missing_stale_or_unvalidated_rejected(self):
        context,records,reviews,_=inputs();concepts=release.context()[1]['conceptDefinitions'] if released() else c.batch03_concepts(context);links=c.batch03_associations(context,records,reviews,concepts)
        original_read=c.h.read_json;ledger=original_read(c.batch03_folder()/'source-review.json')
        structural=[{k:r[k] for k in ['conceptId','status']} for r in original_read(c.batch03_folder()/'manifest.json')['highlightIntegration']]
        changes=[None,dict(ledger,ownerApprovalGranted=True)]
        for field,value in [('sourceBinding',{}),('visibleSha256','stale'),('reviewSha256','stale')]:
            bad=deepcopy(ledger);bad['questions'][0][field]=value;changes.append(bad)
        bad=deepcopy(ledger);bad['questions'][0]['checks']['answerNeutrality']=False;changes.append(bad)
        bad=deepcopy(ledger);bad['highlights'][0]['bindingSha256']='stale';changes.append(bad)
        bad=deepcopy(ledger);bad['highlights'][0]['checks']['allAssociations']=False;changes.append(bad)
        for value in changes:
            def read(path,*args):return value if str(path).endswith('source-review.json') else original_read(path,*args)
            with self.subTest(value=value is None),patch.object(c.h,'read_json',side_effect=read),patch.object(c.subprocess,'run',return_value=subprocess.CompletedProcess([],0,json.dumps(structural),'')),self.assertRaises(ValueError):
                c.validate_batch03_reviews(context,records,reviews,concepts,links)

    @unittest.skipUnless((c.batch03_folder()/'manifest.json').exists(),'private final package intentionally absent from Git')
    def test_actual_repreparation_is_byte_idempotent_and_does_not_touch_reviews(self):
        root=c.batch03_folder();files=['manifest.json','index.html','completion-report.md','highlight-integration-report.json','equality-report.json','owner-review-checklist.json']
        before={f:(root/f).read_bytes() for f in files};native=c.qa.snapshot_hashes(c.h.WORK)
        if released():
            # Repreparation must refuse to rebind an owner-authorized snapshot.
            self.assertRaises(ValueError,c.prepare_batch03)
            release.validate_package();release.validate_package()
        else:
            with contextlib.redirect_stdout(io.StringIO()):c.prepare_batch03()
        self.assertEqual(before,{f:(root/f).read_bytes() for f in files});self.assertEqual(native,c.qa.snapshot_hashes(c.h.WORK))

    def test_batch3_without_dry_run_is_rejected_before_publication(self):
        root=c.h.ROOT;before=(root/'public/data/questions.json').read_bytes()
        result=subprocess.run(['node','node_modules/tsx/dist/cli.mjs','scripts/publish-historical-questions.ts','--batch','3'],cwd=root,capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0);self.assertIn('publication-gate',result.stderr);self.assertEqual(before,(root/'public/data/questions.json').read_bytes())


if __name__=='__main__':unittest.main()
