"""Reproduce the private Batch 6 owner handoff without approving or publishing."""
import csv,io,json,subprocess
from collections import Counter
from pathlib import Path
import hardware_batch06 as b
import approval_batch06 as f


def write():
    h=b.h;qa=b.qa;work=b.WORK;m=f.check()
    ledger,records,before,reviews,expected,published=b.load_context()
    preservation=h.read_json(work/'preservation-report.json')
    if not preservation or preservation['candidateManifestSha256']!=h.digest((f.folder()/'manifest.json').read_bytes()):raise ValueError('Reproduce current preservation evidence first')
    bank=h.read_json(b.APP/'src/content/pilot-bank.json')
    counts=Counter(e['review']['mapping']['conceptId'] for e in m['candidates'])
    sections=Counter(e['review']['mapping']['sectionId'] for e in m['candidates'])
    headings=Counter(e['review']['mapping']['headingNumber'] for e in m['candidates'])
    out=io.StringIO();writer=csv.writer(out)
    writer.writerow(['canonical_id','technology01_physical_pdf_page','year','season','question_number','section','heading','concept','book_printed_pages','book_physical_pages','technical_eligibility','approval','publication_fingerprint','context_fingerprint'])
    rows=[];bindings=[];repairs=['# Batch 6 editorial and mapping repairs','', 'Only the selected classification, mapping and accessible extraction dimensions changed. All source images/raw transcripts, academic verification/explanation objects, owner metadata and approval objects are unchanged. The precise before/after data is in review-diff.json.','']
    for e in m['candidates']:
        r=e['record'];v=e['review'];mapping=v['mapping'];evidence=mapping['evidence'];page=r['regions'][0]['pdfPage']
        labels=', '.join(f"{p['printedPage']} ({p['pdfPage']}) {p['role']}" for p in evidence)
        rows.append(f"| {page} | {r['id']} · {r['year']}{r['season']} Q{r['number']} | {mapping['headingNumber']} / {mapping['conceptId']} | {labels} | Eligible; unapproved |")
        bindings.append(f"| {r['id']} | {e['publicationFingerprint']} | {e['approvalContextFingerprint']} |")
        writer.writerow([r['id'],page,r['year'],r['season'],r['number'],mapping['sectionId'],mapping['headingNumber'],mapping['conceptId'],','.join(str(p['printedPage']) for p in evidence),','.join(str(p['pdfPage']) for p in evidence),e['technicalEligibility'],'unapproved',e['publicationFingerprint'],e['approvalContextFingerprint']])
        repairs += [f"## {r['id']} / original PDF page {page}",'',next(row['editorialNote'] for row in ledger['entries'] if row['id']==r['id']),f"Final source inspection: {e['finalSourceReview']['inspection']}",'']
        for dimension in ['classification','mapping','extraction']:
            if before[r['id']].get(dimension)!=reviews[r['id']].get(dimension):
                repairs += [f'### {dimension}: before','```json',json.dumps(before[r['id']].get(dimension),ensure_ascii=False,indent=2),'```',f'### {dimension}: after','```json',json.dumps(reviews[r['id']].get(dimension),ensure_ascii=False,indent=2),'```','']
    (work/'inventory.csv').write_text(out.getvalue(),encoding='utf8')
    (work/'editorial-repairs.md').write_text('\n'.join(repairs)+'\n',encoding='utf8')
    # Coverage for every authoritative numbered subsection, including empty ones.
    nodes=h.read_json(h.ROOT/'src/content/hardware-toc.json')['nodes'];audit_rows=[]
    for node in nodes:
        old=[q for q in published if q.get('format')=='historical' and q['review']['mappings'][0]['subsectionId']==node['id']]
        audit_rows.append({'subsectionId':node['id'],'headingNumber':node['number'],'title':node['title'],'sectionId':node['sectionId'],'publishedHistorical':len(old),'newPrivate':headings.get(node['number'],0)})
    h.write_json(work/'subsection-coverage.json',audit_rows)
    deferred=h.read_json(work/'excluded-deferred.json');remaining=[row for row in deferred if row['id'] not in {q['id'] for q in published}]
    h.write_json(work/'selected-distribution.json',{'concepts':dict(counts),'sections':dict(sections),'headings':dict(headings),'selected':40,'privateDeferred':len(remaining),'privateDeferredCategories':dict(Counter(row['category'] for row in remaining))})
    log=work/'validation/gates.log'
    raw=log.read_text('utf8');dry=json.loads(raw[raw.rfind('\n{\n  "dryRun"'):].strip())
    if dry!={'dryRun':True,'approvedInputs':196,'additions':[],'updates':[],'conflicts':[]}:raise ValueError('Expected zero-publication dry run required')
    h.write_json(work/'publisher-dry-run.json',{**dry,'newlyApprovedInputs':0})
    sources={c['id']:c for c in h.read_json(h.ROOT/'src/content/concepts.json')}
    coverage=h.read_json(work/'coverage-analysis.json')
    lines=['# Technology-01 Hardware Batch 6 — final private owner handoff','',
      '**Forty independently verified candidates are technically eligible for owner review. All forty remain unapproved and private. No publication, merge or deployment occurred.**','',
      '## Baseline and verified inventory','',
      f'Fresh feature branch `{b.BRANCH}` was created from fetched main `{b.BASELINE}`. The original audit source identities were revalidated against all 333 immutable records and the complete 487-page Volume 1. Metadata remains owner-confirmed FE / Morning / Subject A for all 333.',
      'Historical classification inventory remains 292 Hardware, 29 other Volume 1, three provisionally outside Volume 1 and nine uncertain. Of 333 historical records, 196 are published and 137 remain private. The 96 unpublished Hardware classifications include seven protected qualified cases and are not a readiness guarantee. Only the forty selected classification/editorial proposals were applied. Academic totals remain 326 independently verified and seven qualified owner adjudications.','',
      '## Exact forty-question selection','',
      '| Technology-01 physical page | Canonical ID / examination | Exact heading / concept | Book printed (physical), evidence role | Readiness |','|---|---|---|---|---|',*rows,'',
      'All original occurrence identities are retained. No matched authoritative Practice occurrence/image collision was selected. No qualified owner-adjudicated question is in this set. Source image/raw text checksums and exact FE/AM/A metadata are bound in the final manifest.','',
      '## Coverage and selection rationale','',
      'Coverage was evaluated across all 45 public concepts and every authoritative numbered subsection, rather than treating the 616-question sitewide catalog as a Hardware collection. See coverage-analysis.json and subsection-coverage.json for the full inventory. Existing zero-history concepts include bit-masks, bus-transfer and 3D printing; no unsupported association was made merely to fill those gaps.',
      'The defensible remaining exact teaching placements are concentrated in Data Representation and CPU/Main Memory. No additional Basic Configuration, Auxiliary Storage or I/O question was forced into this batch. Their unsupported or crop/insert-dependent candidates remain explicitly deferred. Selection includes literal multi-stage gate evaluation, a four-input selector network, truth-table interpretation, Boolean range negation, bitwise applications, fractional radix arithmetic, indirect-address diagrams and distinct cache timing conditions.','',
      '| Existing concept | Previously published historical | New private questions |','|---|---:|---:|']
    for cid,count in sorted(counts.items()):
        old=next(c['beforeHistoricalCount'] for c in coverage if c['conceptId']==cid)
        lines.append(f'| {cid} | {old} | {count} |')
    lines += ['',f'Section distribution: `{dict(sections)}`. Subsection distribution: `{dict(headings)}`.',
      'The one-question cache-write-policies collection gains a private comparison exercise; memory-hierarchy gains a direct multi-level-cache application. The generic logic-gates collection supplies the existing exact source anchor for literal gate operations; the unrelated Data Representation shift/bit-masks anchor is never reused. No new highlight is necessary: **13 reused, zero newly proposed**, with deferred source locations separately inventoried.','',
      '## Editorial/source decisions','',
      'All forty original crops were pixel-compared against their Technology-01 PDF regions using the existing QA engine. Complete source images, labels, option order and original symbols are preserved. Source pages were rendered for readable visual review; no original image was edited or regenerated. Supporting text was copied literally from normalized original page text, with text/source hashes and actual printed/physical labels.',
      'Accessible descriptions restore complete stems, all circuit branches, arrow direction, junction dots, negation scope, table rows/columns and timing units. The selector network now describes all four branches equally; it no longer focuses only on the path requested by the question. The source dictates that main-memory miss timing already includes the cache lookup where applicable. No derived answer or correct-choice label is inserted before grading.',
      'Physical p.220 contains missing opening parentheses in choices a/c. The source image/raw transcript and final literal-option layer retain this source defect. Balanced accessible notation is explicitly identified as editorial; no option identity, independent answer or worked explanation changes. This bounded typographic repair is distinct from missing table headers or ambiguous source labels, which remain deferred.',
      'Broad cache mappings were narrowed to the actual memory-hierarchy and cache-write-policy paragraphs. The selector question uses directly taught AND/OR/NOT evaluation applied to a network defined by the question; no named multiplexer-design passage is invented. The bitwise exercises apply the taught Boolean truth functions per supplied bit position and radix weights; the book is not claimed to state the examination’s modulo identity. A range-negation question is classified by the Boolean skill it tests, not automatically as Chapter 2 because its stem mentions a loop.',
      'All exact before/after editorial fields and per-question inspection notes are in editorial-repairs.md, review-diff.json and final-approval/source-review.json. Academic answer/explanation/verification objects were not rewritten.','',
      '## Deferred records and source-capability proposals','',
      f'The complete exclusion ledger has {len(deferred)} nonselected records: 196 already published and {len(remaining)} still private. Every row preserves its source ID/page, classification, reason and original review hash. Other-chapter/outside/uncertain recommendations were not applied.',
      *[f"- Physical p.{row['pdfPage']}: {row['reason']}" for row in ledger['deferred']],
      'Additional nonselected Hardware rows are explicitly marked as lower-priority comparable/repeated exercises within this bounded forty-question selection, without claiming new readiness. The full JSON ledger is authoritative, including all seven protected cases.',
      'Potential future capability work is documented in deferred-capability-proposals.md: typed figure/crop evidence and highlight anchors, genuine null printed-page/unnumbered insertion support, and separately labeled secondary-chapter support. Existing daisy-chain teaching, UART text and a JK inset are acknowledged as present. They are not repeatedly dismissed as absent merely because an older mapping strategy failed. No broad mapping/publishing change was implemented here.','',
      '## Exact final owner approval package','',
      f'Final manifest: `{f.folder()/"manifest.json"}`.',
      f'Manifest SHA-256: `{preservation["candidateManifestSha256"]}`.',
      f'Candidate-set fingerprint: `{m["candidateSetFingerprint"]}`.',
      'Forty candidates are technically eligible; forty owner-approval blockers remain, one per question. Every approval object is unchanged and unapproved. The manifest binds original/source hashes, academic/explanation/extraction/metadata/classification/mapping dimensions, exact textbook support, grading eligibility and final visual review. All forty student-visible payloads and thirteen concept definitions equal the validated preview.','',
      '| Canonical ID | Future publication approval fingerprint | Source/preview context fingerprint |','|---|---|---|',*bindings,'',
      'A separate explicit owner authorization must identify this exact manifest/set and each publication/context fingerprint. Material changes to question text, choices, answer, explanation, image, accessibility, metadata, placement, supporting passage or highlight require new review and invalidate old bindings. Use the existing native owner-approval system only after that separate authorization; the current publisher rejects non-dry-run Batch 6 publication before source access.','',
      '## Private review and representative walkthroughs','',
      'Student preview: http://127.0.0.1:4344/ — `node scripts/private-student-preview-server.mjs --batch06`.',
      'Final owner gallery: http://127.0.0.1:4346/ — `node scripts/question-review-server.mjs --approval-candidates --batch6`.',
      'Counts: 616 published sitewide; 219 unchanged published Hardware collection references; forty new private additions; 259 preview questions. Per-concept published/private, collection, source, year and unanswered counts are separate. All 13 source links, all 40 question images/transcriptions/options/grades and feedback were exercised in the private student browser suite. Owner review groups all 40 by concept, exposes exact support/fingerprints/blockers and links to the private source reader. Its complete source images open full-size.',
      'Both servers are loopback-only, GET/HEAD-only, exact Host/Origin restricted and SHA-allowlisted. Raw PDFs, native review JSON, private manifest paths and unselected images are denied. The preview uses only the disposable `itpecTextbook:privateHardwareBatch06:` namespace. The owner gallery has no scripts/forms/approval controls/progress writes. No real guest/account progress or production Firebase data is touched.','',
      '## Preservation and validation','',
      'All 616 published records/images/explanations, 196 prior historical approvals, all 333 academic/metadata histories and seven qualified adjudications are unchanged. The other 293 native review objects are unchanged. Original source/import files remain byte-identical. All 137 unpublished historical records remain private/unapproved, including this batch.',
      f'Effective extraction totals: `{preservation["beforeExtraction"]}` → `{preservation["effectiveExtraction"]}`. Mapping totals: `{preservation["beforeMapping"]}` → `{preservation["effectiveMapping"]}`. The immutable historical import manifest was not rewritten to recount these reviewed totals.',
      f'All {preservation["priorPrivateEvidenceFilesUnchanged"]} previous private release/preparation evidence files remain byte-identical. The local production build matches all 996 Release 5 baseline files, with no added, missing or changed file.',
      'See validation-results.md/json and retained logs for final Python, source-calculation, application, browser, demo-account/rules, types, build and dry-run results. Publisher dry run: 196 existing approved inputs; **zero newly approved inputs, zero additions, zero updates, zero conflicts**. No public image or record was added.',
      'One initial owner-browser assertion correctly found absent direct source-reader links on reused-concept cards. The initial unapproved package was preserved under draft-01-owner-concept-links. The established Batch 4 link pattern was added privately; gallery-link-revalidation.json proves identical forty candidate payloads, candidate-set fingerprint, all preview source/served asset bytes, native bytes and public bytes. Only implementation/preparation/gallery bindings changed, explicitly rather than silently. The full owner suite then passed. Exact private arithmetic operands/choices/keys were moved into bound ignored fixtures before commit; generic calculation tests reproduce the checks without checking source content into Git.','',
      '## Git and operational handoff','',
      'Only reusable adapters/tests and sanitized documentation are committed. No native records, source crops, PDF, private manifests, answer keys, screenshots or approval-candidate data are committed. The final feature commit, normal remote push, clean working tree and unchanged main are recorded in completion-receipt.json. Changed-file inventory is recorded there and in staged-files.json.',
      'Release 5 remains the production baseline; its 55 provider/local HTML hash differences and incomplete live HTML/UI verification remain unresolved. No benign transformation is assumed. No exhaustive transport probes, production requests, deployment, rollback, merge, hosting/Firebase/DNS change, new infrastructure or student-progress migration occurred during Batch 6.',
      '**Stop for owner review. A separate explicit Release 6 authorization is required before approval/publication/integration/deployment.**']
    index=lines.index('## Git and operational handoff')
    lines[index:index]=['## Final regression results','',*(work/'validation-results.md').read_text('utf8').splitlines()[2:],'']
    (work/'completion-report.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    return m


if __name__=='__main__':
    manifest=write();print('Private Batch 6 handoff reproduced:',len(manifest['candidates']),'unapproved candidates;',manifest['candidateSetFingerprint'])
