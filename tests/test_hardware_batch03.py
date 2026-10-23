"""Later-batch reuse must preserve the original gates and all prior academic objects."""
from copy import deepcopy
import json
import unittest
from pathlib import Path
from test_hardware_batch02 import fixture
import hardware_batch03 as b
import hardware_batch02 as core
import release_3 as release
from contextlib import nullcontext


def batch_fixture():
    records,before,ledger,pages,concepts,nodes=fixture()
    ledger.update(schema=b.SPEC['schema'],baseline=b.BASELINE)
    for r,e,page in zip(records,ledger['entries'],sorted(b.PAGES)):
        r['regions'][0]['pdfPage']=page;e['pdfPage']=page
        before[r['id']]['extraction']['sourceBinding']=b.qa.extraction_binding(r)
        e['extraction']['sourceBinding']=b.qa.extraction_binding(r)
        e['beforeReviewSha256']=b.qa.object_hash(before[r['id']])
    for r in records[76:116]:
        v=before[r['id']];v['approval']={'status':'approved','reviewer':'prior-owner','fingerprint':b.h.publication_fingerprint(r,v)}
    return records,before,ledger,pages,concepts,nodes


class Batch03Tests(unittest.TestCase):
    def setUp(self):self.records,self.before,self.ledger,self.pages,self.concepts,self.nodes=batch_fixture()
    def validate(self):return core.validate_decisions(self.records,self.before,self.ledger,self.pages,[],self.concepts,self.nodes,spec=b.SPEC)
    def result(self):return core.reconcile(self.records,self.before,self.validate(),'fixed-ledger',milestone='technology01-hardware-batch03')

    def test_exact_scope_and_prior_batch_defaults_remain_separate(self):
        self.assertEqual(len(self.validate()),40);self.assertFalse(b.PAGES&core.PROTECTED)
        with self.assertRaisesRegex(ValueError,'baseline'):core.validate_decisions(self.records,self.before,self.ledger,self.pages,[],self.concepts,self.nodes)
        for entries in [self.ledger['entries'][:-1],self.ledger['entries']+[self.ledger['entries'][0]]]:
            with self.assertRaisesRegex(ValueError,'Exact 40'):core.validate_decisions(self.records,self.before,{**self.ledger,'entries':entries},self.pages,[],self.concepts,self.nodes,spec=b.SPEC)

    def test_stale_source_image_review_and_unreviewed_description_rejected(self):
        for key,value in [('contentSha256','stale'),('imageSha256',['stale']),('beforeReviewSha256','stale'),('sourceImageVisuallyChecked',False)]:
            old=self.ledger['entries'][0][key];self.ledger['entries'][0][key]=value
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,'Stale'):self.validate()
            self.ledger['entries'][0][key]=old
        self.ledger['entries'][0]['extraction']['sourceBinding']={}
        self.assertRaisesRegex(ValueError,'accessible',self.validate)

    def test_heading_similarity_or_context_alone_is_insufficient(self):
        self.ledger['entries'][0]['classification']=deepcopy(self.ledger['entries'][0]['classification'])
        self.ledger['entries'][0]['classification']['evidence'][0]['role']='context'
        self.assertRaisesRegex(ValueError,'Context alone',self.validate)

    def test_private_reconciliation_preserves_326_answers_and_76_approvals(self):
        result=self.result();selected={e['id'] for e in self.ledger['entries']}
        for current in [self.before,result]:core.validate_transition(self.records,self.before,current,result,selected,approved_count=76)
        self.assertEqual(sum(b.h.valid_approval(r,result[r['id']]) for r in self.records),76)
        for r in self.records:
            for key in set(self.before[r['id']])-core.DIMENSIONS-{'preparationHistory'}:self.assertEqual(result[r['id']][key],self.before[r['id']][key])
            if r['id'] not in selected:self.assertEqual(result[r['id']],self.before[r['id']])
        self.assertEqual(result,self.result())
        self.assertEqual(result[self.records[0]['id']]['preparationHistory'][-1]['milestone'],'technology01-hardware-batch03')

    def test_changed_live_review_or_approval_rejected(self):
        result=self.result();changed=deepcopy(result);changed[self.records[0]['id']]['explanation']['summary']='Changed'
        with self.assertRaisesRegex(ValueError,'stale'):core.validate_transition(self.records,self.before,changed,result,set(self.before),approved_count=76)
        changed=deepcopy(result);changed[self.records[0]['id']]['approval']['status']='approved'
        with self.assertRaises(ValueError):core.validate_transition(self.records,self.before,result,changed,set(self.before),approved_count=76)

    def test_occurrence_authority_and_metadata_not_guessed(self):
        r=self.records[0];published=[{'id':'Practice','year':r['year'],'season':r['season'],'number':r['number']}]
        with self.assertRaisesRegex(ValueError,'collision'):core.validate_decisions(self.records,self.before,self.ledger,self.pages,published,self.concepts,self.nodes,spec=b.SPEC)
        self.before[r['id']]['metadata']['subject']=None;self.ledger['entries'][0]['beforeReviewSha256']=b.qa.object_hash(self.before[r['id']])
        self.assertRaisesRegex(ValueError,'Morning',self.validate)

    def test_approval_fingerprint_changes_with_editorial_and_mapping_changes(self):
        r=self.records[0];v=self.result()[r['id']];fp=b.h.publication_fingerprint(r,v)
        for dimension,key in [('extraction','imageDescription'),('mapping','conceptId'),('explanation','summary')]:
            revised=deepcopy(v);revised[dimension][key]='Changed';self.assertNotEqual(fp,b.h.publication_fingerprint(r,revised))
        self.assertFalse(b.h.valid_approval(r,v))

    def test_private_namespace_idempotent_and_distinct(self):
        keys='itpecTextbook:guest:v1 itpecTextbook:privatePilot36:'
        private=b.pilot.namespace(keys,b.PREFIX)
        self.assertEqual(b.pilot.namespace(private,b.PREFIX),private);self.assertNotIn(core.PREFIX,private)

    @unittest.skipUnless((b.WORK/'decisions.json').exists(),'private source fixtures intentionally absent in fresh clones')
    def test_actual_source_reviewed_selection_preservation_and_preview_equality(self):
        with release.preparation_fixture() if (release.FOLDER/'state.json').exists() else nullcontext():
            manifest=b.check();ledger,records,before,current,expected,published=b.load_context()
            self.assertEqual({e['pdfPage'] for e in ledger['entries']},b.PAGES)
            self.assertEqual(len(manifest['questionIds']),40);self.assertEqual(len(published),496)
            self.assertTrue(all(current[e['id']]['approval']['status']=='unapproved' for e in ledger['entries']))
            bank,answers,concepts,links=b.payload(ledger,records,current,published)
            self.assertEqual(len(bank),139);self.assertEqual(len(links),40)
            live={e['questionId']:e for e in b.h.read_json(b.h.ROOT/'src/content/explanations.json')}
            for e in answers:
                if e['questionId'] in live:self.assertEqual(e,live[e['questionId']])
            page={e['pdfPage']:e['extraction'] for e in ledger['entries']}
            self.assertEqual(page[299]['optionText'],dict(zip('abcd',['1/4','1/2','2','4'])))
            self.assertIn('2⁻¹⁶',page[157]['optionText']['a']);self.assertEqual(page[317]['optionText']['d'],'2²⁴ × 16')
            self.assertIn('cash memory',page[75]['optionText']['b'])
            for n in [9,108,155,157]:self.assertNotRegex(page[n]['imageDescription'],r'checked|must not|correct answer|A=XOR')
            for r in records:
                for key in ['verification','explanation','approval','metadata','ownerAdjudication']:self.assertEqual(before[r['id']].get(key),current[r['id']].get(key))


if __name__=='__main__':unittest.main()
