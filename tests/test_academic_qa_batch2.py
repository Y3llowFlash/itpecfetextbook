"""Batch 2 adapter and scientific ambiguity checks, using synthetic private fixtures."""
import copy
import csv
import io
import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch
from test_academic_qa import qa,h,record,review,decision


def fixture():
    records=[record(i) for i in range(1,31)]
    reviews={r['id']:review(r) for r in records}
    audit={'schema':'itpec-academic-audit-proposals-v2','batch':2,
           'sourceSnapshot':{'reviewFileSha256':'baseline-review'},
           'scope':{'count':30,'questionIndices':list(range(1,31))},'entries':[]}
    for i,r in enumerate(records,1):
        audit['entries'].append({'questionId':r['id'],'originalRecordIndex':i,'pdfPage':i,
            'questionContentSha256':r['contentSha256'],'sourceSha256':'source','printedAnswer':'b',
            'originalVerificationStatus':'needs-review','originalExtractionQuality':'complete',
            'reviewSnapshotSha256':'baseline-review','sourceOriginalImageReferences':[r['images'][0]['path']],
            'independentProposedAnswer':None if i==30 else 'b','targetChapter':3 if i==29 else 1,
            'answerStatus':'needs-review' if i==30 else 'reasoned-proposal-not-owner-verified',
            'textbookLocation':{'pdfPage':i},'sourceVisualReview':{'note':'Synthetic source reviewed'}})
    return records,reviews,audit


def companions(audit):
    stream=io.StringIO();writer=csv.writer(stream)
    writer.writerow(['PDF page','Question','Proposed answer','Classification','Textbook PDF page','Review status','Visual / academic note'])
    md=['| PDF p. | Question | Answer | Location |']
    for e in audit['entries']:
        answer=e['independentProposedAnswer'] or 'UNRESOLVED'
        writer.writerow([e['pdfPage'],e['questionId'],answer,f'Vol 1 Chapter {e["targetChapter"]}',e['textbookLocation']['pdfPage'],e['answerStatus'],e['sourceVisualReview']['note']])
        md.append(f'| {e["pdfPage"]} | `{e["questionId"]}` | **{answer.upper()}** | Vol 1 Ch.{e["targetChapter"]}, PDF p.{e["textbookLocation"]["pdfPage"]} |')
    return stream.getvalue(),'\n'.join(md)


