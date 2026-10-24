"""Batch 7 reuses the existing gates with an exact smaller private scope."""
from copy import deepcopy
import subprocess
import unittest
from test_hardware_batch02 import fixture
import hardware_batch07 as b
import release_7 as release
from contextlib import nullcontext
from functools import wraps


def archived_preparation(test):
    @wraps(test)
    def run(*args,**kwargs):
        with release.preparation_fixture() if (release.FOLDER/'state.json').exists() else nullcontext():
            return test(*args,**kwargs)
    return run

import approval_batch07 as final


def batch_fixture():
    records,before,ledger,pages,concepts,nodes=fixture()
    ledger.update(schema=b.SPEC['schema'],baseline=b.BASELINE)
    ledger['entries']=ledger['entries'][:b.COUNT]
    for r,e,page in zip(records,ledger['entries'],sorted(b.PAGES)):
        r['regions'][0]['pdfPage']=page;e['pdfPage']=page
        before[r['id']]['extraction']['sourceBinding']=b.qa.extraction_binding(r)
        e['extraction']['sourceBinding']=b.qa.extraction_binding(r)
        e['beforeReviewSha256']=b.qa.object_hash(before[r['id']])
    for r in records[b.COUNT:b.COUNT+236]:
        v=before[r['id']];v['approval']={'status':'approved','reviewer':'prior-owner','fingerprint':b.h.publication_fingerprint(r,v)}
    for r,page in zip(records[-7:],sorted(b.core.PROTECTED)):
        r['regions'][0]['pdfPage']=page;before[r['id']]['ownerAdjudication']={'qualification':'preserve'}
    return records,before,ledger,pages,concepts,nodes


class Batch07Tests(unittest.TestCase):
    def setUp(self):self.records,self.before,self.ledger,self.pages,self.concepts,self.nodes=batch_fixture()
    def validate(self):return b.core.validate_decisions(self.records,self.before,self.ledger,self.pages,[],self.concepts,self.nodes,spec=b.SPEC)
    def result(self):return b.core.reconcile(self.records,self.before,self.validate(),'ledger-sha',milestone='technology01-hardware-batch07')

    def test_exact_scope_and_no_published_or_protected_selection(self):
        self.assertEqual(len(self.validate()),b.COUNT);self.assertFalse(b.PAGES & b.core.PROTECTED)
        for entries in [self.ledger['entries'][:-1],self.ledger['entries']+[self.ledger['entries'][0]]]:
            with self.assertRaisesRegex(ValueError,'Exact 31'):b.core.validate_decisions(self.records,self.before,{**self.ledger,'entries':entries},self.pages,[],self.concepts,self.nodes,spec=b.SPEC)
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

    def test_all_326_answers_seven_qualifications_and_236_approvals_preserved(self):
        result=self.result();selected={e['id'] for e in self.ledger['entries']}
        for current in [self.before,result]:b.core.validate_transition(self.records,self.before,current,result,selected,approved_count=236)
        self.assertEqual(sum(b.h.valid_approval(r,result[r['id']]) for r in self.records),236)
        for r in self.records:
            old=self.before[r['id']];new=result[r['id']]
            for key in set(old)-b.core.DIMENSIONS-{'preparationHistory'}:self.assertEqual(old[key],new[key])
            if r['id'] not in selected:self.assertEqual(old,new)
        self.assertTrue(all(result[i]['approval']['status']=='unapproved' for i in selected))

    def test_idempotent_reconciliation_and_changed_live_record_rejection(self):
        result=self.result();self.assertEqual(result,self.result())
        result[self.records[0]['id']]['explanation']['summary']='Unauthorized change'
        with self.assertRaisesRegex(ValueError,'stale'):b.core.validate_transition(self.records,self.before,result,self.result(),set(self.before),approved_count=236)

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
        result=subprocess.run(['node','node_modules/tsx/dist/cli.mjs','scripts/publish-historical-questions.ts','--batch','7'],cwd=b.h.ROOT,capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0);self.assertIn('publication-gate',result.stderr)

    @unittest.skipUnless((b.WORK/'preview/manifest.json').exists(),'Private source package absent from clones')
    @archived_preparation
    def test_actual_scope_immutability_and_final_equality(self):
        m=b.check();ledger,records,before,current,expected,published=b.load_context()
        self.assertEqual(len(m['questionIds']),31);self.assertEqual(len(published),656)
        self.assertEqual(len(set(e['mapping']['conceptId'] for e in ledger['entries'])),8)
        self.assertEqual(ledger['newHighlights'],[])
        for r in records:
            old,new=before[r['id']],current[r['id']]
            for key in set(old)-b.core.DIMENSIONS-{'preparationHistory'}:self.assertEqual(old[key],new[key])
            if r['id'] not in m['questionIds']:self.assertEqual(old,new)
        self.assertEqual(sum(b.h.valid_approval(r,current[r['id']]) for r in records),236)
        self.assertEqual(final.check()['previewEquality']['questions'],31)


if __name__=='__main__':unittest.main()
