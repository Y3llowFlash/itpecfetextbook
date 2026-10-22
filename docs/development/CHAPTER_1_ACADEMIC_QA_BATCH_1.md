# Chapter 1 academic QA — Batch 1

22 October 2026. Continues `feature/chapter1-question-integration` from `33e1cba`. This is a private review milestone. No historical question was approved, published, merged or deployed. The three supplied review documents were treated as advisory evidence, separately checked against the original sources.

## Results

| Measure | Result |
|---|---:|
| Batch 1 proposals independently reconciled / answers accepted | 30 / 30 |
| Previously verified answers and explanations preserved exactly | 191 / 191 |
| Additional answer resolved outside Batch 1 | 1 (historical PDF p.268) |
| Total verified answers / unresolved answers | 222 / 111 |
| New worked explanations for verified answers | 31 |
| Canonical IDs and raw transcript checksums preserved | 333 / 333 |
| Manually inspected original question pages | 37 |
| Active crops compared to fresh 300-dpi original PDF renders | 333 / 333 |
| Confirmed crop defects / corrected crops | 1 / 1 |
| Other active crops left unchanged | 332 |
| Owner approvals / public historical questions | 0 / 0 |
| Published Practice questions retained | 420 |

All 30 proposed answer letters were accepted after independent reasoning. Some proposed mappings, page references and image interpretations were modified, as described below. There were no new independently established answer-key conflicts. Two additional examined questions, pp.112 and 180, remain unresolved. The other 109 unresolved answers were outside this focused batch.

All `src/` and `public/` files match the hashes captured before reconciliation. The textbook, public question catalog, highlights, explanations, progress schema, Firebase code and original Practice checkout were not modified. No historical PDF other than Technology-01 was processed.

## Source and preservation evidence

The primary question source is `data-sources/historical-pdfs/Technology-01.pdf`, 333 physical pages, SHA-256 `5c74e109ff2129f70189b55e79e7af3a806183cf0c1aa8082195aa942d1c16b1`.

Mapping checks used the complete 487-page `D:/ITPEC Old Questions/database/raw/FE Vol 1.pdf`, SHA-256 `1e1f2ec364a52751333b1e3ab2a2f2548e9345cd06a7c300b8a7075fb51c3d1b`. Evidence records distinguish printed textbook labels from physical PDF pages and store source/text hashes and checked excerpts. The unnumbered inserted PDF p.83 makes a universal printed-page offset incorrect.

All three supplied artifacts were read in full. Their private copies have these SHA-256 values:

| Advisory file | SHA-256 |
|---|---|
| `ITPEC_Chapter1_Academic_Audit_Batch01_With_Images.json` | `8535ad506f698bf0248f802e81ee325a410566690155ac0c1e8df55783f29dbb` |
| `ITPEC_Chapter1_Image_QA_Addendum.json` | `4cf28010d5b7b0ee1c4ed740b47a88a0b50594222b298e9dcd0914f5b53a7518` |
| `ITPEC_Chapter1_Image_QA_Addendum.md` | `7e5d9f487824774d0a33f57d5366c72d05d0c6117a02950e9eb5d9e3ca653503` |

The 30 proposal IDs, question-content checksums and source identities matched the existing records. All 23 visual-finding references matched their original crop hashes. Original hashes remain acceptable references after the p.45 repair because that image is retained explicitly in `imageHistory`; an unknown hash is rejected.

Before changes, byte-exact copies of `questions.json`, `reviews.json`, `manifest.json`, `pages.json` and `duplicate-report.json` were saved under `.local/historical/technology-01/qa-batch1/before/`. Further reconciliation snapshots and per-dimension changes live under `qa-batch1/history/`. The original crop remains recoverable alongside the corrected one. `pages.json`, raw transcripts, printed keys and source references remain unchanged.

## Image and transcription review

All 30 batch pages plus seven additional flagged pages (82, 112, 148, 180, 195, 216, 268) were viewed against original renders. The 333-page automated comparison also checks text, visible embedded images, vector bounds, crop coordinates, footer exclusion, dimensions, encoded checksums and exact decoded RGB pixels. This is **37 pages manually inspected**, not a claim of manual visual approval of all 333.

