import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import fitz

spec=importlib.util.spec_from_file_location('historical',Path(__file__).resolve().parents[1]/'scripts/historical_questions.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)

def question_page(pdf,question=True,key='b',date=True):
    p=pdf.new_page()
    p.insert_text((50,60),'Q1. What is the result?' if question else 'Continuation of question')
    p.insert_text((50,100),'a) One\nb) Two\nc) Three\nd) Four')
    p.draw_line((60,180),(180,200));p.draw_rect(fitz.Rect(50,170,190,210))
    if key:p.insert_text((50,780),f'Ans: ({key})')
    if date:p.insert_text((450,800),'2020 April')
    return p

class HistoricalImportTests(unittest.TestCase):
    def test_complete_source_crop_includes_vector_and_excludes_key(self):
        with fitz.open() as pdf:
            p=question_page(pdf);page=h.describe_page(p,1);r=h.assemble_questions([page],'sha')[0]
            self.assertEqual(r['options']['d'],'Four');self.assertEqual(r['printedAnswer'],'b')
            self.assertGreater(page['bbox'][3],210);self.assertLess(page['bbox'][3],780)
            self.assertEqual(r['extractionQuality'],'complete')
    def test_missing_key_and_multi_page_are_not_silently_dropped(self):
        with fitz.open() as pdf:
            p=question_page(pdf,key=None);a=h.describe_page(p,1)
            self.assertIn('missing-or-conflicting-answer-key',h.assemble_questions([a],'sha')[0]['issues'])
            b=h.describe_page(question_page(pdf,question=False),2)
            rows=h.assemble_questions([a,b],'sha');self.assertEqual(len(rows),1)
            self.assertEqual(rows[0]['sourceReferences'][0]['pages'],[1,2]);self.assertEqual(len(rows[0]['regions']),2)
    def test_exact_occurrence_duplicates_merge_but_conflicts_are_flagged(self):
        with fitz.open() as pdf:
            a=h.describe_page(question_page(pdf),1);b={**a,'pdfPage':2}
            rows=h.assemble_questions([a,b],'sha');self.assertEqual(len(rows),1)
            self.assertEqual(len(rows[0]['sourceReferences']),2)
            conflict=h.assemble_questions([a,{**b,'answerKeys':['c']}],'sha')[0]
            self.assertIn('duplicate-answer-key-conflict',conflict['issues'])
            self.assertEqual(conflict['sourceReferences'][1]['printedAnswer'],'c')
            rows=h.assemble_questions([a,{**b,'body':b['body']+'Changed'}],'sha')
            self.assertEqual(len(rows),2)
            self.assertTrue(all('ambiguous-examination-occurrence' in r['issues'] for r in rows))
    def test_idempotency_checksum_reprocessing_and_lossless_assets(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);source=root/'Technology-01.pdf';work=root/'private'
            with fitz.open() as pdf:question_page(pdf);pdf.save(source)
            with patch.object(h,'WORK',work),patch.object(h,'SOURCE',source):
                first=h.extract(source);files={p.relative_to(work):p.read_bytes() for p in work.rglob('*') if p.is_file()}
                self.assertEqual(h.extract(source),first)
                self.assertEqual(files,{p.relative_to(work):p.read_bytes() for p in work.rglob('*') if p.is_file()})
                h.verify_source();rows=h.read_json(work/'questions.json');h.verify_assets(rows)
                self.assertEqual(rows[0]['images'][0]['dpi'],300)
                with patch.object(h,'VERSION','improved'):
                    self.assertRaisesRegex(ValueError,'Importer changed',h.verify_source)
                    second=h.extract(source);self.assertNotEqual(first['importerFingerprint'],second['importerFingerprint'])
                source.write_bytes(source.read_bytes()+b'\n% changed source\n')
                self.assertRaisesRegex(ValueError,'Source changed',h.verify_source)
                changed=h.extract(source);self.assertNotEqual(first['sourceSha256'],changed['sourceSha256'])
                image=work/rows[0]['images'][0]['path'];image.write_bytes(b'changed')
                self.assertRaises(ValueError,h.verify_assets,rows)
    def test_printed_answer_match_is_not_verification_or_approval(self):
        r={'contentSha256':'sha','printedAnswer':'b','extractionQuality':'complete','images':[{'sha256':'image'}]}
        v={'contentSha256':'sha','verification':{'status':'verified','independentAnswer':'b'}}
        self.assertFalse(h.valid_verification(r,v));self.assertFalse(h.valid_approval(r,v))
        v['verification'].update(method='calculation',evidence=['1+1=2'],reasoning='Count one and one')
        v['explanation']={'summary':'Two','steps':['1+1=2'],'takeaway':'Add both inputs'}
        self.assertTrue(h.valid_verification(r,v));self.assertFalse(h.valid_approval(r,v))
        v['mapping']={'status':'verified','chapterId':'fe-v1-ch01','sectionId':'s','subsectionId':'sub','conceptId':'logic','headingNumber':'3-4-1','evidence':'page61'}
        v['extraction']={'status':'complete','reviewedImages':['image'],'imageDescription':'Question and all four options','optionText':{k:k for k in 'abcd'}}
        v['metadata']={'status':'verified','examType':'FE','paper':'AM','subject':'A','evidence':'owner supplied original exam cover'}
        v['approval']={'status':'approved','reviewer':'owner','fingerprint':h.publication_fingerprint(r,v)}
        self.assertTrue(h.valid_approval(r,v))
        v['explanation']['summary']='Changed';self.assertFalse(h.valid_approval(r,v))
    def test_other_sources_and_multiple_starts_fail_closed(self):
        self.assertRaisesRegex(ValueError,'Only Technology-01',h.extract,Path('Technology-02.pdf'))
        with fitz.open() as pdf:
            p=question_page(pdf);p.insert_text((50,300),'Q2. Another question')
            self.assertRaisesRegex(ValueError,'multiple questions',h.describe_page,p,1)
    def test_published_practice_authority_survives_a_disagreeing_pdf_key(self):
        record={'year':2020,'season':'S','number':1,'images':[{'sha256':'same'}],'printedAnswer':'b'}
        review={'metadata':{'status':'verified','examType':'FE','paper':'AM'}}
        q={'id':'canonical-practice','is_published':True,'year':2020,'season':'S','number':1,'paper':'AM','correctAnswer':'a','image':{'sha256':'same'}}
        with patch.object(h,'_PRACTICE_SNAPSHOT',[q]):
            self.assertEqual(h.authoritative_duplicate(record,review)['correctAnswer'],'a')
            self.assertIsNone(h.authoritative_duplicate({**record,'year':2019},review))
        with patch.object(h,'_PRACTICE_SNAPSHOT',[q,{**q,'id':'ambiguous'}]):
            self.assertIsNone(h.authoritative_duplicate(record,review))

if __name__=='__main__':unittest.main()
