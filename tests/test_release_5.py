"""Release 5 negative regressions; approvals are simulated only in temporary files."""
import copy
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import release_5 as r
import historical_questions as h


class Release5Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (r.FOLDER/'state.json').exists():raise unittest.SkipTest('Private release evidence is local only')
        cls.state,cls.package=r.context()
        cls.before=h.read_json(r.FOLDER/'before-reviews.json')
        cls.manifest=h.read_json(r.FOLDER/'before-manifest.json')
        cls.records=h.read_json(h.WORK/'questions.json')

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=h.ROOT/'.local');self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.work=self.root/'native';self.work.mkdir()
        h.write_json(self.root/'before-reviews.json',self.before);h.write_json(self.root/'before-manifest.json',self.manifest)
        self.reviews=copy.deepcopy(self.before)
        for e in self.package['candidates']:
            self.reviews[e['id']]['approval']={'status':'approved','reviewer':'synthetic owner','fingerprint':e['publicationFingerprint'],**r.authorization_fields(self.state,e)}
        h.write_json(self.work/'questions.json',self.records)
        # Preserve immutable original file bytes (write_json may skip differently encoded input).
        (self.work/'questions.json').write_bytes((h.WORK/'questions.json').read_bytes())
        for target,value in [('FOLDER',self.root)]:self.enterContext(patch.object(r,target,value))
        self.enterContext(patch.object(h,'WORK',self.work))
        self.enterContext(patch.object(r,'context',return_value=(self.state,self.package)))
        self.enterContext(patch.object(h,'verify_source'));self.enterContext(patch.object(h,'verify_assets'))

    def save(self):
        h.write_json(self.work/'reviews.json',self.reviews)
        m=copy.deepcopy(self.manifest);m['approvedQuestions']=196;h.write_json(self.work/'manifest.json',m)

    def test_exact_40_approval_transition_preserves_156_and_137(self):
        self.save();r.verify_native()

    def test_refuses_to_refresh_existing_approvals(self):
        self.save();self.assertRaises(ValueError,r.verify_native,False)

    def test_rejects_missing_or_stale_package_context_and_editorial_binding(self):
        e=next(e for e in self.package['candidates'] if e['highlightIntegration']['newConcept'])
        for field in ['fingerprint','candidateManifestSha256','candidateSetFingerprint','approvalContextFingerprint','highlightEditorialAuthorization','releaseAuthorization']:
            with self.subTest(field=field):
                original=copy.deepcopy(self.reviews[e['id']]['approval']);self.reviews[e['id']]['approval'][field]='stale';self.save()
                self.assertRaises(ValueError,r.verify_native);self.reviews[e['id']]['approval']=original

    def test_rejects_answer_explanation_accessibility_or_mapping_edits(self):
        qid=self.package['questionIds'][0]
        for field in ['verification','explanation','extraction','mapping','metadata']:
            with self.subTest(field=field):
                old=self.reviews[qid][field];self.reviews[qid][field]={'changed':True};self.save()
                self.assertRaises(ValueError,r.verify_native);self.reviews[qid][field]=old

    def test_rejects_changed_prior_approval_and_excluded_approval(self):
        for qid in [self.state['releasedQuestionIds'][0],next(qid for qid in self.reviews if qid not in self.state['releasedQuestionIds']+self.state['questionIds'])]:
            old=self.reviews[qid]['approval'];self.reviews[qid]['approval']={'status':'approved','reviewer':'unauthorized'};self.save()
            self.assertRaises(ValueError,r.verify_native);self.reviews[qid]['approval']=old

    def test_rejects_lost_source_history_or_editorial_receipt(self):
        self.save();m=h.read_json(self.work/'manifest.json');m.pop('editorialReconciliation');h.write_json(self.work/'manifest.json',m)
        self.assertRaises(ValueError,r.verify_native)

    def test_frozen_extraction_summary_survives_generic_approval_regeneration(self):
        self.save();r.verify_native()
        m=h.read_json(self.work/'manifest.json');m['extractionQuality']={'complete':324,'partial':9};h.write_json(self.work/'manifest.json',m)
        self.assertRaisesRegex(ValueError,'outside approval count',r.verify_native)

    def test_all_seven_qualified_records_remain_unapproved_and_unchanged(self):
        protected={110,112,119,152,179,180,181};found=[]
        for record in self.records:
            if record['regions'][0]['pdfPage'] in protected:
                found.append(record['id']);self.assertNotIn(record['id'],self.state['questionIds'])
                self.assertEqual(self.reviews[record['id']],self.before[record['id']]);self.assertEqual(self.reviews[record['id']]['approval']['status'],'unapproved')
        self.assertEqual(len(found),7)

    def test_publication_requires_exact_fresh_successful_dry_run(self):
        self.save()
        result={'dryRun':True,'approvedInputs':196,'additions':self.state['questionIds'],'updates':[],'conflicts':[]}
        evidence={'reviewsSha256':h.digest((self.work/'reviews.json').read_bytes()),'publisherSha256':h.digest((h.ROOT/'scripts/publish-historical-questions.ts').read_bytes()),'resultSha256':r.checksum(result),'manifestSha256':r.MANIFEST_SHA}
        with patch.object(r,'publisher_check'):
            self.assertRaises(ValueError,r.publication_gate)
            h.write_json(self.root/'publisher-dry-run.json',result);h.write_json(self.root/'dry-run-evidence.json',evidence);r.publication_gate()
            for key,value in [('approvedInputs',197),('additions',self.state['questionIds'][:-1]),('updates',['existing']),('conflicts',[{'id':'conflict'}]),('dryRun',False)]:
                h.write_json(self.root/'publisher-dry-run.json',{**result,key:value});self.assertRaises(ValueError,r.publication_gate)
            h.write_json(self.root/'publisher-dry-run.json',result);h.write_json(self.root/'dry-run-evidence.json',{**evidence,'reviewsSha256':'stale'});self.assertRaisesRegex(ValueError,'Stale',r.publication_gate)

    def test_original_image_bytes_are_independently_checked(self):
        self.save();image=self.root/'changed.webp';image.write_bytes(b'changed')
        altered=copy.deepcopy(self.state);altered['nativeImages']={str(image):'original'}
        with patch.object(r,'context',return_value=(altered,self.package)):self.assertRaisesRegex(ValueError,'Original image changed',r.verify_native)


if __name__=='__main__':unittest.main()
