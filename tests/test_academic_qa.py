"""Synthetic source/reconciliation regressions. No private question text is required."""
import copy
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import fitz

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import academic_qa as qa
from test_historical_questions import question_page
h=qa.h


def record(index=1):
    return {'id':f'SYNTHETIC-{index}','contentSha256':h.digest(b'Original'),
            'rawText':'Original','printedAnswer':'b','extractionQuality':'complete',
            'images':[{'path':f'images/{index}.webp','sha256':f'image-{index}','pdfPage':index}],
            'regions':[{'pdfPage':index,'bbox':[0,0,100,100]}],
            'sourceReferences':[{'sha256':'source'}]}


def review(r,verified=False):
    return {'contentSha256':r['contentSha256'],
            'verification':{'status':'verified' if verified else 'needs-review','independentAnswer':'b',
                            'method':'calculation','evidence':['1+1=2'],'reasoning':'Count two units'},
            'explanation':{'summary':'Two','steps':['1+1=2'],'takeaway':'Add the inputs'},
            'approval':{'status':'unapproved'}}


def decision(r):
    v=review(r,True)
    return {'contentSha256':r['contentSha256'],'sourceChecked':True,
            'imageHashes':[a['sha256'] for a in r['images']],
            'verification':v['verification'],'explanation':v['explanation'],
            'classification':{'category':'ch1','chapter':1},
            'extraction':{'status':'complete','imageDescription':'Synthetic four choices',
                          'optionText':dict(zip('abcd',['One','Two','Three','Four']))}}


