# Academic QA Batch 2 reconciliation

22 October 2026. Branch: `feature/chapter1-question-integration`. Baseline: `febdcbb`. This milestone updates only the private academic queue and its reconciliation tooling. No owner approval, historical publication, main merge or deployment was performed.

## Outcome

| Measure | Result |
|---|---:|
| Advisory records reconciled | 30 |
| Proposed answer letters independently evaluated | 29 |
| Newly accepted answers and verified worked explanations | 27 |
| Proposals withheld from verification | 2: historical pp.110 and 119 |
| Previously unresolved numeric-only case retained | 1: historical p.112 |
| Previous verified answers and explanations preserved exactly | 222 / 222 |
| Final verified answers / unresolved answers | **249 / 84** |
| Batch questions classified Chapter 1 / Chapter 2 / Chapter 3 | **27 / 1 / 2** |
| Batch classifications outside Volume 1 / uncertain | 0 / 0 |
| Original source question pages manually inspected | 30 |
| Active crops verified against fresh original PDF renders | 333 / 333 |
| Crops changed or regenerated | 0 |
| Canonical IDs, raw question records and image hashes preserved | 333 / 333 |
| Owner-approved historical records / public historical records | 0 / 0 |
| Existing published Practice questions retained | 420 |

The final unresolved total includes the three Batch 2 cases below and 81 other questions outside this batch. All 30 batch reviews gained source reconciliation history; 27 gained verified answer explanations, while three retain explanations of what can and cannot be established. No previous verified answer needed replacement. There is no new conflict with a previously verified answer or a reliably matched published Practice record.

## Findings requiring owner review

**Historical PDF p.119 — HIST-TECH01-2012A-Q030:** with its actual negation bars, source option A is `A AND NOT B`, and option D is `(A OR (B AND C)) AND (A AND NOT B)`. The source circuit simplifies to the same function. Exhaustive evaluation of all eight A/B/C combinations confirms **both A and D**. The stem asks for an equivalent expression, not the simplest expression. The advisory's A-only verification was therefore withheld. The printed key remains A; the review records `matchingOptions: [a,d]`, retains A as a proposal, and keeps answer status `needs-review`. The original D overbar was inspected again in a high-resolution option-region render and in the PDF's vector-line bounds. No source image or option was changed to manufacture uniqueness.

