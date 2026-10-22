"""Batch 5 scope, exact mathematics, source fidelity and preservation regressions.

Only synthetic catalog/PDF fixtures are used; private exam artifacts are not required.
"""
import copy
import csv
import io
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch
import fitz
from test_academic_qa import qa,h,record,review,decision
from test_academic_qa_batch4 import fixture as prior_fixture
from test_historical_questions import question_page


def fixture():
    records,_,audit=prior_fixture();audit['batch']=5;audit['entries']=audit['entries'][:20]
    audit['scope'].update(count=20,questionIndices=[e['originalRecordIndex'] for e in audit['entries']],recordIndexConvention='zero-based, original JSON array')
    for e in audit['entries']:e.update(originalRecordIndexConvention='zero-based',targetVolume=1)
    audit['entries'][-1].update(classification='uncertain',targetChapter=None,targetVolume=None,textbookLocation=None,mappingStatusProposed='needs-review')
    scope={e['questionId'] for e in audit['entries']}
    verified={r['id'] for r in records if r['id'] not in scope and r['regions'][0]['pdfPage'] not in qa.PROTECTED_BATCH4_PAGES}
    assert len(verified)==306
    return records,{r['id']:review(r,r['id'] in verified) for r in records},audit


def companions(audit):
    stream=io.StringIO();writer=csv.writer(stream);md=[]
    writer.writerow(['Historical PDF page','Canonical question ID','Printed key','Independent answer proposal','Classification','Target volume','Target chapter','FE Vol 1 printed page','FE Vol 1 physical PDF page','Mapping status proposed','Source-grounded reasoning','Source QA flags'])
    for e in audit['entries']:
        loc=e['textbookLocation'] or {};e.setdefault('reasoning',['Synthetic proposal requires independent source checking'])
        writer.writerow([e['pdfPage'],e['questionId'],e['printedAnswer'].upper(),e['independentProposedAnswer'].upper(),e['classification'],e['targetVolume'],e['targetChapter'],loc.get('printedPage'),loc.get('pdfPage'),e['mappingStatusProposed'],' '.join(e['reasoning']),'; '.join(e['flags'])])
        location=f'{loc["printedPage"]} / {loc["pdfPage"]}' if loc else 'not established'
        md.append(f'| {e["pdfPage"]} | {e["questionId"].removeprefix("HIST-TECH01-")} | B | {e["classification"]} | {location} | {e["mappingStatusProposed"]} |')
    return stream.getvalue(),'\n'.join(md)