class AcademicReconciliationTests(unittest.TestCase):
    def advisory(self):
        records=[record(i) for i in range(1,31)]
        audit={'schema':'itpec-academic-audit-proposals-v1-with-image-addendum','questionCount':30,
               'entries':[{'questionId':r['id'],'questionContentSha256':r['contentSha256'],
                           'sourceSha256':'source','pdfPage':r['regions'][0]['pdfPage']} for r in records]}
        addendum={'schema':'itpec-academic-image-audit-addendum-v1','visualFindings':[
            {'questionId':records[0]['id'],'pdfPage':1,'imageFile':'images/1.webp','imageSha256':'image-1'}]}
        return records,audit,addendum

    def test_advisory_identity_hashes_and_duplicate_rejection(self):
        records,audit,addendum=self.advisory()
        self.assertEqual(len(qa.validate_proposals(records,audit,addendum,'source')),30)
        for field,value in [('questionId','missing'),('sourceSha256','wrong'),
                            ('questionContentSha256','stale'),('pdfPage',999)]:
            changed=copy.deepcopy(audit);changed['entries'][0][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):
                qa.validate_proposals(records,changed,addendum,'source')
        changed=copy.deepcopy(audit);changed['entries'][1]=changed['entries'][0]
        self.assertRaises(ValueError,qa.validate_proposals,records,changed,addendum,'source')
        records[0]['rawText']='Changed source text'
        self.assertRaisesRegex(ValueError,'transcript checksum',qa.validate_proposals,records,audit,addendum,'source')

    def test_visual_history_accepts_known_original_but_rejects_fabricated_hash(self):
        records,audit,addendum=self.advisory();r=records[0]
        r['imageHistory']=[{'images':copy.deepcopy(r['images'])}];r['images'][0]['sha256']='new-reviewed'
        qa.validate_proposals(records,audit,addendum,'source')
        addendum['visualFindings'][0]['imageSha256']='invented'
        self.assertRaisesRegex(ValueError,'Stale visual',qa.validate_proposals,records,audit,addendum,'source')

    def test_advisory_cannot_verify_without_separate_current_source_decision(self):
        r=record();v=review(r);e=[{'questionId':r['id'],'proposedAnswer':'b'}]
        self.assertRaisesRegex(ValueError,'separate source-checked',qa.merge_reviews,[r],{r['id']:v},e,{},'batch')
        for field,value in [('sourceChecked',False),('contentSha256','stale'),('imageHashes',['old'])]:
            d=decision(r);d[field]=value
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,'Stale independent decision'):
                qa.merge_reviews([r],{r['id']:v},e,{r['id']:d},'batch')
        self.assertEqual(v,review(r))

    def test_preserves_191_verified_answers_and_explanations_without_granting_approval(self):
        records=[record(i) for i in range(1,192)];reviews={r['id']:review(r,True) for r in records}
        decisions={r['id']:decision(r) for r in records}
        for d in decisions.values():d['explanation']['summary']='New proposed explanation'
        output,changes,conflicts=qa.merge_reviews(records,reviews,[],decisions,'batch')
        self.assertEqual(len(changes),191);self.assertFalse(conflicts)
        for r in records:
            old=reviews[r['id']];new=output[r['id']]
            self.assertEqual(old['verification'],new['verification'])
            self.assertEqual(old['explanation'],new['explanation'])
            self.assertEqual(new['approval']['status'],'unapproved')
            self.assertEqual(new['metadata']['examTypeStatus'],'owner-confirmed')
            self.assertEqual(new['metadata']['status'],'needs-review')
            self.assertIsNone(new['metadata'].get('paper'));self.assertIsNone(new['metadata'].get('subject'))
        repeated,changes,_=qa.merge_reviews(records,output,[],decisions,'batch')
        self.assertEqual(output,repeated);self.assertFalse(changes)

    def test_conflicting_verified_answer_is_retained_and_logged_once(self):
        r=record();v=review(r,True);d=decision(r);d['verification']['independentAnswer']='c'
        merged,_,conflicts=qa.merge_reviews([r],{r['id']:v},[],{r['id']:d},'batch')
        current=merged[r['id']];self.assertEqual(current['verification'],v['verification'])
        self.assertEqual(current['explanation'],v['explanation']);self.assertEqual(len(conflicts),2)
        self.assertEqual(len(current['academicConflicts']),2)
        again,changes,_=qa.merge_reviews([r],merged,[],{r['id']:d},'batch')
        self.assertEqual(again,merged);self.assertFalse(changes)

    def test_stale_review_rejected_and_existing_approval_invalidated(self):
        r=record();v=review(r);v['contentSha256']='stale'
        self.assertRaisesRegex(ValueError,'Existing review',qa.merge_reviews,[r],{r['id']:v},[],{},'batch')
        v=review(r,True);v['approval']={'status':'approved','fingerprint':h.publication_fingerprint(r,v),'reviewer':'synthetic'}
        merged,_,_=qa.merge_reviews([r],{r['id']:v},[],{},'batch')
        self.assertEqual(merged[r['id']]['approval']['status'],'invalidated')

    def test_all_four_classifications_are_private_and_unknown_category_rejected(self):
        r=record();v=review(r)
        for category in ['ch1','other-vol1','outside-vol1','uncertain']:
            d=decision(r);d['classification']['category']=category
            merged,_,_=qa.merge_reviews([r],{r['id']:v},[],{r['id']:d},'batch')
            self.assertFalse(h.valid_approval(r,merged[r['id']]))
            if category!='ch1':self.assertIn('This question is not classified for Chapter 1 publication',h.approval_errors(r,merged[r['id']]))
        d['classification']['category']='invented'
        self.assertRaisesRegex(ValueError,'classification',qa.merge_reviews,[r],{r['id']:v},[],{r['id']:d},'batch')

    def test_truth_table_enumerates_all_cases_and_rejects_wrong_identity(self):
        proof={'variables':['A','B','C'],'expression':['or',['and','A','C'],['and','B','C']],
               'expected':['and',['or','A','B'],'C']}
        self.assertEqual(len(qa.check_proof(proof)),8)
        proof['expected']=['or','A','B']
        self.assertRaisesRegex(ValueError,'truth table',qa.check_proof,proof)

    def test_partial_raw_review_conflict_and_source_missing_header_regression(self):
        r=record();r['extractionQuality']='partial';v=review(r);v['extraction']=decision(r)['extraction']
        self.assertRaisesRegex(ValueError,'Conflicting extraction',h.validate_review_statuses,[r],{r['id']:v})
        v['extraction'].update(sourceBinding=qa.extraction_binding(r),reviewedImages=['image-1'])
        self.assertEqual(h.effective_extraction(r,v),'complete')
        v['extraction']['sourceDefects']=['Second header missing in original PDF']
        self.assertRaisesRegex(ValueError,'Conflicting extraction',h.validate_review_statuses,[r],{r['id']:v})
        v['extraction']['status']='partial';h.validate_review_statuses([r],{r['id']:v})
        self.assertEqual(h.effective_extraction(r,v),'partial')
        r['extractionQuality']='complete';v['extraction']['status']='complete'
        self.assertEqual(h.effective_extraction(r,v),'partial')

    def test_stale_image_binding_cannot_hide_behind_raw_complete(self):
        r=record();v=review(r);v['extraction']={**decision(r)['extraction'],
            'sourceBinding':{'contentSha256':r['contentSha256'],'images':['stale']},'reviewedImages':['image-1']}
        self.assertEqual(h.effective_extraction(r,v),'partial')
        self.assertRaisesRegex(ValueError,'Conflicting extraction',h.validate_review_statuses,[r],{r['id']:v})

    def test_validated_record_snapshot_rejects_later_metadata_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);source=root/'Technology-01.pdf';source.write_bytes(b'synthetic source')
            with patch.object(h,'WORK',root),patch.object(h,'SOURCE',source):
                h.write_json(root/'questions.json',[record()])
                h.write_json(root/'manifest.json',{'sourceSha256':h.digest(source.read_bytes()),
                    'importerFingerprint':h.processing_fingerprint(),
                    'recordsSha256':h.digest((root/'questions.json').read_bytes())})
                h.verify_source();h.write_json(root/'questions.json',[{**record(),'paper':'invented'}])
                self.assertRaisesRegex(ValueError,'snapshot changed',h.verify_source)
    def test_manifest_and_gallery_share_effective_status_without_rewriting_unchanged_gallery(self):
        with tempfile.TemporaryDirectory() as directory,patch.object(h,'WORK',Path(directory)):
            r=record();r.update(extractionQuality='partial',issues=[],sourceReferences=[{'pages':[1]}])
            v=review(r);v['extraction']={**decision(r)['extraction'],'sourceBinding':qa.extraction_binding(r),'reviewedImages':['image-1']}
            h.write_json(h.WORK/'reviews.json',{r['id']:v})
            self.assertEqual(h.manifest_for([r],'sha',1)['extractionQuality'],{'complete':1})
            self.assertEqual(h.manifest_for([r],'sha',1)['rawExtractionQuality'],{'partial':1})
            h.write_review_gallery([r]);target=h.WORK/'index.html';stamp=target.stat().st_mtime_ns
            self.assertIn('partial/complete',target.read_text('utf8'))
            h.write_review_gallery([r]);self.assertEqual(target.stat().st_mtime_ns,stamp)

    def test_horizontal_vertical_wires_recrop_and_source_pixel_geometry_validation(self):
        with tempfile.TemporaryDirectory() as directory,patch.object(h,'WORK',Path(directory)):
            (h.WORK/'images').mkdir()
            with fitz.open() as pdf:
                for _ in range(44):pdf.new_page()
                page=question_page(pdf)
                page.draw_line((100,200),(550,200));page.draw_line((550,200),(550,350))
                desc=h.describe_page(page,45)
                self.assertGreater(desc['bbox'][2],550);self.assertGreater(desc['bbox'][3],350)
                r=h.assemble_questions([desc],'sha')[0]
                r['regions'][0]['bbox'][2:]=[200,220]
                h.render_crops(pdf,[r])
                self.assertRaisesRegex(ValueError,'Incomplete vector crop',qa.validate_source_images,[r],pdf)
                self.assertTrue(qa.repair_crop(r,page));self.assertFalse(qa.repair_crop(r,page))
                self.assertEqual(qa.validate_source_images([r],pdf),1)
                r['images'][0]['width']+=1
                self.assertRaisesRegex(ValueError,'metadata differ',qa.validate_source_images,[r],pdf)
                r['images'][0]['width']-=1
                r['images'][0]['pixelBox'][2]-=1
                self.assertRaisesRegex(ValueError,'crop geometry',qa.validate_source_images,[r],pdf)
                r['regions'][0]['pdfPage']=44
                self.assertRaisesRegex(ValueError,'only authorizes',qa.repair_crop,r,pdf[43])


if __name__=='__main__':unittest.main()
