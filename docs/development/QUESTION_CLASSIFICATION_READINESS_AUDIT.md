# Complete historical question classification and publication-readiness audit

23 October 2026. Feature branch: `feature/chapter1-question-integration`. Baseline: `db83363ba6510857845d75bef0e6c58e5903f1d0`.

Audited all **333 Technology-01 questions** against the complete **487-page FE Volume 1**, current private reviews and current website section/concept definitions. The audit recommends **292 Hardware candidates**, **29 questions for other Volume 1 chapters**, **three provisionally outside Volume 1**, and **nine uncertain**. These are audit recommendations for owner review, not applied classification changes or publication decisions.

All **326 independently verified answers and explanations**, **seven qualified owner-adjudicated records**, original question records, source images, checksums, provenance and review history are unchanged. All **1,491 protected private-catalog and `src/`/`public/` files** retain their original bytes and modification times. The public catalog remains **420 questions / 420 images**. No owner approval, historical publication, main merge, deployment, other historical-PDF processing or original Practice repository modification occurred.

## Coverage and evidence

The complete textbook was text-indexed and its 487 physical pages visually scanned in 14 numbered contact sheets. Focused readings cross-checked relevant passages throughout all seven chapters; 29 selected pages were rendered at larger scale. All 12 currently partial question images were visually examined. This was a classification/layout audit, not a claim of line-by-line proofreading of the entire volume or a new independent solve of every answer.

Every question's year, April/October season, question number and immutable transcript checksum were checked against its original PDF page. All current question-image file hashes were checked. Earlier academic and owner-review source-pixel comparisons were reused; this milestone did not regenerate images or claim 333 new pixel comparisons. The ledger binds every canonical ID to its current content hash, source pages, image hashes and complete review-object hash. Every recommended textbook passage is checked against a freshly extracted page, its text checksum, physical page and printed label.

| Source | SHA-256 |
|---|---|
| Technology-01.pdf, 333 physical pages | `5c74e109ff2129f70189b55e79e7af3a806183cf0c1aa8082195aa942d1c16b1` |
| FE Vol 1.pdf, 487 physical pages | `1e1f2ec364a52751333b1e3ab2a2f2548e9345cd06a7c300b8a7075fb51c3d1b` |

Physical textbook p.83 is an **unnumbered UART insert** between printed pp.77 and 78. Physical p.181 is a **visual-only MIDI connection illustration** between printed pp.171 and 172. Empty extracted text on p.181 is not a blank page or absence of evidence. Printed labels are extracted and checked individually; a single PDF-to-print offset is unsafe. Negative text searches alone are not treated as conclusive proof that a visual topic is absent.

## Classification inventory

The private ledger explicitly annotates all 333 questions, including **187 previously lacking a `classification` object**. The original reviews remain untouched, so those original annotation gaps are preserved until a separately reviewed implementation milestone applies decisions.

| Recommended classification | Count | Placement result |
|---|---:|---|
| Chapter 1 Hardware | **292** | 269 numbered-subsection recommendations; 22 context-only placements; one unnumbered UART insert |
| Chapter 2 Information Processing System | **11** | Performance evaluation, multimedia and code design |
| Chapter 3 Software | **12** | Utilities, fonts, languages, OS memory and I/O management |
| Chapter 5 Network | **5** | ECC/Hamming and wireless-LAN teaching |
| Chapter 7 Data Structure and Algorithm | **1** | Decision-table teaching |
| Provisionally outside Volume 1 | **3** | Actuator, battery chemistry and electrical-energy calculation; no forced subsection |
| Uncertain | **9** | Existing eight uncertain mathematics/set questions plus expression-cost optimization on historical p.312 |
| Total | **333** | Each canonical occurrence retained |

The 41 non-Hardware/uncertain records are explicitly excluded from the audit's Hardware candidate list. Other-chapter records and their answer evidence are preserved in a separate list, without invented routes for chapters not implemented on the website. Cross-chapter supporting passages are labeled secondary; their presence does not automatically change a question's primary teaching home.

Key corrections and retained placements are below. Historical page means physical `Technology-01.pdf` page. Textbook pages are **printed / physical PDF**.