**Historical PDF p.110 — HIST-TECH01-2012A-Q001:** A is explicitly IEEE binary32, but B is only a 1/7/24-bit sign/exponent/fraction layout. The source does not define B's radix, bias or normalization. The proposed C comparison requires extra conventions. A concrete counterexample compatible with that layout is hexadecimal excess-64 floating point: `(1−2⁻²⁴)×16⁶³` exceeds IEEE binary32's `(2−2⁻²³)×2¹²⁷`, despite having fewer exponent bits. Also, binary32 normal significands include an implicit leading bit, so 23 stored fraction bits alone do not prove lower precision than 24 stored bits in an unspecified format. C is retained as the proposed exam-intent answer, with `needs-review`, rather than accepted unconditionally. This does **not** assert that B must be IBM hexadecimal format. The textbook itself discusses radix 2 or 16, IEEE and IBM exponent encodings, and omitted leading bits at printed pp.38–39 / physical PDF pp.43–44. [IBM's hexadecimal representation documentation](https://www.ibm.com/docs/en/hla-and-tf/1.6.0?topic=lq-representation-hexadecimal-floating-point) supplies the counterexample's radix/exponent convention; its indexed primary-source excerpt was available, while direct page retrieval returned HTTP 403.

**Historical PDF p.112 — HIST-TECH01-2012A-Q013:** effective address is `100+200=300`; the memory table gives `memory[300]=1300`. The original prints only `a)` beside 1201 and no b/c/d labels beside 1300, 2200 or 2300. Numeric result **1300** is retained, but no reliable answer-letter identity was recovered. `independentAnswer` remains null, answer verification remains `needs-review`, and extraction remains partial. The printed B key is preserved without being treated as independent proof.

## All 30 Batch 2 decisions

All rows remain **unapproved for publication**. “Verified” describes the independently supported answer. “Mapping” is the Chapter 1 placement status; the three other-chapter questions have verified classifications and supporting locations, but remain outside the Chapter 1 publication mapping. Page pairs in the location column are **printed textbook page / physical textbook PDF page**, not historical question pages.

| Historical PDF p. | Canonical question ID | Proposed → reconciled answer | Classification | Textbook evidence and final mapping |
|---:|---|---|---|---|
| 68 | HIST-TECH01-2016S-Q024 | D → D, verified | Ch.1 | 3-4-1 logical laws, 65/70; mapping proposed |
| 70 | HIST-TECH01-2016S-Q026 | A → A, verified | Ch.1 | 5-2-1 Display context, 97/103; seven-segment mapping proposed |
| 71 | HIST-TECH01-2016S-Q027 | D → D, verified | Ch.3 | 1-1 Systematic Classification / Application software / word processing fonts, 189/199; Chapter 1 mapping pending |
| 72 | HIST-TECH01-2015A-Q002 | B → B, verified | Ch.1 | 3-4-1 logical laws, 65/70; mapping proposed |
| 73 | HIST-TECH01-2015A-Q010 | C → C, verified | Ch.1 | 3-3-3 Indirect addressing, 59/64; mapping verified |
| 74 | HIST-TECH01-2015A-Q011 | B → B, verified | Ch.1 | 3-5-1 cache-fill explanation, 70/75; mapping verified |
| 77 | HIST-TECH01-2015A-Q022 | B → B, verified | Ch.1 | 3-4-1 logical laws, 65/70; mapping proposed |
| 79 | HIST-TECH01-2015S-Q020 | A → A, verified | Ch.3 | 1-1 Service/utility programs, 185/195; Chapter 1 mapping pending |
| 80 | HIST-TECH01-2015S-Q023 | A → A, verified | Ch.1 | 3-4-1 Sequential circuit context, 62/67; exact JK mapping proposed |
| 83 | HIST-TECH01-2014A-Q011 | C → C, verified | Ch.1 | 3-3-3 Indirect addressing, 59/64; mapping verified |
| 84 | HIST-TECH01-2014A-Q012 | C → C, verified | Ch.1 | 5-5-2 Bluetooth, 109–110/115–116; mapping verified |
| 85 | HIST-TECH01-2014A-Q021 | C → C, verified | Ch.1 | 3-4-1 logical design/laws, 65/70; selector mapping proposed |
| 87 | HIST-TECH01-2014S-Q011 | D → D, verified | Ch.1 | 3-3-3 addressing context, 59/64; exact register-indirect mapping proposed |
| 93 | HIST-TECH01-2014S-Q027 | B → B, verified | Ch.1 | 3-4-1 De Morgan laws, 65/70; mapping proposed |
| 95 | HIST-TECH01-2013A-Q002 | B → B, verified | Ch.1 | 3-4-1 XOR/logical design, 64/69; mapping verified |
| 102 | HIST-TECH01-2013A-Q028 | C → C, verified | Ch.1 | 5-2-1 Display context, 97/103; seven-segment mapping proposed |
| 103 | HIST-TECH01-2013A-Q029 | B → B, verified | Ch.1 | 3-4-1 XOR/logical design, 64/69; mapping proposed; extraction partial |
| 105 | HIST-TECH01-2013S-Q006 | D → D, verified | Ch.1 | 3-4-1 logical laws, 65/70; mapping proposed |
| 108 | HIST-TECH01-2013S-Q027 | C → C, verified | Ch.1 | 3-4-2 full-adder table, 68/73; mapping verified |
| 109 | HIST-TECH01-2013S-Q028 | D → D, verified | Ch.1 | 3-4-1 XOR/logical design, 64/69; mapping proposed |
| 110 | HIST-TECH01-2012A-Q001 | C → needs-review | Ch.1 | 2-3-2 floating point, 38–39/43–44; mapping verified; B format unspecified |
| 111 | HIST-TECH01-2012A-Q002 | A → A, verified | Ch.1 | 3-4-2 arithmetic/adders, 68/73; mapping verified; extraction partial |
| 112 | HIST-TECH01-2012A-Q013 | Unresolved → unresolved, value 1300 | Ch.1 | 3-3-3 Base addressing, 58/63; mapping verified; choice labels absent |
| 114 | HIST-TECH01-2012A-Q015 | C → C, verified | Ch.1 | 3-3-3 Indirect addressing, 59/64; mapping verified |
| 118 | HIST-TECH01-2012A-Q029 | C → C, verified | Ch.1 | 3-4-1 De Morgan laws, 65/70; mapping proposed |
| 119 | HIST-TECH01-2012A-Q030 | A → needs-review, A and D equivalent | Ch.1 | 3-4-1 logical laws, 65/70; mapping proposed |
| 124 | HIST-TECH01-2012S-Q016 | D → D, verified | Ch.2 | 5-1-2 Sound Processing / PCM, 170–171/179–180; Chapter 1 mapping pending |
| 125 | HIST-TECH01-2012S-Q026 | B → B, verified | Ch.1 | 3-4-1 logical laws, 65/70; mapping proposed |
| 126 | HIST-TECH01-2012S-Q027 | B → B, verified | Ch.1 | 3-4-1 XOR/logical design, 64/69; mapping proposed |
| 129 | HIST-TECH01-2011A-Q003 | C → C, verified | Ch.1 | 3-4-1 De Morgan laws, 65/70; mapping proposed |

All 30 chapter-level classifications are supported: 27 Chapter 1, one Chapter 2 (PCM), two Chapter 3 (fonts and archiver). Within the batch there are 10 verified Chapter 1 mappings, 17 proposed precise mappings, and three other-chapter mappings held out of Chapter 1. Across the entire private queue, mapping statuses are **219 verified / 75 proposed / 39 needing review**. Chapter classification, exact mapping and answer verification are deliberately separate.

## Visual, mathematical and mapping corrections

Thirty distinct original Technology-01 question pages were rendered and visually inspected. Additional enlarged views were used for overbars, small segments, table headers and subscripts. These checks are not a claim of manual visual approval for the whole 333-question bank. All 333 active crop files were separately decoded and compared with fresh 300-dpi RGB source renders, and checked for source text, vectors, embedded-image extent, geometry, dimensions, hash integrity and answer-footer exclusion. **No crop defect requiring replacement was found in Batch 2.** The Batch 1 p.45 repair and all other existing crop files remain unchanged.

| Historical pages | Source-confirmed treatment |
|---|---|
| 68,72,77,93,95,105,109,118,119,129 | Restore explicit NOT/AND/OR/XOR/NAND/NOR scope in reviewed descriptions/options. Preserve every original image and immutable raw transcript. Eleven complete four-option Boolean comparisons include the p.111 adder alternatives and detect p.119's duplicate equivalence. |
| 70 | Independently derive active-low common-anode input `0110000` from lit segments A,D,E,F,G. Preserve the source bit order A (MSB) through G (LSB). |
| 80 | Transcribe all four original JK truth tables, including hold/toggle and Q/Qbar ordering. Enumerate all eight combinations of J,K,previous-Q. Apply the rising-edge behavior stipulated by the question. The textbook's example is a different flip-flop; exact JK mapping remains proposed. |
| 85 | Trace the actual C3 selector path as direct S1 and inverted S2; restore all four S1/S2 option pairs. |
| 102 | Derive `6D₁₆=01101101₂`; map P0–P6 to a–g and P7 to the dot. Independently compare all eight states in each original image. Only C lights a,c,d,f,g with the dot off. |
| 103 | Restore all XOR/XNOR and AND/OR table entries. The source second output-column header is genuinely blank. Store source headers `[C,null]` and interpreted headers `[C,D]` separately; retain partial extraction. The explicit row label B and the diagram's two outputs support the answer with that documented inference. |
| 108 | Restore the full-adder answer table in **carry, sum** order: 00,01,10,11 for a–d. Inputs 1,0,1 give carry=1,sum=0, C. |
| 111 | Preserve subscripts x0,y0,x1,y1 and verify all 16 two-bit additions. Original option C lacks a closing parenthesis. Flag the source typo and keep extraction partial; the semantic XOR grouping used for comparison is explicitly an interpretation. A remains independently supported. |
| 112 | Preserve the original unlabeled options and numeric 1300 result; do not create b/c/d labels. |
| 125 | Restore the actual source option rows `(A,B,C)`: a=001, b=100, c=110, d=111. Trace branches `AC`, `B NOT C`, `NOT A C`; output simplifies to B OR C. Only row B gives zero. |
| 126 | Preserve the timing chart; six stable intervals give AB=`00,11,10,01,10,11` and F=`1,1,0,0,0,1`. Validate these observations against XNOR. |

Raw extraction remains **292 complete / 41 partial**, exactly as at the baseline. Six raw-partial questions (72,77,93,102,105,129) now have complete source-bound enrichment. Two raw-complete questions (103,111) now correctly have partial reviewed extraction because of source defects. Effective extraction is therefore **305 complete / 28 partial**, derived from the shared status function rather than edited totals. The earlier p.148 missing-header state remains partial.

The complete 487-page FE Volume 1 text, contents and index were available for classification and context searches. Reference corrections include:

- p.110's proposed textbook physical p.39 actually discusses fixed point. Floating-point radix and normalization evidence is at physical pp.43–44 (printed pp.38–39).
- p.71's font passage is on the proposed page, but under Chapter 3 **1-1 / Application software / word processing**, not **2-2 OS Management Functions**.
- p.74's explicit cache block-fill statement is at physical p.75 (printed p.70), more precise than adjacent access-time material.
- p.112 uses **base addressing**, explicitly explained at physical p.63 (printed p.58); the advisory p.64 is the adjacent indirect-addressing explanation.
- Seven-segment display, register-indirect, JK and selector contexts remain proposed where the textbook supplies broader coverage without the exact passage. No future-chapter public concept or new highlight was created.
- Bluetooth evidence retains the textbook's historical class-dependent ranges. It is not presented as a universal modern Bluetooth range limit.

## Source identity and advisory handling

All three supplied files were read completely and treated as advisory proposals. CSV rows and the Markdown decision table are checked for consistency with JSON identities, source pages, letters, classifications and proposed textbook locations. Their prose is never executed or interpreted as approval authority.

| Artifact | SHA-256 |
|---|---|
| Batch02 JSON | `bdfb06857bc94d4f645d1181ce66d79aaa0a0295dbb680425035dc69ca0525df` |
| Batch02 Markdown | `ee0046b855300270dac22a5e8562cfcf1818a2b4cd47ac18810c731dd8448ade` |
| Batch02 CSV | `4f4edd7ed1c5590388d347048fc1ff399d56f3118986cdb49c03a39974d1e12a` |
| Original Technology-01 PDF | `5c74e109ff2129f70189b55e79e7af3a806183cf0c1aa8082195aa942d1c16b1` |
| Complete FE Volume 1 PDF | `1e1f2ec364a52751333b1e3ab2a2f2548e9345cd06a7c300b8a7075fb51c3d1b` |

The three advisory snapshot hashes matched the actual starting files: questions `9beb6466c28ac6b273ddd33f5a4352c07acb4b592b41ce15eae2c129c1947c5a`, reviews `67a4986af6a2872c57673ed0643bbd76ba75fc264c8723d85ec62313b39e6591`, manifest `59bc1be58243c2d100cc7677e6e23508efcecc68791ce1052e182b4ee7f08415`. All 30 IDs, record positions, raw-content hashes, source references, printed keys, raw extraction flags, review-snapshot references and crop paths matched. None of the batch records was previously verified.

Supporting textbook evidence stores printed/physical page references, source hashes, checked excerpts and page-text hashes. Independent evidence includes eleven full four-option Boolean comparisons, three other Boolean-equivalence proofs, all eight JK input/state combinations, all 16 two-bit additions, segment calculations, selector cases, a general n-input Boolean argument, source option-row evaluation and checked waveform intervals. [TI's JK datasheet](https://www.ti.com/lit/ds/symlink/sn74hc112.pdf) supports the characteristic state table; that device is falling-edge triggered, and is not used to override the question's stated rising-edge behavior.

## Framework, history and integrity

The existing `scripts/academic_qa.py` now accepts explicit `--batch 2`. It reuses the same question/review files, proof evaluator, crop validator, manifest and gallery. There is no second live review system. Private `decisions.json` is editorial staging prepared after source inspection; advisory answer/status fields never become verified merely by import.

Batch 2 requires exactly its 30 decision IDs and binds its preserved baseline, both source PDFs, all three advisory hashes and independent decision hash. Repeat application is accepted only against the same baseline or its recorded applied state. Stale source, review, input, scope, image identity or companion data is rejected. Earlier Batch 1 replay is blocked after Batch 2 so it cannot overwrite later reconciliation state; select the batch explicitly.

Existing verified verification/explanation objects are preserved. A proposed contradiction to verified work would be retained for owner review rather than silently replacing it. The new four-option proof check requires exactly one matching choice before a verified single-answer decision can pass; it also supports documenting multiple matches on unresolved questions. Observation checks reject inconsistent waveform transcription.

Before modification, byte-exact copies of questions, reviews, manifest, page records and duplicate report were preserved under `.local/historical/technology-01/qa-batch2/before/`. Per-dimension changes and recoverable snapshots are in `qa-batch2/history/`; per-review provenance records Batch 2 and advisory/decision fingerprints. The manifest retains Batch 1 under `qaReconciliation.previousBatches` and keeps the original source/importer history. No importer fingerprint migration or question re-extraction was necessary.

Real integrity checks confirmed:

- The entire `questions.json` file remains byte-identical to the baseline, including all 333 IDs, content hashes, printed keys, source references, image metadata and owner-confirmed FE provenance.
- All 222 prior verified answers and explanations remain identical; reviews outside the 30-question scope are entirely unchanged.
- All metadata objects remain unchanged. FE stays owner-confirmed from Batch 1; precise paper and subject remain pending. No Morning designation is inferred.
- All 333 active image hashes are unchanged and source-pixel exact. The original source PDFs and page records are unchanged.
- Both a real dry-run and a repeated apply left all private-workspace bytes **and modification times** unchanged. Freshly derived manifest counts match the saved manifest.
- Every `src/` and `public/` file matches its pre-reconciliation hash. Student question IDs, attempt/bookmark schemas, guest storage, Firebase synchronization and textbook content are untouched.
- Fresh duplicate reconciliation found 333 distinct historical occurrences, zero reliably matched or ambiguous published occurrences and zero Practice answer conflicts. The existing matcher/promoter continues to preserve published Practice authority.
- Promotion dry-run reported zero approved inputs, additions, updates or conflicts. All 333 historical records remain unapproved and absent from the public build.

## Validation and inspection

The 82 existing Vitest tests, 13 Batch 1 academic tests, 10 new Batch 2 regression tests, seven existing extraction/approval tests and three isolated promotion tests passed. Astro/TypeScript reported zero errors, warnings or hints. The production build passed with 420 published records/images, 100 source-reader pages, 47 numbered figures and 81 spatial crops; its existing large-client-chunk warning remains.

All 52 production-browser tests also passed, giving **167 passing tests** across these suites. Browser coverage includes the original question viewer, answer/filter navigation, image enlargement, keyboard use, 320px layouts, bookmarks, exact reading-position restoration, saved progress and storage-denied behavior. Playwright ran with normal Windows process permissions for local preview-server startup and teardown.

The new tests cover v2 schema and source identity, companion consistency, preserved baseline/applied-state replay, stale snapshot/input rejection, preservation of 222 verified records and unchanged metadata, exact scope, numeric-only unresolved choices, duplicate-equivalent answers, overbar scope, waveform observations, cross-radix float counterexamples, n-input identities, two-bit addition and older-batch replay prevention. Existing synthetic promotion tests run in isolated temporary fixtures and never publish into the real catalog.

Local commands:

```powershell
npm.cmd run questions:qa -- --batch 2          # Read-only source/snapshot validation
npm.cmd run questions:qa -- --batch 2 --apply  # Reapply this private reconciliation; no approval/publication
npm.cmd run questions:historical -- verify
npm.cmd run questions:historical -- gallery
npm.cmd run questions:review
npm.cmd run test:academic-batch2
```

Open `http://127.0.0.1:4319/#HIST-TECH01-2012A-Q030` for the duplicate-equivalence case. The gallery also exposes p.110's missing-format assumptions, p.112's numeric-only result, source-bound reviewed options, classification evidence, extraction quality and approval blockers. Select an image to inspect its original resolution. The gallery remains read-only and loopback-only.

All source-page renders, enlarged region views, contact sheets, advisories, staging decisions, baseline backups, applied-state bindings, integrity report and change history remain in ignored `.local/historical/technology-01/qa-batch2/`. Only implementation, synthetic tests and this completion report are committed. A fresh clone needs these private artifacts and original PDFs to reproduce this private reconciliation; ordinary public builds and synthetic tests do not require them.

Changed tracked files: `scripts/academic_qa.py`, `tests/test_academic_qa_batch2.py`, `package.json`, README and this report. No dependency or application code changed. The exact feature-branch commit is supplied in the final handoff and available with `git log -1 --format=fuller`. Remaining work is owner examination of the three Batch 2 ambiguities, the other 81 unresolved records, pending precise mappings and paper/subject evidence, followed by separate approval before any publication.
