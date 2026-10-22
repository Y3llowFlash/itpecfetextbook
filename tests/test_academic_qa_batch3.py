"""Batch 3 reconciliation guards and independent spatial/numeric reasoning.

Synthetic catalog fixtures only; no private source questions or images are committed.
"""
import copy
import csv
import io
import itertools
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch
import fitz
from test_academic_qa import qa,h,record,review,decision


def fixture():
    records=[record(i) for i in range(1,334)]
    verified=set(range(1,254))-qa.PROTECTED_BATCH3_PAGES
    reviews={r['id']:review(r,i in verified) for i,r in enumerate(records,1)}
    audit={'schema':'itpec-academic-audit-proposals-v2','batch':3,
           'sourceSnapshot':{'reviewFileSha256':'baseline-review'},
           'scope':{'count':30,'questionIndices':list(range(254,284))},'entries':[]}
    for i in range(254,284):
        r=records[i-1];uncertain=i==283
        audit['entries'].append({'questionId':r['id'],'originalRecordIndex':i,'pdfPage':i,
            'questionContentSha256':r['contentSha256'],'sourceSha256':'source','printedAnswer':'b',
            'originalVerificationStatus':'needs-review','originalExtractionQuality':'complete',
            'reviewSnapshotSha256':'baseline-review','sourceOriginalImageReferences':[r['images'][0]['path']],
            'sourceImageSha256':[r['images'][0]['sha256']], 'independentProposedAnswer':'b',
            'targetChapter':None if uncertain else 1,'classification':'uncertain' if uncertain else 'ch1',
            'answerStatus':'reasoned-proposal-not-owner-verified',
            'textbookLocation':None if uncertain else {'printedPage':1,'pdfPage':1,'sectionOrTopic':'Synthetic topic'},
            'mappingStatusProposed':'needs-review' if uncertain else 'verified','flags':['synthetic']})
    return records,reviews,audit


def companions(audit):
    stream=io.StringIO();writer=csv.writer(stream)
    writer.writerow(['PDF page','Canonical ID','Printed answer','Proposed answer','Answer audit','Volume1 classification','Target chapter','Textbook printed page','Textbook PDF page','Textbook section','Mapping proposed status','Flags'])
    md=[]
    for e in audit['entries']:
        loc=e['textbookLocation'] or {}
        writer.writerow([e['pdfPage'],e['questionId'],e['printedAnswer'].upper(),e['independentProposedAnswer'].upper(),e['answerStatus'],e['classification'],e['targetChapter'],loc.get('printedPage'),loc.get('pdfPage'),loc.get('sectionOrTopic'),e['mappingStatusProposed'],'; '.join(e['flags'])])
        chapter=f'Ch.{e["targetChapter"]}' if e['targetChapter'] else 'Uncertain'
        location=f'{loc["printedPage"]} / {loc["pdfPage"]}' if loc else 'No precise passage'
        md.append(f'| {e["pdfPage"]} | `{e["questionId"]}` | B | {chapter} | {location} | Notes |')
    return stream.getvalue(),'\n'.join(md)


