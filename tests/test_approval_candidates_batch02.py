"""Synthetic regressions for the existing candidate system's second exact scope."""
from copy import deepcopy
from pathlib import Path
import unittest
from unittest.mock import patch
from test_hardware_batch02 import fixture
import approval_candidates as c


def package_fixture(new=True,status='source-validated-pending-owner-editorial-approval'):
    records,reviews,ledger,_,definitions,_=fixture();ids=[e['id'] for e in ledger['entries']]
    concepts=[{**definitions[0],'title':'Binary values','summary':'Count binary combinations.','newConcept':new}]
    selected=[{'id':i} for i in ids]
    bank,answers,_,associations=c.pilot.project(selected,records,reviews,concepts,counts={'bits':40},associate=lambda q,d:{'questionId':q['id'],
        'bookEvidence':deepcopy(ledger['entries'][0]['classification']['evidence']),'paragraphText':'Count binary values in the original source.',
        'sourceParagraphId':'source-paragraph','highlightPrintedPage':21,'highlightPhysicalPdfPage':26})
    context={'questionIds':ids,'conceptCounts':{'bits':40},'sourceSha256':'source','textbookSha256':'book'}
    report=[{'conceptId':'bits','status':status}] if new else []
    def read(path,*args):
        if str(path).endswith('reviews.json'):return deepcopy(reviews)
        if str(path).endswith('pilot-bank.json'):return deepcopy(bank)
        if str(path).endswith('explanations.json'):return deepcopy(answers)
        raise AssertionError(path)
    with patch.object(c.h,'read_json',side_effect=read),patch.object(c.h,'_PRACTICE_SNAPSHOT',[]),patch.object(c,'batch02_associations',return_value=associations):
        entries=c.batch02_entries(context,records,reviews,concepts,report)
    manifest={'schema':'itpec-final-approval-candidates-v1','batch':2,'privateOnly':True,'readOnly':True,'publicationApprovalGranted':False,
        'questionIds':ids,'conceptCounts':context['conceptCounts'],'candidates':entries,'conceptDefinitions':concepts,'highlightIntegration':report}
    manifest['candidateSetFingerprint']=c.qa.object_hash({'ids':ids,'candidates':entries,'conceptDefinitions':concepts,'highlightIntegration':report,'sourceSha256':'source','textbookSha256':'book'})
    return records,reviews,context,concepts,report,entries,manifest,bank,answers,associations


