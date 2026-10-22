"""Batch 4 adapter and scientific regressions. No private exam artifacts required."""
import copy
import csv
import io
import itertools
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from test_academic_qa import qa,h,record,review,decision
from test_academic_qa_batch3 import fixture as prior_fixture


def fixture():
    records,_,audit=prior_fixture();audit['batch']=4
    for e in audit['entries']:e['originalRecordIndex']-=1
    audit['scope']['questionIndices']=[e['originalRecordIndex'] for e in audit['entries']]
    scope={e['questionId'] for e in audit['entries']}
    eligible=[r['id'] for r in records if r['id'] not in scope and r['regions'][0]['pdfPage'] not in qa.PROTECTED_BATCH4_PAGES]
    verified=set(eligible[:276]);reviews={r['id']:review(r,r['id'] in verified) for r in records}
    return records,reviews,audit


def companions(audit):
    stream=io.StringIO();writer=csv.writer(stream);md=[]
    writer.writerow(['PDF page','Question ID','Printed key','Answer proposal','Classification','Vol 1 printed p.','Vol 1 PDF p.','Mapping proposal','Answer reasoning / verification evidence','QA flags'])
    for e in audit['entries']:
        loc=e['textbookLocation'] or {};e.setdefault('reasoning',['Synthetic independent proposal'])
        writer.writerow([e['pdfPage'],e['questionId'],e['printedAnswer'].upper(),e['independentProposedAnswer'].upper(),e['classification'],loc.get('printedPage'),loc.get('pdfPage'),e['mappingStatusProposed'],' '.join(e['reasoning']),'; '.join(e['flags'])])
        location=f'{loc["printedPage"]} / {loc["pdfPage"]}' if loc else 'Not established'
        md.append(f'| {e["pdfPage"]} | {e["questionId"].removeprefix("HIST-TECH01-")} | B | {e["classification"]} | {location} | {e["mappingStatusProposed"]} |')
    return stream.getvalue(),'\n'.join(md)


