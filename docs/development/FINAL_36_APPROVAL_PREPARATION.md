# Final 36-question owner approval preparation

23 October 2026. Feature branch: `feature/chapter1-question-integration`. Preparation baseline: `9bf34bf904788f88fe12e1cdc8531d82d27cf4f3`, verified clean before work.

Exactly **36** candidates across the existing seven concepts are prepared. All 36 are independently verified, FE / Morning / Subject A, source-bound, single-answer eligible, precisely mapped, and **unapproved**. The only remaining approval blocker for each candidate is separate final owner publication authorization. The other 297 records, including all seven qualified owner-adjudicated cases, are excluded from the approval manifest and gallery.

## Native accessibility reconciliation

| Historical PDF / canonical ID | Native extraction fields updated | Preserved |
|---|---|---|
| 22 / `HIST-TECH01-2019A-Q012` | Diagram description now includes the directed sequence and enclosing processor boundary; source-bound editorial provenance added | All options, answer, worked explanation, verification evidence, original crop and raw transcript |
| 28 / `HIST-TECH01-2019S-Q023` | Diagram description now includes gate wiring and junction details; stray diagram labels removed from accessible option D; source-bound editorial provenance added | Other options, answer, worked explanation, verification evidence, original crop and raw transcript |

Both descriptions are the previously validated overlay text, rechecked against the original diagrams and pixel-matched source crops. No replacement image or new answer was created. `extraction.editorialProvenance` binds the prior review hash, exact validated overlay hash, source-content hash, original image hash and physical PDF page. Immutable before snapshots and a two-record change ledger remain private.

The existing publisher now receives the corrected **native reviews**. There is no remaining overlay handoff prerequisite. All 331 other reviews are unchanged; all 326 independent verification records, seven owner adjudications, classifications, mappings, metadata and source histories are preserved. Existing metadata/audit snapshot checking accepts only the exact authorized two-field transfer plus its editorial provenance; it still rejects arbitrary non-metadata changes. The two repaired records' review/approval fingerprints change, while their private academic revisions and canonical progress identities remain stable.

## Exact payload and owner review

Private workspace: `.local/historical/approval-candidates/technology-01/`.

- `manifest.json`: exactly 36 native records/reviews, existing publication fingerprints, image/source bindings, metadata, grading eligibility, precise textbook support, original/current preview equality and the exact gallery asset allowlist.
- `index.html`: read-only owner gallery grouped by seven concepts, with a 36-question index and previous/next navigation. Each entry shows the original image, accessible question/options, correct answer, worked explanation, textbook passage/page/anchor, integrity information and unapproved status.
- `editorial-reconciliation.json`: exact before/after review hashes and corrected field names for the two native transfers.
- `completion-report.md`: complete 36-row eligibility/blocker/fingerprint table.
- `equality-report.json`: per-question hashes proving original pilot, current pilot and native candidate equality in every student-visible academic field.
- `integrity-report.json`: preservation and actual negative publisher checks, with zero-write publication dry-run results.
- `repeatability-report.json`: identical candidate bytes/mtimes and unchanged protected catalog/source/public data on repeated preparation.
- `before/`: frozen internal QA evidence, including the pre-transfer catalog snapshot. Those preservation inputs are not approval candidates and are never served by the gallery.

Counts remain: logic gates 24; radix conversion six; USB two; CPU registers, cache memory, disk access and defragmentation one each. All 36 images and all visible academic content match the validated preview. No student-facing editorial notice was introduced. Website highlight context is distinguished from exact checked textbook excerpts; gallery quotations omit the website's exam-count annotation without altering source evidence.

```powershell
python scripts/approval_candidates.py prepare
python scripts/approval_candidates.py check
node scripts/question-review-server.mjs --approval-candidates
```

Owner gallery: **http://127.0.0.1:4319/**. The existing student preview remains separate at **http://127.0.0.1:4324/**, launched with `npm.cmd run questions:pilot`. Preparation uses the validated existing preview and rebuilds it only when stale. Repeating preparation neither changes the candidate payload nor duplicates editorial history.