| Historical page(s) | Audit recommendation and evidence |
|---|---|
| 231, 324 | Replace Hardware processor-speed recommendations with **Chapter 2, 3-1-2 Evaluation of the CPU**, pp.140–141 / 149–150. The instruction-mix example and CPI/clock/MIPS derivation are explicitly taught there. |
| 273, 307 | Recommend **Chapter 2, 5-1-4 Moving Image Processing**, p.173 / 183, for frame-rate/duration video-data calculations. Hardware VRAM capacity p.98 / 104 is secondary support for single-frame size. |
| 236, 257 | Recommend **Chapter 5, 1-3-3 Error Control**, p.299 / 309. The book explicitly connects ECC to memory. Hardware numerical approximation/rounding error is not ECC. The source-supplied redundancy formula is not claimed as a textbook formula. |
| 285 | Recommend **Chapter 2, 5-1-2 Sound Processing**, pp.170–171 / 179–180. Sampling frequency and quantization rate determine PCM capacity; flash is just the storage medium. |
| 312 | Keep **uncertain**, with no exact subsection. The cited arithmetic-circuit page does not teach the decisive algebraic factorization/expression-cost optimization. No unsupported exact replacement is proposed. |
| 20 | Retain Hardware classification and reference the unnumbered physical p.83 UART insert. The current interface subsection is not the actual location of that source explanation. |
| 70, 102, 134, 249 | Retain Hardware context, propose logic-circuit context rather than equating seven-segment encoding with a display-resolution paragraph. No exact seven-segment teaching passage was established; placement stays context-only. |
| 199 | Recommend CPU bus context, **3-1**, p.48 / 53, with cache/access-gap support p.70 / 75. Keep the named bottleneck placement context-only. |
| 322 | Retain Character Data, **2-3-1**, p.29 / 34, as character-code/parity context; use Chapter 5 p.297 / 307 for the actual even-parity algorithm. |
| 183 | Preserve Chapter 5 ECC classification. Ordinary Hamming/ECC teaching on p.299 / 309 does not establish every extended SECDED assertion. Existing independent answer evidence remains unchanged. |
| 213 | Preserve Hardware optical-disc context. The DVD-RAM row p.88 / 94 establishes rewritability, not the numerical endurance claim; retain the existing independent primary-source answer evidence separately. |
| 275, 326 | Preserve both distinct examination occurrence IDs under Chapter 3 I/O-management context, p.209 / 219. The general I/O paragraph does not teach the exact LOOK scheduling algorithm. |
| 245 | Retain Hardware **4-1-2**, p.82 / 88: cluster/sector allocation and rounding occupied blocks are explicitly taught. Chapter 3 file systems is secondary support. |
| 284 | Retain Hardware **2-3-3 Error**, p.43 / 48: the relative-error ratio is explicitly printed. |
| 169 | Preserve Chapter 7 **2-5 Algorithm Design**, p.443 / 453, which explicitly teaches decision tables. Do not force this into a circuit highlight merely because it uses Boolean expressions. |
| 185 | Preserve the precise RS-232C/modem interface mapping in **5-5-2**, p.106 / 112. A general serial/parallel paragraph is not a reason to move this question. |

The private JSON inventory supplies the full question-by-question rationale, original classification/mapping, proposed chapter/heading/topic, actual website section/anchor where applicable, supporting excerpts, evidence role and source bindings. The CSV and Markdown inventories cover the same 333 IDs.

## Mapping audit

All **40 proposed**, **36 needs-review** and **257 verified** mappings were audited. Their authoritative statuses remain unchanged. The audit flags **293 distinct mappings** for one or more citation, placement, concept/editorial or future-chapter actions. This includes context-preservation work, not 293 claims that the question's answer or broad chapter is wrong. Forty mappings have no additional mapping issue under this audit; they still need the separate publication gates.

| Mapping finding | Records; counts overlap |
|---|---:|
| Existing mapping not verified | 76 |
| Legacy heading-only citation needs a bounded structured passage | 184 |
| Existing mapping has no textbook evidence | 12 |
| Current Hardware mapping contradicts the recommended classification | 5 |
| Recommended Hardware subsection/context differs | 6 |
| Exact numbered placement not established | 42 |
| Hardware concept/highlight requires specific editorial review | 133 |
| Exclude from Hardware highlights | 41 |

The five classification contradictions are historical pp.231, 273, 307, 312 and 324. The six Hardware subsection/context recommendations concern pp.70, 102, 134, 199, 249 and 313; none is automatically applied. For context-only rows, a suggested context heading is not an approved exact placement.

Verified stamps were not accepted as sufficient source evidence. Many older citations point to a subsection's opening page rather than the actual definition, formula or example. The audit supplies actual supporting pages, such as CPU registers p.47 / 52 and VRAM p.98 / 104. One older superscalar evidence object binds `checkedText` plus line IDs with a **fragment checksum**, rather than a full-page checksum; it was validated using its actual checksum convention and was not falsely reported as corrupted.

Existing concepts are checked against both section membership and TOC `conceptIds`. Matching concepts can be reused in principle; an empty `sourceHighlight` field alone does not invalidate the 13 existing public concepts. New concepts still need a specific reviewed source paragraph/fragment, title and summary. No automatic highlight creation or question association occurs.

