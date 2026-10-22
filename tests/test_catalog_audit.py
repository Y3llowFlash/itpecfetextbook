"""Synthetic classification/readiness regressions; no private questions required."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from test_academic_qa import h, qa, record, review, decision
import catalog_audit as a


def fixture():
    records = [record(i) for i in range(1, 334)]
    pages = [{'pdfPage': i, 'text': 'CPU register instruction cache context',
              'textSha256': h.digest(b'CPU register instruction cache context'), 'printedPage': None} for i in range(1, 488)]
    pages[51]['printedPage'] = 47
    ev = {'kind': 'textbook-source', 'sourceSha256': a.BOOK_SHA, 'pdfPage': 52, 'printedPage': 47,
          'textSha256': pages[51]['textSha256'], 'checkedExcerpt': 'CPU register', 'role': 'direct'}
    entries = []; reviews = {}
    for r in records:
        r.update(year=2020, season='A', number=1, examType='FE', examTypeStatus='owner-confirmed')
        r['sourceReferences'] = [{'sha256': a.SOURCE_SHA}]
        v = review(r, True)
        v.update(mapping={'status': 'verified', 'chapterId': 'fe-v1-ch01', 'sectionId': 's03', 'subsectionId': 'register-anchor',
                          'headingNumber': '3-1', 'conceptId': 'cpu-registers', 'evidence': [copy.deepcopy(ev)]},
                 extraction={**decision(r)['extraction'], 'sourceBinding': qa.extraction_binding(r), 'reviewedImages': [r['images'][0]['sha256']]})
        reviews[r['id']] = v
        entries.append({'id': r['id'], 'contentSha256': r['contentSha256'], 'reviewSha256': qa.object_hash(v),
                        'images': [x['sha256'] for x in r['images']], 'sourcePages': [x['pdfPage'] for x in r['regions']],
                        'classification': {'category': 'ch1', 'chapter': 1, 'status': 'audit-recommendation', 'reason': 'Source register definition',
                                           'headingNumber': '3-1', 'placement': 'exact', 'evidence': [copy.deepcopy(ev)]}})
    ledger = {'schema': 'itpec-private-catalog-audit-v1', 'baseline': a.BASELINE, 'snapshot': {'questionFileSha256': 'snapshot'},
              'sourceSha256': a.SOURCE_SHA, 'bookSha256': a.BOOK_SHA, 'entries': entries, 'bookReview': {'scope': 'synthetic'}}
    return records, reviews, ledger, pages


def validate(records, reviews, ledger, pages):
    return a.validate_ledger(records, reviews, ledger, {'questionFileSha256': 'snapshot'}, pages, a.SOURCE_SHA, a.BOOK_SHA)


class CatalogAuditTests(unittest.TestCase):
    def setUp(self):
        self.records, self.reviews, self.ledger, self.pages = fixture()
        self.r = self.records[0]; self.v = self.reviews[self.r['id']]; self.d = self.ledger['entries'][0]
        self.nodes = [{'id': 'register-anchor', 'sectionId': 's03', 'number': '3-1', 'conceptIds': ['cpu-registers']}]
        self.concepts = {'cpu-registers': {'id': 'cpu-registers', 'sectionId': 's03'}}

    def row(self):
        return a.audit_row(self.r, self.v, self.d, self.nodes, self.concepts, self.pages, True)

    def test_exact_333_scope_and_duplicates_rejected(self):
        self.assertEqual(len(validate(self.records, self.reviews, self.ledger, self.pages)), 333)
        for entries in [self.ledger['entries'][:-1], self.ledger['entries'] + [self.d], [self.d] * 333]:
            bad = {**self.ledger, 'entries': entries}
            self.assertRaisesRegex(ValueError, 'exact unique catalog scope', validate, self.records, self.reviews, bad, self.pages)
        self.records[1]['id'] = self.r['id']
        self.assertRaises(ValueError, validate, self.records, self.reviews, self.ledger, self.pages)

    def test_stale_global_source_and_snapshot_rejected(self):
        for key in ['snapshot', 'sourceSha256', 'bookSha256', 'baseline', 'schema']:
            bad = copy.deepcopy(self.ledger); bad[key] = 'stale'
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate(self.records, self.reviews, bad, self.pages)

    def test_stale_each_question_source_image_review_identity_rejected(self):
        for key in ['contentSha256', 'reviewSha256', 'images', 'sourcePages']:
            bad = copy.deepcopy(self.ledger); bad['entries'][0][key] = 'stale'
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'Stale per-record'):
                validate(self.records, self.reviews, bad, self.pages)
        self.r['rawText'] = 'Changed'
        self.assertRaisesRegex(ValueError, 'Immutable question', validate, self.records, self.reviews, self.ledger, self.pages)

    def test_review_edit_stales_even_unchanged_answer(self):
        self.v['explanation']['summary'] = 'Proposed change'
        self.assertRaisesRegex(ValueError, 'Stale per-record', validate, self.records, self.reviews, self.ledger, self.pages)

    def test_passages_hashes_printed_labels_and_roles_are_not_invented(self):
        for key, value in [('textSha256', 'stale'), ('sourceSha256', 'other'), ('checkedExcerpt', 'invented paragraph'),
                           ('printedPage', 46), ('role', 'verified'), ('pdfPage', 0), ('pdfPage', 488)]:
            bad = copy.deepcopy(self.ledger); bad['entries'][0]['classification']['evidence'][0][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                validate(self.records, self.reviews, bad, self.pages)

    def test_classification_is_independent_from_answer_status(self):
        original = copy.deepcopy(self.v['verification'])
        c = self.d['classification']; c.update(category='other-vol1', chapter=2)
        c['evidence'][0].update(pdfPage=149, printedPage=None)
        self.assertEqual(len(validate(self.records, self.reviews, self.ledger, self.pages)), 333)
        row = self.row()
        self.assertTrue(row['academic']['independentlyVerified'])
        self.assertFalse(row['chapter1Candidate'])
        self.assertIn('existing-hardware-mapping-contradicts-classification', row['mapping']['issues'])
        self.assertEqual(self.v['verification'], original)

    def test_uncertain_and_outside_questions_do_not_acquire_exact_hardware_placement(self):
        for category in ['uncertain', 'outside-vol1']:
            self.d['classification'].update(category=category, chapter=None, headingNumber=None, placement='unassigned', evidence=[])
            validate(self.records, self.reviews, self.ledger, self.pages)
            row = self.row()
            self.assertFalse(row['chapter1Candidate']); self.assertFalse(row['priorityAfterMandatoryRepairs'])
            self.assertIn('exclude-from-hardware-highlights', row['mapping']['issues'])
            self.d['classification']['headingNumber'] = '3-1'
            self.assertRaisesRegex(ValueError, 'Unassigned questions', validate, self.records, self.reviews, self.ledger, self.pages)

    def test_owning_chapter_must_have_a_primary_passage(self):
        self.d['classification'].update(chapter=2, category='other-vol1')
        self.assertRaisesRegex(ValueError, 'another chapter', validate, self.records, self.reviews, self.ledger, self.pages)
        self.d['classification'].update(chapter=1, category='ch1', status='verified')
        self.assertRaisesRegex(ValueError, 'audit recommendation', validate, self.records, self.reviews, self.ledger, self.pages)

    def test_metadata_cannot_be_guessed_from_fe_or_occurrence(self):
        row = self.row()
        self.assertIsNone(row['metadata']['paper']); self.assertIsNone(row['metadata']['subject'])
        self.assertTrue(row['metadata']['sourceOccurrenceVerified'])
        self.assertFalse(row['metadata']['publicationMetadataComplete']); self.assertFalse(row['publicationReady'])
        self.assertIn('paper-subject-metadata-unverified', row['blockers'])
        self.assertIn('classification-annotation-missing-in-current-review', row['blockers'])
        self.assertEqual(self.row()['id'], self.r['id'])

    def test_existing_authoritative_practice_matching_is_reused_without_edit(self):
        with patch.object(h, 'authoritative_duplicate', return_value={'correctAnswer': 'a'}) as match:
            row = self.row()
        match.assert_called_once_with(self.r, self.v)
        self.assertTrue(row['publishedPracticeAuthority']['reliableMatchEstablished'])
        self.assertEqual(self.v['verification']['independentAnswer'], 'b')
        self.assertFalse(row['publicationReady'])

    def test_owner_qualifications_and_multi_answer_grading_block_survive(self):
        self.v['verification']['status'] = 'needs-review'
        self.v['ownerAdjudication'] = {'gradingEligibility': {'status': 'blocked', 'acceptedOptions': ['a', 'd']}, 'selectedAnswer': 'a'}
        old = copy.deepcopy(self.v)
        with patch.object(h, 'valid_adjudication', return_value=True):
            row = self.row()
        self.assertTrue(row['academic']['ownerAdjudicatedWithQualifications'])
        self.assertFalse(row['academic']['independentlyVerified'])
        self.assertEqual(row['grading']['qualifiedOwnerSelection']['acceptedOptions'], ['a', 'd'])
        self.assertFalse(row['grading']['productionEligibilityGranted']); self.assertEqual(self.v, old)

    def test_partial_editorial_transcript_does_not_become_literal_complete(self):
        self.v['extraction'].update(status='partial', sourceDefects=['Missing literal labels'], editorialTranscription={'status': 'owner-confirmed'})
        self.d['partialExtraction'] = {'sourceImageIntact': True, 'defect': 'Missing labels', 'action': 'Keep editorial labels separate'}
        old = copy.deepcopy(self.v); row = self.row()
        self.assertEqual(row['extraction']['effective'], 'partial')
        self.assertFalse(row['extraction']['accessibleReviewComplete']); self.assertEqual(self.v, old)
        self.assertTrue(row['academic']['independentlyVerified'])

    def test_raw_complete_legacy_extraction_is_separate_accessibility_blocker(self):
        self.v['extraction'] = {'status': 'complete'}
        row = self.row()
        self.assertEqual(row['extraction']['effective'], 'complete')
        self.assertFalse(row['extraction']['accessibleReviewComplete'])
        self.assertEqual(len(row['extraction']['accessibleReviewDefects']), 4)
        self.assertIn('accessible-image-option-review-incomplete', row['blockers'])

    def test_mapping_verification_does_not_validate_wrong_anchor_or_concept(self):
        for key, value in [('subsectionId', 'missing'), ('sectionId', 'wrong'), ('headingNumber', '5-5-2')]:
            old = copy.deepcopy(self.v['mapping']); self.v['mapping'][key] = value
            self.assertIn('invalid-or-inconsistent-website-anchor', self.row()['mapping']['issues'])
            self.v['mapping'] = old
        self.v['mapping']['conceptId'] = 'new-concept'
        self.assertIn('concept-highlight-needs-specific-editorial-review', self.row()['mapping']['issues'])

    def test_legacy_heading_and_fragment_hashes_have_distinct_validation(self):
        self.v['mapping']['evidence'] = 'Heading-only citation'
        self.assertIn('legacy-heading-citation-needs-structured-passage', self.row()['mapping']['issues'])
        fragment = 'CPU register'
        self.v['mapping']['evidence'] = [{'kind': 'textbook-source', 'sourceSha256': a.BOOK_SHA, 'pdfPage': 52, 'printedPage': 47,
            'lineIds': ['line-1'], 'checkedText': fragment, 'textSha256': h.digest(fragment.encode())}]
        self.assertNotIn('existing-structured-passage-binding-invalid', self.row()['mapping']['issues'])
        self.v['mapping']['evidence'][0]['checkedText'] = 'Different'
        self.assertIn('existing-structured-passage-binding-invalid', self.row()['mapping']['issues'])

    def test_idempotent_reports_and_no_input_mutation(self):
        old = copy.deepcopy((self.records, self.reviews, self.ledger, self.pages))
        rows = [self.row()]
        first = a.artifacts(rows, self.ledger, {'physicalPages': 487})
        self.assertEqual(first, a.artifacts(rows, self.ledger, {'physicalPages': 487}))
        self.assertEqual((self.records, self.reviews, self.ledger, self.pages), old)
        self.assertEqual(json.loads(first['classification-inventory.json'])['questions'][0]['ownerApproval']['status'], 'unapproved')

    def test_safe_writes_and_check_only_preserve_mtime(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(h, 'WORK', Path(directory)):
            folder = h.WORK/'catalog-audit/reports'; output = {'summary.json': '{"synthetic":true}\n'}
            self.assertRaisesRegex(ValueError, 'missing or stale', a.write_outputs, folder, output, True)
            self.assertFalse(folder.exists())
            a.write_outputs(folder, output); path = folder/'summary.json'; before = path.stat().st_mtime_ns
            a.write_outputs(folder, output); a.write_outputs(folder, output, True)
            self.assertEqual(before, path.stat().st_mtime_ns)
            self.assertRaisesRegex(ValueError, 'nonpublic', a.write_outputs, h.WORK.parent/'public', output)
            self.assertRaisesRegex(ValueError, 'Unsafe', a.write_outputs, folder, {'../reviews.json': '[]'})

    def test_existing_private_review_bytes_and_mtime_are_guarded(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(h, 'WORK', Path(directory)/'private'), patch.object(h, 'ROOT', Path(directory)):
            h.WORK.mkdir(); path=h.WORK/'reviews.json'; path.write_bytes(b'original')
            with patch.object(a, 'FOLDER', h.WORK/'catalog-audit'):
                guard={'reviews.json': {'sha256': h.digest(path.read_bytes()), 'mtimeNs': path.stat().st_mtime_ns}}
                a.verify_preservation(guard)
                path.write_bytes(b'edited')
                self.assertRaisesRegex(ValueError, 'Protected', a.verify_preservation, guard)

    def test_all_487_pages_including_visual_only_inserts_have_correct_chapter_context(self):
        self.assertIsNone(a.chapter_at(1)); self.assertEqual(a.chapter_at(83), 1)
        self.assertEqual(a.chapter_at(181), 2); self.assertEqual(a.chapter_at(309), 5)
        self.assertEqual(a.chapter_at(453), 7); self.assertIsNone(a.chapter_at(460)); self.assertIsNone(a.chapter_at(487))


if __name__ == '__main__':
    unittest.main()
