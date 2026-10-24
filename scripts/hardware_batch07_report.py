"""Render private Batch 7 reports from the existing validated candidate package."""
from collections import Counter
import json
import hardware_batch07 as b
import approval_batch07 as final


def write():
    m=final.check();h=b.h;qa=b.qa;root=b.WORK
    audit=h.read_json(root/'audit.json');triage=h.read_json(root/'uncertain-triage.json')
    ledger,records,before,current,expected,published=b.load_context()
    entries={e['id']:e for e in m['candidates']}
    byid={r['id']:r for r in records}
    selected=set(entries)
    preserved=0
    for r in records:
        old,new=before[r['id']],current[r['id']]
        for key in set(old)|set(new):
            if key not in b.core.DIMENSIONS|{'preparationHistory'} and old.get(key)!=new.get(key):raise ValueError('Academic, metadata or approval history changed')
        if r['id'] not in selected:
            if old!=new:raise ValueError('Nonselected review changed')
            preserved+=1
    totals={'native':333,'independentlyVerified':sum(h.valid_verification(r,current[r['id']]) for r in records),
        'priorApprovals':sum(h.valid_approval(r,current[r['id']]) for r in records),
        'publicQuestions':len(published),'unpublishedHistorical':333-sum(q['id'].startswith('HIST-') for q in published),
        'selected':len(selected),'unchangedNonselectedReviews':preserved,'academicChanges':0,'newApprovals':0,
        'dispositions':audit['counts'],'existingHighlightsReused':len(m['conceptDefinitions']),'newHighlights':len(m['highlightIntegration']),
        'remainingHardwareAfterCandidateSelection':56-len(selected),
        'mappingTotals':dict(Counter(v['mapping']['status'] for v in current.values())),
        'extractionTotals':dict(Counter(h.effective_extraction(r,current[r['id']]) for r in records))}
    h.write_json(root/'preservation-and-totals.json',totals)
    # Full source excerpts and native evidence stay in the ignored JSON package.
    lines=['# Complete remaining Hardware audit — private','',
        f'Baseline `{b.BASELINE}`. All 56 original crops were pixel-compared against Technology-01. The complete 487-page Volume 1 text was indexed and searched; relevant teaching pages and figures were visually checked. All 56 received individual source-image and explanation review. No classifications outside this list were applied.',
        '', '| Initial disposition | Count | Final preparation |','|---|---:|---|',
        '| Ready without repairs | 0 | None claimed |','| Repairable | 31 | Bounded editorial/source-mapping repairs completed |',
        '| Deferred / protected | 25 | Native objects unchanged; includes all seven protected cases |','| Reclassified | 0 | No evidence-supported reclassification applied |',
        '', 'Disposition is mutually exclusive. The 31 repairable entries become technically eligible after documented repairs; they are not counted twice. Every candidate remains unapproved. The other 41 private records remain outside selection; the nine uncertain records received read-only triage.',
        '', '| Canonical ID / physical PDF | Exam | Academic / protected | Disposition | Source heading / concept | Book printed / physical pages | Decision and next action |', '|---|---|---|---|---|---|---|']
    for row in audit['questions']:
        r=byid[row['id']];refs=', '.join(f'{e["printedPage"] if e["printedPage"] is not None else "unnumbered"}/{e["pdfPage"]} ({e["role"]})' for e in row['textbookEvidence'])
        lines.append(f'| {r["id"]} / {row["pdfPage"]} | {r["year"]}{r["season"]} Q{r["number"]} FE AM A | {row["academicVerified"]} / {row["protected"]} | {row["disposition"]} | {row["headingNumber"]} / {row["conceptId"] or "unassigned"} | {refs} | {row["decisionReason"]} Next: {row["nextAction"]} |')
    lines+=['','The JSON audit includes full source excerpts, raw page-text hashes, question/image bindings, baseline review hashes, exact routes, accessibility status, grading flags, highlight availability and per-record blockers. `review-diff.json` records each selected native before/after editorial dimension. No raw images or private question payloads enter Git or the public build.']
    (root/'HARDWARE-AUDIT.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    lines=['# Batch 7 exact final owner-review candidates','',f'{len(selected)} questions; eight existing highlights; zero new highlights. Candidate-set fingerprint: `{m["candidateSetFingerprint"]}`.',
        f'Final manifest SHA-256: `{h.digest((final.folder()/"manifest.json").read_bytes())}`. All student-visible fields equal the frozen reviewed preview. No final owner approval has been granted.',
        '', '| ID / PDF page | Exact heading / concept | Source evidence | Editorial repair | Publication fingerprint | Context fingerprint |', '|---|---|---|---|---|---|']
    for e in m['candidates']:
        r=e['record'];v=e['review'];old=before[r['id']]
        changed=[key for key in b.core.DIMENSIONS if old.get(key)!=v.get(key)]
        refs=', '.join(f'printed {p["printedPage"]}/PDF {p["pdfPage"]}' for p in v['mapping']['evidence'])
        lines.append(f'| {r["id"]} / {r["regions"][0]["pdfPage"]} | {v["mapping"]["headingNumber"]} / {v["mapping"]["conceptId"]} | {refs} | {", ".join(sorted(changed))} | {e["publicationFingerprint"]} | {e["approvalContextFingerprint"]} |')
    lines+=['','All 31 retain independent verification, original immutable image, original correct answer, complete worked explanation, FE/Morning/Subject A metadata and stable occurrence identity. Final approval is the only publication blocker.',
        '', 'Three LED questions explicitly supply ON polarity and all port-to-segment wiring; their primary teaching is radix conversion. The textbook is not claimed to teach LED decoder circuitry. The common-anode question without an explicit polarity rule remains deferred. Separate cache-table and alternating-bit examination occurrences retain distinct IDs and images.',
        '', 'The first private draft is preserved in `draft-01/`. Final source reinspection restored the p.224 negation-bar wording and the explicit question prompts on pp.93/114/118/142. No option, academic answer, explanation, source image or metadata changed in that correction. Every final review records literal/image-only source options separately from editorial notation and diagram descriptions.',
        '', '## Local review', '',
        '`node scripts/private-student-preview-server.mjs --batch07` — http://127.0.0.1:4348/',
        '', '`node scripts/question-review-server.mjs --approval-candidates --batch7` — http://127.0.0.1:4350/',
        '', 'Both services bind loopback, require exact Host/Origin, serve hash-allowlisted assets and reject mutation methods. Student progress uses a separate disposable namespace. The owner gallery has no scripts, forms or approval controls.',
        '', '## Later approval procedure', '',
        'Owner review must authorize this exact manifest SHA-256, candidate-set fingerprint, all 31 individual publication/context fingerprints and the eight unchanged concept definitions. This milestone provides no authorization or release transition. A later explicit release milestone must revalidate the frozen package, source pixels, all academic/editorial mappings, all prior approvals and publication dry run, then use the existing fingerprint-bound approval/publisher architecture. Any material content, image, answer, explanation, mapping, accessible description or highlight change invalidates the reviewed authorization. Do not refresh stale fingerprints automatically.',
        '', 'The Batch 7 publisher entry point currently rejects every non-dry-run invocation before loading source material. No approval, publication, merge or deployment occurred.']
    (root/'PREPARED-CANDIDATES.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    lines=['# Remaining Hardware roadmap — private','',
        'After preparing 31 candidates, 25 Hardware records remain deferred; none is ready-but-unselected. The whole private catalog still contains 97 records because preparation does not publish anything.',
        '', '| Blocker | PDF pages | Required next action |','|---|---|---|']
    deferred=[r for r in audit['questions'] if not r['selected']]
    for code in sorted({k for r in deferred for k in r['blockers']}):
        group=[r for r in deferred if code in r['blockers']]
        lines.append(f'| {code} | {", ".join(str(r["pdfPage"]) for r in group)} | {group[0]["nextAction"]} |')
    lines+=['','Daisy-chain physical p.112 / printed p.106 has genuine direct teaching in an intact topology box. A future bounded extension must bind an existing source crop/figure to its actual 5-5-1 node; the current paragraph-only highlight validator cannot do so. Do not replace it with an unrelated SCSI paragraph or redraw the source.',
        '', 'For ASCII parity, retain Chapter 1 character-code context at physical p.34 / printed p.29 and explicit Chapter 5 even-parity algorithm support at physical p.307 / printed p.297 as separately typed evidence. A future secondary-evidence extension must validate real chapter/page labels without changing the primary chapter merely to satisfy current gates.',
        '', 'The p.313 numeric distractor contradiction and p.191 incomplete worked reasoning require separate academic review; current verified answers and explanations were preserved. The seven qualified cases remain excluded, especially p.119 with two valid answers A and D.',
        '', 'Other Volume 1 chapters: 29 preserved; provisionally outside Volume 1: three preserved; uncertain classifications: nine preserved and unselected. Chapter 1 integration is not complete.',
        '', '## Nine uncertain classifications — read-only','', '| ID / PDF | Context | Reason / next action |','|---|---|---|']
    for row in triage['questions']:lines.append(f'| {row["id"]} / {row["pdfPage"]} | {row["likelyContext"]} | {row["reason"]} {row["nextAction"]} |')
    (root/'REMAINING-HARDWARE-ROADMAP.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    h.write_json(final.folder()/'equality-report.json',m['previewEquality']|{'candidateSetFingerprint':m['candidateSetFingerprint'],'studentHashes':{e['id']:e['studentVisibleSha256'] for e in m['candidates']}})
    h.write_json(final.folder()/'owner-review-checklist.json',[{'id':e['id'],'pdfPage':e['record']['regions'][0]['pdfPage'],'readiness':e['readiness'],'remainingBlockers':e['remainingBlockers'],'publicationFingerprint':e['publicationFingerprint'],'approvalContextFingerprint':e['approvalContextFingerprint']} for e in m['candidates']])
    print(json.dumps(totals))


if __name__=='__main__':write()