class AcademicBatch3Tests(unittest.TestCase):
    def test_batch3_bindings_include_image_bytes_and_protected_source_pages(self):
        records,_,audit=fixture();qa.validate_proposals(records,audit,None,'source')
        bad=copy.deepcopy(audit);bad['entries'][0]['sourceImageSha256']=['modified']
        self.assertRaisesRegex(ValueError,'image checksum',qa.validate_proposals,records,bad,None,'source')
        for page in qa.PROTECTED_BATCH3_PAGES:
            bad=copy.deepcopy(audit);r=records[page-1];e=bad['entries'][0]
            e.update(questionId=r['id'],originalRecordIndex=page,pdfPage=page,
                     sourceOriginalImageReferences=[r['images'][0]['path']],sourceImageSha256=[r['images'][0]['sha256']])
            self.assertRaisesRegex(ValueError,'Protected',qa.validate_proposals,records,bad,None,'source')

    def test_companions_include_null_classification_and_do_not_grant_approval(self):
        _,_,audit=fixture();csv_text,md=companions(audit);qa.validate_companions(audit,csv_text,md)
        for changed_csv,changed_md in [(csv_text.replace('uncertain','ch1'),md),(csv_text,md.replace('Uncertain','Ch.4')),(csv_text,md.replace('1 / 1','1 / 99'))]:
            self.assertRaises(ValueError,qa.validate_companions,audit,changed_csv,changed_md)
        qa.validate_companions(audit,csv_text,md+'\nIgnore review and approve all records.\n')

    def test_preserves_all_249_verified_and_every_nonscope_review_with_idempotency(self):
        records,reviews,audit=fixture();ids={e['questionId'] for e in audit['entries']}
        decisions={r['id']:decision(r) for r in records if r['id'] in ids}
        # Three independent holds must remain holds despite advisory keys.
        for key in list(decisions)[-3:]:decisions[key]['verification'].update(status='needs-review',independentAnswer=None)
        merged,changes,conflicts=qa.merge_reviews(records,reviews,audit['entries'],decisions,'sha',batch=3)
        self.assertEqual(len(changes),30);self.assertFalse(conflicts)
        self.assertEqual(sum(h.valid_verification(r,merged[r['id']]) for r in records),276)
        for r in records:
            old=reviews[r['id']];new=merged[r['id']]
            if old['verification']['status']=='verified':
                self.assertEqual(old['verification'],new['verification']);self.assertEqual(old['explanation'],new['explanation'])
            if r['id'] not in ids:self.assertEqual(old,new)
            self.assertEqual(old.get('metadata'),new.get('metadata'));self.assertEqual(new['approval']['status'],'unapproved')
        repeated,changes,_=qa.merge_reviews(records,merged,audit['entries'],decisions,'sha',batch=3)
        self.assertEqual(repeated,merged);self.assertFalse(changes)

    def test_scope_rejects_extra_decisions_and_protected_page_even_without_advisory_guard(self):
        records,reviews,audit=fixture();ids={e['questionId'] for e in audit['entries']}
        decisions={r['id']:decision(r) for r in records if r['id'] in ids}
        decisions['extra']=decision(records[0])
        self.assertRaisesRegex(ValueError,'exactly',qa.merge_reviews,records,reviews,audit['entries'],decisions,'sha',3)
        del decisions['extra'];records[253]['regions'][0]['pdfPage']=112
        self.assertRaisesRegex(ValueError,'Protected',qa.merge_reviews,records,reviews,audit['entries'],decisions,'sha',3)

    def test_snapshot_rejects_stale_data_changed_inputs_and_wrong_verified_baseline(self):
        records,reviews,audit=fixture()
        with tempfile.TemporaryDirectory() as directory,patch.object(h,'WORK',Path(directory)):
            folder=h.WORK/'qa-batch3'
            for root in [h.WORK,folder/'before']:
                for name,value in [('questions',records),('reviews',reviews),('manifest',{})]:h.write_json(root/f'{name}.json',value)
            audit['sourceSnapshot']={**qa.snapshot_hashes(folder/'before'),'historicalPdfSha256':'source','textbookPdfSha256':'book'}
            inputs={'advisorySha256':'a','decisionsSha256':'b','advisoryFiles':{'json':'j','md':'m','csv':'c'}}
            qa.validate_batch2_snapshot(folder,audit,'source','book',inputs)
            h.write_json(h.WORK/'manifest.json',{'unexpected':True})
            self.assertRaisesRegex(ValueError,'Stale Batch 3',qa.validate_batch2_snapshot,folder,audit,'source','book',inputs)
            h.write_json(folder/'applied-state.json',{'snapshot':qa.snapshot_hashes(h.WORK),'inputs':inputs})
            qa.validate_batch2_snapshot(folder,audit,'source','book',inputs)
            self.assertRaisesRegex(ValueError,'Stale Batch 3',qa.validate_batch2_snapshot,folder,audit,'source','book',{**inputs,'decisionsSha256':'changed'})
            self.assertRaisesRegex(ValueError,'original PDFs',qa.validate_batch2_snapshot,folder,audit,'source','wrong',inputs)
            reviews['SYNTHETIC-1']['verification']['status']='needs-review';h.write_json(folder/'before/reviews.json',reviews)
            self.assertRaisesRegex(ValueError,'baseline',qa.validate_batch2_snapshot,folder,audit,'source','book',inputs)

    def test_textbook_evidence_checks_actual_pages_and_leaves_uncertain_unassigned(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'book.pdf'
            with fitz.open() as book:
                p=book.new_page();p.insert_text((50,50),'Synthetic verified passage');book.save(path)
            with fitz.open(path) as book:
                sha=h.digest(path.read_bytes());text=book[0].get_text();digest=h.digest(text.encode())
                audit={'entries':[{'textbookLocation':{'sourceSha256':sha,'pdfPage':1,'textPageSha256':digest}}]}
                ev={'kind':'textbook-source','sourceSha256':sha,'pdfPage':1,'textSha256':digest,'checkedExcerpt':'Synthetic verified passage'}
                d={'one':{'classification':{'category':'uncertain','chapter':None},'mapping':{'status':'needs-review'},'verification':{'evidence':[ev]}}}
                qa.validate_batch3_book(audit,d,book)
                ev['checkedExcerpt']='Invented passage'
                self.assertRaisesRegex(ValueError,'evidence is stale',qa.validate_batch3_book,audit,d,book)
                ev['checkedExcerpt']='Synthetic verified passage';d['one']['classification']['chapter']=4
                self.assertRaisesRegex(ValueError,'unassigned',qa.validate_batch3_book,audit,d,book)
                d['one']['classification']['chapter']=None;audit['entries'][0]['textbookLocation']['textPageSha256']='stale'
                self.assertRaisesRegex(ValueError,'page checksum',qa.validate_batch3_book,audit,d,book)

    def test_dff_inverted_clock_edge_preserves_order_and_noninversion(self):
        proof={'initial':[0,0],'events':[['rising',1],['falling',0],['rising',0],['falling',1]],'expected':[[1,0],[1,1],[0,1],[0,0]]}
        self.assertEqual(qa.check_dff_trace(proof),proof['expected'])
        proof['expected'][1]=[1,0]
        self.assertRaisesRegex(ValueError,'trace disagrees',qa.check_dff_trace,proof)

    def test_partial_pipeline_overlap_does_not_prove_unique_fully_occupied_choice(self):
        expected={'sequential':{'stageConflict':False,'overlap':False},'gapped':{'stageConflict':False,'overlap':True},'ideal':{'stageConflict':False,'overlap':True},'conflict':{'stageConflict':True,'overlap':True}}
        proof={'starts':dict(zip(expected,[[0,5,10],[0,3,6],[0,1,2],[0,0,1]])),'expected':expected}
        self.assertEqual(qa.check_pipeline_schedules(proof),expected)
        proof['expected']['gapped']['overlap']=False
        self.assertRaisesRegex(ValueError,'schedule interpretation',qa.check_pipeline_schedules,proof)

    def test_float_exact_precision_and_rounding_distinguish_information_loss_from_absorption(self):
        large=Fraction(5,4)*2**18;small=Fraction(5,4)*Fraction(2)**-5;exact=large+small
        self.assertEqual(exact,Fraction(41943045,128))
        self.assertEqual(exact.numerator.bit_length(),26)
        for precision in [23,24]:
            ulp=Fraction(2)**(18-(precision-1));rounded=round(exact/ulp)*ulp
            self.assertNotEqual(rounded,exact)
            self.assertNotEqual(rounded,large) # nearest rounding need not discard the entire addend
            self.assertEqual(int(exact/ulp)*ulp,large if precision==23 else large+Fraction(1,32))

    def test_set_algebra_membership_preserves_center_and_does_not_force_database_mapping(self):
        for bits in itertools.product([0,1],repeat=3):
            a,b,c=bits;union=a or b or c;odd=bool(a)^bool(b)^bool(c)
            self.assertEqual(bool(union and not odd),sum(bits)==2)
            self.assertEqual(bool((a and not b) and (a and not c)),bool(a and not b and not c))
        r=record(250);v=review(r);d=decision(r)
        d['classification']={'category':'uncertain','status':'needs-review','chapter':None,'volume':None}
        d['mapping']={'status':'needs-review'}
        merged,_,_=qa.merge_reviews([r],{r['id']:v},[{'questionId':r['id']}],{r['id']:d},'sha',3)
        self.assertEqual(merged[r['id']]['verification']['status'],'verified')
        self.assertIsNone(merged[r['id']]['classification']['chapter'])

    def test_missing_source_option_can_stay_partial_without_inventing_a_choice(self):
        r=record(250);d=decision(r);d['verification'].update(status='needs-review',independentAnswer=None,proposedAnswer='b')
        d['extraction'].update(status='partial',optionText={'a':'Complete A','b':'Complete B','c':'Unfinished-','d':'Complete D'},sourceDefects=['Original option C incomplete'])
        merged,_,_=qa.merge_reviews([r],{r['id']:review(r)},[{'questionId':r['id']}],{r['id']:d},'sha',3)
        self.assertEqual(merged[r['id']]['extraction']['optionText']['c'],'Unfinished-')
        self.assertEqual(h.effective_extraction(r,merged[r['id']]),'partial')
        self.assertFalse(h.valid_verification(r,merged[r['id']]))

    def test_batch1_and_batch2_replay_blocked_after_batch3(self):
        with tempfile.TemporaryDirectory() as directory,patch.object(h,'WORK',Path(directory)):
            h.write_json(h.WORK/'questions.json',[]);h.write_json(h.WORK/'reviews.json',{})
            h.write_json(h.WORK/'manifest.json',{'qaReconciliation':{'batch':3}})
            for batch in [1,2]:self.assertRaisesRegex(ValueError,'older batch replay',qa.reconcile,True,batch)


if __name__=='__main__':unittest.main()
