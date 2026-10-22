# Chapter 1 question integration — owner review

Date: 22 October 2026. Branch: `feature/chapter1-question-integration`, based on `f88f3b3`.
The approved bookshelf landing page was already on `main`; its implementation was not changed.
This milestone adds the question workflow and Practice filters. **Historical publication remains pending owner review. No merge or production deployment was performed.**

## Extraction and verification results

Only `data-sources/historical-pdfs/Technology-01.pdf` was processed. None of the other 13 source PDFs was opened, moved or imported.

| Result | Actual count |
|---|---:|
| PDF pages inspected structurally | 333 |
| Questions extracted | 333 |
| Internal duplicate examination occurrences | 0 |
| Unique historical questions | 333 |
| Complete original question crops generated | 333 |
| Failed image crops | 0 |
| Raw extraction classified complete / partial | 292 / 41 |
| Answers independently checked with evidence | 191 |
| Worked explanations completed | 191 |
| Answers still requiring review | 142 |
| Reliable duplicates with published Practice | 0 |
| Answer conflicts with published Practice | 0 |
| Owner-approved historical questions | 0 |
| Unapproved historical questions | 333 |
| Precise concept mappings verified / proposed / needing review | 188 / 104 / 41 |
| Questions without a precise proposed mapping | 41 |

The 41 uncertain mappings are a subset of the 333 questions, not an additional question count. Material outside or uncertain for Hardware remains in the private review queue. A correctly calculated answer does not imply a verified Chapter 1 mapping.

Source SHA-256: `5c74e109ff2129f70189b55e79e7af3a806183cf0c1aa8082195aa942d1c16b1`.
Printed dates span 2007–2022. Published Practice questions currently cover 2024–2026 plus undated samples, so there are no matching examination occurrences. Similar questions repeated in different years retain distinct IDs.

The pages print their question number, date and answer, but **do not establish examination type or paper**. These fields remain unknown; `HIST-TECH01-…` IDs make that provisional source identity explicit. Approval requires evidence for the missing exam metadata, rather than assuming FE Morning.

Independent verification uses either a cited textbook passage (printed page, PDF page, line IDs, source checksum and excerpt checksum) or a written calculation/Boolean derivation. Agreement with the printed key is recorded separately. The private review records contain the reasoning and worked steps. Matching the printed key alone never counts as verification.

All crops use original 300-dpi PDF rendering, including vector lines, tables and notation. Each exported lossless WebP was decoded and compared with the original rendered RGB crop. Total crop size is 8,525,870 bytes, about 25 KB per question. Crop coordinates, pixel hashes, dimensions and source pages are recorded. The answer/date footer is excluded from the student question image and retained separately as editorial metadata.

Visual checks sampled 22 crops, including the five unusual option layouts, tables, superscripts, Boolean overbars and both ends of the source. Twenty received a completed visual check; pages 112 and 180 remain explicitly unresolved. This is not a claim that all 333 crops have received manual visual approval. The private gallery presents every original for that remaining review.

Examples of review issues:

- PDF page 53 places the stem after the options in extraction order; the original crop preserves the correct reading order.
- Pages 82, 112, 148, 195 and 216 have nonstandard option layouts. Page 148 now has a reviewed accessible formula and option table in the private review record.
- Page 180 has register descriptions that do not clearly agree with the textbook; no potentially misleading explanation was supplied.
- Page 268 needs visual confirmation of radix notation before its calculated result is accepted.
- ECC and audio questions are not assigned to numerical-error section 2-3-3 merely because their wording mentions errors or data.

## Local review and approval

The raw PDF, extracted transcripts, unapproved records, review decisions and crops are ignored by Git and remain outside `public/` and `dist/`:

| Private location | Purpose |
|---|---|
| `.local/historical/technology-01/manifest.json` | Source checksum, processing fingerprint and actual counts |
| `…/questions.json` | All extracted records, options, keys, geometry and source references |
| `…/pages.json` | Original text spans, fonts and bounding boxes |
| `…/reviews.json` | Independent solutions, explanation steps, mapping evidence and separate statuses |
| `…/duplicate-report.json` | Canonical matches, ambiguity and any answer discrepancies |
| `…/images/` | Original complete question crops |
| `…/index.html` | All-question review gallery with blockers and original images |
| `…/contact-review/` | Local visual sampling sheets |

