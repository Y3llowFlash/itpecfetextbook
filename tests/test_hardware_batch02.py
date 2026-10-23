"""Preparation scope, evidence, preservation and private-preview regressions."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from test_academic_qa import h,qa,record,review
import hardware_batch02 as b


def fixture():
    passage='A binary digit has two possible values. Groups of n binary digits distinguish 2^n values.'
    pages=[{'text':'','textSha256':h.digest(b''),'printedPage':None} for _ in range(487)]
    pages[25]={'text':passage,'textSha256':h.digest(passage.encode()),'printedPage':21}
    proof={'kind':'textbook-source','sourceSha256':b.audit.BOOK_SHA,'pdfPage':26,'printedPage':21,'textSha256':pages[25]['textSha256'],'checkedExcerpt':passage,'role':'direct'}
    concept={'id':'bits','sectionId':'s02','sectionUrl':'/chapters/hardware/data-representation/','questionIds':[],'videos':[]}
    node={'id':'source-heading','number':'2-1','sectionId':'s02','path':concept['sectionUrl']}
    records=[];reviews={};entries=[]
    for i,page in enumerate(sorted(b.PAGES)+list(range(500,793))):
        r=record(page);r.update(year=2000+i,season='S',number=1)
        r['images'][0].update(width=600,height=400)
        v=review(r,i<326)
        v['metadata']={'status':'verified','examType':'FE','paper':'AM','subject':'A','evidence':['Synthetic owner receipt'],'history':[{'paper':None}]}
        v['mapping']={'status':'verified','chapterId':'fe-v1-ch01','conceptId':'bits','sectionId':'s02','subsectionId':'source-heading','headingNumber':'2-1','evidence':[proof]}
        v['extraction']={'status':'complete','imageDescription':'Original question text','optionText':dict(zip('abcd',['One','Two','Three','Four'])),'sourceBinding':qa.extraction_binding(r),'reviewedImages':[r['images'][0]['sha256']]}
        v['academicReviews']=[{'status':'preserved'}]
        if 40<=i<76:v['approval']={'status':'approved','reviewer':'prior-owner','fingerprint':h.publication_fingerprint(r,v)}
        records.append(r);reviews[r['id']]=v
        if page in b.PAGES:
            entries.append({'id':r['id'],'pdfPage':page,'contentSha256':r['contentSha256'],'imageSha256':[r['images'][0]['sha256']],
                'beforeReviewSha256':qa.object_hash(v),'sourceImageVisuallyChecked':True,
                'classification':{'status':'source-reviewed','category':'ch1','chapter':1,'placement':'exact','headingNumber':'2-1','reason':'Count binary values','evidence':[proof]},
                'mapping':deepcopy(v['mapping']),'extraction':deepcopy(v['extraction']),'editorialNote':'Bounded source transcription.'})
    ledger={'schema':'itpec-hardware-batch02-preparation-v1','baseline':b.BASELINE,'sourceSha256':b.audit.SOURCE_SHA,'bookSha256':b.audit.BOOK_SHA,'entries':entries}
    return records,reviews,ledger,pages,[concept],[node]


class BatchPreparationTests(unittest.TestCase):
    def setUp(self):self.records,self.before,self.ledger,self.pages,self.concepts,self.nodes=fixture()
    def validate(self):return b.validate_decisions(self.records,self.before,self.ledger,self.pages,[],self.concepts,self.nodes)
    def result(self):return b.reconcile(self.records,self.before,self.validate(),'ledger-sha')

    def test_exact_40_and_nonlogic_concepts_supported(self):
        self.assertEqual(len(self.validate()),40)
        for rows in [self.ledger['entries'][:-1],self.ledger['entries']+[self.ledger['entries'][0]],[self.ledger['entries'][0]]*40]:
            with self.assertRaisesRegex(ValueError,'Exact 40'):b.validate_decisions(self.records,self.before,{**self.ledger,'entries':rows},self.pages,[],self.concepts,self.nodes)

    def test_stale_source_image_and_review_decisions_rejected(self):
        for field,value in [('contentSha256','stale'),('imageSha256',['other']),('beforeReviewSha256','stale'),('sourceImageVisuallyChecked',False)]:
            old=self.ledger['entries'][0][field];self.ledger['entries'][0][field]=value
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,'Stale'):self.validate()
            self.ledger['entries'][0][field]=old

    def test_published_and_qualified_or_unverified_records_excluded(self):
        for key,value in [('ownerAdjudication',{'selectedAnswer':'b'}),('approval',{'status':'approved'}),('verification',{'status':'needs-review'})]:
            identifier=self.records[0]['id'];original=deepcopy(self.before[identifier]);self.before[identifier][key]=value
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,'exclude'):self.validate()
            self.before[identifier]=original

    def test_guessed_or_changed_metadata_rejected(self):
        for key,value in [('paper',None),('subject','B'),('evidence',[])]:
            v=self.before[self.records[0]['id']];old=v['metadata'][key];v['metadata'][key]=value
            self.ledger['entries'][0]['beforeReviewSha256']=qa.object_hash(v)
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,'Morning'):self.validate()
            v['metadata'][key]=old;self.ledger['entries'][0]['beforeReviewSha256']=qa.object_hash(v)

    def test_no_duplicate_authority_bypass(self):
        r=self.records[0]
        for published in [[{'id':r['id']}],[{'id':'PRACTICE','year':r['year'],'season':r['season'],'number':r['number']}],[{'id':'OTHER','image':{'sha256':r['images'][0]['sha256']}}]]:
            with self.subTest(published=published),self.assertRaisesRegex(ValueError,'collision'):
                b.validate_decisions(self.records,self.before,self.ledger,self.pages,published,self.concepts,self.nodes)

    def test_invented_page_offset_hash_or_passage_rejected(self):
        proof=self.ledger['entries'][0]['classification']['evidence'][0]
        for key,value in [('pdfPage',126),('printedPage',20),('sourceSha256','other'),('textSha256','other'),('checkedExcerpt','Invented teaching passage'),('role','context')]:
            old=proof[key];proof[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.validate()
            proof[key]=old

    def test_heading_only_or_nonhardware_classification_rejected(self):
        c=self.ledger['entries'][0]['classification']
        for key,value in [('category','other-vol1'),('placement','context-only'),('headingNumber','3-9')]:
            old=c[key];c[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):self.validate()
            c[key]=old

    def test_mapping_independent_of_answer_and_must_match_source(self):
        self.ledger['entries'][0]['mapping']['subsectionId']='invented'
        self.assertRaisesRegex(ValueError,'subsection',self.validate)
        self.assertTrue(h.valid_verification(self.records[0],self.before[self.records[0]['id']]))

    def test_accessibility_binding_choices_or_defects_block_preparation(self):
        x=self.ledger['entries'][0]['extraction']
        for key,value in [('sourceBinding',{}),('reviewedImages',[]),('imageDescription',''),('optionText',{'a':'One'}),('sourceDefects',['unresolved'])]:
            old=deepcopy(x.get(key));x[key]=value
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,'accessible'):self.validate()
            if old is None:del x[key]
            else:x[key]=old

    def test_reconciliation_preserves_all_academic_metadata_history_and_approvals(self):
        original=deepcopy(self.before);result=self.result();selected={e['id'] for e in self.ledger['entries']}
        b.validate_transition(self.records,self.before,self.before,result,selected)
        b.validate_transition(self.records,self.before,result,result,selected)
        self.assertEqual(self.before,original)
        for identifier,v in result.items():
            for key in ['verification','explanation','metadata','academicReviews','approval']:self.assertEqual(v[key],original[identifier][key])
            if identifier not in selected:self.assertEqual(v,original[identifier])
        self.assertEqual(sum(h.valid_approval(r,result[r['id']]) for r in self.records),36)
        self.assertTrue(all(result[i]['approval']['status']=='unapproved' for i in selected))

    def test_repeat_is_deterministic_but_changed_live_review_is_stale(self):
        first=self.result();self.assertEqual(first,self.result())
        first[self.records[0]['id']]['explanation']['summary']='Changed'
        with self.assertRaisesRegex(ValueError,'stale'):b.validate_transition(self.records,self.before,first,self.result(),set(self.before))

    def test_existing_publication_fingerprint_binds_editorial_changes(self):
        r=self.records[0];v=self.result()[r['id']];fingerprint=h.publication_fingerprint(r,v)
        for key in ['imageDescription','optionText']:
            changed=deepcopy(v);changed['extraction'][key]='Changed'
            self.assertNotEqual(fingerprint,h.publication_fingerprint(r,changed))
        self.assertFalse(h.valid_approval(r,v))

    def test_adapter_supports_later_scope_without_changing_original_36_selector(self):
        records=self.records[:2];selected=[{'id':r['id']} for r in records]
        bank,answers,scoped,links=b.pilot.project(selected,records,self.before,self.concepts,
            associate=lambda q,c:{'questionId':q['id']},counts={'bits':2})
        self.assertEqual(len(bank),2);self.assertEqual(len(scoped),1);self.assertEqual(len(links),2)
        self.assertEqual(scoped[0]['questionIds'],[r['id'] for r in records])
        self.assertTrue(all(q['is_published'] is False and q['privatePreview'] is True for q in bank))
        for r,e in zip(records,answers):self.assertEqual(e['steps'],self.before[r['id']]['explanation']['steps'])

    def test_reset_and_guest_keys_share_one_namespace_without_pilot_suffix(self):
        original="itpecTextbook:guest:v1 itpecTextbook:privatePilot36:"
        result=b.pilot.namespace(original,b.PREFIX)
        self.assertEqual(result,b.PREFIX+'guest:v1 '+b.PREFIX)
        self.assertEqual(b.pilot.namespace(result,b.PREFIX),result)
        self.assertEqual(b.pilot.namespace(original,b.pilot.PREFIX),b.pilot.PREFIX+'guest:v1 '+b.pilot.PREFIX)


if __name__=='__main__':unittest.main()
