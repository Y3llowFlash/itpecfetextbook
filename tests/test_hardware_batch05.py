"""Batch 5 uses the existing academic/editorial gates with an exact private scope."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import unittest
from test_hardware_batch02 import fixture
import hardware_batch05 as b
import approval_batch05 as final
from contextlib import nullcontext


def batch_fixture():
    records,before,ledger,pages,concepts,nodes=fixture()
    ledger.update(schema=b.SPEC['schema'],baseline=b.BASELINE)
    for r,e,page in zip(records,ledger['entries'],sorted(b.PAGES)):
        r['regions'][0]['pdfPage']=page;e['pdfPage']=page
        before[r['id']]['extraction']['sourceBinding']=b.qa.extraction_binding(r)
        e['extraction']['sourceBinding']=b.qa.extraction_binding(r)
        e['beforeReviewSha256']=b.qa.object_hash(before[r['id']])
    for r in records[40:196]:
        v=before[r['id']];v['approval']={'status':'approved','reviewer':'prior-owner','fingerprint':b.h.publication_fingerprint(r,v)}
    for r,page in zip(records[-7:],sorted(b.core.PROTECTED)):
        r['regions'][0]['pdfPage']=page;before[r['id']]['ownerAdjudication']={'qualification':'preserve'}
    return records,before,ledger,pages,concepts,nodes


class Batch05Tests(unittest.TestCase):
    def setUp(self):self.records,self.before,self.ledger,self.pages,self.concepts,self.nodes=batch_fixture()
    def validate(self):return b.core.validate_decisions(self.records,self.before,self.ledger,self.pages,[],self.concepts,self.nodes,spec=b.SPEC)
    def result(self):return b.core.reconcile(self.records,self.before,self.validate(),'ledger-sha',milestone='technology01-hardware-batch05')

    def test_exact_scope_and_no_published_or_protected_selection(self):
        self.assertEqual(len(self.validate()),40);self.assertFalse(b.PAGES & b.core.PROTECTED)
        for entries in [self.ledger['entries'][:-1],self.ledger['entries']+[self.ledger['entries'][0]]]:
            with self.assertRaisesRegex(ValueError,'Exact 40'):b.core.validate_decisions(self.records,self.before,{**self.ledger,'entries':entries},self.pages,[],self.concepts,self.nodes,spec=b.SPEC)
        self.before[self.records[0]['id']]['approval']['status']='approved'
        self.assertRaisesRegex(ValueError,'exclude',self.validate)

    def test_stale_bindings_and_unvalidated_image_rejected(self):
        for key,value in [('contentSha256','stale'),('imageSha256',['stale']),('beforeReviewSha256','stale'),('sourceImageVisuallyChecked',False)]:
            previous=self.ledger['entries'][0][key];self.ledger['entries'][0][key]=value
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,'Stale'):self.validate()
            self.ledger['entries'][0][key]=previous

    def test_exact_source_not_heading_or_context_only(self):
        proof=self.ledger['entries'][0]['classification']['evidence'][0]
        for key,value in [('printedPage',999),('checkedExcerpt','Invented teaching'),('role','context'),('textSha256','stale')]:
            old=proof[key];proof[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.validate()
            proof[key]=old

    def test_accessibility_must_be_complete_source_bound_and_defect_free(self):
        x=self.ledger['entries'][0]['extraction']
        for key,value in [('imageDescription',''),('optionText',{'a':'incomplete'}),('sourceBinding',{}),('sourceDefects',['unresolved'])]:
            old=deepcopy(x.get(key));x[key]=value
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,'accessible'):self.validate()
            if old is None:x.pop(key)
            else:x[key]=old

    def test_all_326_answers_seven_qualifications_and_156_approvals_preserved(self):
        result=self.result();selected={e['id'] for e in self.ledger['entries']}
        for current in [self.before,result]:b.core.validate_transition(self.records,self.before,current,result,selected,approved_count=156)
        self.assertEqual(sum(b.h.valid_approval(r,result[r['id']]) for r in self.records),156)
        for r in self.records:
            old=self.before[r['id']];new=result[r['id']]
            for key in set(old)-b.core.DIMENSIONS-{'preparationHistory'}:self.assertEqual(old[key],new[key])
            if r['id'] not in selected:self.assertEqual(old,new)
        self.assertTrue(all(result[i]['approval']['status']=='unapproved' for i in selected))

    def test_idempotent_reconciliation_and_changed_live_record_rejection(self):
        result=self.result();self.assertEqual(result,self.result())
        result[self.records[0]['id']]['explanation']['summary']='Unauthorized change'
        with self.assertRaisesRegex(ValueError,'stale'):b.core.validate_transition(self.records,self.before,result,self.result(),set(self.before),approved_count=156)

    def test_occurrence_authority_and_fingerprint_binding(self):
        r=self.records[0]
        with self.assertRaisesRegex(ValueError,'collision'):b.core.validate_decisions(self.records,self.before,self.ledger,self.pages,[{'id':'PRACTICE','year':r['year'],'season':r['season'],'number':r['number']}],self.concepts,self.nodes,spec=b.SPEC)
        old=self.result()[r['id']];new=deepcopy(old);new['extraction']['imageDescription']='Changed'
        self.assertNotEqual(b.h.publication_fingerprint(r,old),b.h.publication_fingerprint(r,new))

    def test_namespace_is_distinct_and_idempotent(self):
        original='itpecTextbook:guest:v1 itpecTextbook:privatePilot36:'
        private=b.pilot.namespace(original,b.PREFIX)
        self.assertEqual(private,b.pilot.namespace(private,b.PREFIX))
        self.assertNotIn(b.preview.PREFIX,private);self.assertNotIn('itpecTextbook:guest:v1',private)

    def test_publisher_rejects_non_dry_run_before_loading_any_source(self):
        result=subprocess.run(['node','node_modules/tsx/dist/cli.mjs','scripts/publish-historical-questions.ts','--batch','5'],cwd=b.h.ROOT,capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0);self.assertIn('separate explicit owner authorization',result.stderr)

    @unittest.skipUnless((b.WORK/'preview/manifest.json').exists(),'Private local source package intentionally absent from clones')
    def test_actual_selection_images_public_baseline_and_preview_equality(self):
        m=b.check();ledger,records,before,current,expected,published=b.load_context()
        self.assertEqual({e['pdfPage'] for e in ledger['entries']},b.PAGES)
        self.assertEqual(len(m['questionIds']),40);self.assertEqual(len(published),576)
        self.assertEqual(set(ledger['newHighlights']),{'flip-flops'})
        self.assertEqual(len(set(e['mapping']['conceptId'] for e in ledger['entries'])),16)
        for r in records:
            old,new=before[r['id']],current[r['id']]
            for key in set(old)-b.core.DIMENSIONS-{'preparationHistory'}:self.assertEqual(old[key],new[key])
            if r['id'] not in m['questionIds']:self.assertEqual(old,new)
        bypage={e['pdfPage']:e for e in ledger['entries']}
        self.assertEqual(bypage[298]['mapping']['headingNumber'],'2-1')
        self.assertRegex(bypage[288]['extraction']['optionText']['d'],r'[⁰¹²³⁴⁵⁶⁷⁸⁹]')
        self.assertNotRegex(str(bypage[128]['extraction']['optionText']),r'[\ue000-\uf8ff]')
        self.assertNotIn('only B',bypage[125]['extraction']['imageDescription'])
        self.assertNotIn('XNOR topology',bypage[223]['extraction']['imageDescription'])
        self.assertNotIn(258,b.PAGES);self.assertNotIn(99,b.PAGES)


if __name__=='__main__':unittest.main()