| Historical PDF page | Repair or finding | Final state |
|---:|---|---|
| 45 | Horizontal output wires were missing from the crop bounds. PyMuPDF treats zero-height/width path rectangles as empty in a rectangle union. Include their stroke extent before calculating the crop. | One new lossless WebP; complete a–d circuits and right-side wires; original footer excluded; 300-dpi source pixels verified. Independent truth table gives D. |
| 112 | The source itself prints only `a`; the other three numeric choices have no letter labels. | Preserve original image and unlabeled option sequence. Effective address 300 gives numeric result 1300. Do not invent b/c/d; answer-letter verification and extraction remain pending. |
| 148 | The original second input-column heading is blank. The old raw extraction was partial, while review enrichment incorrectly asserted complete. | Preserve original image and prior verified answer/explanation. Mark extraction partial; store source headers with a null second heading and a separate inferred B interpretation. Formula gives outputs 1,0,1 (C). |
| 180 | “Complement register” is printed in the original. The book describes a complementer, which does not establish the register description. | Original crop is complete. Academic status stays needs-review; printed B is not forced into an accepted answer. |
| 268 | Re-read all original radix subscripts and choices. | `6140₈ + 10011100₂ − C46₁₆ = 3168 + 156 − 3142 = 182 = B6₁₆`, choice D. Other choices are 181,174,180. No printed-key conflict; original crop unchanged. |
| 1, 36 | Set union/intersection notation is not faithfully represented by extracted glyphs. | Reviewed options spell out the operators; exhaustive membership truth tables establish distributivity. Raw text unchanged. |
| 9, 40 | Gate A/B choices need semantic transcription. | Reviewed table explicitly pairs sum XOR and carry AND. Original images unchanged. |
| 29, 41, 56, 61, 63 | Boolean bars, circuit alternatives or nested gates need readable descriptions. | Explicit NOT/AND/OR/XOR/NAND/NOR transcripts and exhaustive independent truth tables; no redraws. |
| 53 | PDF extraction puts the question stem after its choices, contaminating option D. | Correct reviewed reading order and option text; raw transcript and image unchanged. |
| 82 | Inline choice c was swallowed into choice b by the line-based extractor. | Four reviewed options: Pipeline, Super-pipeline, Superscalar, VLIW. Prior verified answer/explanation unchanged. |
| 195, 216 | Visually present table-choice labels were not represented correctly in raw options. | Restore reviewed a–d tables from the original; prior verified answer/explanation and source images unchanged. |

No further crop omission was found by the complete geometry scan. The remaining source-label defects on pp.112/148 and terminology ambiguity on p.180 require explicit editorial decisions; they are not claimed fixed by cropping. Active images total 8,525,996 bytes, only 126 bytes more than before; 333 original files plus the one corrected file remain private. No entire question bank was re-rendered to disk.

## Batch 1 question table

Every answer below is independently verified in the private queue and **unapproved for publication**. “Mapping” refers to eligibility for an exact Chapter 1 placement; another chapter can have verified classification while its Chapter 1 publication mapping remains pending. Pages in the location column are **printed textbook page / physical textbook PDF page**. The historical PDF page is a separate column.

