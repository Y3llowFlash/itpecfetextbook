"""Read-only, source-bound historical classification/readiness reporting.

Human classification decisions live in .local, never in the public catalog.
This command cannot reconcile reviews, approve, export, or publish questions.
"""
import argparse
from collections import Counter
import csv
import io
import json
from pathlib import Path
import re
import subprocess
import fitz
import historical_questions as h
import academic_qa as qa

BASELINE = 'db83363ba6510857845d75bef0e6c58e5903f1d0'
BRANCH = 'feature/chapter1-question-integration'
FOLDER = h.WORK / 'catalog-audit'
BOOK_SHA = '1e1f2ec364a52751333b1e3ab2a2f2548e9345cd06a7c300b8a7075fb51c3d1b'
SOURCE_SHA = '5c74e109ff2129f70189b55e79e7af3a806183cf0c1aa8082195aa942d1c16b1'
CHAPTERS = [(17, 1), (126, 2), (193, 3), (256, 4), (298, 5), (361, 6), (412, 7)]


def report_folder():
    from metadata_integration import FOLDER as metadata_folder
    return FOLDER/('metadata-reports' if (metadata_folder/'applied-state.json').exists() else 'reports')


def dump(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n'


def chapter_at(page):
    if not 17 <= page < 460:
        return None
    return next(ch for start, ch in reversed(CHAPTERS) if page >= start)


def validate_ledger(records, reviews, ledger, snapshot, pages, source_sha, book_sha, expected=333):
    """Reject stale decisions; an audit label can never become review authority."""
    if ledger.get('schema') != 'itpec-private-catalog-audit-v1' or ledger.get('baseline') != BASELINE:
        raise ValueError('Unsupported audit schema or baseline')
    if ledger.get('snapshot') != snapshot or ledger.get('sourceSha256') != source_sha or ledger.get('bookSha256') != book_sha:
        raise ValueError('Stale catalog snapshot or PDF checksums')
    entries = ledger.get('entries', [])
    ids = [r['id'] for r in records]
    if len(records) != expected or len(set(ids)) != expected or len(entries) != expected or {e['id'] for e in entries} != set(ids) or len({e['id'] for e in entries}) != expected or set(reviews) != set(ids):
        raise ValueError('Audit must contain the exact unique catalog scope')
    index = {r['id']: r for r in records}
    for e in entries:
        r = index[e['id']]
        if e.get('contentSha256') != r['contentSha256'] or e.get('reviewSha256') != qa.object_hash(reviews[r['id']]) or e.get('images') != [a['sha256'] for a in r['images']] or e.get('sourcePages') != [a['pdfPage'] for a in r['regions']]:
            raise ValueError('Stale per-record source/review/image binding')
        if h.digest(r['rawText'].encode()) != r['contentSha256'] or any(s['sha256'] != source_sha for s in r['sourceReferences']):
            raise ValueError('Immutable question transcript or source changed')
        c = e['classification']
        if c.get('status') != 'audit-recommendation' or not c.get('reason'):
            raise ValueError('Classification must remain a reasoned audit recommendation')
        category, chapter = c.get('category'), c.get('chapter')
        if category not in ['ch1', 'other-vol1', 'outside-vol1', 'uncertain'] or (category == 'ch1' and chapter != 1) or (category == 'other-vol1' and chapter not in range(2, 8)) or (category in ['uncertain', 'outside-vol1'] and chapter is not None):
            raise ValueError('Contradictory classification/chapter')
        evidence = c.get('evidence', [])
        if category in ['ch1', 'other-vol1'] and not evidence:
            raise ValueError('Chapter recommendation needs real textbook context')
        for ev in evidence:
            n = ev.get('pdfPage')
            if not isinstance(n, int) or not 1 <= n <= len(pages):
                raise ValueError('Invalid textbook page')
            p = pages[n-1]
            if ev.get('sourceSha256') != book_sha or ev.get('textSha256') != p['textSha256'] or not ev.get('checkedExcerpt') or ev['checkedExcerpt'] not in h.norm(p['text']):
                raise ValueError('Stale or invented textbook passage')
            if ev.get('printedPage') != p['printedPage'] or ev.get('role') not in ['direct', 'context', 'secondary']:
                raise ValueError('Printed page or evidence role disagrees')
        if category in ['ch1', 'other-vol1'] and not any(chapter_at(ev['pdfPage']) == chapter and ev['role'] != 'secondary' for ev in evidence):
            raise ValueError('Primary passage belongs to another chapter')
        if c.get('placement') == 'exact' and not c.get('headingNumber'):
            raise ValueError('Exact placement requires a real numbered heading')
        if category in ['uncertain', 'outside-vol1'] and c.get('headingNumber'):
            raise ValueError('Unassigned questions cannot acquire exact subsection claims')
        if e.get('partialExtraction') and e['partialExtraction'].get('sourceImageIntact') is not True:
            raise ValueError('Extraction repair must state the inspected image result')
    return {e['id']: e for e in entries}


def mapping_audit(mapping, decision, nodes, concepts, pages):
    c = decision['classification']
    issues = list(decision.get('mappingIssues', []))
    status = mapping.get('status', 'missing')
    if status != 'verified':
        issues.append('mapping-not-verified')
    if c['category'] != 'ch1':
        issues.append('exclude-from-hardware-highlights')
        if mapping.get('chapterId') == 'fe-v1-ch01':
            issues.append('existing-hardware-mapping-contradicts-classification')
    node = next((n for n in nodes if n['id'] == mapping.get('subsectionId')), None)
    if mapping.get('chapterId') == 'fe-v1-ch01':
        if not node or node['sectionId'] != mapping.get('sectionId') or node['number'] != mapping.get('headingNumber'):
            issues.append('invalid-or-inconsistent-website-anchor')
        if c['category'] == 'ch1' and c.get('headingNumber') and mapping.get('headingNumber') != c['headingNumber']:
            issues.append('recommended-textbook-subsection-differs')
    evs = mapping.get('evidence')
    if isinstance(evs, str):
        issues.append('legacy-heading-citation-needs-structured-passage')
    elif isinstance(evs, list):
        for ev in evs:
            if ev.get('kind') != 'textbook-source':
                continue
            n = ev.get('pdfPage')
            valid = isinstance(n, int) and 1 <= n <= len(pages)
            excerpt = ev.get('checkedExcerpt') or ev.get('checkedText')
            # Early source-review evidence binds a line-ID fragment, not a full page.
            fragment_bound = bool(ev.get('checkedText') and ev.get('lineIds') and ev.get('textSha256') == h.digest(ev['checkedText'].encode()))
            if not valid or ev.get('sourceSha256') != BOOK_SHA or not (fragment_bound or ev.get('textSha256') == pages[n-1]['textSha256']) or not excerpt or h.norm(excerpt) not in h.norm(pages[n-1]['text']):
                issues.append('existing-structured-passage-binding-invalid')
            elif ev.get('printedPage') != pages[n-1]['printedPage']:
                issues.append('existing-printed-page-label-needs-correction')
    else:
        issues.append('mapping-evidence-missing')
    concept = concepts.get(mapping.get('conceptId'))
    reuse = bool(c['category'] == 'ch1' and node and concept and concept['id'] in node['conceptIds'] and concept['sectionId'] == node['sectionId'] and node['number'] == c.get('headingNumber'))
    if c['category'] == 'ch1' and not reuse:
        issues.append('concept-highlight-needs-specific-editorial-review')
    if c.get('placement') != 'exact':
        issues.append('exact-placement-not-established')
    return {'existingStatus': status, 'issues': sorted(set(issues)), 'existingConceptReusableInPrinciple': reuse,
            'recommendedHeading': c.get('headingNumber'), 'recommendedPlacement': c['placement'],
            'anchorExists': node is not None, 'publicationMappingApproved': False}


def audit_row(record, review, decision, nodes, concepts, pages, occurrence):
    independent = h.valid_verification(record, review)
    owner = h.valid_adjudication(record, review)
    extraction = h.effective_extraction(record, review)
    mapping = mapping_audit(review.get('mapping', {}), decision, nodes, concepts, pages)
    c = decision['classification']
    meta = review.get('metadata', {})
    blockers = ['owner-publication-approval-absent']
    if not review.get('classification'):
        blockers.append('classification-annotation-missing-in-current-review')
    # No inference from FE, season, source file name, answer choice or similar question.
    metadata_complete = bool(meta.get('status') == 'verified' and meta.get('examType') == 'FE' and meta.get('paper') and meta.get('subject') in ['A', 'B'] and meta.get('evidence'))
    if not metadata_complete:
        blockers.append('paper-subject-metadata-unverified')
    if not independent:
        blockers.append('independent-academic-verification-incomplete')
    if owner:
        blockers.append('qualified-owner-selection-grading-and-publication-blocked')
    if extraction != 'complete':
        blockers.append('partial-extraction')
    if c['category'] != 'ch1':
        blockers.append('not-a-chapter1-candidate')
    if mapping['issues']:
        blockers.append('mapping-remediation-or-editorial-review-required')
    bound_review = review.get('extraction', {})
    transcript_ready = bool(extraction == 'complete' and bound_review.get('status') == 'complete' and bound_review.get('reviewedImages') == [a['sha256'] for a in record['images']] and bound_review.get('imageDescription') and set(bound_review.get('optionText', {})) == set('abcd') and all(bound_review['optionText'].values()))
    accessible_defects = []
    if not bound_review.get('sourceBinding'):
        accessible_defects.append('content-and-image-review-binding-missing')
    if bound_review.get('reviewedImages') != [a['sha256'] for a in record['images']]:
        accessible_defects.append('reviewed-image-hashes-incomplete')
    if not bound_review.get('imageDescription'):
        accessible_defects.append('image-description-missing')
    if set(bound_review.get('optionText', {})) != set('abcd') or not all(bound_review.get('optionText', {}).values()):
        accessible_defects.append('complete-accessible-option-text-missing')
    if not transcript_ready:
        blockers.append('accessible-image-option-review-incomplete')
    fast_track = bool(c['category'] == 'ch1' and independent and transcript_ready and mapping['existingStatus'] == 'verified' and c['placement'] == 'exact' and mapping['existingConceptReusableInPrinciple'] and not decision.get('mappingIssues'))
    return {'id': record['id'], 'sourcePdfPages': decision['sourcePages'], 'contentSha256': record['contentSha256'],
            'reviewSha256': decision['reviewSha256'], 'sourceSha256': SOURCE_SHA, 'images': record['images'],
            'currentClassification': review.get('classification'), 'classificationAnnotationWasMissing': not bool(review.get('classification')),
            'auditClassification': c, 'academic': {'independentlyVerified': independent, 'ownerAdjudicatedWithQualifications': owner,
                'existingVerificationStatus': review.get('verification', {}).get('status'), 'answerEvidenceUnchanged': True},
            'extraction': {'raw': record.get('extractionQuality'), 'effective': extraction,
                'accessibleReviewComplete': transcript_ready, 'accessibleReviewDefects': accessible_defects,
                'accessibleReviewAction': 'Verify the intact image; bind content/image hashes, transcribe all source options and provide image description. Do not equate raw extraction completeness with accessible publication review.' if accessible_defects else None,
                'repair': decision.get('partialExtraction')},
            'mapping': mapping, 'currentMapping': review.get('mapping'),
            'metadata': {'sourceOccurrenceVerified': occurrence, 'year': record['year'], 'season': record['season'], 'questionNumber': record['number'],
                'examType': record.get('examType'), 'examTypeStatus': record.get('examTypeStatus'), 'examTypeProvenance': record.get('examTypeProvenance'),
                'paper': meta.get('paper'), 'subject': meta.get('subject'), 'existingReviewStatus': meta.get('status'), 'publicationMetadataComplete': metadata_complete},
            'grading': {'singleAnswerEvidenceAvailable': independent, 'qualifiedOwnerSelection': review.get('ownerAdjudication', {}).get('gradingEligibility'),
                'sourcePresentationReady': transcript_ready, 'productionEligibilityGranted': False},
            'publishedPracticeAuthority': {'reliableMatchEstablished': bool(h.authoritative_duplicate(record, review)),
                'policy': 'Retain published ITPEC Practice authority only after reliable occurrence and image matching; no speculative match.'},
            'ownerApproval': review.get('approval', {}), 'publicationReady': False,
            'chapter1Candidate': c['category'] == 'ch1', 'priorityAfterMandatoryRepairs': fast_track, 'blockers': sorted(set(blockers))}


def totals(rows):
    counts = lambda values: dict(sorted(Counter(values).items()))
    return {'questions': len(rows), 'independentlyVerified': sum(r['academic']['independentlyVerified'] for r in rows),
            'ownerAdjudicatedWithQualifications': sum(r['academic']['ownerAdjudicatedWithQualifications'] for r in rows),
            'missingExistingClassificationAnnotations': sum(r['classificationAnnotationWasMissing'] for r in rows),
            'classification': counts(r['auditClassification']['category'] for r in rows),
            'chapter': counts(str(r['auditClassification']['chapter']) for r in rows),
            'placement': counts(r['auditClassification']['placement'] for r in rows),
            'hardwareExactPlacementRecommendations': sum(r['chapter1Candidate'] and r['auditClassification']['placement'] == 'exact' for r in rows),
            'existingMapping': counts(r['mapping']['existingStatus'] for r in rows),
            'mappingIssues': counts(i for r in rows for i in r['mapping']['issues']),
            'effectiveExtraction': counts(r['extraction']['effective'] for r in rows),
            'rawExtraction': counts(r['extraction']['raw'] for r in rows),
            'blockersOverlapping': counts(i for r in rows for i in r['blockers']),
            'priorityAfterMandatoryRepairs': sum(r['priorityAfterMandatoryRepairs'] for r in rows),
            'reliablePublishedPracticeMatches': sum(r['publishedPracticeAuthority']['reliableMatchEstablished'] for r in rows),
            'publicationReady': sum(r['publicationReady'] for r in rows),
            'ownerApprovals': sum(r['ownerApproval'].get('status') == 'approved' for r in rows)}


def table(rows):
    lines = ['| Historical PDF | Canonical ID | Classification | Proposed textbook placement (printed / physical PDF) | Academic | Extraction | Existing map | Blockers |', '|---|---|---|---|---|---|---|---|']
    for r in rows:
        c = r['auditClassification']; ev = c['evidence']
        refs = '; '.join(f"{e['printedPage'] if e['printedPage'] is not None else 'unnumbered'} / {e['pdfPage']} ({e['role']})" for e in ev)
        loc = (c.get('headingNumber') or 'No exact subsection') + ': ' + refs
        fields = [','.join(map(str, r['sourcePdfPages'])), r['id'], f"{c['category']} / {c['chapter']}", loc,
                  'independent' if r['academic']['independentlyVerified'] else 'qualified owner selection', r['extraction']['effective'], r['mapping']['existingStatus'], '; '.join(r['blockers'])]
        lines.append('| ' + ' | '.join(str(v).replace('|', '\\|').replace('\n', ' ') for v in fields) + ' |')
    return '\n'.join(lines) + '\n'


def artifacts(rows, ledger, coverage):
    summary = totals(rows)
    envelope = {'schema': 'itpec-catalog-readiness-audit-v1', 'baseline': BASELINE, 'branch': BRANCH,
                'sourceSnapshot': ledger['snapshot'], 'sourceSha256': SOURCE_SHA, 'textbookSha256': BOOK_SHA,
                'decisionLedgerSha256': qa.object_hash(ledger), 'engineSha256': h.digest(Path(__file__).read_bytes()),
                'authority': 'Audit recommendations only; existing review records unchanged; no approval or publication.', 'totals': summary}
    candidates = [r for r in rows if r['chapter1Candidate']]
    preserved = [r for r in rows if not r['chapter1Candidate']]
    queue = [{'id': r['id'], 'sourcePdfPages': r['sourcePdfPages'], 'mapping': r['mapping'], 'extraction': r['extraction'],
              'classification': r['auditClassification'], 'priorityAfterMandatoryRepairs': r['priorityAfterMandatoryRepairs']} for r in rows if r['mapping']['issues'] or not r['extraction']['accessibleReviewComplete']]
    outputs = {'classification-inventory.json': dump({**envelope, 'questions': rows}),
               'chapter1-candidates.json': dump({**envelope, 'questions': candidates}),
               'other-chapter-preservation.json': dump({**envelope, 'questions': preserved}),
               'mapping-extraction-repair-queue.json': dump({**envelope, 'repairs': queue}),
               'book-coverage.json': dump(coverage), 'summary.json': dump(envelope)}
    outputs['audit-input-manifest.json'] = dump({'baseline': BASELINE, 'sourceSha256': SOURCE_SHA, 'textbookSha256': BOOK_SHA,
        'snapshot': ledger['snapshot'], 'decisionLedgerSha256': qa.object_hash(ledger), 'bookReview': ledger['bookReview'],
        'questionBindings': [{'id': r['id'], 'contentSha256': r['contentSha256'], 'reviewSha256': r['reviewSha256'], 'pdfPages': r['sourcePdfPages'],
                              'images': [{'path': im['path'], 'sha256': im['sha256']} for im in r['images']]} for r in rows]})
    stream = io.StringIO(newline=''); writer = csv.writer(stream, lineterminator='\n')
    writer.writerow(['id', 'historicalPdfPages', 'category', 'chapter', 'heading', 'placement', 'bookPrintedPages', 'bookPhysicalPages', 'independentVerified', 'qualifiedOwnerSelection', 'extraction', 'existingMapping', 'paper', 'subject', 'ownerApproval', 'publicationReady', 'blockers', 'mappingIssues', 'reason'])
    for r in rows:
        c = r['auditClassification']
        writer.writerow([r['id'], ','.join(map(str,r['sourcePdfPages'])), c['category'], c['chapter'], c.get('headingNumber'), c['placement'],
                         ';'.join(str(e['printedPage']) for e in c['evidence']), ';'.join(str(e['pdfPage']) for e in c['evidence']),
                         r['academic']['independentlyVerified'], r['academic']['ownerAdjudicatedWithQualifications'], r['extraction']['effective'], r['mapping']['existingStatus'],
                         r['metadata']['paper'], r['metadata']['subject'], r['ownerApproval'].get('status'), False, ';'.join(r['blockers']), ';'.join(r['mapping']['issues']), c['reason']])
    outputs['classification-inventory.csv'] = stream.getvalue()
    outputs['classification-inventory.md'] = '# Private 333-question classification and readiness inventory\n\n' + table(rows)
    outputs['chapter1-candidates.md'] = '# Private Hardware candidates — none approved for publication\n\n' + table(candidates)
    outputs['other-chapter-preservation.md'] = '# Preserve outside Hardware highlights\n\n' + table(preserved)
    partial = [r for r in rows if r['extraction']['effective'] != 'complete']
    report = '# Private publication-readiness audit\n\nAudit recommendations, not changes to review status or publication approval. Blocker counts overlap.\n\n'
    report += '```json\n' + dump(summary) + '```\n\n'
    report += 'All 487 physical textbook pages were indexed and scanned in 14 overview contact sheets; selected passages and 12 partial source images received focused visual review. This is not a claim of word-by-word proofreading. The image-only MIDI insert at physical p.181 was visually inspected; empty extracted text does not mean a blank page. Physical p.83 is an unnumbered UART insert, not printed p.78.\n\n'
    report += 'All 333 historical source occurrences, immutable transcript checksums, current review bindings and original image hashes were checked. Source pixels were already checked during prior academic/owner review; this audit does not regenerate crops or pretend to repeat 333 new pixel comparisons.\n\n'
    report += '## Partial extraction repairs\n\n'
    for r in partial:
        repair = r['extraction']['repair']
        report += f"- PDF {r['sourcePdfPages'][0]} — {r['id']}: {repair['defect']} Repair: {repair['action']}\n"
    report += '\nThe 12 effective partial extractions are not the entire accessibility queue: 182 additional raw-complete records retain legacy extraction.status=complete without sourceBinding, image descriptions, optionText or reviewed image hashes. Their current effective extraction status remains complete under the existing framework, but their publication review is incomplete. The combined accessible-review backlog is 194; each missing field appears in the JSON repair queue. No raw/partial status was changed by this audit.\n'
    report += '\n## Classification and mapping findings\n\n'
    for r in rows:
        if r['mapping']['issues'] and (r['currentMapping'].get('chapterId') == 'fe-v1-ch01' and not r['chapter1Candidate'] or r['auditClassification'].get('specialFinding')):
            report += f"- PDF {r['sourcePdfPages'][0]} — {r['id']}: {r['auditClassification']['reason']} {'; '.join(r['mapping']['issues'])}.\n"
    metadata_note = 'Morning / Subject A is now separately owner-confirmed for all 333 questions; it was not extracted from the PDF. The original unknown fields remain in the immutable source records and prior review history.' if all(r['metadata']['publicationMetadataComplete'] for r in rows) else 'Paper and subject remain unknown; neither can be inferred from season, topic, filename or a similar occurrence.'
    report += '\n## Reliable metadata and grading\n\nYear, April/October season and question number match the original PDF on every record. FE is owner-confirmed provenance, not printed evidence. '+metadata_note+' Distinct pages 275 and 326 retain distinct canonical occurrence IDs. Published Practice authority still requires the existing strict occurrence and image matching rule; no Practice answer is overridden. All seven qualified owner selections retain their grading/publication blockers, including multiple valid choices on p.119 and editorial option labels on p.112.\n\n'
    report += '## Next milestone plan (requires owner review)\n\n1. Review the private decision ledger and accept/correct chapter recommendations, especially cross-chapter and uncertain cases. Apply only classification/mapping annotations in a separate source-bound, stale-snapshot-checked change; preserve answers and IDs.\n2. Replace legacy heading citations with the actual bounded passages and page bindings in this inventory. Correct contradictory mappings before considering any Hardware highlight. Retain future-chapter questions privately; do not manufacture routes for unavailable chapters.\n3. Repair the 12 extraction reviews using the listed source defects and editorial boundaries. Five require accessible transcription/provenance completion, seven retain literal-source/editorial defects. Keep original source images; no blanket recropping.\n4. For Hardware candidates, reuse matching existing concepts where appropriate. Review each specific question-to-highlight link; new concepts require an owner-reviewed source paragraph, fragment binding, title and summary. Context-only topics remain unmapped until an exact suitable placement is justified.\n5. Establish paper/subject evidence without guessing; preserve FE owner provenance. Recheck published Practice occurrence/image matches before grading or eventual promotion.\n6. Resolve grading policy for the seven owner-adjudicated records separately; do not turn selected answers into independent verification or approval.\n7. Run dry-run promotion and all publication-boundary/progress/browser checks. Request explicit per-record publication approval only after a concrete, reviewable eligible set exists. No approval is granted by this audit.\n\n'
    report += '## Complete per-question readiness table\n\n' + table(rows)
    outputs['publication-readiness-report.md'] = report
    return outputs


def safe_output(folder):
    resolved = folder.resolve()
    if not resolved.is_relative_to((h.WORK / 'catalog-audit').resolve()):
        raise ValueError('Audit output must stay in the nonpublic catalog-audit workspace')
    return resolved


def write_outputs(folder, outputs, check=False):
    folder = safe_output(folder)
    # Only dedicated generated report names may be written; never arbitrary paths.
    for name, content in outputs.items():
        if Path(name).name != name or not name.endswith(('.json', '.csv', '.md')):
            raise ValueError('Unsafe audit artifact name')
    for name, content in outputs.items():
        path = folder / name; data = content.encode('utf-8')
        if path.exists() and path.read_bytes() == data:
            continue
        if check:
            raise ValueError(f'Audit report missing or stale: {name}')
        folder.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def verify_preservation(snapshot):
    for name, binding in snapshot.items():
        path = Path(name) if Path(name).is_absolute() else h.WORK / name
        if not path.is_file() or h.digest(path.read_bytes()) != binding['sha256'] or path.stat().st_mtime_ns != binding['mtimeNs']:
            raise ValueError(f'Protected source/review/application file changed: {name}')
    current = {str(p.relative_to(h.WORK)) for p in h.WORK.rglob('*') if p.is_file() and not p.is_relative_to(FOLDER)}
    previous = {name for name in snapshot if not Path(name).is_absolute()}
    if current != previous:
        raise ValueError('Private catalog files added or removed outside audit workspace')
    application = {str(p) for root in ['src', 'public'] for p in (h.ROOT/root).rglob('*') if p.is_file()}
    if application != {name for name in snapshot if Path(name).is_absolute()}:
        raise ValueError('Public application asset set changed')


def run(check=False, textbook=qa.TEXTBOOK):
    git = lambda *args: subprocess.check_output(['git', *args], cwd=h.ROOT, text=True).strip()
    if git('branch', '--show-current') != BRANCH or subprocess.run(['git', 'merge-base', '--is-ancestor', BASELINE, 'HEAD'], cwd=h.ROOT, capture_output=True).returncode:
        raise ValueError('Audit requires the existing feature branch and baseline ancestry')
    before = h.read_json(FOLDER / 'before-files.json')
    if not before:
        raise ValueError('A pre-audit preservation snapshot is required')
    ledger = h.read_json(FOLDER/'decisions.json')
    from metadata_integration import FOLDER as metadata_folder,rebind_audit
    if (metadata_folder/'applied-state.json').exists():ledger,before=rebind_audit(ledger,before)
    verify_preservation(before)
    h.verify_source()
    records = h.read_json(h.WORK/'questions.json'); reviews = h.read_json(h.WORK/'reviews.json')
    h.verify_assets(records)
    source_sha = h.digest(h.SOURCE.read_bytes()); book_sha = h.digest(textbook.read_bytes())
    if source_sha != SOURCE_SHA or book_sha != BOOK_SHA:
        raise ValueError('This audit is restricted to the authorized two source PDFs')
    pages = []
    with fitz.open(textbook) as book:
        if len(book) != 487:
            raise ValueError('Expected the complete 487-page Volume 1 textbook')
        for i, page in enumerate(book):
            text = page.get_text()
            # Page labels must be checked, never derived with a single PDF offset.
            labels = [int(s.strip()) for s in text.splitlines()[:8] if re.fullmatch(r'\d{1,3}', s.strip())]
            pages.append({'pdfPage': i+1, 'text': text, 'textSha256': h.digest(text.encode()), 'printedPage': labels[0] if labels else None})
    decisions = validate_ledger(records, reviews, ledger, qa.snapshot_hashes(h.WORK), pages, source_sha, book_sha)
    expected_sheets = [f'visual-review/book-overview-{s:03}-{min(s+35,487):03}.jpg' for s in range(1,488,36)]
    if ledger['bookReview'].get('overviewSheets') != expected_sheets:
        raise ValueError('Visual overview must cover all 487 textbook pages')
    bindings = {v['path']: v['sha256'] for v in ledger['bookReview'].get('visualArtifacts', [])}
    if not set(expected_sheets).issubset(bindings):
        raise ValueError('Missing visual-review source bindings')
    for name, sha in bindings.items():
        path = (FOLDER/name).resolve()
        if not path.is_relative_to((FOLDER/'visual-review').resolve()) or not path.is_file() or h.digest(path.read_bytes()) != sha:
            raise ValueError('Visual-review evidence changed or escaped private workspace')
    coverage = {'sourceSha256': book_sha, 'physicalPages': 487, 'review': ledger['bookReview'],
                'pages': [{k: p[k] for k in ['pdfPage', 'printedPage', 'textSha256']} | {'chapter': chapter_at(p['pdfPage']), 'textLength': len(p['text'])} for p in pages]}
    nodes = h.read_json(h.ROOT/'src/content/hardware-toc.json')['nodes']
    concepts = {c['id']: c for c in h.read_json(h.ROOT/'src/content/concepts.json')}
    occurrence = {}
    with fitz.open(h.SOURCE) as source:
        if len(source) != 333:
            raise ValueError('Only the 333-page Technology-01 source is authorized')
        for r in records:
            desc = h.describe_page(source[r['regions'][0]['pdfPage']-1], r['regions'][0]['pdfPage'])
            expected_date = (str(r['year']), 'October' if r['season'] == 'A' else 'April')
            if desc['questionNumber'] != r['number'] or expected_date not in desc['dates'] or h.digest(desc['body'].encode()) != r['contentSha256']:
                raise ValueError(f'Question identity/transcript differs from original PDF: {r["id"]}')
            occurrence[r['id']] = True
    rows = [audit_row(r, reviews[r['id']], decisions[r['id']], nodes, concepts, pages, occurrence[r['id']]) for r in records]
    result = totals(rows)
    if result['independentlyVerified'] != 326 or result['ownerAdjudicatedWithQualifications'] != 7 or result['ownerApprovals'] != 0 or result['existingMapping'] != {'needs-review': 36, 'proposed': 40, 'verified': 257}:
        raise ValueError('Protected academic/mapping/approval baseline differs')
    if {r['sourcePdfPages'][0] for r in rows if r['extraction']['effective'] == 'partial'} != {e['sourcePages'][0] for e in decisions.values() if e.get('partialExtraction')}:
        raise ValueError('Partial extraction repair queue must match all 12 current defects')
    write_outputs(report_folder(), artifacts(rows, ledger, coverage), check)
    verify_preservation(before)
    print(dump({'checkOnly': check, 'protectedFilesUnchanged': len(before), **result}))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Verify report idempotency without writing')
    parser.add_argument('--textbook', type=Path, default=qa.TEXTBOOK)
    args = parser.parse_args()
    run(args.check, args.textbook)