Start the private gallery:

```powershell
npm.cmd run questions:review
```

Open `http://127.0.0.1:4319/`. Search the page for a question ID or PDF page. Select its crop to inspect the full-resolution original, then compare its printed key, independent reasoning, extraction flags and precise mapping. The server is read-only, loopback-only, host-checked and restricted to review assets. It does not serve the source PDF or provide a web approval endpoint.

Edit only the chosen entry in private `reviews.json`. Keep these independent dimensions explicit:

1. `verification`: status, independently determined answer, method, evidence and reasoning.
2. `mapping`: verified chapter `fe-v1-ch01`, exact section ID, subsection anchor, heading number, concept ID, reason and source evidence.
3. `extraction`: complete status, every reviewed image SHA, faithful `imageDescription` and complete `optionText` for a–d.
4. `metadata`: verified exam type, paper, subject and supporting evidence.
5. `explanation`: summary, worked steps and takeaway consistent with the verified answer.

For a new concept, additionally provide `mapping.title`, `mapping.summary`, and `mapping.sourceHighlight` containing the exact paragraph `passageId` and SHA-256 of its rendered inner HTML (`fragmentSha256`). The paragraph must sit within the approved heading and contain no existing link. This review can be prepared against `presentSourceHTML()` and `passageMatch()` in the supplied helpers. Promotion rejects a changed passage or an inconsistent heading. It adds a runtime annotation and derives its actual question count without editing the released textbook files.

After completing those checks, the **owner** can explicitly record approval:

```powershell
npm.cmd run questions:historical -- approve --id HIST-TECH01-2021A-Q011 --reviewer "Owner name"
npm.cmd run questions:publish -- --dry-run
```

That example ID is currently unapproved; the command will refuse it until its missing review dimensions are complete. Approval binds the source, content, crops, metadata, mapping and explanation by checksum. Editing any of them invalidates approval. Actual promotion is a separate `npm.cmd run questions:publish` command; it does not deploy. Follow promotion with `npm.cmd run check`, `npm.cmd test` and `npm.cmd run build`, then review the Git diff.

For reliably matched published Practice questions, the existing canonical ID, answer, verified fields and explanation are retained. Additional historical references and discrepant printed answers are attached without adding another question. New contradictory explanations are withheld. Ambiguous matches block promotion; a published answer is never silently corrected.

Multi-page extraction is supported and tested. This PDF has one question per page. Public promotion intentionally rejects a multi-page record until a complete composite has been separately reviewed. Other PDFs may need a layout adapter; multiple question starts on one page fail clearly rather than being guessed.

## Reprocessing and manual synchronization

Tested PDF dependencies: Python with PyMuPDF 1.27.2.3 and Pillow 11.1.0.

```powershell
npm.cmd run questions:historical -- extract
npm.cmd run questions:historical -- verify
npm.cmd run questions:historical -- gallery
npm.cmd run questions:reconcile
npm.cmd run questions:sync -- --dry-run
npm.cmd run questions:sync
```

The extractor checks both source checksum and importer fingerprint. An unchanged import verifies existing assets and performs no writes. An improved importer or changed source reprocesses the source, retains separately stored reviews and invalidates stale approval. Reprocessing never grants publication approval. Missing/unreadable sources, unsupported layouts and invalid crop geometry fail closed. The other PDFs remain out of scope for this command in this milestone.

Practice sync defaults to the read-only `D:/ITPEC Old Questions` checkout; `--source <path>` can select another prepared checkout. It imports only literal `is_published === true`, preserves canonical IDs, reuses the existing normalizer and checks images. Additions require mapping review before contextual lesson links are created. Safe source-location updates preserve verified content; changed answers, images, content, mappings or ambiguous occurrences block the write and are reported. Missing source publication retains an existing approved record for review rather than withdrawing it or deleting attempts automatically.

Actual sync results, including repeated normal and dry-run executions:

```text
additions: 0
updates: 0
conflicts: 0
skippedUnpublished: 160
unchanged: 420
total: 420
```

