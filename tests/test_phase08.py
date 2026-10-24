"""Final-66 read-only scope, source and publication-safety regressions."""
import copy
import sys
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import phase08 as p


@unittest.skipUnless((p.WORK/'audit.json').exists(),'Private source audit is intentionally absent from clones')
class Phase08Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.state,cls.report,cls.records,cls.reviews,cls.rows=p.inputs()
        cls.pages=p.core.book_pages();cls.overlays=p.h.read_json(p.WORK/'editorial-overlays.json');cls.dups=p.h.read_json(p.WORK/'duplicate-check.json')

    def validate(self,report=None,overlays=None,duplicates=None):
        return p.validate_inventory(report or self.report,self.state,self.records,self.reviews,self.pages,overlays or self.overlays,duplicates or self.dups)

    def altered(self):return copy.deepcopy(self.report)

    def test_exact_66_all_four_tracks_and_29_original_scope(self):
        self.assertEqual(len(self.validate()),66)
        self.assertEqual({k:len(v) for k,v in self.state['groups'].items()},p.COUNTS)
        self.assertEqual(self.report['selectedIds'],[])

    def test_missing_duplicate_or_replaced_record_rejected(self):
        for replacement in [self.report['questions'][:-1],self.report['questions']+[self.report['questions'][0]],self.report['questions'][:-1]+[self.report['questions'][0]]]:
            report=self.altered();report['questions']=replacement;self.assertRaises(ValueError,self.validate,report)

    def test_original_category_cannot_be_reclassified_to_expand_candidates(self):
        report=self.altered();report['questions'][0]['originalCategory']='other-vol1';self.assertRaises(ValueError,self.validate,report)

    def test_protected_cases_remain_entirely_untouched_and_never_selected(self):
        self.assertEqual(len(self.state['protectedIds']),7)
        protected=[r for r in self.rows if r['protected']]
        self.assertEqual({r['pdfPage'] for r in protected},{110,112,119,152,179,180,181})
        self.assertFalse(any(q['id'] in self.state['protectedIds'] for q in self.overlays['repairs']))
        for field,value in [('protected',False),('selected',True),('approval','approved')]:
            report=self.altered();next(r for r in report['questions'] if r['protected'])[field]=value;self.assertRaises(ValueError,self.validate,report)

    def test_source_image_hash_or_review_snapshot_mismatch_rejected(self):
        for field,value in [('sourceBinding',{}),('beforeReviewSha256','stale'),('sourceImageIntegrity','uninspected')]:
            report=self.altered();report['questions'][0][field]=value;self.assertRaises(ValueError,self.validate,report)

    def test_invented_textbook_page_quote_or_label_rejected(self):
        for field,value in [('pdfPage',999),('printedPage',999),('checkedExcerpt','fabricated source sentence'),('textSha256','stale')]:
            report=self.altered();next(r for r in report['questions'] if r.get('textbookEvidence'))['textbookEvidence'][0][field]=value;self.assertRaises(ValueError,self.validate,report)

    def test_actual_chapter_headings_exist_and_fake_titles_rejected(self):
        other=[r for r in self.rows if r['originalCategory']=='other-vol1']
        self.assertEqual({c:sum(r['chapter']==c for r in other) for c in [2,3,5,7]},{2:11,3:12,5:5,7:1})
        for r in other:p.actual_heading(r['chapter'],r['headingNumber'],r['headingTitle'],self.pages)
        self.assertRaises(ValueError,p.actual_heading,3,'2-2-3','Fake Virtual TLB Chapter',self.pages)

    def test_fake_routes_and_unavailable_chapter_selection_rejected(self):
        for field,value in [('websiteRoute','/chapters/software/invented/'),('websiteAnchor','fake-anchor'),('publicationEligible',True)]:
            report=self.altered();next(r for r in report['questions'] if r['originalCategory']=='other-vol1')[field]=value;self.assertRaises(ValueError,self.validate,report)
        report=self.altered();report['selectedIds']=self.state['groups']['other-vol1'][:1];self.assertRaises(ValueError,self.validate,report)

    def test_contextual_mapping_cannot_be_promoted_by_answer_verification(self):
        report=self.altered();next(r for r in report['questions'] if r.get('classificationConfidence')=='context-only')['classificationConfidence']='direct-source-teaching';self.assertRaises(ValueError,self.validate,report)

    def test_metadata_and_academic_dossier_fingerprints_preserved(self):
        for field,value in [('academicAnswerFingerprint','stale'),('workedExplanationFingerprint','stale'),('examMetadataFingerprint','stale')]:
            report=self.altered();next(r for r in report['questions'] if r['originalCategory']=='other-vol1')[field]=value;self.assertRaises(ValueError,self.validate,report)
        report=self.altered();report['questions'][0]['exam']['year']=9999;self.assertRaises(ValueError,self.validate,report)

    def test_all_29_accessible_reviews_source_bound_and_no_option_garbling(self):
        other=[r for r in self.rows if r['originalCategory']=='other-vol1']
        self.assertTrue(all(set(r['accessibleReview']['content']['optionText'])==set('abcd') for r in other))
        r=next(r for r in other if r['pdfPage']==239)
        self.assertEqual(list(r['accessibleReview']['content']['optionText'].values()),['2^4','2^10','2^20','2^32'])
        report=self.altered();next(r for r in report['questions'] if r['pdfPage']==239)['accessibleReview']['content']['optionText']['a']='garbled';self.assertRaises(ValueError,self.validate,report)

    def test_answer_leak_removed_but_original_party_typo_preserved(self):
        r=next(r for r in self.rows if r['pdfPage']==163)['accessibleReview']['content']
        self.assertNotIn('C explicitly',r['imageDescription']);self.assertEqual(r['optionText']['d'],'Party')

    def test_missing_stale_or_non_accessibility_overlay_rejected(self):
        for field,value in [('sourceBinding',{}),('beforeReviewSha256','stale'),('status','unreviewed'),('academicChanged',True),('nativeApplied',True)]:
            overlays=copy.deepcopy(self.overlays);overlays['repairs'][0][field]=value;self.assertRaises(ValueError,self.validate,None,overlays)
        overlays=copy.deepcopy(self.overlays);overlays['repairs'][0]['after']['correctAnswer']='a';self.assertRaises(ValueError,self.validate,None,overlays)
        overlays=copy.deepcopy(self.overlays);overlays['repairs'].pop();self.assertRaises(ValueError,self.validate,None,overlays)

    def test_protected_accessibility_overlay_rejected(self):
        overlays=copy.deepcopy(self.overlays);overlays['repairs'][0]['id']=self.state['protectedIds'][0];self.assertRaises(ValueError,self.validate,None,overlays)

    def test_source_figure_and_separate_secondary_evidence_cannot_be_faked(self):
        report=self.altered();next(r for r in report['questions'] if r['pdfPage']==4)['privateMappingProposal']['sourceFigureBinding']['asset']['sha256']='changed';self.assertRaises(ValueError,self.validate,report)
        report=self.altered();next(r for r in report['questions'] if r['pdfPage']==322)['privateMappingProposal']['evidence'][1]['role']='direct';self.assertRaises(ValueError,self.validate,report)

    def test_distinct_occurrences_and_practice_authority_remain_independent(self):
        rows=[r for r in self.rows if r['pdfPage'] in [275,326]]
        self.assertEqual(len({r['id'] for r in rows}),2);self.assertEqual(len({r['sourceBinding']['contentSha256'] for r in rows}),2)
        dups=copy.deepcopy(self.dups);dups['questions'][0]['result']={'status':'needs-review'};self.assertRaises(ValueError,self.validate,None,None,dups)

    def test_prior_687_public_and_267_approval_snapshot_changes_rejected(self):
        with patch.object(p.core,'public_fingerprints',return_value={}):self.assertRaises(ValueError,p.verify_baseline)
        with patch.object(p.qa,'snapshot_hashes',return_value={}):self.assertRaises(ValueError,p.verify_baseline)

    def test_no_new_owner_fingerprint_generated_for_any_protected_case(self):
        with patch.object(p.h,'publication_fingerprint',side_effect=AssertionError('No new publication fingerprint authorized')):
            self.validate()

    def test_specific_hardware_source_defect_is_repaired_only_in_private_overlay(self):
        repair=next(r for r in self.overlays['repairs'] if r['pdfPage']==313)
        self.assertIn('3FFFFF;',repair['after']['optionText']['a']);self.assertIn('3FFFFFF;',repair['before']['optionText']['a'])
        self.assertFalse(repair['academicChanged']);self.assertFalse(repair['nativeApplied'])
        self.assertTrue(any('source-explanation' in b for r in self.rows if r['pdfPage']==313 for b in r['blockers']))

    def test_exact_empty_package_is_explicitly_blocked_not_approval_ready(self):
        if not (p.WORK/'final-approval/manifest.json').exists():self.skipTest('Final package not prepared yet')
        manifest=p.check();self.assertEqual(manifest['questionIds'],[]);self.assertEqual(manifest['futureApprovalFingerprints'],{})
        self.assertFalse(manifest['publicationReady']);self.assertFalse(manifest['publicationApprovalGranted'])
        context=p.h.read_json(p.WORK/'final-approval/preparation-inputs.json')
        for field,value in [('candidateSetFingerprint','stale'),('questionIds',self.state['groups']['other-vol1'][:1]),('publicationApprovalGranted',True)]:
            altered=copy.deepcopy(manifest);altered[field]=value;self.assertRaises(ValueError,p.candidates.validate_final_package,altered,[],[],[],context,batch=8,expected_count=0)


class Phase08PublicationSafetyTests(unittest.TestCase):
    def test_non_dry_publication_rejected_before_private_source_access(self):
        result=subprocess.run(['node','node_modules/tsx/dist/cli.mjs','scripts/publish-historical-questions.ts','--batch','8'],cwd=p.h.ROOT,capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0);self.assertIn('Phase 8 is private audit/preparation only',result.stderr)


if __name__=='__main__':unittest.main()
