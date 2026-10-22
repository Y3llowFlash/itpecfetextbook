"""Synthetic private-preview scope and non-promotion regressions."""
import copy
import unittest
from unittest.mock import patch
from test_academic_qa import h,qa,record,review,decision
import private_student_preview as p


def fixture():
    records=[];reviews={};inventory=[];rows=[];i=0
    for concept,count in p.COUNTS.items():
        for _ in range(count):
            i+=1;r=record(i);r.update(year=2019,season='A',number=i)
            v=review(r,True);v.update(metadata={'status':'needs-review','paper':None,'subject':None},
                mapping={'status':'verified','conceptId':concept,'headingNumber':'3-4-1','sectionId':'s03','subsectionId':'anchor'},
                extraction={**decision(r)['extraction'],'sourceBinding':qa.extraction_binding(r),'reviewedImages':[r['images'][0]['sha256']]})
            r['images'][0].update(width=600,height=400)
            q={'id':r['id'],'contentSha256':r['contentSha256'],'reviewSha256':qa.object_hash(v),'images':copy.deepcopy(r['images']),
                'priorityAfterMandatoryRepairs':True,'currentMapping':copy.deepcopy(v['mapping']),
                'auditClassification':{'category':'ch1','chapter':1,'placement':'exact','evidence':[{'printedPage':65,'pdfPage':70}]},
                'extraction':{'accessibleReviewComplete':True},'mapping':{'issues':[],'existingConceptReusableInPrinciple':True}}
            row={'canonical_id':r['id'],'historical_pdf_page':str(i),'exam_year':'2019','exam_season':'A','exam_question_number':str(i),
                'book_heading':'3-4-1','concept_id':concept,'book_printed_page':'65','book_physical_page':'70','existing_section_id':'s03','existing_subsection_id':'anchor',
                'priority_status':'private-pilot-candidate-only','publication_approval':'unapproved','paper_metadata':'unknown','subject_metadata':'unknown'}
            records.append(r);reviews[r['id']]=v;inventory.append(q);rows.append(row)
    # Unselected unrelated/disputed records must not be pulled into this bank.
    inventory.append({'id':'DISPUTED-OUTSIDE','priorityAfterMandatoryRepairs':False})
    return records,reviews,inventory,rows


