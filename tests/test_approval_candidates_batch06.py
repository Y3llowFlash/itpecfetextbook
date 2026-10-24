"""Final Batch 6 packages reuse the established manifest and source-review gates."""
from copy import deepcopy
import contextlib
import io
import json
import subprocess
import unittest
from unittest.mock import patch
from test_approval_candidates_batch03 import fixture
import approval_candidates as c
import hardware_batch06 as b
import release_6 as release
from contextlib import nullcontext
from functools import wraps

def archived_preparation(test):
    @wraps(test)
    def run(*args,**kwargs):
        with release.preparation_fixture() if (release.FOLDER/'state.json').exists() else nullcontext():
            return test(*args,**kwargs)
    return run
import approval_batch06 as f



class FinalBatch06Tests(unittest.TestCase):
    def setUp(self):
        self.records,self.reviews,self.context,self.concepts,self.report,self.entries,self.manifest,*_=fixture()
        self.manifest['batch']=6
    def validate(self,manifest=None):return c.validate_final_package(manifest or self.manifest,self.entries,self.concepts,self.report,self.context,batch=6)

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
        result=subprocess.run(['node','node_modules/tsx/dist/cli.mjs','scripts/publish-historical-questions.ts','--batch','6'],cwd=c.h.ROOT,capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0);self.assertIn('publication-gate',result.stderr)

    @unittest.skipUnless((f.folder()/'manifest.json').exists(),'Private source package is not committed')
    @archived_preparation
    def test_actual_package_preview_equality_and_read_only_preservation(self):
        manifest=f.check();context,records,reviews=f.inputs()
        self.assertEqual(len(manifest['candidates']),40);self.assertEqual(len(manifest['conceptDefinitions']),13)
        self.assertEqual([r['conceptId'] for r in manifest['highlightIntegration']],[])
        self.assertEqual(len(context['releasedQuestionIds']),196)
        self.assertEqual(sum(c.h.valid_approval(r,reviews[r['id']]) for r in records),196)
        self.assertEqual(sum(c.h.valid_verification(r,reviews[r['id']]) for r in records),326)
        for e in manifest['candidates']:
            self.assertTrue(e['technicalEligibility']);self.assertEqual(e['review']['approval']['status'],'unapproved')
            self.assertNotIn(e['record']['regions'][0]['pdfPage'],b.core.PROTECTED)
            self.assertEqual(e['publicationFingerprint'],c.h.publication_fingerprint(e['record'],e['review']))

    @unittest.skipUnless((f.folder()/'manifest.json').exists(),'Private source package is not committed')
    @archived_preparation
    def test_source_review_stale_missing_and_false_checks_rejected(self):
        context,records,reviews=f.inputs();definitions=f.concepts(context);links=f.associations(context,records,reviews,definitions)
        read=c.h.read_json;ledger=read(f.folder()/'source-review.json')
        structural=[{k:r[k] for k in ['conceptId','status']} for r in read(f.folder()/'manifest.json')['highlightIntegration']]
        variants=[None,{**ledger,'ownerApprovalGranted':True}]
        for key,value in [('sourceBinding',{}),('reviewSha256','stale'),('visibleSha256','stale')]:
            bad=deepcopy(ledger);bad['questions'][0][key]=value;variants.append(bad)
        bad=deepcopy(ledger);bad['questions'][0]['checks']['answerNeutrality']=False;variants.append(bad)
        bad=deepcopy(ledger);bad['highlights']=[{'conceptId':'unauthorized'}];variants.append(bad)
        for value in variants:
            def replace(path,*args):return value if str(path).endswith('source-review.json') else read(path,*args)
            with patch.object(c.h,'read_json',side_effect=replace),patch.object(c.subprocess,'run',return_value=subprocess.CompletedProcess([],0,json.dumps(structural),'')),self.assertRaises(ValueError):
                f.source_reviews(context,records,reviews,definitions,links)

    @unittest.skipUnless((f.folder()/'manifest.json').exists(),'Private source package is not committed')
    @archived_preparation
    def test_combined_preparation_idempotent_and_stale_manifest_rejected(self):
        paths=[f.folder()/'manifest.json',f.folder()/'index.html',b.WORK/'preview/manifest.json',c.h.WORK/'reviews.json']
        before={str(p):p.read_bytes() for p in paths}
        b.prepare();f.prepare()
        self.assertEqual(before,{str(p):p.read_bytes() for p in paths})
        read=c.h.read_json;manifest=read(f.folder()/'manifest.json');manifest['implementation']={}
        def replace(path,*args):return manifest if path==f.folder()/'manifest.json' else read(path,*args)
        with patch.object(c.h,'read_json',side_effect=replace),self.assertRaisesRegex(ValueError,'Stale'):f.check()


if __name__=='__main__':unittest.main()
