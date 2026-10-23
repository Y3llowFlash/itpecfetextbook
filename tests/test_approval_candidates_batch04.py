"""Final Batch 4 packages reuse the established manifest and source-review gates."""
from copy import deepcopy
import contextlib
import io
import json
import subprocess
import unittest
from unittest.mock import patch
from test_approval_candidates_batch03 import fixture
import approval_candidates as c
import hardware_batch04 as b
import release_4 as release

def released():return (release.FOLDER/'state.json').exists()
def inputs():return release.archived_inputs() if released() else c.batch04_inputs()


class FinalBatch04Tests(unittest.TestCase):
    def setUp(self):
        self.records,self.reviews,self.context,self.concepts,self.report,self.entries,self.manifest,*_=fixture()
        self.manifest['batch']=4
    def validate(self,manifest=None):return c.validate_final_package(manifest or self.manifest,self.entries,self.concepts,self.report,self.context,batch=4)

    def test_exact_40_ordered_scope_no_duplicate_extra_or_missing_ids(self):
        self.validate()
        for ids in [self.context['questionIds'][:-1],self.context['questionIds'][::-1],self.context['questionIds']+[self.context['questionIds'][0]]]:
            with self.assertRaises(ValueError):self.validate({**self.manifest,'questionIds':ids})
        self.assertRaises(ValueError,self.validate,{**self.manifest,'candidates':self.entries[:-1]})

    def test_every_source_and_visible_dimension_is_bound(self):
        for field in ['record','review','studentVisible','sourceTranscription','conceptDefinition','textbookSupport','finalSourceReview','finalHighlightReview','publicationFingerprint','approvalContextFingerprint']:
            m=deepcopy(self.manifest);m['candidates'][0][field]={'changed':True}
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,'stale'):self.validate(m)

    def test_approval_flags_set_digest_and_highlight_definition_are_bound(self):
        for field,value in [('readOnly',False),('privateOnly',False),('publicationApprovalGranted',True),('candidateSetFingerprint','stale'),('batch',3),('conceptDefinitions',[])]:
            with self.subTest(field=field),self.assertRaises(ValueError):self.validate({**self.manifest,field:value})
        entry=self.entries[0];changed=deepcopy(entry);changed['sourceTranscription']['literalSourceTypos']=['new interpretation']
        self.assertNotEqual(c.approval_context_fingerprint(entry,entry['conceptDefinition']),c.approval_context_fingerprint(changed,changed['conceptDefinition']))

    def test_native_approval_or_academic_edits_are_read_only_violations(self):
        for field in ['approval','verification','extraction','mapping','metadata','explanation']:
            bad=deepcopy(self.reviews);bad[self.context['questionIds'][0]][field]={'changed':True}
            with self.subTest(field=field),self.assertRaises(ValueError):c.validate_live_reviews(self.records,bad,self.reviews,self.context['questionIds'])

    def test_batch4_cannot_publish_without_separate_release_implementation(self):
        result=subprocess.run(['node','node_modules/tsx/dist/cli.mjs','scripts/publish-historical-questions.ts','--batch','4'],cwd=c.h.ROOT,capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0);self.assertIn('publication-gate',result.stderr)

    @unittest.skipUnless((c.batch04_folder()/'manifest.json').exists(),'Private source package is intentionally not committed')
    def test_actual_frozen_40_20_two_highlights_and_18_reused_definitions(self):
        manifest=release.validate_package() if released() else c.check_batch04();context,records,reviews,frozen=inputs()
        self.assertEqual(manifest['questionIds'],c.h.read_json(c.batch04_folder()/'before/batch/preview/manifest.json')['questionIds'])
        self.assertEqual(len(manifest['candidates']),40);self.assertEqual(len(manifest['conceptDefinitions']),20)
        self.assertEqual({r['conceptId'] for r in manifest['highlightIntegration']},{'display-memory','cache-write-policies'})
        public={d['id']:d for d in c.h.read_json(c.h.ROOT/'src/content/concepts.json')}
        reused=[d for d in manifest['conceptDefinitions'] if not d['newConcept']];self.assertEqual(len(reused),18)
        for d in reused:self.assertEqual(c.concept_view(d),c.concept_view(public[d['id']]))
        self.assertEqual(len(c.h.read_json(release.FOLDER/'before-public-questions.json') if released() else c.h.read_json(c.h.ROOT/'public/data/questions.json')),536)
        self.assertEqual(len(context['releasedQuestionIds']),116);self.assertEqual(reviews,frozen)
        self.assertEqual(sum(c.h.valid_approval(r,reviews[r['id']]) for r in records),116)
        self.assertEqual(sum(c.h.valid_verification(r,reviews[r['id']]) for r in records),326)
        for e in manifest['candidates']:
            self.assertTrue(e['technicalEligibility']);self.assertFalse(e['publicationApprovalGranted']);self.assertEqual(e['review']['approval']['status'],'unapproved')
            self.assertNotIn(e['record']['regions'][0]['pdfPage'],b.core.PROTECTED);self.assertFalse(e['review'].get('ownerAdjudication'))
            self.assertEqual(e['publicationFingerprint'],c.h.publication_fingerprint(e['record'],e['review']))
            self.assertEqual(e['dimensionFingerprints']['explanation'],c.qa.object_hash(e['review']['explanation']))
        bypage={e['record']['regions'][0]['pdfPage']:e for e in manifest['candidates']}
        self.assertIn('bimary',bypage[111]['sourceTranscription']['immutableRawTranscript'])
        self.assertIn('binary number',bypage[111]['studentVisible']['imageDescription'])
        self.assertIn('unmatched parenthesis',' '.join(bypage[111]['sourceTranscription']['editorialClarifications']))
        for p in [111,283,287]:self.assertEqual(bypage[p]['review']['extraction']['status'],'complete')

    @unittest.skipUnless((c.batch04_folder()/'manifest.json').exists(),'Private source package intentionally absent from Git')
    def test_actual_stale_missing_or_unvalidated_source_ledger_rejected(self):
        context,records,reviews,_=inputs();concepts=release.context()[1]['conceptDefinitions'] if released() else c.batch04_concepts(context);links=c.batch04_associations(context,records,reviews,concepts)
        read=c.h.read_json;ledger=read(c.batch04_folder()/'source-review.json');structural=[{k:r[k] for k in ['conceptId','status']} for r in read(c.batch04_folder()/'manifest.json')['highlightIntegration']]
        variants=[None,{**ledger,'ownerApprovalGranted':True}]
        for key,value in [('sourceBinding',{}),('reviewSha256','stale'),('visibleSha256','stale')]:
            bad=deepcopy(ledger);bad['questions'][0][key]=value;variants.append(bad)
        bad=deepcopy(ledger);bad['questions'][0]['checks']['answerNeutrality']=False;variants.append(bad)
        bad=deepcopy(ledger);bad['highlights'][0]['bindingSha256']='stale';variants.append(bad)
        for value in variants:
            def replace(path,*args):return value if str(path).endswith('source-review.json') else read(path,*args)
            with self.subTest(value=value is None),patch.object(c.h,'read_json',side_effect=replace),patch.object(c.subprocess,'run',return_value=subprocess.CompletedProcess([],0,json.dumps(structural),'')),self.assertRaises(ValueError):c.batch04_reviews(context,records,reviews,concepts,links)

    @unittest.skipUnless((c.batch04_folder()/'manifest.json').exists(),'Private package intentionally absent from Git')
    def test_actual_repreparation_is_byte_idempotent_and_preserves_native_history(self):
        root=c.batch04_folder();names=['manifest.json','index.html','completion-report.md','equality-report.json','highlight-integration-report.json','owner-review-checklist.json']
        original={name:(root/name).read_bytes() for name in names};snapshot=c.qa.snapshot_hashes(c.h.WORK)
        if released():
            self.assertRaises(ValueError,c.prepare_batch04)
            release.validate_package();release.validate_package()
        else:
            with contextlib.redirect_stdout(io.StringIO()):c.prepare_batch04()
        self.assertEqual(original,{name:(root/name).read_bytes() for name in names});self.assertEqual(snapshot,c.qa.snapshot_hashes(c.h.WORK))


if __name__=='__main__':unittest.main()
