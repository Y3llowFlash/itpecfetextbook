# Final owner adjudication of seven historical questions

22 October 2026. Branch: `feature/chapter1-question-integration`. Baseline: `b9f8829e7edc19ad8de6ec596e1844dc3f0ee1da`.

Recorded all seven explicit owner selections in the existing private `reviews.json`. There are **326 independently verified answers, seven qualified owner-adjudicated answers and zero questions awaiting an owner answer selection**. There are **zero new independent verifications and zero publication approvals**. The seven original independent-verification objects still say `needs-review`; their academic qualifications have not been erased. The legacy `unresolvedQuestions: 7` counts independent verification, whereas `unadjudicatedQuestions: 0` counts pending owner selections.

All 326 earlier complete review objects, including evidence, explanations, provenance and metadata, are unchanged. The 333 raw records and original crop bytes are unchanged. The public catalog remains at **420 Practice questions / 420 images**. No publication, main merge, deployment or modification to the original Practice repository occurred. Work stops for owner review.

## Seven decisions and review states

All seven have `ownerAdjudication.status: owner-adjudicated`, retain independent `verification.status: needs-review`, and remain `approval.status: unapproved`. Owner-selected answer letters are not stored in `verification.independentAnswer` as new verified findings. New qualified explanations are explicitly labeled `owner-adjudication-with-academic-qualifications`.

Historical pages are physical, one-based `Technology-01.pdf` pages. Textbook references below are **printed / physical FE Volume 1 pages**. Mapping V/P means verified/proposed context, not answer verification.

| PDF | Canonical ID | Owner / printed | Qualification and editorial treatment | Textbook placement; mapping | Effective extraction |
|---:|---|:---:|---|---|---|
| 110 | HIST-TECH01-2012A-Q001 | C / C | A has exponent/fraction fields 8/23; B has 7/24. C records the comparable-encoding interpretation of greater A range and greater B precision. B's unspecified encoding and IEEE's implicit significand bit remain explicit qualifications. | Ch.1, 2-3-2 floating point; 38–39 / 43–44; V | Complete |
| 112 | HIST-TECH01-2012A-Q013 | B / B | Base 100 + displacement 200 = address 300; its content is 1300. A:1201, B:1300, C:2200, D:2300 is an **owner-confirmed editorial transcription**. The source prints only a); three missing labels are not represented as literal source text. | Ch.1, 3-3-3 base addressing; 58 / 63; V | Partial source; owner transcription present |
| 119 | HIST-TECH01-2012A-Q030 | A / A | **D is also mathematically valid.** Source circuit and D give (A + B·C)·(A·NOT(B)) = A·NOT(B), matching A for all eight assignments. Primary historical answer A and additional valid D are stored separately. | Ch.1, 3-4-1 logical laws; 65 / 70; P | Complete |
| 152 | HIST-TECH01-2010S-Q018 | A / A | Device registers map into the processor's memory address space. A's reference to dedicated I/O address space within main memory remains literal source wording, with a separate terminology clarification; it does not imply physical RAM storage or separate port I/O. | Ch.1, 5-4 I/O context; 104 / 110; P | Partial source terminology |
| 179 | HIST-TECH01-2008A-Q017 | B / B | Timing chart supports XNOR: output 1 for equal input values. C remains literally `Exclusive-`. Owner-proposed `Exclusive-OR` is marked **probable-owner-proposal**, not verified source text. | Ch.1, 3-4-1 logic circuits/XOR context; 64 / 69; V | Partial truncated option |
| 180 | HIST-TECH01-2008A-Q018 | B / B | Complement generation supports the intended arithmetic role. `Complement register` is qualified as historical/nonstandard, not asserted to be a standard register in modern processors. | Ch.1, 3-1 CPU/ALU; 46 / 51; V. Additional register context 47 / 52 is source-bound supporting evidence. | Complete |
| 181 | HIST-TECH01-2008A-Q020 | C / C | C is the intended continuously overlapping, fully utilized steady-state pipeline. B also overlaps with idle cycles under the general definition. That distinction remains in the explanation; diagrams are unchanged. | Ch.1, 3-5-2 pipeline control; 74–75 / 79–80; V | Complete |

## Grading and publication

The current `Question` model and `Practice.tsx` compare each response with one `correctAnswer`. There is no safe existing multiple-accepted-answer scoring path. Accordingly p.119 stores desired accepted options `['a','d']`, primary historical answer `a`, and an explicit blocked grading state. It is not configured in public Practice. Both the explanation and private gallery explicitly state that D also produces the correct function. No student response to D is silently marked wrong by publishing this record.