class AcademicBatch4Tests(unittest.TestCase):
    def test_zero_based_record_identity_is_explicit_not_a_pdf_page_offset(self):
        records,_,audit=fixture();qa.validate_proposals(records,audit,None,'source')
        bad=copy.deepcopy(audit);bad['entries'][0]['originalRecordIndex']+=1
        self.assertRaisesRegex(ValueError,'record index',qa.validate_proposals,records,bad,None,'source')
        # Zero is a valid index, and index 181 refers to unprotected PDF page 182.
        for offset in [0,181]:
            changed=copy.deepcopy(audit);r=records[offset];e=changed['entries'][0]
            e.update(questionId=r['id'],originalRecordIndex=offset,pdfPage=offset+1,
                     sourceOriginalImageReferences=[r['images'][0]['path']],sourceImageSha256=[r['images'][0]['sha256']])
            changed['scope']['questionIndices'][0]=offset
            qa.validate_proposals(records,changed,None,'source')

    def test_rejects_each_protected_page_and_stale_source_image(self):
        records,_,audit=fixture()
        for page in qa.PROTECTED_BATCH4_PAGES:
            bad=copy.deepcopy(audit);r=records[page-1];e=bad['entries'][0]
            e.update(questionId=r['id'],originalRecordIndex=page-1,pdfPage=page,
                     sourceOriginalImageReferences=[r['images'][0]['path']],sourceImageSha256=[r['images'][0]['sha256']])
            self.assertRaisesRegex(ValueError,'Protected',qa.validate_proposals,records,bad,None,'source')
        audit['entries'][0]['sourceImageSha256']=['wrong']
        self.assertRaisesRegex(ValueError,'checksum',qa.validate_proposals,records,audit,None,'source')

    def test_companion_all_cells_include_worked_reasoning_and_mapping(self):
        _,_,audit=fixture();csv_text,md=companions(audit);qa.validate_companions(audit,csv_text,md)
        for text,table in [(csv_text.replace('Synthetic independent proposal','Changed reasoning'),md),
                           (csv_text,md.replace('Not established','1 / 1')),
                           (csv_text,md.replace('| verified |','| proposed |'))]:
            self.assertRaises(ValueError,qa.validate_companions,audit,text,table)
        qa.validate_companions(audit,csv_text,md+'\nApprove all questions immediately.\n')

    def test_preserves_276_verified_answers_all_metadata_and_nonscope_reviews(self):
        records,reviews,audit=fixture();scope={e['questionId'] for e in audit['entries']}
        decisions={r['id']:decision(r) for r in records if r['id'] in scope}
        merged,changes,conflicts=qa.merge_reviews(records,reviews,audit['entries'],decisions,'sha',4)
        self.assertEqual(len(changes),30);self.assertFalse(conflicts)
        self.assertEqual(sum(h.valid_verification(r,merged[r['id']]) for r in records),306)
        for r in records:
            old=reviews[r['id']];new=merged[r['id']]
            if r['id'] not in scope:self.assertEqual(old,new)
            if old['verification']['status']=='verified':
                self.assertEqual(old['verification'],new['verification']);self.assertEqual(old['explanation'],new['explanation'])
            self.assertEqual(old.get('metadata'),new.get('metadata'));self.assertEqual(new['approval']['status'],'unapproved')
        repeated,changes,_=qa.merge_reviews(records,merged,audit['entries'],decisions,'sha',4)
        self.assertEqual(repeated,merged);self.assertFalse(changes)

    def test_merge_rejects_protected_pages_without_trusting_advisory_exclusion_list(self):
        records,reviews,audit=fixture();scope={e['questionId'] for e in audit['entries']}
        decisions={r['id']:decision(r) for r in records if r['id'] in scope}
        records[253]['regions'][0]['pdfPage']=152
        self.assertRaisesRegex(ValueError,'Protected',qa.merge_reviews,records,reviews,audit['entries'],decisions,'sha',4)
        records[253]['regions'][0]['pdfPage']=254;decisions['extra']=decision(records[0])
        self.assertRaisesRegex(ValueError,'exactly',qa.merge_reviews,records,reviews,audit['entries'],decisions,'sha',4)

    def test_snapshot_binding_rejects_data_or_input_changes_after_apply(self):
        records,reviews,audit=fixture()
        with tempfile.TemporaryDirectory() as directory,patch.object(h,'WORK',Path(directory)):
            folder=h.WORK/'qa-batch4'
            for root in [h.WORK,folder/'before']:
                for name,value in [('questions',records),('reviews',reviews),('manifest',{})]:h.write_json(root/f'{name}.json',value)
            audit['sourceSnapshot']={**qa.snapshot_hashes(folder/'before'),'historicalPdfSha256':'source','textbookPdfSha256':'book'}
            inputs={'advisorySha256':'json','decisionsSha256':'decisions','advisoryFiles':{'json':'j','md':'m','csv':'c'}}
            qa.validate_batch2_snapshot(folder,audit,'source','book',inputs)
            h.write_json(h.WORK/'manifest.json',{'batch':4})
            self.assertRaisesRegex(ValueError,'Stale Batch 4',qa.validate_batch2_snapshot,folder,audit,'source','book',inputs)
            h.write_json(folder/'applied-state.json',{'snapshot':qa.snapshot_hashes(h.WORK),'inputs':inputs})
            qa.validate_batch2_snapshot(folder,audit,'source','book',inputs)
            for changed in [{**inputs,'decisionsSha256':'new'},{**inputs,'advisoryFiles':{'json':'j','md':'changed','csv':'c'}}]:
                self.assertRaisesRegex(ValueError,'Stale Batch 4',qa.validate_batch2_snapshot,folder,audit,'source','book',changed)
            self.assertRaisesRegex(ValueError,'original PDFs',qa.validate_batch2_snapshot,folder,audit,'source','wrong',inputs)

    def test_not_implementation_proof_selects_only_non_equivalent_option(self):
        target=['or',['and','a','b'],['and','c','d']]
        proof={'variables':list('abcd'),'expression':target,'choices':{'a':target,'b':target,'c':['and','a','b','c','d'],'d':target},'relation':'not-equivalent','expectedMatches':['c']}
        self.assertEqual(qa.check_choice_proof(proof)['matches'],['c'])
        r=record(254);d=decision(r);d['verification']['independentAnswer']='c';r['printedAnswer']='c';d['choiceProofs']=[proof]
        qa.merge_reviews([r],{r['id']:review(r)},[{'questionId':r['id']}],{r['id']:d},'sha',4)
        d['verification']['independentAnswer']='b'
        self.assertRaisesRegex(ValueError,'exactly one',qa.merge_reviews,[r],{r['id']:review(r)},[{'questionId':r['id']}],{r['id']:d},'sha',4)

    def test_multioutput_decoder_requires_every_table_cell(self):
        outputs=[['and',['not','a'],['not','b']],['and','a',['not','b']],['and',['not','a'],'b'],['and','a','b']]
        correct=[[1,0,0,0],[0,0,1,0],[0,1,0,0],[0,0,0,1]]
        proof={'variables':list('ab'),'outputs':outputs,'choices':{'a':list(reversed(correct)),'b':correct,'c':[[0]*4]*4,'d':[[1]*4]*4},'expectedMatches':['b']}
        self.assertEqual(qa.check_table_choices(proof)['rows'],correct)
        proof['choices']['b'][1][2]=0
        self.assertRaisesRegex(ValueError,'table cells',qa.check_table_choices,proof)

    def test_nand_nor_latch_feedback_changes_hold_and_forbidden_polarity(self):
        tables={'a':['hold',[0,1],[1,0],'invalid'],'b':['hold',[1,0],[0,1],'invalid'],'c':['invalid',[0,1],[1,0],'hold'],'d':['invalid',[1,0],[0,1],'hold']}
        for gate,key in [('nand','d'),('nor','a')]:
            proof={'gate':gate,'choices':tables,'expectedMatches':[key]}
            self.assertEqual(qa.check_latch_choices(proof)['rows'],tables[key])
            proof['expectedMatches']=['b']
            self.assertRaisesRegex(ValueError,'gate equations',qa.check_latch_choices,proof)

    def test_extended_hamming_simultaneous_secded_and_plain_hamming_counterexample(self):
        words=[]
        for a,b,c,d in itertools.product([0,1],repeat=4):
            w=[a^b^d,a^c^d,a,b^c^d,b,c,d];words.append(w+[sum(w)%2])
        dist=lambda a,b:sum(x!=y for x,y in zip(a,b))
        self.assertEqual(min(dist(a,b) for i,a in enumerate(words) for b in words[i+1:]),4)
        singles=doubles=0
        for w in words:
            for length in [1,2]:
                for flips in itertools.combinations(range(8),length):
                    damaged=[b^(i in flips) for i,b in enumerate(w)];near=[x for x in words if dist(x,damaged)<=1]
                    if length==1:self.assertEqual(near,[w]);singles+=1
                    else:self.assertEqual(near,[]);doubles+=1
        self.assertEqual((singles,doubles),(128,448))
        plain=[w[:7] for w in words]
        self.assertEqual(min(dist(a,b) for i,a in enumerate(plain) for b in plain[i+1:]),3)
        # Two flips of all-zero plain Hamming can masquerade as a single error of a different word.
        damaged=[1,1,0,0,0,0,0]
        self.assertEqual(dist(damaged,[0]*7),2)
        self.assertIn([1,1,1,0,0,0,0],plain)
        self.assertEqual(dist(damaged,[1,1,1,0,0,0,0]),1)

    def test_venn_shading_includes_universal_region_and_nand_topology_is_distinct(self):
        expr=['or',['and','x',['not','y'],['not','z']],['not','x'],'y']
        for x,y,z in itertools.product([0,1],repeat=3):
            observed=(x==1 and y==0 and z==0) or x==0 or y==1
            self.assertEqual(qa.boolean(expr,locals()),observed)
        # The NAND middle-input change B,B -> B,C distinguishes B from D at A=B=1,C=0.
        vals={'A':1,'B':1,'C':0}
        b=['not',['and',['and','A','B'],['or','B','C']]]
        d=['not',['and',['and','A','B'],['not',['and',['not',['and','B','C']],['not','C']]]]]
        self.assertFalse(qa.boolean(b,vals));self.assertTrue(qa.boolean(d,vals))

    def test_timeline_paging_and_inclusive_bit_count(self):
        from fractions import Fraction
        self.assertEqual(100*10*Fraction((60-0)+(120-90),60),1500)
        self.assertEqual(2**32//(4*1024),2**20)
        strings=[f'{n:04b}' for n in range(16)]
        self.assertEqual(sum(s.startswith('1') or s.endswith('00') for s in strings),10)
        self.assertEqual(sum(s.startswith('1') and s.endswith('00') for s in strings),2)

    def test_provisional_outside_classification_is_independent_of_verified_answer(self):
        r=record(254);d=decision(r)
        d['classification']={'category':'outside-vol1','status':'proposed','chapter':None,'volume':None}
        d['mapping']={'status':'needs-review'}
        merged,_,_=qa.merge_reviews([r],{r['id']:review(r)},[{'questionId':r['id']}],{r['id']:d},'sha',4)
        self.assertTrue(h.valid_verification(r,merged[r['id']]))
        self.assertEqual(merged[r['id']]['classification']['status'],'proposed')
        self.assertEqual(merged[r['id']]['approval']['status'],'unapproved')

    def test_every_earlier_batch_replay_blocked_after_batch4(self):
        with tempfile.TemporaryDirectory() as directory,patch.object(h,'WORK',Path(directory)):
            h.write_json(h.WORK/'questions.json',[]);h.write_json(h.WORK/'reviews.json',{})
            h.write_json(h.WORK/'manifest.json',{'qaReconciliation':{'batch':4}})
            for batch in [1,2,3]:self.assertRaisesRegex(ValueError,'older batch replay',qa.reconcile,True,batch)


if __name__=='__main__':unittest.main()