| Canonical question ID | Historical PDF p. | Answer | Classification | Textbook location | Mapping |
|---|---:|:---:|---|---|---|
| HIST-TECH01-2021A-Q003 | 1 | D | Uncertain | General set distributivity; database set operators at 250/260 do not establish a precise placement | Pending |
| HIST-TECH01-2021A-Q020 | 5 | C | Outside Vol.1, provisional | Actuator; no supporting Vol.1 passage located | Pending |
| HIST-TECH01-2021S-Q013 | 7 | C | Ch.1 | 3-1 CPU, 46/51 | Verified |
| HIST-TECH01-2021S-Q014 | 8 | B | Ch.1 | 5-5-2 Interfaces, 108/114; USB-IF rate evidence | Verified |
| HIST-TECH01-2021S-Q021 | 9 | A | Ch.1 | 3-4-2 Arithmetic circuits, 67/72 | Verified |
| HIST-TECH01-2021S-Q023 | 10 | C | Vol.1 Ch.2 | 4-2-1 input checks, 159/168; 4-2-2 Code Design, 162/171 | Pending |
| HIST-TECH01-2021S-Q024 | 11 | D | Vol.1 Ch.2 | 5-2 Multimedia/CG drawing software, 176/186 | Pending |
| HIST-TECH01-2020A-Q021 | 16 | C | Outside Vol.1, provisional | Rechargeable lithium-ion cells; no supporting Vol.1 passage located | Pending |
| HIST-TECH01-2020S-Q012 | 20 | D | Ch.1 | Unnumbered UART insertion, physical PDF 83; between printed 77 and 78 | Proposed |
| HIST-TECH01-2019A-Q012 | 22 | C | Ch.1 | 3-1 CPU/registers, 47/52 | Verified |
| HIST-TECH01-2019S-Q023 | 28 | C | Ch.1 | 3-4-1 Logic Circuit, 61/66 | Verified |
| HIST-TECH01-2018A-Q001 | 29 | B | Ch.1 | 3-4-1 Logic Circuit, 61/66 | Verified |
| HIST-TECH01-2018A-Q009 | 30 | B | Vol.1 Ch.3 | 3-1-3 Java Servlet, 213/223 | Pending |
| HIST-TECH01-2018A-Q011 | 32 | C | Ch.1 | 3-3-3 Addressing Mode, 59/64 | Verified |
| HIST-TECH01-2018A-Q013 | 33 | A | Ch.1 | 5-5-2 Interfaces, 108/114; USB-IF rate evidence | Verified |
| HIST-TECH01-2018A-Q021 | 34 | D | Vol.1 Ch.3 | 2-2 OS Management/page replacement LRU, 207/217 | Pending |
| HIST-TECH01-2018A-Q022 | 35 | D | Ch.1 | 3-4-1 Logic Circuit, 61/66 | Verified |
| HIST-TECH01-2018S-Q002 | 36 | D | Uncertain | General set distributivity; no precise textbook placement established | Pending |
| HIST-TECH01-2018S-Q011 | 39 | C | Ch.1 | 5-2-2 Printer, 100/106 | Verified |
| HIST-TECH01-2018S-Q022 | 40 | A | Ch.1 | 3-4-2 Arithmetic circuits, 67/72 | Verified |
| HIST-TECH01-2018S-Q023 | 41 | C | Ch.1 | 3-4-1 Logic Circuit, 61/66 | Verified |
| HIST-TECH01-2017A-Q021 | 45 | D | Ch.1 | 3-4-1 Logic Circuit, 61/66 | Verified |
| HIST-TECH01-2017S-Q013 | 53 | B | Ch.1 | 5-5-3 Device Driver, 110/116 | Verified |
| HIST-TECH01-2017S-Q014 | 54 | B | Ch.1 | 4-1-3 Disk access/fragmentation, 85/91; secondary Ch.3 185/195 | Verified |
| HIST-TECH01-2017S-Q024 | 56 | C | Ch.1 | 3-4-1 Logic Circuit, 61/66 | Verified |
| HIST-TECH01-2016A-Q009 | 58 | C | Ch.1 | 3-3-3 Addressing Mode, 59/64 | Verified |
| HIST-TECH01-2016A-Q022 | 61 | C | Ch.1 | 3-4-1 Logic Circuit, 61/66 | Verified |
| HIST-TECH01-2016S-Q002 | 63 | D | Ch.1 | 3-4-1 Logic Circuit, 61/66 | Verified |
| HIST-TECH01-2016S-Q014 | 66 | C | Vol.1 Ch.3 | 2-2 OS Management/DAT, 206/216; primary Arm MMU terminology | Pending |
| HIST-TECH01-2016S-Q015 | 67 | B | Ch.1 | 3-5-1 Cache context, 72/77; primary Arm coherence evidence | Proposed |