All seven currently retain blocked grading/publication readiness. For p.119, multiple-answer scoring, feedback and progress compatibility must be addressed before any graded publication. The other six retain the qualifications in the table, plus the existing independent-verification gate. This milestone records the owner's selections; it does not relax that gate or infer independent verification from owner authority. p.112's numerical calculation is already independently established, while its answer-letter identity is now owner-confirmed editorial data.

All seven also require separate fingerprint-bound final publication approval and reliable paper/subject metadata. Proposed subsection mappings on pp.119/152 remain proposed. Original source defects on pp.112/152/179 remain partial even where an editorial clarification is supplied. Owner selection is not a bypass for extraction, mapping, metadata, grading or approval requirements. Approval validation now explicitly honors owner-adjudication grading/readiness blockers, including when an authoritative Practice duplicate is available.

## Schema, evidence and preservation

Added the optional `ownerAdjudication` object to the existing private review schema. It records the selected and printed answers, additional mathematically valid options, source/content/image binding, prior review fingerprint, source evidence, editorial reconstructions, academic qualifications, qualified student explanation, grading eligibility, publication blockers and explicit owner-instruction provenance. Existing reviews without the optional object retain their previous behavior.

The seven original verification, mapping, classification, metadata, approval and academic-review-history objects are preserved exactly. Qualified explanations are updated only for these seven. p.112's reviewed option transcription is updated separately from immutable raw content, with a source-formatting note and owner-instruction checksum. p.179's raw and reviewed literal option C remain `Exclusive-`; the probable reconstruction exists only in the editorial annotation. No canonical ID, original content hash, image, original key, student-progress schema or public explanation is replaced.

Retained all seven existing Chapter 1 classifications based on the actual textbook content, rather than the historical filename: numeric representation, addressing, logic circuits, I/O control, CPU registers and pipelines. Exact prior textbook page hashes/excerpts are revalidated. Added original printed p.47 / physical p.52 register definitions as supporting material for p.180. No exact MMIO definition or standard `complement register` definition is invented. The two proposed exact mappings remain pending.

| Integrity input | SHA-256 |
|---|---|
| Exact attached owner directions | `20cfbe5c4addd1ada5b5ebc9f18f18c37918cafcdc8a1c73b81941a76ab03a07` |
| Private seven-decision package, canonical JSON fingerprint | `53befca9bd2f757c98931ba59953f80a0664216a45b1bebdafebc04c76795f07` |
| Original Technology-01.pdf | `5c74e109ff2129f70189b55e79e7af3a806183cf0c1aa8082195aa942d1c16b1` |
| Complete FE Vol 1.pdf | `1e1f2ec364a52751333b1e3ab2a2f2548e9345cd06a7c300b8a7075fb51c3d1b` |
| Baseline manifest.json | `f4db8bcf2e284eaf2f5345bfe0acad7149a7beb351215bb6d321d382991afa7b` |

The current attachment directory contained the instruction text. The preserved local original PDF was reused and verified against its established source checksum. All 333 existing crops were compared with freshly rendered original source pixels, including geometry, labels, vector extents and footer exclusion. Zero crops were regenerated or overwritten. Original printed keys, source question numbers and examination dates were checked again for the seven selected records.

The legacy importer fingerprint covers the entire Python module, including review-only functions. Because the new review/approval checks change that fingerprint, the existing extraction was source-revalidated and a **review-only-code-revalidation** event appended to source history. It retains the previous fingerprint `022c6946069e43536c5210aee8bb912e36894d0fd20f083e2476972737086dff`, records the validating fingerprint `70c0632c3da674f0dee6a90fbf8616e6d5364819dce818c419a24a01b9cbfcd4`, and records 333 comparisons / zero regenerated crops. Earlier history entries, imported timestamp, raw records and Batch 1–5 reconciliation metadata remain unchanged. This was not a re-extraction.

`academic_qa.py --owner-adjudication` reuses source-pixel, Boolean-choice, exact-numeric, textbook-evidence and snapshot validation from the existing QA framework. The seven owner IDs, page identities and answer selections are an exact authorized scope. The owner instruction, decision package, original PDFs, before snapshots, review engine and applied state are hash-bound. Stale or changed input fails before writes. Academic Batch 1–5 replay is blocked after this checkpoint. Read-only execution and repeated apply produce zero changes to any private file's bytes or modification time.