class PrivatePreviewTests(unittest.TestCase):
    def setUp(self):self.records,self.reviews,self.inventory,self.rows=fixture()
    def select(self):return p.select_questions(self.inventory,self.records,self.reviews,self.rows)
    def rebind(self):self.inventory[0]['reviewSha256']=qa.object_hash(self.reviews[self.records[0]['id']])

    def test_exact_36_and_seven_concepts_not_all_candidates(self):
        self.assertEqual(len(self.select()),36)
        self.assertNotIn('DISPUTED-OUTSIDE',[q['id'] for q in self.select()])
        self.assertEqual(len({q['id'] for q in self.select()}),36)
    def test_shortlist_extra_missing_duplicate_or_wrong_id_rejected(self):
        for rows in [self.rows[:-1],self.rows+[self.rows[0]],[self.rows[0]]*36]:
            with self.assertRaisesRegex(ValueError,'exact 36'):p.select_questions(self.inventory,self.records,self.reviews,rows)
        self.rows[0]['canonical_id']='OTHER'
        self.assertRaises(ValueError,self.select)
    def test_extra_priority_candidate_is_not_automatically_included(self):
        self.inventory[-1]['priorityAfterMandatoryRepairs']=True
        self.assertRaisesRegex(ValueError,'exact 36',self.select)
    def test_source_review_or_image_edit_rejects_stale_snapshot(self):
        for key,value in [('contentSha256','changed'),('reviewSha256','changed'),('images',[])]:
            original=self.inventory[0][key];self.inventory[0][key]=value
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,'Stale'):self.select()
            self.inventory[0][key]=original
    def test_owner_disputes_and_unverified_answers_cannot_enter_pilot(self):
        v=self.reviews[self.records[0]['id']]
        v['ownerAdjudication']={'selectedAnswer':'b'};self.rebind()
        self.assertRaisesRegex(ValueError,'Pilot requires',self.select)
        del v['ownerAdjudication'];v['verification']['status']='needs-review';self.rebind()
        self.assertRaisesRegex(ValueError,'Pilot requires',self.select)
    def test_incomplete_accessibility_or_mapping_issue_excludes_association(self):
        for dimension,key,value in [('mapping','issues',['needs-editorial-review']),('mapping','existingConceptReusableInPrinciple',False),('extraction','accessibleReviewComplete',False)]:
            original=self.inventory[0][dimension][key];self.inventory[0][dimension][key]=value
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,'Pilot requires'):self.select()
            self.inventory[0][dimension][key]=original
    def test_no_approval_or_guessed_paper_subject_values(self):
        v=self.reviews[self.records[0]['id']]
        for key,value in [('paper','AM'),('subject','A')]:
            v['metadata'][key]=value;self.rebind()
            with self.assertRaisesRegex(ValueError,'unknown-metadata'):self.select()
            v['metadata'][key]=None
        v['approval']['status']='approved';self.rebind()
        self.assertRaisesRegex(ValueError,'approval',self.select)
    def test_advisory_dates_source_pages_sections_and_metadata_must_match(self):
        for key in ['historical_pdf_page','exam_year','exam_season','exam_question_number','book_heading','concept_id','book_printed_page','book_physical_page','existing_section_id','existing_subsection_id','paper_metadata','subject_metadata','publication_approval']:
            old=self.rows[0][key];self.rows[0][key]='invented'
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,'Shortlist'):self.select()
            self.rows[0][key]=old
    def test_projection_is_unpublished_preserves_exact_verified_explanations(self):
        selected=self.select();before=copy.deepcopy((self.records,self.reviews,self.inventory,self.rows))
        concepts=[{'id':c,'questionIds':['PUBLIC-EXAMPLE'],'videos':[{'url':'https://example.com'}]} for c in p.COUNTS]
        with patch.object(p,'association',side_effect=lambda q,c:{'id':q['id'],'concept':c['id']}):
            bank,answers,scoped,links=p.project(selected,self.records,self.reviews,concepts)
            repeated=p.project(selected,self.records,self.reviews,concepts)
        self.assertEqual((bank,answers,scoped,links),repeated)
        self.assertEqual((self.records,self.reviews,self.inventory,self.rows),before)
        self.assertEqual(len(bank),36);self.assertEqual(len(answers),36);self.assertEqual(len(links),36)
        for q,e in zip(bank,answers):
            self.assertFalse(q['is_published']);self.assertTrue(q['privatePreview'])
            self.assertIsNone(q['paper']);self.assertIsNone(q['subject'])
            self.assertEqual(q['review']['publicationStatus'],'unapproved')
            original=self.reviews[q['id']]['explanation']
            for key in ['summary','steps','takeaway']:self.assertEqual(e[key],original[key])
            self.assertTrue(q['image']['src'].startswith('/__pilot/images/'))
        self.assertEqual(sum(len(c['questionIds']) for c in scoped),36)
        self.assertTrue(all(c['videos']==[] for c in scoped))

    def test_editorial_findings_are_pending_source_bound_and_cannot_expand_scope(self):
        selected=self.select();r=self.records[0];v=self.reviews[r['id']]
        f={'questionId':r['id'],'contentSha256':r['contentSha256'],'reviewSha256':qa.object_hash(v),'imageSha256':r['images'][0]['sha256'],
           'finding':'Diagram labels leaked into accessible options','studentNotice':'Use original image; transcript awaits editorial review.','status':'editorial-review-pending'}
        before=copy.deepcopy(self.reviews)
        self.assertEqual(p.validated_findings(selected,self.records,self.reviews,[f]),[f])
        for key in ['questionId','contentSha256','reviewSha256','imageSha256','status']:
            bad={**f,key:'stale'}
            with self.subTest(key=key),self.assertRaises(ValueError):p.validated_findings(selected,self.records,self.reviews,[bad])
        self.assertEqual(self.reviews,before)
        with patch.object(h,'read_json',return_value=None):
            self.assertRaisesRegex(ValueError,'editorial findings input',p.validated_findings,selected,self.records,self.reviews)


if __name__=='__main__':unittest.main()