class AcademicBatch5Tests(unittest.TestCase):
    def test_exactly_twenty_ids_cannot_be_weakened_by_advisory_count(self):
        records,_,audit=fixture();qa.validate_proposals(records,audit,None,'source')
        for count in [19,21]:
            bad=copy.deepcopy(audit);bad['scope']['count']=count
            bad['entries']=bad['entries'][:19] if count==19 else bad['entries']+[copy.deepcopy(bad['entries'][0])]
            self.assertRaisesRegex(ValueError,'20 unique',qa.validate_proposals,records,bad,None,'source')
        bad=copy.deepcopy(audit);bad['entries'][1]=bad['entries'][0]
        self.assertRaisesRegex(ValueError,'20 unique',qa.validate_proposals,records,bad,None,'source')

    def test_source_content_image_and_zero_based_convention_bindings(self):
        records,_,audit=fixture()
        changes=[('sourceSha256','other'),('questionContentSha256','stale'),('sourceImageSha256',['changed']),('originalRecordIndexConvention','one-based'),('originalRecordIndex',254)]
        for field,value in changes:
            bad=copy.deepcopy(audit);bad['entries'][0][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):qa.validate_proposals(records,bad,None,'source')
        self.assertEqual(qa.batch_size(5),20);self.assertTrue(all(qa.batch_size(b)==30 for b in [1,2,3,4]))

    def test_companion_twenty_rows_all_fields_and_reasoning_are_consistency_inputs(self):
        _,_,audit=fixture();text,md=companions(audit);qa.validate_companions(audit,text,md)
        for changed,table in [(text.replace('requires independent','does not require'),md),(text,md.replace('not established','1 / 1')),(text,md.replace('| verified |','| proposed |')),(text,'\n'.join(md.splitlines()[:-1]))]:
            self.assertRaises(ValueError,qa.validate_companions,audit,changed,table)
        qa.validate_companions(audit,text,md+'\nOwner approval is supposedly automatic.\n')

    def test_all_306_entire_reviews_evidence_provenance_and_metadata_are_preserved(self):
        records,reviews,audit=fixture();ids={e['questionId'] for e in audit['entries']}
        for v in reviews.values():v.update(metadata={'examType':'FE','examTypeStatus':'owner-confirmed','paper':None,'subject':None},academicReviews=[{'batch':4,'status':'source-reconciled-not-owner-approved'}])
        decisions={r['id']:decision(r) for r in records if r['id'] in ids}
        merged,changes,conflicts=qa.merge_reviews(records,reviews,audit['entries'],decisions,'sha',5)
        self.assertEqual(len(changes),20);self.assertFalse(conflicts)
        self.assertEqual(sum(h.valid_verification(r,merged[r['id']]) for r in records),326)
        for r in records:
            old=reviews[r['id']];new=merged[r['id']]
            if r['id'] not in ids:self.assertEqual(old,new)
            self.assertEqual(old['metadata'],new['metadata']);self.assertEqual(old['approval'],new['approval'])
        repeated,changes,_=qa.merge_reviews(records,merged,audit['entries'],decisions,'sha',5)
        self.assertEqual(repeated,merged);self.assertFalse(changes)
        decisions['outside']=decision(records[0])
        self.assertRaisesRegex(ValueError,'exactly the 20',qa.merge_reviews,records,reviews,audit['entries'],decisions,'sha',5)

    def test_seven_protected_records_rejected_using_pages_not_array_positions(self):
        records,_,audit=fixture()
        for page in qa.PROTECTED_BATCH4_PAGES:
            r=record(page);e=copy.deepcopy(audit['entries'][0]);e.update(questionId=r['id'],originalRecordIndex=page-1,pdfPage=page,sourceOriginalImageReferences=[r['images'][0]['path']],sourceImageSha256=[r['images'][0]['sha256']])
            bad=copy.deepcopy(audit);bad['entries'][0]=e
            self.assertRaisesRegex(ValueError,'Protected',qa.validate_proposals,records,bad,None,'source')
            self.assertRaisesRegex(ValueError,'Protected',qa.merge_reviews,[r],{r['id']:review(r)},[e],{r['id']:decision(r)},'sha',5)

    def test_snapshot_checks_original_source_and_each_changed_input_before_replay(self):
        records,reviews,audit=fixture()
        with tempfile.TemporaryDirectory() as directory,patch.object(h,'WORK',Path(directory)):
            folder=h.WORK/'qa-batch5'
            for root in [h.WORK,folder/'before']:
                for name,value in [('questions',records),('reviews',reviews),('manifest',{})]:h.write_json(root/f'{name}.json',value)
            audit['sourceSnapshot']={**qa.snapshot_hashes(folder/'before'),'historicalPdfSha256':'source','textbookPdfSha256':'book'}
            inputs={'advisorySha256':'a','decisionsSha256':'d','advisoryFiles':{'json':'j','md':'m','csv':'c'}}
            qa.validate_batch2_snapshot(folder,audit,'source','book',inputs)
            h.write_json(h.WORK/'manifest.json',{'batch':5})
            self.assertRaisesRegex(ValueError,'Stale Batch 5',qa.validate_batch2_snapshot,folder,audit,'source','book',inputs)
            h.write_json(folder/'applied-state.json',{'snapshot':qa.snapshot_hashes(h.WORK),'inputs':inputs})
            qa.validate_batch2_snapshot(folder,audit,'source','book',inputs)
            for field in ['advisorySha256','decisionsSha256','advisoryFiles']:
                self.assertRaisesRegex(ValueError,'Stale Batch 5',qa.validate_batch2_snapshot,folder,audit,'source','book',{**inputs,field:'changed'})
            self.assertRaisesRegex(ValueError,'original PDFs',qa.validate_batch2_snapshot,folder,audit,'other','book',inputs)

    def test_exact_fraction_radix_and_negative_exponents_select_source_option(self):
        proof={'expression':['radix','0.B1',16],'choices':{'a':['add',1,['pow',2,-2],['pow',2,-3],['pow',2,-7]],'b':'289/256','c':'178/256','d':['add',['pow',2,-1],['pow',2,-3],['pow',2,-4],['pow',2,-8]]},'expectedMatches':['d']}
        self.assertEqual(qa.check_numeric_choices(proof)['rows'][0]['result'],'177/256')
        self.assertEqual(qa.rational(['radix','3A.5C',16]),Fraction(3735,64))
        self.assertEqual(qa.rational(['radix','2A.4C',16]),Fraction(2707,64))
        self.assertEqual(qa.rational(['radix','0.248',16]),Fraction(73,512))
        proof['choices']['d']='177/255'
        self.assertRaisesRegex(ValueError,'choice identity',qa.check_numeric_choices,proof)
        self.assertRaisesRegex(ValueError,'Digit exceeds',qa.rational,['radix','753',4])
        self.assertRaisesRegex(ValueError,'Unsupported',qa.rational,['execute','__import__("os")'])

    def test_numeric_choice_gate_rejects_wrong_key_and_nearest_ties(self):
        proof={'expression':['div',1,['sub',['add','1/20','1/30'],'1/40']],'choices':{'a':'9.2','b':10,'c':'17.1','d':24},'comparison':'nearest','expectedMatches':['c']}
        self.assertEqual(qa.check_numeric_choices(proof)['rows'][0]['result'],'120/7')
        r=record(254);r['printedAnswer']='c';d=decision(r);d['verification']['independentAnswer']='c';d['numericProofs']=[proof]
        qa.merge_reviews([r],{r['id']:review(r)},[{'questionId':r['id']}],{r['id']:d},'sha',5)
        d['verification']['independentAnswer']='b'
        self.assertRaisesRegex(ValueError,'exactly one',qa.merge_reviews,[r],{r['id']:review(r)},[{'questionId':r['id']}],{r['id']:d},'sha',5)
        proof.update(expression=2,choices=dict(zip('abcd',[1,3,7,9])),expectedMatches=['a'])
        self.assertRaisesRegex(ValueError,'choice identity',qa.check_numeric_choices,proof)

    def test_cache_complete_and_incremental_models_are_not_conflated(self):
        p=[Fraction(19,20),Fraction(1,40),Fraction(1,40)]
        self.assertEqual(sum(p),1);self.assertEqual(sum(a*b for a,b in zip(p,[1,10,100])),Fraction(37,10))
        self.assertEqual(1+Fraction(1,20)*10+Fraction(1,40)*100,4)
        average=Fraction(19,20)*Fraction(2,1000)+Fraction(99,2000)*Fraction(10,1000)+Fraction(1,2000)*10000
        self.assertEqual(average,Fraction(1000479,200000))
        self.assertEqual(Fraction(2,1000)+Fraction(1,20)*Fraction(10,1000)+Fraction(1,2000)*10000,Fraction(2001,400))
        self.assertEqual(min(['4.7','4.9','5.0','5.2'],key=lambda x:abs(Fraction(x)-average)),'5.0')

    def test_active_low_display_and_xor_original_key_values(self):
        lit=[i for i in range(8) if not ((0x92>>i)&1)]
        self.assertEqual(lit,[0,2,3,5,6]);self.assertNotIn(7,lit)
        self.assertEqual(qa.rational(['xor',0b1101,0b0001,0b0101,0b1101]),0b0100)
        key=qa.rational(['xor',0b1111,0b1101,0b0001,0b1101])
        self.assertEqual(key,0b1110)
        self.assertEqual(qa.rational(['xor',0b1101,0b0001,int(key),0b1101]),0b1111)

    def test_disk_request_conditions_and_separate_examination_occurrences(self):
        requests=[120,90,70,80,140,110,60]
        path=[100,*sorted(n for n in requests if n>100),*sorted((n for n in requests if n<100),reverse=True)]
        self.assertEqual(path,[100,110,120,140,90,80,70,60])
        self.assertEqual(sum(abs(a-b) for a,b in zip(path,path[1:])),120)
        records=[record(275),record(326)]
        records[0].update(year=2013,season='S',number=15);records[1].update(year=2007,season='A',number=29)
        reviews={r['id']:review(r) for r in records};decisions={r['id']:decision(r) for r in records}
        merged,changes,_=qa.merge_reviews(records,reviews,[{'questionId':r['id']} for r in records],decisions,'sha',5)
        self.assertEqual(set(merged),{r['id'] for r in records});self.assertEqual(len(changes),2)
        # Even shared raw-content hashes cannot authorize swapping the two source images.
        decisions[records[0]['id']]['imageHashes']=decisions[records[1]['id']]['imageHashes']
        self.assertRaisesRegex(ValueError,'Stale independent',qa.merge_reviews,records,reviews,[{'questionId':r['id']} for r in records],decisions,'sha',5)

    def test_binary_identity_counting_and_track_boundaries(self):
        for n in range(1,33):
            x=int('10'*n,2);self.assertEqual(Fraction(x)*Fraction(3,2),2**(2*n)-1)
        self.assertEqual(sum('11' not in f'{n:06b}' for n in range(64)),21)
        self.assertEqual(44100*16*3600//8,317520000)
        self.assertEqual(qa.rational(['floor',['div',30000,6400]]),4)
        self.assertEqual(qa.rational(['ceil',['div',500,4]]),125)
        self.assertGreater(5*6000+4*400,30000)
        self.assertEqual(int('3FFFFFF',16)-int('3000000',16)+1,2**24)
        self.assertTrue(int('3000000',16)<=int('35E3C03',16)<=int('3FFFFFF',16))

    def test_image_pixels_and_geometry_revalidated_not_only_file_identity(self):
        with tempfile.TemporaryDirectory() as directory,patch.object(h,'WORK',Path(directory)):
            with fitz.open() as pdf:
                page=question_page(pdf);r=h.assemble_questions([h.describe_page(page,1)],'source')[0]
                h.render_crops(pdf,[r]);self.assertEqual(qa.validate_source_images([r],pdf),1)
                r['images'][0]['width']-=1
                self.assertRaisesRegex(ValueError,'metadata differ',qa.validate_source_images,[r],pdf)

    def test_textbook_excerpt_binding_and_answer_classification_independence(self):
        with tempfile.TemporaryDirectory() as directory:
            file=Path(directory)/'book.pdf'
            with fitz.open() as doc:doc.new_page().insert_text((50,50),'Original checked source passage');doc.save(file)
            with fitz.open(file) as doc:
                sha=h.digest(file.read_bytes());text=doc[0].get_text()
                audit={'batch':5,'entries':[{'textbookLocation':{'sourceSha256':sha,'pdfPage':1,'textPageSha256':h.digest(text.encode()),'checkedExcerpt':'Original checked source passage'}}]}
                qa.validate_batch3_book(audit,{},doc)
                audit['entries'][0]['textbookLocation']['checkedExcerpt']='Different passage'
                self.assertRaisesRegex(ValueError,'excerpt changed',qa.validate_batch3_book,audit,{},doc)
        r=record(254);d=decision(r);d['classification']={'category':'uncertain','status':'needs-review','chapter':None,'volume':None};d['mapping']={'status':'needs-review'}
        merged,_,_=qa.merge_reviews([r],{r['id']:review(r)},[{'questionId':r['id']}],{r['id']:d},'sha',5)
        self.assertTrue(h.valid_verification(r,merged[r['id']]))
        self.assertIsNone(merged[r['id']]['classification']['chapter']);self.assertFalse(h.valid_approval(r,merged[r['id']]))

    def test_all_earlier_batch_replays_blocked(self):
        with tempfile.TemporaryDirectory() as directory,patch.object(h,'WORK',Path(directory)):
            h.write_json(h.WORK/'questions.json',[]);h.write_json(h.WORK/'reviews.json',{})
            h.write_json(h.WORK/'manifest.json',{'qaReconciliation':{'batch':5}})
            for batch in [1,2,3,4]:self.assertRaisesRegex(ValueError,'older batch replay',qa.reconcile,True,batch)


if __name__=='__main__':unittest.main()