The gallery extends the existing private review server. It binds to loopback, validates host/origin and GET/HEAD, checks exact asset hashes, and serves only its HTML and 36 selected original images. Raw PDFs, catalog/review JSON, the other historical images and mutation routes are unavailable. It has no approval controls, scripts, storage writes, authentication or network dependencies. No historical asset or payload enters production `src/`, `public/` or the production build.

## Publication gate and later approval procedure

The existing `publication_fingerprint(record, review)`, approval validator and native exporter remain the authority. The fingerprint covers the full question, image/source references, metadata, answer, explanation, mapping and corrected extraction; it excludes only the mutable approval object. Any subsequent content change invalidates an old approval.

For this Technology-01 source, the existing TypeScript publisher now checks the exact candidate package before native export. Removing the package or validated overlay evidence, changing a candidate transcription, or changing native content causes rejection. Removing the optional catalog editorial marker does not bypass this source-bound gate. An approved input outside the exact candidate IDs is rejected. Reliably matched published Practice occurrences retain their existing authoritative answers and explanations; strict matching rules were not changed. The current occurrence reconciliation reports all 333 distinct, with zero matches, ambiguities or answer conflicts.

No approval command was run. For a **later explicitly owner-authorized milestone**:

1. Obtain explicit authorization naming the reviewed canonical IDs and their publication fingerprints, or this exact manifest hash and scope. Technical eligibility, answer selection and preview inclusion are not authorization.
2. Stop the read-only owner gallery before changing approval state. Revalidate source/image evidence and run `python scripts/approval_candidates.py check --publisher-check`; compare authorized fingerprints with the frozen manifest and current native reviews. Abort on any difference or missing correction.
3. Only for the explicitly authorized IDs, use the existing per-record CLI: `python scripts/historical_questions.py approve --id <authorized-ID> --reviewer <owner-identity>`. It computes the fingerprint from the actual corrected native record. Do not infer approval of the other 297 records, or relax any qualified-owner grading restriction.
4. Reconcile approval-only receipts/manifest bookkeeping as a separately authorized state transition, preserving the editorial transfer receipt and original source history. The preparation snapshot deliberately requires all records unapproved; do not rerun preparation to reset or silently carry approvals. The publisher-specific check permits approval-field changes while rejecting changes to any reviewed payload field.
5. Run the existing publication dry run and all relevant boundary/progress/build checks. Verify exactly the owner-authorized scope, expected additions/updates and unchanged Practice authority before any separately authorized publication. Main merge and deployment require their own authorization.

No approval or publication API, bulk approval action or second publishing system was added.

## Validation and preservation

| Check | Result |
|---|---|
| Python regressions | 155 passed, including eight new exact-candidate/native-transfer/fingerprint/scope regressions |
| Application tests | 82 passed |
| Owner-gallery browser checks | Four passed: all 36 image/content bindings, privacy, keyboard navigation, 375px and 1280px review |
| Existing student-pilot browser checks | 49 passed |
| Production browser checks | All 52 passed in the final complete run |
| Production/private Astro and TypeScript | Zero errors, warnings or hints |
| Production/private build | Passed; production remains 420 public questions/images |
| Actual negative publisher checks | Missing package, stale transcription and missing overlay evidence all rejected |
| Publication dry run | Zero approved inputs, additions, updates or conflicts; protected bytes/mtimes unchanged |
| Repeated preparation | Candidate bytes/mtimes identical; protected catalog/source/public files unchanged |

The initial gallery integrity check exposed Windows CRLF versus normalized-text hashing. It was corrected to hash actual asset bytes after checking semantic HTML content; no content, image or gate was weakened. An initial production browser run timed out waiting for an existing guest-progress key; the unchanged spatial-reader suite passed all three checks when rerun alone, followed by a complete 52-test pass. No reader, authentication, progress or unrelated textbook implementation was modified.

All original 333 question/image bindings and source content remain unchanged. The 420 published Practice records/images and original application assets retain their bytes/mtimes. Zero approvals, historical publications, main merges, deployments, additional historical PDF processing or Practice repository modifications occurred. The final commit and running local server details are in the private handoff and final response. Stop for explicit owner authorization.