Dry-run performs no writes. Unchanged normal sync also performs no writes. Changed snapshots are staged with recovery copies and roll back caught write failures; they never write to Practice or student storage. A hard process termination during a multi-file replacement is not a database transaction: retain `.local/question-transactions/` recovery copies and rerun validation before building if that occurs.

## Practice experience and compatibility

The existing 420 published questions, 13 contextual concepts and 23 distinct worked questions remain available. No historical crop or unapproved question is in the public build.

The Practice screen now provides inclusive From/To year controls, All years, source membership selection and Unanswered only. Years come from the actual published bank. Undated samples remain visible under All years and are excluded when a year boundary is selected. Invalid ranges and empty results are explicit. Preferences use a separate local-storage key; the progress schema, Firebase rules, attempts and canonical IDs are unchanged.

The eligible list drives counts and numbered/Previous/Next navigation. Changing filters selects a valid question or the empty state and updates the URL safely. In Unanswered only, submitting keeps the answer feedback visible until navigation, even though the answered question leaves the remaining list. Attempts in any concept count as answered; retrying does not erase attempt history. Bookmarks, account restoration, image enlargement, reading checkpoints and exact return position remain in the existing flow.

For a local application preview, run `npm.cmd run dev`, then open `/practice/cache-memory/`. Historical-only correctly produces an empty result until owner-approved historical questions are promoted.

## Validation

All checks below passed; no failing checks remain:

- Astro and TypeScript diagnostics.
- 82 Vitest unit/component tests: filters, source membership, inclusive/invalid ranges, preserved progress, occurrence matching, canonical answer priority, sync safety/idempotency and reviewed highlight overlays, plus existing regressions.
- 7 Python extraction/approval tests: vector crops, continuation pages, missing keys, conflicting duplicate keys, checksums, reprocessing, idempotency and Practice authority.
- 3 isolated synthetic promotion tests: unapproved exclusion, dry-run safety, repeated promotion, preserved Practice IDs/answers/explanations, discrepancy metadata and a new concept tied to an exact source paragraph. They run entirely under ignored `.local/` and never publish test questions into the real catalog.
- 52 production-browser tests, including new filter flows, keyboard interaction, 320px layout, original crops, landing page, reading restoration, bookmarks and storage failure.
- 3 Firebase-emulator account regressions: migration, two devices, offline recovery, account switching and restored reading/bookmark/completion.
- Production build and closed public-asset allowlist: 420 approved question records/images, all 100 source-reader pages, 47 numbered figures and 81 spatial crops preserved.
- Unchanged historical import, repeated real Practice sync and historical promotion dry-run.

The existing large-client-chunk build warning remains. No new package or Firebase infrastructure was added.

## Changed implementation

The feature reuses the existing importer, catalog, concepts, original source renderer, Practice viewer, guest store and account synchronization. Changes are limited to:

- `scripts/historical_questions.py`: local extraction, manifest, visual gallery, evidence and fingerprint-bound approval.
- `scripts/reconcile-historical-questions.ts`: private duplicate/discrepancy report.
- `scripts/question-review-server.mjs`: private read-only review server.
- `scripts/question-sync.ts`, `scripts/sync-questions.ts`, `scripts/question-snapshot.ts`: manual sync planning, exact publication flag, safe writes and recovery. The legacy `import-questions.ts` entry point delegates to this safe sync too.
- `scripts/publish-historical-questions.ts`: separately approved promotion, authoritative duplicate handling, explanations and precise concept annotations.
- `src/lib/question-policy.ts`, `src/lib/question-highlights.ts`, `src/lib/models.ts`: reusable filtering, provenance, statuses, reliable occurrence matching and reviewed annotations.
- Practice component, its Astro route, HardwareReader, styles, TOC generation and data validation.
- Focused unit, Python and browser tests; npm commands; PDF ignore rule; this report and README.

The implementation commit is the tip of `feature/chapter1-question-integration`; inspect it with `git log -1 --format=fuller`. The final handoff records the exact hash. Review this branch before considering a merge. The local question review queue requires owner decisions before any historical publication.