## Final totals

| Measure | Before | After |
|---|---:|---:|
| Historical questions / original active crops | 333 / 333 | 333 / 333 |
| Independently verified answers | 326 | **326** |
| Newly independently verified in this milestone | — | **0** |
| Independently unresolved/qualified reviews | 7 | **7** |
| Owner-adjudicated answers | 0 | **7** |
| Questions awaiting an owner answer selection | 7 | **0** |
| Owner publication approvals | 0 | **0** |
| These seven blocked from graded publication | 7 | **7** |
| Raw extraction complete / partial | 292 / 41 | 292 / 41 |
| Effective extraction complete / partial | 321 / 12 | 321 / 12 |
| Mapping verified / proposed / needs review | 257 / 40 / 36 | 257 / 40 / 36 |
| Published Practice questions / images | 420 / 420 | 420 / 420 |

The seven classifications remain Chapter 1; five precise context mappings remain verified and two proposed. This is not a reclassification of the other 326 questions. The independent `completedExplanations` metric remains 326; seven separately qualified owner explanations are now recorded.

## Validation

All **265 distinct suite tests passed**:

| Check | Result |
|---|---|
| Python `unittest discover -s tests -p test_*.py` | **99 passed**, including 12 new owner-adjudication regressions, all five academic batches, extraction, promotion, editorial conversion and figure tests |
| Application Vitest | **82 passed** |
| Firebase security-rule/real-SDK sync tests | **12 passed**, local demo emulators only |
| Production-preview Playwright | **52 passed** |
| Editorial reader Playwright | **16 passed**, including all 100 source pages |
| Account/migration/offline/cross-device Playwright | **3 passed**, isolated local demo build and emulators |
| Editorial server Node test | **1 passed** |
| Astro / TypeScript | Zero errors, warnings or hints |
| Production build and release verification | Passed: 420 question/image bindings, 100 reader pages, 47 figures, 81 spatial crops |
| Real private integrity and replay | Passed: 326 whole prior reviews preserved, exactly seven updated, all raw records/images unchanged, no replay writes |
| Private gallery smoke check | Passed: seven owner states, seven original images, D qualification and grading blocker visible, POST 405, raw PDF request 404 |
| Historical publication dry run | Zero approved inputs, additions, updates or conflicts |

The eight Python editorial-converter tests were also rerun by `test:editorial`; they are counted once above. Browser checks retain progress, practice, keyboard navigation, reading checkpoints, bookmarks, mobile layout and account compatibility. Firebase tests use `demo-itpec-textbook`, never production learning records. Existing build chunk-size and optional Firebase CLI remote-MOTD warnings do not affect passing validation.

Real-data integrity checks compare every `src/` and `public/` file against the saved prechange hash; all match. The complete 326 earlier review objects compare identically, including their serialization. Original `questions.json`, `pages.json` and `duplicate-report.json` bytes match the preserved baseline. No new historical crop or question enters the production build.

## Private gallery and handoff

From the repository root:

```powershell
npm.cmd run questions:qa -- --owner-adjudication          # Read-only validation
npm.cmd run questions:qa -- --owner-adjudication --apply  # Idempotent private replay
npm.cmd run test:owner-adjudication
npm.cmd run questions:historical -- gallery               # Refresh the existing private gallery
npm.cmd run questions:review
```

Open `http://127.0.0.1:4319/`, then use a canonical anchor such as `#HIST-TECH01-2012A-Q013` or `#HIST-TECH01-2012A-Q030`. Each selected record shows its original image, owner-selection object, separate independent verification and publication blockers. For p.112 inspect the editorial option transcription; for p.119 inspect primary A, additional valid D, and the blocked grading state. The read-only server binds to loopback and does not serve raw PDFs or accept mutation requests. The verification-only browser server was stopped after testing.

Private inputs, exact before copies, decisions, change history, applied fingerprints, integrity report and gallery screenshot remain under ignored `.local/historical/technology-01/owner-adjudication/`. They are not public assets and are not committed. A fresh clone requires those private inputs and original PDFs to replay this reconciliation; ordinary builds and synthetic regressions do not.

Tracked changes: `scripts/academic_qa.py`, `scripts/historical_questions.py`, `tests/test_owner_adjudication.py`, `package.json`, `README.md`, and this report. The validated changes are committed/pushed only to the existing feature branch. The final commit hash is supplied in the final handoff and private completion report. No merge, deployment, publication or final publication approval is authorized or performed.