Classification totals: **21 Chapter 1 / 5 other Volume 1 / 2 provisionally outside Volume 1 / 2 uncertain**. No public concepts or future-chapter highlights were created. The 19 verified Chapter 1 placements do not automatically approve a new public highlight: an exact paragraph binding remains required by the existing promoter where applicable.

Important corrections to advisory mapping and source interpretation:

- Fragmentation (historical p.54) is explicitly discussed in Chapter 1 printed p.85. Chapter 3 service utilities are useful secondary evidence, not a reason to exclude the question from Hardware.
- The textbook explicitly mentions USB 3.0 at printed p.108, but gives “5,120Mbps.” [USB-IF's specification supplement](https://usb.org/document-library/inter-chip-supplement-usb-revision-30-specification-revision-102) states 5 Gbps support. Preserve that numerical discrepancy and the unmodified textbook.
- UART (historical p.20) is supported by the unnumbered textbook insertion at physical p.83. It is not printed p.78. The exact Chapter 1 highlight remains proposed.
- [Arm's memory-management documentation](https://documentation-service.arm.com/static/5efa1d23dbdee951c1ccdec5) establishes MMU address translation; the textbook uses DAT terminology at printed p.206. Classify historical p.66 under Chapter 3.
- [Arm's memory-ordering explanation](https://developer.arm.com/community/arm-community-blogs/b/architectures-and-processors-blog/posts/memory-access-ordering---an-introduction) supports the cache-coherence answer. The book's Chapter 1 cache context does not supply an exact coherence definition; historical p.67 retains a proposed precise mapping.
- Actuator and battery placements are provisional inferences after searching the entire Volume 1 text, contents and index. Absence from text search is not proof of absence. Answer evidence comes from [Emerson's actuator description](https://www.emerson.com/en/measurement-instrumentation/products/damcos-kc-linear-double-acting-actuator) and [EPA's lithium-ion explanation](https://www.epa.gov/hw/lithium-ion-battery-recycling). The two generic set questions remain uncertain rather than being forced into the database chapter.

## Extraction status and metadata

`questions.json.extractionQuality` retains the original extractor result: **292 complete / 41 partial**. Reviewed completeness now comes from one shared `effective_extraction()` function, used by the manifest, gallery and approval gate. A complete enrichment of raw partial data requires a current content-and-image binding, complete reviewed a–d transcript and description, and no unresolved source defect. A stale binding cannot fall back to raw-complete status. Conflicting complete claims are rejected by verification/export.

The original p.148 discrepancy came from **incorrect review enrichment**, not missing image pixels or a stale summary. Its original missing header was never restored in the source. The corrected review explicitly remains partial. Nine other raw-partial records have source-checked complete enrichment, giving **301 effective complete / 32 partial**. Both raw and effective counts remain visible. Mapping statuses across all 333 are **210 verified / 84 proposed / 39 needing review**.

All 333 records now state FE as **owner-confirmed**, with provenance pointing to section 7 of this integration request. No historical page was claimed to print FE. Paper and subject remain unestablished; metadata approval stays pending. No Morning designation was inferred. All 333 records remain unapproved, including the 222 with verified answers.

## Adapter and local review

The extension reuses `questions.json` and `reviews.json`; it does not introduce a second live review database. `scripts/academic_qa.py` validates the advisory schemas, unique IDs, source identity, raw transcript checksums and image references, then merges **separately prepared source-checked decisions**. The flag `sourceChecked` records the manual work described above; it is not an automatic claim that an arbitrary JSON proposal has been verified.

The private staging file `qa-batch1/decisions.json` contains those checked decisions, exact evidence and Boolean proof expressions. Staging data is not read by the application or public promoter. Existing verified answers/explanations are retained verbatim; proposed contradictions would be kept separately in `academicConflicts` for owner review. Changes carry advisory/decision hashes and snapshot history. No advisory field can grant approval. Existing Practice duplicate authority remains enforced by the original matcher and promoter.

Only p.45 is eligible for the targeted crop helper. Applying reconciliation checks all 333 source crops, migrates the importer fingerprint after those checks, and retains the original fingerprint in `sourceHistory`. `recordsSha256` binds the validated question snapshot; later changes fail verification. Repeated real reconciliation produced **zero review changes, zero new crops, and identical bytes and modification times** throughout the private workspace.

Commands from the repository root:

```powershell
npm.cmd run questions:qa                 # Read-only validation and proposed change counts
npm.cmd run questions:qa -- --apply      # Explicit private reconciliation; never approval/publication
npm.cmd run questions:historical -- verify
npm.cmd run questions:historical -- gallery
npm.cmd run questions:review
```

Open `http://127.0.0.1:4319/#HIST-TECH01-2017A-Q021` for the repaired crop, or search for another ID from the table. Click the image for its full-resolution source crop. The read-only loopback gallery shows reviewed options, worked evidence, source classification, raw/effective extraction statuses and approval blockers. It has no web approval endpoint.

Private review artifacts remain under `.local/historical/technology-01/qa-batch1/`: all three advisories, the pre-change plan, immutable backups, independent decisions, source-page renders/contact sheets, history, `reconciliation-report.json` and `integrity-report.json`. None are in Git, `public/` or `dist/`. A fresh clone needs these private materials and the authorized source PDF to reproduce this local reconciliation; ordinary application tests and builds do not need them. Do not rerun the old `author-review.py`, and do not use full-bank `extract --force` as a substitute for this targeted migration.

## Engineering validation

- 82 Vitest unit/component tests passed, including question authority, filters, sync safety and preserved progress.
- 13 new Python academic tests passed: proposal schema/identity/hash rejection, original-image history, separate source decision requirement, preservation of 191 verified records, conflict retention/idempotency, approval invalidation, four-way classification, exhaustive Boolean proof, missing-header status reconciliation, stale image binding, validated snapshot tampering, shared manifest/gallery status, unchanged gallery writes, clipped wire detection, targeted repair, source pixels and geometry.
- 7 existing Python extraction/approval tests and 3 isolated promotion tests passed. Synthetic promotions operate in temporary ignored fixtures, never the real catalog.
- Astro/TypeScript check passed with zero errors, warnings or hints.
- Production build passed: 420 published records/images, 100 textbook pages, 47 numbered figures and 81 spatial crops. The pre-existing large-client-chunk warning remains.
- All 52 production-browser tests passed on the final full run. Coverage includes mobile reader layout, original crops, image enlargement, keyboard navigation, saved checkpoints, unanswered/year/source filters, bookmarks and denied storage. The BCD regression test now waits for the debounced guest checkpoint before editing its synthetic saved state, avoiding a race with null storage; application behavior is unchanged. Playwright needed normal Windows process permissions to finish local preview-server teardown.
- Real reconciliation verified all 333 source-image comparisons, all 191 preserved verification/explanation objects, unchanged 333 IDs/raw transcripts/source references, and unchanged application/textbook file hashes. Manifest counts match freshly derived counts.
- Duplicate reconciliation found 0 matched/ambiguous/conflicting published occurrences and 333 distinct historical occurrences. Promotion **dry-run only** reported 0 approved inputs, 0 additions, 0 updates and 0 conflicts.

Changed tracked implementation: `scripts/historical_questions.py`, `scripts/academic_qa.py`, `tests/test_academic_qa.py`, the realistic raw-status fixture in `tests/test_historical_questions.py`, the checkpoint wait in `tests/e2e/source-spatial.spec.ts`, npm commands, README and this report. No dependency or application-code change.

The implementation commit is recorded in the final handoff and can be inspected with `git log -1 --format=fuller` on `feature/chapter1-question-integration`. Only this feature branch is pushed. Remaining work is academic review of the 111 unresolved answers, source-label/terminology decisions noted above, precise pending mappings, reliable paper/subject evidence and separate owner approval before any historical publication.