class FinalBatch02Tests(unittest.TestCase):
    def setUp(self):
        self.records,self.reviews,self.context,self.concepts,self.report,self.entries,self.manifest,self.bank,self.answers,self.associations=package_fixture()

    def validate(self,manifest=None):return c.validate_batch02_package(manifest or self.manifest,self.entries,self.concepts,self.report,self.context)

    def test_existing_builder_supports_exact_40_without_relaxing_default_36(self):
        ids=self.context['questionIds']
        result=c.build_entries(self.records,self.reviews,ids,self.associations,self.bank,self.answers,expected_count=40)
        self.assertEqual(len(result),40)
        self.assertRaisesRegex(ValueError,'same 36',c.build_entries,self.records,self.reviews,ids,self.associations,self.bank,self.answers)
        for changed in [ids[:-1],ids+[ids[0]],[ids[0]]*40]:
            with self.assertRaisesRegex(ValueError,'same 40'):c.build_entries(self.records,self.reviews,changed,self.associations,self.bank,self.answers,expected_count=40)

    def test_exact_payload_equal_to_private_preview_and_native_academic_objects(self):
        self.validate()
        for e,q,a in zip(self.entries,self.bank,self.answers):
            self.assertEqual(e['studentVisible'],c.preview_visible(q,a))
            self.assertEqual(e['review'],self.reviews[e['id']])
            self.assertEqual(e['publicationFingerprint'],c.h.publication_fingerprint(e['record'],e['review']))
            self.assertEqual(e['review']['approval']['status'],'unapproved')
            self.assertFalse(c.h.valid_approval(e['record'],e['review']))

    def test_extra_duplicate_missing_or_reordered_scope_rejected(self):
        for key,value in [('questionIds',self.context['questionIds'][::-1]),('candidates',self.entries[:-1]),('candidates',self.entries+[self.entries[0]]),('conceptCounts',{}),('publicationApprovalGranted',True),('readOnly',False)]:
            with self.subTest(key=key),self.assertRaises(ValueError):self.validate({**self.manifest,key:value})

    def test_stale_answer_explanation_option_image_mapping_or_metadata_rejected(self):
        for dimension,key,value in [('verification','independentAnswer','d'),('explanation','steps',['Changed']),('extraction','imageDescription','Changed'),('extraction','optionText',{'a':'Changed'}),('mapping','conceptId','elsewhere'),('metadata','paper','B')]:
            changed=deepcopy(self.manifest);changed['candidates'][0]['review'][dimension][key]=value
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,'stale'):self.validate(changed)
        changed=deepcopy(self.manifest);changed['candidates'][0]['record']['images'][0]['sha256']='changed'
        self.assertRaisesRegex(ValueError,'stale',self.validate,changed)

    def test_concept_definition_and_support_passage_bound_beyond_native_fingerprint(self):
        entry=self.entries[0];original=entry['approvalContextFingerprint']
        for field in ['title','summary','sectionUrl']:
            concept={**entry['conceptDefinition'],field:'Changed'}
            self.assertNotEqual(original,c.approval_context_fingerprint(entry,concept))
        changed=deepcopy(entry);changed['textbookSupport']['bookEvidence']=['Changed source passage']
        self.assertNotEqual(original,c.approval_context_fingerprint(changed,changed['conceptDefinition']))
        changed=deepcopy(self.manifest);changed['conceptDefinitions'][0]['summary']='Changed'
        self.assertRaisesRegex(ValueError,'stale',self.validate,changed)

    def test_candidate_set_fingerprint_cannot_be_changed_or_dropped(self):
        self.assertRaisesRegex(ValueError,'fingerprint',self.validate,{**self.manifest,'candidateSetFingerprint':'stale'})
        changed=deepcopy(self.manifest);del changed['candidateSetFingerprint']
        self.assertRaisesRegex(ValueError,'fingerprint',self.validate,changed)

    def test_no_new_approval_is_needed_for_readonly_package(self):
        original=deepcopy(self.reviews)
        c.validate_batch02_approvals(self.manifest,self.records,self.reviews,'manifest-sha')
        self.assertEqual(self.reviews,original)
        self.assertTrue(all(e['remainingBlockers']==['final-owner-publication-approval-absent','final-owner-editorial-highlight-approval-absent'] for e in self.entries))

    def synthetic_authorization(self):
        # In-memory test fixture only; never writes a native review or calls approve.
        entries=self.entries;reviews=deepcopy(self.reviews);e=entries[0]
        reviews[e['id']]['approval']={'status':'approved','reviewer':'synthetic unit fixture only','fingerprint':e['publicationFingerprint'],
            'candidateManifestSha256':'manifest-sha','candidateSetFingerprint':self.manifest['candidateSetFingerprint'],
            'approvalContextFingerprint':e['approvalContextFingerprint'],'highlightEditorialAuthorization':e['highlightIntegration']['previewDefinitionSha256']}
        return reviews

    def test_future_native_approval_alone_cannot_bypass_exact_package_context(self):
        reviews=self.synthetic_authorization();e=self.entries[0]
        self.assertTrue(c.h.valid_approval(e['record'],reviews[e['id']]))
        c.validate_batch02_approvals(self.manifest,self.records,reviews,'manifest-sha')
        for key in ['candidateManifestSha256','candidateSetFingerprint','approvalContextFingerprint','highlightEditorialAuthorization']:
            bad=deepcopy(reviews);bad[e['id']]['approval'].pop(key)
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,'exact package'):c.validate_batch02_approvals(self.manifest,self.records,bad,'manifest-sha')

    def test_future_approval_invalid_after_source_or_visible_question_change(self):
        reviews=self.synthetic_authorization();first=self.entries[0]['id']
        for dimension,key in [('explanation','summary'),('extraction','imageDescription'),('mapping','reason')]:
            changed=deepcopy(reviews);changed[first][dimension][key]='Changed'
            with self.subTest(key=key),self.assertRaises(ValueError):c.validate_batch02_approvals(self.manifest,self.records,changed,'manifest-sha')

    def test_bad_highlight_flags_affected_candidates_and_blocks_future_approval(self):
        records,reviews,context,concepts,report,entries,manifest,*_=package_fixture(status='correction-required')
        self.assertTrue(all(not e['technicalEligibility'] and 'source-highlight-correction-required' in e['remainingBlockers'] for e in entries))
        page=c.render_gallery(manifest,concepts)
        self.assertIn('Technical correction required before approval',page)
        self.assertIn('0 of 15 new source highlights are source validated',page)
        fake=self.synthetic_authorization()
        with self.assertRaises(ValueError):c.validate_batch02_approvals(manifest,records,fake,'manifest-sha')

    def test_check_rejects_tampered_generated_concept_plan_without_repairing_it(self):
        with patch.object(c.h,'read_json',return_value=[{'id':'tampered'}]),patch.object(c,'save') as save:
            with self.assertRaisesRegex(ValueError,'concept plan changed'):c.validate_batch02_highlights(self.concepts)
            save.assert_not_called()

    def test_gallery_is_readonly_with_complete_checklist_and_individual_blockers(self):
        page=c.render_gallery(self.manifest,self.concepts)
        self.assertIn('Final 40-question owner review',page)
        self.assertEqual(page.count('data-checklist='),40);self.assertEqual(page.count('data-question='),40)
        self.assertNotRegex(page,r'<(?:form|input|button|script)\b')
        self.assertEqual(page.count('class="blockers"'),40)
        for e in self.entries:self.assertIn(e['publicationFingerprint'],page);self.assertIn(e['approvalContextFingerprint'],page)

    def test_all_293_nonselected_native_objects_and_their_approvals_are_protected(self):
        ids=self.context['questionIds'];frozen=deepcopy(self.reviews)
        c.validate_live_reviews(self.records,self.reviews,frozen,ids)
        other=next(r['id'] for r in self.records if r['id'] not in ids)
        for dimension in ['verification','metadata','approval']:
            changed=deepcopy(self.reviews);changed[other][dimension]={'changed':True}
            with self.subTest(dimension=dimension),self.assertRaisesRegex(ValueError,'Noncandidate'):c.validate_live_reviews(self.records,changed,frozen,ids,True)

    def test_readonly_rejects_new_approval_and_publisher_allows_only_approval_dimension(self):
        frozen=deepcopy(self.reviews);changed=self.synthetic_authorization();ids=self.context['questionIds']
        with self.assertRaisesRegex(ValueError,'read-only'):c.validate_live_reviews(self.records,changed,frozen,ids)
        c.validate_live_reviews(self.records,changed,frozen,ids,True)
        changed[ids[0]]['extraction']['imageDescription']='Changed'
        with self.assertRaisesRegex(ValueError,'content/approval'):c.validate_live_reviews(self.records,changed,frozen,ids,True)


if __name__=='__main__':unittest.main()