There are **36 priority Hardware candidates** with independent verification, a complete bound accessible review, verified existing mapping and a matching existing concept/numbered subsection. They are a planning subset **after mandatory repairs and approvals**, not an eligible publication batch. Legacy passage binding and per-question highlight review can still be required.

## Extraction and accessibility repair queue

Raw extraction remains **292 complete / 41 partial**. Effective reviewed extraction remains **321 complete / 12 partial**. All 12 original images are intact; blanket recropping is not warranted.

| Historical PDF | Specific remaining defect | Proposed repair |
|---|---|---|
| 103 | Second output-table column heading blank | Preserve the literal blank; label any interpreted signal separately and bind an accessible table. |
| 111 | Option C lacks a closing parenthesis | Preserve original text; explain grouping as editorial interpretation. |
| 112 | Only A is labeled in the source | Retain the existing owner-confirmed option reconstruction as editorial and retain the grading block. |
| 128 | Private-font logical/comparison symbols; incomplete bound accessible review | Transcribe all operators/parentheses and choices; add content/image binding and description. |
| 148 | Second input-column heading blank | Preserve blank source heading; distinguish the inferred signal label. |
| 152 | Imprecise literal MMIO terminology | Keep the source wording and existing owner clarification separate. |
| 163 | Literal option D reads `Party` | Preserve literal text and separately label the probable typo. |
| 179 | Literal option C ends `Exclusive-` | Keep the probable reconstruction separate from verified literal source text. |
| 283 | Multiplication/gray-level notation; no complete bound accessible record | Bind the intact image and all original choices; supply readable notation. |
| 285 | Multiplication and decimal exponent in PCM capacity | Complete bound accessible options, description and units/exponent transcription. |
| 287 | VRAM multiplication notation; reviewed-image hashes absent | Bind image and transcribe dimensions, color depth and decimal MB definition. |
| 288 | Products/superscripts and address/data roles | Transcribe all original options faithfully and bind image/content review. |

Seven retain source/editorial defects; five chiefly need accessible transcription/provenance completion. No literal source defect is erased by an editorial interpretation.

An additional **182 raw-complete records** have legacy `extraction.status=complete` but no source binding, image description, accessible `optionText` or reviewed-image hash list. The current framework still counts these as effectively complete, which was preserved. Publication review is stricter: **194 records** need accessible review completion when these 182 are combined with the 12 partials. The repair queue identifies missing fields for each record; this is distinct from the 12-partial statistic.

## Publication readiness

Every row independently reports academic verification, qualified owner selection, raw/effective extraction, accessible review, classification, mapping, source metadata, grading constraints, existing approval and publication blockers.

| Blocker or status | Count |
|---|---:|
| Independently verified answers/explanations, preserved | 326 |
| Qualified owner-adjudicated selections, preserved | 7 |
| Paper/subject metadata not established for publication | 333 |
| Separate owner publication approval absent | 333 |
| Classification annotation missing in original review; audit recommendation prepared | 187 |
| Accessible image/option review incomplete | 194 |
| Mapping remediation/editorial review required | 293 |
| Effective extraction partial | 12 |
| Qualified owner selection still blocked from graded publication | 7 |
| Not a Hardware candidate | 41 |
| Ready for publication now | **0** |

Blocker counts overlap and must not be added. Owner answer selection remains separate from independent verification and final publication approval. The seven original academic `needs-review` objects remain intact, including the multiple-valid-choice and editorial-reconstruction qualifications. No grading model or student-progress key changes were made.

Reliable metadata established for all records: source PDF/page, original content/image identity, year, season and question number. FE is preserved as **owner-confirmed provenance**, not represented as printed on these pages. Paper and subject remain unknown; no value was inferred from a topic, season, filename or similar question. The existing strict Practice occurrence/image matching rule establishes **zero reliable published duplicates** here. No Practice answer or explanation was overridden, and both disk-scheduling occurrences remain separate.

## Reproduction and private deliverables

```powershell
npm.cmd run questions:audit                # Generate private audit reports only
npm.cmd run questions:audit -- --check     # Recheck evidence and report idempotency; no writes
npm.cmd run test:catalog-audit              # Synthetic regressions; no private inputs needed
```

`scripts/catalog_audit.py` reuses `historical_questions.py` verification/extraction/authority helpers and `academic_qa.py` object/snapshot hashing. The existing reconciliation engines are unchanged, preserving importer and owner-adjudication fingerprints. It refuses stale snapshot/PDF/record/review/image/page evidence, invalid classifications, invented printed labels, wrong feature-branch ancestry and output outside the private audit workspace. It also checks visual-review artifact hashes and a before/after guard over all 1,491 protected files. Unchanged output is not rewritten; `--check` compares deterministic reports without writing.