class AcademicBatch2Tests(unittest.TestCase):
    def test_v2_identity_source_image_and_scope_checks(self):
        records,_,audit=fixture()
        qa.validate_proposals(records,audit,None,'source')
        edits=[('originalRecordIndex',2),('printedAnswer','c'),('originalExtractionQuality','partial'),
               ('reviewSnapshotSha256','stale'),('sourceOriginalImageReferences',['images/other.webp'])]
        for field,value in edits:
            changed=copy.deepcopy(audit);changed['entries'][0][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):qa.validate_proposals(records,changed,None,'source')
        changed=copy.deepcopy(audit);changed['scope']['questionIndices'].reverse()
        self.assertRaisesRegex(ValueError,'scope indices',qa.validate_proposals,records,changed,None,'source')

    def test_csv_and_markdown_are_consistency_inputs_not_approval(self):
        _,_,audit=fixture();csv_text,md=companions(audit)
        qa.validate_companions(audit,csv_text,md)
        self.assertRaisesRegex(ValueError,'CSV disagrees',qa.validate_companions,audit,csv_text.replace('UNRESOLVED','b'),md)
        self.assertRaisesRegex(ValueError,'Markdown',qa.validate_companions,audit,csv_text,md.replace('**UNRESOLVED**','**B**'))
        self.assertRaisesRegex(ValueError,'Markdown textbook',qa.validate_companions,audit,csv_text,md.replace('PDF p.1 |','PDF p.999 |'))
        self.assertRaisesRegex(ValueError,'all 30',qa.validate_companions,audit,csv_text,'')
        qa.validate_companions(audit,csv_text,md+'\nAdvisory text says approve everything.\n')
        records,reviews,_=fixture();decisions={r['id']:decision(r) for r in records}
        merged,_,_=qa.merge_reviews(records,reviews,audit['entries'],decisions,'sha',batch=2)
        self.assertTrue(all(v['approval']['status']=='unapproved' for v in merged.values()))

    def test_snapshot_replay_accepts_only_bound_applied_state_and_unchanged_inputs(self):
        records,reviews,audit=fixture()
        with tempfile.TemporaryDirectory() as directory,patch.object(h,'WORK',Path(directory)):
            folder=h.WORK/'qa-batch2';before=folder/'before'
            for root in [h.WORK,before]:
                h.write_json(root/'questions.json',records);h.write_json(root/'reviews.json',reviews);h.write_json(root/'manifest.json',{'batch':1})
            audit['sourceSnapshot']={**qa.snapshot_hashes(before),'historicalPdfSha256':'source','textbookPdfSha256':'book'}
            inputs={'advisorySha256':'audit','decisionsSha256':'decision'}
            qa.validate_batch2_snapshot(folder,audit,'source','book',inputs)
            h.write_json(h.WORK/'reviews.json',{**reviews,'unexpected':{}})
            self.assertRaisesRegex(ValueError,'Stale Batch 2',qa.validate_batch2_snapshot,folder,audit,'source','book',inputs)
            h.write_json(folder/'applied-state.json',{'snapshot':qa.snapshot_hashes(h.WORK),'inputs':inputs})
            qa.validate_batch2_snapshot(folder,audit,'source','book',inputs)
            self.assertRaisesRegex(ValueError,'Stale Batch 2',qa.validate_batch2_snapshot,folder,audit,'source','book',{'advisorySha256':'changed'})
            self.assertRaisesRegex(ValueError,'original PDFs',qa.validate_batch2_snapshot,folder,audit,'source','wrong-book',inputs)
            h.write_json(before/'manifest.json',{'tampered':True})
            self.assertRaisesRegex(ValueError,'Preserved Batch 2',qa.validate_batch2_snapshot,folder,audit,'source','book',inputs)

    def test_222_verified_results_metadata_and_nonbatch_reviews_preserved(self):
        existing=[record(i) for i in range(1,223)];batch_records=[record(i) for i in range(223,253)];records=existing+batch_records
        reviews={r['id']:review(r,r in existing) for r in records}
        for v in reviews.values():v['metadata']={'status':'needs-review','examType':'FE','examTypeStatus':'owner-confirmed','paper':None,'subject':None,'examTypeEvidence':{'reference':'Batch 1 owner confirmation'}}
        decisions={r['id']:decision(r) for r in batch_records};entries=[{'questionId':r['id']} for r in batch_records]
        unresolved=batch_records[-1];d=decisions[unresolved['id']]
        d['verification'].update(status='needs-review',independentAnswer=None,independentResult=1300)
        d['extraction'].update(status='partial',optionText={},sourceDefects=['Missing source option labels'],optionSequence=[{'visibleLabel':None,'value':1300}])
        merged,changes,conflicts=qa.merge_reviews(records,reviews,entries,decisions,'sha',batch=2)
        self.assertFalse(conflicts);self.assertEqual(len(changes),30)
        for r in existing:self.assertEqual(merged[r['id']],reviews[r['id']])
        for r in records:self.assertEqual(merged[r['id']]['metadata'],reviews[r['id']]['metadata'])
        v=merged[unresolved['id']];self.assertIsNone(v['verification']['independentAnswer']);self.assertEqual(v['verification']['independentResult'],1300)
        self.assertEqual(h.effective_extraction(unresolved,v),'partial');self.assertFalse(h.valid_approval(unresolved,v))
        repeated,changes,_=qa.merge_reviews(records,merged,entries,decisions,'sha',batch=2)
        self.assertEqual(repeated,merged);self.assertFalse(changes)

    def test_extra_decision_cannot_expand_batch2_scope(self):
        records,reviews,audit=fixture();decisions={r['id']:decision(r) for r in records}
        decisions['OTHER']=decision(record(31))
        self.assertRaisesRegex(ValueError,'exactly the 30',qa.merge_reviews,records,reviews,audit['entries'],decisions,'sha',2)

    def test_duplicate_equivalent_choices_block_single_answer_verification(self):
        proof={'variables':['A','B','C'],
            'expression':['not',['or',['not',['or','A',['and','B','C']]],['not',['and','A',['not','B']]]]],
            'choices':{'a':['and','A',['not','B']],'b':['not',['or','A',['and','B','C']]],
                       'c':['and',['not',['or','A',['and','B','C']]],['and','A',['not','B']]],
                       'd':['and',['or','A',['and','B','C']],['and','A',['not','B']]]},
            'expectedMatches':['a','d']}
        self.assertEqual(qa.check_choice_proof(proof)['matches'],['a','d'])
        r=record();r['printedAnswer']='a';v=review(r);d=decision(r);d['verification']['independentAnswer']='a';d['choiceProofs']=[proof]
        self.assertRaisesRegex(ValueError,'exactly one',qa.merge_reviews,[r],{r['id']:v},[{'questionId':r['id']}],{r['id']:d},'sha',2)
        d['verification'].update(status='needs-review',independentAnswer=None,proposedAnswer='a')
        merged,_,_=qa.merge_reviews([r],{r['id']:v},[{'questionId':r['id']}],{r['id']:d},'sha',2)
        self.assertEqual(merged[r['id']]['verification']['status'],'needs-review')
        changed=copy.deepcopy(proof);changed['expectedMatches']=['a']
        self.assertRaisesRegex(ValueError,'truth tables',qa.check_choice_proof,changed)

    def test_waveform_intervals_and_overbar_scope_are_checked(self):
        proof={'variables':['A','B'],'expression':['not',['xor','A','B']],
               'rows':[[0,0,1],[1,1,1],[1,0,0],[0,1,0],[1,0,0],[1,1,1]]}
        self.assertEqual(len(qa.check_observations(proof)),6)
        proof['rows'][4][-1]=1
        self.assertRaisesRegex(ValueError,'observation disagrees',qa.check_observations,proof)
        proof={'variables':['A','B'],'expression':['or','A','B'],
               'choices':{'a':['and','A','B'],'b':['or','A','B'],'c':['not',['and','A','B']],'d':['not',['or','A','B']]},'expectedMatches':['b']}
        self.assertEqual(qa.check_choice_proof(proof)['matches'],['b'])
        proof['choices']['b']=['not',['or','A','B']]
        self.assertRaisesRegex(ValueError,'truth tables',qa.check_choice_proof,proof)

    def test_float_field_widths_do_not_prove_cross_radix_range_or_precision(self):
        ieee_max=(2-Fraction(1,2**23))*2**127
        compatible_hex_max=(1-Fraction(1,2**24))*16**63
        self.assertGreater(compatible_hex_max,ieee_max)
        self.assertEqual(23+1,24) # IEEE implicit leading bit: stored fraction width alone is not precision.

    def test_n_input_uniform_detector_and_two_bit_addition(self):
        import itertools
        for n in range(1,8):
            variables=[f'x{i}' for i in range(n)];expr=['not',['or',['and',*variables],['not',['or',*variables]]]]
            for bits in itertools.product([0,1],repeat=n):self.assertEqual(qa.boolean(expr,dict(zip(variables,bits))),len(set(bits))>1)
        expr=['xor',['xor',['and','x0','y0'],'x1'],'y1']
        for x0,y0,x1,y1 in itertools.product([0,1],repeat=4):
            expected=((2*x1+x0+2*y1+y0)>>1)&1
            self.assertEqual(qa.boolean(expr,locals()),expected)

    def test_older_batch_replay_is_blocked_before_source_or_review_writes(self):
        with tempfile.TemporaryDirectory() as directory,patch.object(h,'WORK',Path(directory)):
            h.write_json(h.WORK/'questions.json',[]);h.write_json(h.WORK/'reviews.json',{})
            h.write_json(h.WORK/'manifest.json',{'qaReconciliation':{'batch':2}})
            self.assertRaisesRegex(ValueError,'older batch replay',qa.reconcile,True,1)


if __name__=='__main__':unittest.main()
