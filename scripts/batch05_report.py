"""Reproduce the private Batch 5 handoff from the checked candidate package."""
from collections import Counter
import csv
import io
import approval_batch05 as final


def write():
    manifest=final.check();b=final.b;h=final.h;qa=final.qa
    ledger,records,before,current,expected,published=b.load_context()
    entries=manifest['candidates'];ids=set(manifest['questionIds']);work=b.WORK
    preservation={'publishedQuestionImagePairs':len(published),'priorApprovals':156,
        'independentlyVerified':sum(h.valid_verification(r,current[r['id']]) for r in records),
        'qualifiedAdjudications':sum(bool(v.get('ownerAdjudication')) for v in current.values()),
        'privateUnapproved':sum(v['approval']['status']=='unapproved' for v in current.values()),
        'newApprovals':0,'newPublications':0,'academicChanges':0,
        'protectedPages':sorted(b.core.PROTECTED),'publicFilesEqual':True,'priorReleaseEvidenceEqual':True,
        'immutableRecordsEqual':records==h.read_json(work/'before/questions.json'),
        'sourceImportManifestBytesEqual':(h.WORK/'manifest.json').read_bytes()==(work/'before/manifest.json').read_bytes(),
        'beforeExtraction':dict(Counter(v['extraction']['status'] for v in before.values())),
        'effectiveExtraction':dict(Counter(v['extraction']['status'] for v in current.values())),
        'beforeMapping':dict(Counter(v['mapping']['status'] for v in before.values())),
        'effectiveMapping':dict(Counter(v['mapping']['status'] for v in current.values())),
        'academicFingerprints':{r['id']:qa.object_hash({k:current[r['id']].get(k) for k in ['verification','explanation','academicReviews','ownerAdjudication','metadata','approval']}) for r in records}}
    for r in records:
        old,new=before[r['id']],current[r['id']]
        for key in set(old)-b.core.DIMENSIONS-{'preparationHistory'}:
            if old[key]!=new[key]:raise ValueError('Unrelated or academic mutation: '+r['id'])
        if r['id'] not in ids and old!=new:raise ValueError('Unselected review changed')
    final.c.save(work/'preservation-report.json',preservation)
    equality=manifest['previewEquality']|{'candidateSetFingerprint':manifest['candidateSetFingerprint'],
        'studentHashes':{e['id']:e['studentVisibleSha256'] for e in entries},
        'approvalContextFingerprints':{e['id']:e['approvalContextFingerprint'] for e in entries}}
    final.c.save(final.folder()/'equality-report.json',equality)
    eligibility=[{'id':e['id'],'pdfPage':e['record']['regions'][0]['pdfPage'],
        'year':e['record']['year'],'season':e['record']['season'],'number':e['record']['number'],
        'concept':e['review']['mapping']['conceptId'],'readiness':e['readiness'],
        'eligible':e['technicalEligibility'],'blockers':e['remainingBlockers'],
        'publicationFingerprint':e['publicationFingerprint'],'contextFingerprint':e['approvalContextFingerprint'],
        'dimensionFingerprints':e['dimensionFingerprints']} for e in entries]
    if not all(e['eligible'] for e in eligibility):raise ValueError('Final candidate not technically eligible')
    final.c.save(final.folder()/'eligibility-report.json',eligibility)
    final.c.save(work/'highlight-inventory.json',{'reused':[c for c in manifest['conceptDefinitions'] if not c['newConcept']],
        'newSourceValidated':manifest['highlightIntegration'],'deferred':ledger['deferred']})
    buffer=io.StringIO();writer=csv.writer(buffer)
    writer.writerow(['canonicalId','physicalPdfPage','year','season','question','exam','paper','subject','concept','heading','bookPhysicalPages','bookPrintedPages','eligible','approval','publicationFingerprint','approvalContextFingerprint'])
    lines=['# Technology-01 Hardware Batch 5 — combined private preparation and final approval package','',
        '40 independently verified candidates across 16 concepts; 15 existing highlights reused and one original flip-flop paragraph newly source validated. All forty are technically eligible, unapproved and private. Final owner publication approval is absent for all forty; three additionally need explicit owner editorial approval for the new highlight. No technical blocker remains.',
        f'Baseline: `{b.BASELINE}` on `{b.BRANCH}`. Production remains deployment `9cb6b8dc-1914-4676-9ae0-3170b43f2074`. The final implementation commit is recorded separately in `completion-receipt.json`.',
        f'Candidate-set fingerprint: `{manifest["candidateSetFingerprint"]}`. Manifest SHA-256: `{h.digest((final.folder()/"manifest.json").read_bytes())}`.',
        '', '## Selection and exact inventory','',
        'The original audit was checked against its frozen baseline and all 333 immutable current identities. Of 177 private records, 136 are proposed Hardware, 29 another Volume 1 chapter, three outside Volume 1, nine uncertain. All 156 published historical occurrences and seven qualified adjudications were excluded. Selection prioritizes a new sequential-circuit concept, low-count bit representation/memory hierarchy, bounded partial-extraction repairs, and contrasting calculations and circuit/table layouts.',
        'The remaining defensible source pool is concentrated in logic and numeric representation: eight additions in each. Other weak concepts were not forced. No safe new auxiliary-storage candidate was found: DVD-RAM endurance lacks exact teaching; already published disk examples remain references. The exact repeated cache table on PDF p.258 (published p.222) and USB p.99 (selected p.175) were deferred to avoid redundant clones. Coverage for every existing concept, all published associations and every excluded record is in coverage-analysis.json and excluded-deferred.json. The latter contains 156 published plus 137 unselected private records; the forty selected also remain part of the 177 private/unapproved total.',
        '', '| Canonical ID | PDF / exam | Concept / heading | Textbook printed (physical) | Eligible / approval |','|---|---|---|---|---|']
    for e in entries:
        r=e['record'];m=e['review']['mapping'];page=r['regions'][0]['pdfPage'];proof=m['evidence']
        refs=', '.join(f'{p["printedPage"]} ({p["pdfPage"]})' for p in proof)
        lines.append(f'| {e["id"]} | {page} / {r["year"]}{r["season"]} Q{r["number"]} FE AM A | {m["conceptId"]} / {m["headingNumber"]} | {refs} | yes / unapproved |')
        writer.writerow([e['id'],page,r['year'],r['season'],r['number'],'FE','AM','A',m['conceptId'],m['headingNumber'],
            ';'.join(str(p['pdfPage']) for p in proof),';'.join(str(p['printedPage']) for p in proof),True,'unapproved',e['publicationFingerprint'],e['approvalContextFingerprint']])
    (work/'inventory.csv').write_text(buffer.getvalue(),encoding='utf8')
    lines+=['','Section distribution: '+', '.join(f'{key}: {count}' for key,count in sorted(Counter(e['review']['mapping']['sectionId'] for e in entries).items()))+'.',
        'Concept distribution: '+', '.join(f'{key}: {count}' for key,count in manifest['conceptCounts'].items())+'.']
    repairs=['# Exact private editorial before/after','',
        'Images, raw transcripts, academic answers and worked explanations are unchanged. The JSON diff preserves exact native objects; the pairs below show the effective accessible content before and after preparation.']
    for e in entries:
        r=e['record'];prior=before[e['id']]['extraction'];new=e['studentVisible']
        old={'imageDescription':prior.get('imageDescription','[No reviewed accessible description stored. Raw extracted stem follows.] '+r['questionText']),
             'optionText':prior.get('optionText',{key:'[No reviewed accessible choice stored. Raw extraction follows.] '+r['options'][key] for key in 'abcd'})}
        repairs += ['',f'## {e["id"]} — physical PDF p.{r["regions"][0]["pdfPage"]}',
            f'Extraction: {before[e["id"]]["extraction"]["status"]} → {e["review"]["extraction"]["status"]}. Mapping: {before[e["id"]]["mapping"]["status"]} → verified.',
            '', 'Before accessible question:',old['imageDescription'],'','After accessible question:',new['imageDescription'],
            '', '| Choice | Before | After |','|---|---|---|']
        for key in 'abcd':
            clean=lambda s:str(s).replace('|','&#124;').replace('\n','<br>')
            repairs.append(f'| {key.upper()} | {clean(old["optionText"][key])} | {clean(new["optionText"][key])} |')
        repairs+=['',e['finalSourceReview']['inspection'],
            'Previous review SHA-256: `'+qa.object_hash(before[e['id']])+'`. Final extraction SHA-256: `'+e['dimensionFingerprints']['extraction']+'`.']
    (work/'editorial-repairs.md').write_text('\n'.join(repairs)+'\n',encoding='utf8')
    lines+=['','## Editorial and mapping evidence','',
        'review-diff.json contains exact before/after extraction, classification and mapping objects for all forty, with previous/revised fingerprints. Original source images, raw transcripts and all academic/examination/provenance/approval objects remain unchanged. The final source-review ledger and gallery retain literal notation and editorial clarifications separately.',
        'PDF pp.128 and 288 resolve two partial extractions: inequalities and exponent/multiplication layout. PDF pp.125,126,146,223 remove solution-bearing accessible descriptions and substitute literal wiring or signal levels. Full source stems, choice tables and diagram paths were restored for pp.154,158,190,208,209,243,277. Mathematical notation was restored for pp.266,290,291,301; p.252 retains its explicit 0.11 µs miss cost. Other selected stems/options were source-bound and whitespace-normalized. The four original NAND/NOR alternatives and latch table polarities were independently truth-table checked.',
        'PDF p.208 has truncated output group headings “Ou”; the legible Q/Q̅ columns make the table unambiguous. The original image/raw text retain that defect; expanded output wording is labeled editorial. The source latch label “unstable” remains literal, with the existing post-grading explanation of forbidden states preserved. No source images were edited.',
        'PDF p.274 retains the verified explanation’s distinction between complete service times (3.7 cycles) and incremental serial costs (4.0). The source wording and actual textbook weighted-time model support the former; neither a matching key nor absence of 4.0 is treated as proof. PDF p.298 is mapped to the directly taught 2^n bit-combination rule, explicitly as an application to register identifiers rather than a claimed textbook instruction-format definition. p.266 combines main-memory address selection with secondary radix evidence.',
        'All selected mappings have exact source excerpts, printed/physical references and page text hashes. Legacy heading-only citations are replaced. Mapping status remains independent of academic verification. The new flip-flop highlight is the unchanged sequential-circuit paragraph at heading3-4-1, printed62/physical67. Its adjacent original NAND diagram and p.68 NOR definition support the three source questions. No question-specific result or option letter is inserted.',
        '', '## Preservation and gates','',
        '576 public question/image pairs, all 156 earlier approvals, 333 immutable records and all academic histories are preserved. All seven qualified cases (physical110,112,119,152,179,180,181) remain unselected and byte/object unchanged; p.119 is not ordinary single-answer graded. The 420 Practice records, authoritative matching rules and all published concept/image/explanation fingerprints remain unchanged.',
        f'Effective extraction totals: {preservation["beforeExtraction"]} → {preservation["effectiveExtraction"]}. Effective mappings: {preservation["beforeMapping"]} → {preservation["effectiveMapping"]}. The original import manifest is preserved byte-for-byte; these effective totals are computed from reviewed objects, not written into historical import evidence.',
        'The original before snapshot, all prior release files and public source/assets are hash guarded. Final package binds the exact preview visible fields, source images, source passages, concepts and every publication/context fingerprint. Repeated prepare validates existing output and rejects stale inputs; it does not silently rebind them. Initial private packages are archived under initial-diagnostic-count-label and pre-commit-line-ending-normalization after a CLI count-label correction and normalization to the repository LF policy. Explicit revalidation proves identical candidate, native, source-review and served student/owner content; only implementation/preparation bindings change. No previous release evidence was rewritten.',
        '', '## Local review and later authorization','',
        'Student preview: http://127.0.0.1:4340/ — `node scripts/private-student-preview-server.mjs --batch05`.',
        'Final read-only owner gallery: http://127.0.0.1:4342/ — `node scripts/question-review-server.mjs --approval-candidates --batch5`.',
        'The preview contains forty new private additions plus 179 unchanged published Hardware references, with separate collection/filter counts. GET/HEAD-only servers bind loopback and enforce Host/Origin checks, checksum allowlists and CSP. Raw source PDFs/native JSON/unselected images are denied. The preview uses a unique disposable progress namespace and no Firebase/auth runtime. Final owner gallery has no script, form, approval action or progress writer.',
        'Recheck with `python scripts/hardware_batch05.py check` and `python scripts/approval_candidates.py check --batch 5`. The existing publisher `--batch 5 --dry-run` requires the exact candidate package and exports only the already approved156. Expected additions/updates/conflicts are all zero. Batch5 non-dry-run is rejected before source access.',
        'A later separate explicit owner authorization must bind the exact manifest SHA-256, candidate-set fingerprint, each publication fingerprint and approvalContextFingerprint, plus the new highlight definition hash for its three linked questions. Use the existing owner-approval workflow; recheck exact source/preview/fingerprints before approving and again before publication. Any change to the question, answer, explanation, accessible description, metadata, mapping, source image/passage or highlight invalidates the old authorization. This milestone grants none.',
        '', '## Validation and production operations','',
        'Machine-readable test results and raw logs are in validation/. Local browser screenshots are private. validation-results.md summarizes final checks, publisher dry run and production-build comparison. completion-receipt.json records the final pushed feature commit and clean working tree.',
        'Release3/4 live verification remains unresolved: 54 provider/local HTML hash differences have not been proved harmless, and TLS resets/timeouts blocked live UI verification, including previous healthy deployments. Existing deployment/content evidence is preserved; no application regression is established. This milestone uses local production regressions and makes no new transport investigation, deployment or rollback. Report this risk again and consider new evidence before a later release.',
        'No approval, publication, merge, deployment, additional historical PDF, Practice-repository modification, paid infrastructure, Cloudflare/DNS change, Firebase mutation or student-progress reset occurred. Stop for owner review.']
    (work/'completion-report.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    return manifest


if __name__=='__main__':
    result=write();print('Private handoff reproduced:',len(result['candidates']),'unapproved candidates;',result['candidateSetFingerprint'])
