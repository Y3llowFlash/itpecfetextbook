# Hardware Batch 7 — private owner-review preparation

Baseline: Release 6, `1f179640110a374b2329664567eca63218bce344`.
Branch: `feature/technology01-hardware-batch07`.

All 56 remaining proposed Hardware records received individual source-image,
academic-explanation and textbook-placement review. The mutually exclusive initial
dispositions are 0 ready without repairs, 31 repairable, 25 deferred/protected and
0 reclassified. The bounded repairs for all 31 selected records are complete.
The seven protected qualifications are included in the 25 deferred records.
The nine uncertain classifications received separate read-only triage; none was
selected. The other 29 Volume 1 and three outside-Volume-1 records are unchanged.

The final package contains 31 independently verified single-answer candidates
across eight unchanged existing highlights. No new highlight was forced. All
candidates remain unapproved and exactly equal the validated private preview.
Original images, raw transcripts, answers, worked explanations, examination
identities, metadata provenance and academic/adjudication histories are preserved.

The private audit distinguishes genuine missing teaching from source defects,
academic explanation issues and limitations of current figure/secondary-evidence
associations. These have separate next actions; no unsupported exact mappings or
new textbook wording were introduced. The initial private draft and subsequent
source-transcription corrections remain recorded in the preparation history.

## Existing pipeline integration

- `hardware_batch07.py` uses the established native editorial reconciler and
  disposable student-preview adapter.
- `hardware_batch07_audit.py` validates all 56 source/snapshot-bound dispositions,
  the exact eligible selection and the separate nine-record uncertain triage.
- `approval_batch07.py` uses the existing candidate builder, source-review gate,
  student-visible equality, context fingerprints and read-only owner gallery.
- The shared exact-40 defaults remain unchanged for earlier batches. Batch 7
  explicitly supplies its exact smaller count and source-page set.
- `--batch 7 --dry-run` uses the existing publisher. Every non-dry-run Batch 7
  invocation fails before loading source data. No authorization transition was
  added.
- The Release 6 archival regression uses frozen release reviews plus the exact
  recorded approvals inside its test fixture. Live release validators remain
  strict; no native records are reset or rebound for tests.

All private inputs, images, review payloads, source excerpts and screenshots remain
under ignored `.local/historical-batches/technology01-hardware-batch07/`.
This document deliberately omits question text, source choices and answer keys.

## Validation

| Check | Result |
|---|---:|
| Python academic/source/editorial/approval regressions | 340 passed |
| Application unit tests | 111 passed |
| Private student browser checks | 43 passed |
| Read-only owner gallery | 5 passed; 4 other-batch cases not applicable |
| Local production browser regressions | 52 passed |
| Historical release browser regressions | 89 passed |
| Isolated Firebase account browser checks | 9 passed |
| Isolated Firestore rule checks | 12 passed |
| Astro and TypeScript | Passed, zero diagnostics |
| Production build | 56 pages, 656 question/image pairs |
| Production build comparison with Release 6 | All 1,036 files byte-identical |
| Repeated preparation | 541 native/preview/package files unchanged |
| Source-image comparison | All 56 original crops pixel-matched |
| Publisher dry run | 236 prior inputs; 0 additions/updates/conflicts |
| New publication approvals | 0 |

All 302 nonselected native reviews and all 656 public question/image pairs remain
unchanged. There are still 236 historical approvals and 97 private records.
Effective mapping totals: verified 283, proposed 14, needs-review 36. Effective
extraction totals: complete 326, partial 7. Academic history remains 326 independent
verifications plus seven qualified owner adjudications, with no answer rewrites.

Initial sandbox, test-server cleanup and Astro preview-lock failures are preserved
in the private validation logs. The final isolated account run passed. The full
Python suite passed after correcting only the historical test fixture. No cloud
student data was accessed; account/rule checks used the demo-only local emulators.

## Local review and reproducibility

```powershell
python scripts/hardware_batch07.py check
python scripts/approval_candidates.py check --batch 7
python scripts/hardware_batch07_report.py
node scripts/private-student-preview-server.mjs --batch07
node scripts/question-review-server.mjs --approval-candidates --batch7
```

Student preview: http://127.0.0.1:4348/.
Read-only owner gallery: http://127.0.0.1:4350/.
Automated browser tests use separate ports 4349 and 4351.
Private progress uses its own disposable namespace. Services bind loopback, verify
Host/Origin and asset hashes, deny mutation methods and never serve source PDFs or
unselected private records.

The private completion report links the complete 56-record inventory, exact
31-record candidate table, source-page evidence, nine-record triage, deferred
Hardware roadmap, source-calculation checks, eligibility checklist and equality
evidence. The final manifest is `final-approval/manifest.json` within that workspace.
Its candidate-set fingerprint is
`c2a48d56ec7a0e0474e96c8da2e2bb132bf27a28033e8dae2560b0e8d93fb2a6`.
Its SHA-256 is
`5357a9fcb55554b2620a03d1333a6ced1e6d9740b63ad5fa419641df52eca2d8`.

A later owner authorization must identify the exact manifest, candidate set,
individual publication/context fingerprints and unchanged highlight definitions.
Stale inputs or any material content, grading, mapping, accessibility or highlight
change invalidate that reviewed authorization. Preparation never refreshes an
existing frozen package automatically.

The remaining Hardware queue contains 25 deferred records, including all seven
protected cases. There are no ready-but-unselected candidates. Chapter 1
integration is not complete.

Production remains Release 6. Its 55 unexplained deployed HTML hash differences
and incomplete live HTML/UI transport verification remain unresolved. No production
probing, approval, publication, merge, deployment, rollback or progress reset was
performed during this milestone. Stop at private owner review.