Private inputs and reports are under ignored `.local/historical/technology-01/catalog-audit/`:

| Path | Deliverable |
|---|---|
| `decisions.json` | Complete human-reviewed, hash-bound classification recommendation ledger |
| `before-files.json` | Protected pre-audit file hashes and modification times |
| `visual-review/` | 14 full-volume overview sheets, 29 focused textbook renders and 12 partial-question images |
| `reports/classification-inventory.json`, `.csv`, `.md` | All 333 question-by-question classifications and readiness dimensions |
| `reports/chapter1-candidates.json`, `.md` | 292 Hardware candidates, with no approval implied |
| `reports/other-chapter-preservation.json`, `.md` | All 41 other/uncertain/outside records kept out of Hardware highlights |
| `reports/mapping-extraction-repair-queue.json` | Individual placement, citation, concept and accessibility actions |
| `reports/publication-readiness-report.md` | Complete table, blocker totals, extraction details and next-milestone plan |
| `reports/book-coverage.json` | All 487 physical page identities, labels, chapter context and text checksums |
| `reports/audit-input-manifest.json` | Question/review/image/source and visual-review artifact bindings |
| `reports/summary.json` | Source-bound aggregate totals and audit-engine fingerprint |

A fresh clone needs the original PDFs and these private inputs to reproduce the real-data reports. They are intentionally not committed, copied into application assets or included in production. Synthetic tests and ordinary builds do not require them. No new review system or alternate publication gate was created.

## Validation

| Check | Result |
|---|---|
| Full Python suite | **118 passed**, including **19 new audit tests** |
| Application Vitest | **82 passed** |
| Astro / TypeScript | **0 errors, warnings or hints** |
| Production build/release verification | Passed; 420 public question/image bindings, 100 source pages, 47 numbered figures and 81 spatial crops |
| Production-preview browser suite | Initial run **51 passed / 1 failed**; unchanged BCD test **passed** on targeted rerun |
| Real private audit | All 333 source occurrences and 487 textbook page bindings validated; 1,491 protected files unchanged |
| Deterministic audit check | Passed; report bytes/modification times preserved on replay |

The initial browser failure waited for guest local storage after BCD image enlargement; Windows also denied normal preview-process cleanup. The test's preview was stopped, and the identical test passed with normal process permissions and clean cleanup. No application code, test assertion, timeout or unrelated textbook content was changed. The initial failure remains disclosed rather than being reported as a clean 52-test first run. The existing nonblocking build chunk-size warning remains unchanged.

The new synthetic regressions cover exact 333-ID scope, duplicate rejection, stale global and per-question snapshots, review edits, original transcript/source/image bindings, actual passages/page labels, classification independence from verified answers, exclusion of other/uncertain questions, metadata non-inference, Practice authority, qualified owner grading, editorial partials, legacy raw-complete accessibility gaps, website anchor/concept contradictions, fragment-checksum evidence, idempotency, private-only outputs and protected-file preservation.

## Proposed next milestone

1. Owner reviews the complete private ledger, particularly cross-chapter and uncertain decisions. Apply accepted classification/mapping annotations in a separate narrowly scoped, stale-snapshot-checked change, preserving all academic/adjudication objects and canonical IDs.
2. Replace heading-only citations with the actual source-bound passages. Correct the five contradictory Hardware mappings. Keep other-chapter records private until their teaching sections exist; retain context-only and unassigned placements without invented precision.
3. Complete the 12 specific extraction repairs and 182 additional accessible publication reviews. Keep original crops; distinguish literal source wording from editorial corrections and retain qualifications.
4. Review each candidate's exact source-highlight relationship. Reuse matching existing concepts where appropriate; prepare any necessary new concept fragments for explicit editorial review. The 36 priority candidates still need mandatory checks and approvals.
5. Establish paper/subject evidence without guessing; recheck reliable published Practice occurrence/image matches before promotion. Preserve published authority and distinct examination identities.
6. Address the seven qualified grading cases separately, including multiple-accepted-answer handling where needed. Do not turn owner-selected letters into independent verification or implicit publication permission.
7. Produce a concrete eligible promotion dry run, rerun publication/progress/browser safeguards, then obtain separate per-record publication approval. Publication, main merge and deployment remain outside this milestone.

Tracked changes are limited to the audit script, synthetic tests, package commands, README link and this report. Commit/push only to the existing feature branch; the final commit hash is supplied in the handoff. Work stops here for owner review.
