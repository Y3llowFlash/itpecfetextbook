"""Synthetic owner adjudication regressions; no private artifacts required."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from test_academic_qa import qa,h,record,review


def fixture():
    records=[];reviews={};entries=[]
    for page in range(1,334):
        r=record(page)
        if page in qa.OWNER_SCOPE:r.update(id=qa.OWNER_SCOPE[page][0],printedAnswer=qa.OWNER_SCOPE[page][1])
        records.append(r);v=review(r,page not in qa.OWNER_SCOPE)
        v.update(metadata={'examType':'FE','status':'needs-review'},mapping={'status':'proposed'},classification={'category':'ch1','chapter':1},academicReviews=[{'batch':5}])
        if page==112:v['extraction']={'status':'partial','optionText':{'a':'1201'},'sourceBinding':qa.extraction_binding(r),'sourceDefects':['Missing labels']}
        reviews[r['id']]=v
        if page not in qa.OWNER_SCOPE:continue
        a={'status':'owner-adjudicated','selectedAnswer':r['printedAnswer'],'originalPrintedAnswer':r['printedAnswer'],
           'priorReviewSha256':qa.object_hash(v),'sourceBinding':{'sourceSha256':'source',**qa.extraction_binding(r)},
           'provenance':{'kind':'explicit-owner-instruction','instructionsSha256':'request','publicationApprovalGranted':False},
           'studentExplanation':{'summary':'Qualified owner selection','steps':['D is also mathematically valid.'] if page==119 else ['Retain qualifications'],'takeaway':'No publication approval'},
           'supportingEvidence':[{'kind':'original-question','pdfPage':page}],
           'gradingEligibility':{'status':'blocked','reason':'Qualified selection','acceptedOptions':['a','d'] if page==119 else [r['printedAnswer']]},
           'publicationReadiness':{'status':'blocked'},'additionalMathematicallyValidAnswers':['d'] if page==119 else [],'editorialReconstructions':[]}
        e={'questionId':r['id'],'pdfPage':page,'ownerAdjudication':a}
        if page==112:
            a['editorialReconstructions']=[{'kind':'missing-option-labels','status':'owner-confirmed'}]
            e['reviewedOptions']={'a':'1201','b':'1300','c':'2200','d':'2300'}
        if page==119:
            e['choiceProof']={'variables':['A','B','C'],'expression':['and','A',['not','B']],
                'choices':{'a':['and','A',['not','B']],'b':'B','c':['not','A'],'d':['and',['or','A',['and','B','C']],['and','A',['not','B']]]},'expectedMatches':['a','d']}
        if page==179:a['editorialReconstructions']=[{'literalSource':'Exclusive-','proposedText':'Exclusive-OR','status':'probable-owner-proposal'}]
        a['fingerprint']=h.adjudication_fingerprint(r,a);entries.append(e)
    return records,reviews,{'entries':entries}


class OwnerAdjudicationTests(unittest.TestCase):
    def test_exact_scope_and_owner_answers_cannot_be_expanded_or_changed(self):
        records,reviews,p=fixture()
        for entries in [p['entries'][:-1],p['entries']+[p['entries'][0]]]:
            self.assertRaisesRegex(ValueError,'exactly the seven',qa.merge_owner_decisions,records,reviews,{'entries':entries},'request')
        for field,value in [('questionId','unrelated'),('pdfPage',109)]:
            bad=copy.deepcopy(p);bad['entries'][0][field]=value
            self.assertRaises(ValueError,qa.merge_owner_decisions,records,reviews,bad,'request')
        p['entries'][0]['ownerAdjudication']['selectedAnswer']='d'
        self.assertRaisesRegex(ValueError,'answer or source-page',qa.merge_owner_decisions,records,reviews,p,'request')

    def test_326_entire_reviews_and_all_sources_metadata_approvals_preserved(self):
        records,reviews,p=fixture();before=copy.deepcopy(records);old=copy.deepcopy(reviews)
        updated,changes=qa.merge_owner_decisions(records,reviews,p,'request')
        self.assertEqual(records,before);self.assertEqual(reviews,old);self.assertEqual(len(changes),7)
        scope={e['questionId'] for e in p['entries']}
        self.assertEqual(sum(h.valid_verification(r,updated[r['id']]) for r in records),326)
        self.assertEqual(sum(h.valid_adjudication(r,updated[r['id']]) for r in records),7)
        for r in records:
            identity=r['id']
            if identity not in scope:self.assertEqual(updated[identity],reviews[identity])
            else:
                self.assertEqual(updated[identity]['ownerAdjudication']['selectedAnswer'],r['printedAnswer'])
                for dimension in ['verification','mapping','metadata','classification','approval','academicReviews']:
                    self.assertEqual(updated[identity][dimension],reviews[identity][dimension])
                self.assertFalse(h.valid_verification(r,updated[identity]));self.assertFalse(h.valid_approval(r,updated[identity]))

    def test_idempotent_replay_no_duplicate_history_or_mutation(self):
        records,reviews,p=fixture();first,changes=qa.merge_owner_decisions(records,reviews,p,'request')
        second,changes=qa.merge_owner_decisions(records,first,p,'request')
        self.assertEqual(second,first);self.assertEqual(changes,[])
        second[next(iter(qa.OWNER_SCOPE.values()))[0]]['explanation']['summary']='Edited'
        self.assertRaisesRegex(ValueError,'stale applied',qa.merge_owner_decisions,records,second,p,'request')

    def test_page112_owner_labels_are_editorial_and_raw_image_unchanged(self):
        records,reviews,p=fixture();updated,_=qa.merge_owner_decisions(records,reviews,p,'request')
        r=next(r for r in records if r['regions'][0]['pdfPage']==112);v=updated[r['id']]
        self.assertEqual(v['extraction']['optionText'],{'a':'1201','b':'1300','c':'2200','d':'2300'})
        self.assertEqual(v['extraction']['editorialTranscription']['literalSourceLabels'],['a'])
        self.assertEqual(v['extraction']['editorialTranscription']['instructionsSha256'],'request')
        self.assertEqual(h.effective_extraction(r,v),'partial');self.assertEqual(r['rawText'],'Original')
        e=next(e for e in p['entries'] if e['pdfPage']==112);e['reviewedOptions']['b']='1201'
        self.assertRaisesRegex(ValueError,'option sequence',qa.merge_owner_decisions,records,reviews,p,'request')

    def test_page119_both_mathematically_valid_options_and_blocker_required(self):
        records,reviews,p=fixture();e=next(e for e in p['entries'] if e['pdfPage']==119)
        self.assertEqual(qa.check_choice_proof(e['choiceProof'])['matches'],['a','d'])
        for field,value in [('additionalMathematicallyValidAnswers',[]),('gradingEligibility',{'status':'blocked','acceptedOptions':['a']})]:
            bad=copy.deepcopy(p);next(e for e in bad['entries'] if e['pdfPage']==119)['ownerAdjudication'][field]=value
            self.assertRaisesRegex(ValueError,'Option D',qa.merge_owner_decisions,records,reviews,bad,'request')
        e['choiceProof']['choices']['d']='C'
        self.assertRaises(ValueError,qa.merge_owner_decisions,records,reviews,p,'request')

    def test_page179_probable_reconstruction_cannot_be_claimed_literal_verified(self):
        records,reviews,p=fixture();e=next(e for e in p['entries'] if e['pdfPage']==179)
        e['ownerAdjudication']['editorialReconstructions'][0]['status']='verified-source-reading'
        self.assertRaisesRegex(ValueError,'probable proposal',qa.merge_owner_decisions,records,reviews,p,'request')

    def test_stale_content_image_source_and_review_fingerprints_fail_closed(self):
        records,reviews,p=fixture()
        for field,value in [('contentSha256','changed'),('images',[{'sha256':'other'}]),('sourceReferences',[{'sha256':'other'}])]:
            rows=copy.deepcopy(records);next(r for r in rows if r['id']==p['entries'][0]['questionId'])[field]=value
            self.assertRaises(ValueError,qa.merge_owner_decisions,rows,reviews,p,'request')
        old=copy.deepcopy(reviews);old[p['entries'][0]['questionId']]['metadata']['paper']='changed'
        self.assertRaisesRegex(ValueError,'prior review',qa.merge_owner_decisions,records,old,p,'request')

    def test_owner_instruction_authority_is_not_publication_approval(self):
        records,reviews,p=fixture()
        self.assertRaisesRegex(ValueError,'instruction binding',qa.merge_owner_decisions,records,reviews,p,'changed-request')
        p['entries'][0]['ownerAdjudication']['provenance']['publicationApprovalGranted']=True
        self.assertRaisesRegex(ValueError,'publication restriction',qa.merge_owner_decisions,records,reviews,p,'request')

    def test_owner_record_cannot_bypass_grading_gate_via_published_authority(self):
        records,reviews,p=fixture();updated,_=qa.merge_owner_decisions(records,reviews,p,'request')
        r=next(r for r in records if r['regions'][0]['pdfPage']==119);v=updated[r['id']]
        with patch.object(h,'authoritative_duplicate',return_value={'correctAnswer':'a'}):
            errors=h.approval_errors(r,v);self.assertTrue(any('grading remains blocked' in e for e in errors))
            v['approval']={'status':'approved','reviewer':'owner','fingerprint':h.publication_fingerprint(r,v)}
            self.assertFalse(h.valid_approval(r,v))

    def test_manifest_separates_academic_unresolved_from_owner_pending(self):
        records,reviews,p=fixture();updated,_=qa.merge_owner_decisions(records,reviews,p,'request')
        with tempfile.TemporaryDirectory() as directory,patch.object(h,'WORK',Path(directory)):
            h.write_json(h.WORK/'reviews.json',updated)
            m=h.manifest_for(records,'source',333)
            self.assertEqual(m['verifiedAnswers'],326);self.assertEqual(m['unresolvedQuestions'],7)
            self.assertEqual(m['ownerAdjudicatedAnswers'],7);self.assertEqual(m['unadjudicatedQuestions'],0)
            self.assertEqual(m['approvedQuestions'],0);self.assertEqual(m['adjudicatedPublicationBlocked'],7)

    def test_snapshot_and_applied_input_bindings(self):
        records,reviews,p=fixture()
        with tempfile.TemporaryDirectory() as directory,patch.object(h,'WORK',Path(directory)):
            folder=h.WORK/'owner-adjudication'
            for root in [h.WORK,folder/'before']:
                for name,value in [('questions',records),('reviews',reviews),('manifest',{})]:h.write_json(root/f'{name}.json',value)
            p['baselineSnapshot']=qa.snapshot_hashes(folder/'before');inputs={'instructionsSha256':'request','decisionsSha256':'d','reviewEngineFingerprint':'engine'}
            qa.validate_owner_snapshot(folder,p,inputs)
            h.write_json(h.WORK/'manifest.json',{'changed':'applied'})
            self.assertRaisesRegex(ValueError,'Stale owner',qa.validate_owner_snapshot,folder,p,inputs)
            h.write_json(folder/'applied-state.json',{'snapshot':qa.snapshot_hashes(h.WORK),'inputs':inputs})
            qa.validate_owner_snapshot(folder,p,inputs)
            for key in inputs:
                self.assertRaisesRegex(ValueError,'Stale owner',qa.validate_owner_snapshot,folder,p,{**inputs,key:'changed'})

    def test_earlier_academic_batches_cannot_erase_adjudication(self):
        with tempfile.TemporaryDirectory() as directory,patch.object(h,'WORK',Path(directory)):
            h.write_json(h.WORK/'questions.json',[]);h.write_json(h.WORK/'reviews.json',{})
            h.write_json(h.WORK/'manifest.json',{'ownerAdjudication':{'questions':7}})
            for batch in range(1,6):self.assertRaisesRegex(ValueError,'academic-batch replay',qa.reconcile,True,batch)


if __name__=='__main__':unittest.main()
