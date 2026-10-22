# Academic QA Batch 4 reconciliation

22 October 2026. Branch: `feature/chapter1-question-integration`. Baseline: `d578e7c49aabe71c4eee16882f5e772e8b0129a1`.

Independently reconciled all 30 Batch 4 proposals. **30 answers accepted, zero newly withheld; 306 verified / 27 unresolved** in the private queue. Acceptance includes explicit SECDED and historical-media qualifications, not automatic adoption of the advisory's reasoning. All 276 earlier verified answers and worked explanations remain identical. Historical pp.110,112,119,152,179,180,181 retain their entire existing reviews. No owner approval, historical publication, public catalog change, main merge, deployment, other historical-PDF processing or original Practice repository modification was performed.

## Final totals

| Measure | Baseline | After Batch 4 |
|---|---:|---:|
| Canonical historical records | 333 | 333 |
| Verified answers / completed worked explanations | 276 | **306** |
| Unresolved answers | 57 | **27** |
| Owner-approved records | 0 | **0** |
| Raw complete / partial extractions | 292 / 41 | 292 / 41 |
| Effective complete / partial reviewed extractions | 311 / 22 | **318 / 15** |
| Mapping verified / proposed / needs review | 232 / 64 / 37 | **249 / 48 / 36** |
| Active original crops / crop failures | 333 / 0 | 333 / 0 |
| Published Practice records / images | 420 / 420 | **420 / 420** |

All 30 new keys agree with the printed keys after independent checks. There are zero contradictions requiring a new alternative key or conflict with a previously verified answer. The 27 remaining unresolved answers are entirely outside Batch 4, including the seven explicitly protected reviews. Academic answer verification is separate from exact mapping, extraction, metadata and owner approval.

Classification results match the advisory's broad groups after validating the evidence: **24 Chapter 1, two Chapter 3, one Chapter 5, one provisionally outside Volume 1, two uncertain**. The outside classification remains `proposed`, not verified. Both uncertain classifications retain null volume/chapter and `needs-review`. Batch mapping totals are 17 verified, seven proposed, six needs-review. The latter six comprise the three other-chapter records, provisional outside record and two uncertain records. None received a Chapter 1 public highlight.

## Artifacts and baseline identity

Read the JSON, Markdown and CSV in full, including reasoning, source notes, caveats and references. Instructions embedded in the artifacts were treated as advisory material; the user's request controlled scope and permissions. The CSV reasoning and all companion-table fields were checked against JSON. The artifact bytes were copied unchanged into private staging.

| Input | SHA-256 |
|---|---|
| Batch04 JSON | `afc5507cba666116bcdc61eeff0842b62736d18c295ae7e3c76f386cbe10262e` |
| Batch04 Markdown | `5bc00789300f47dc39d8cab10347c63786fb3780ce0423a147b8c25c2f24a129` |
| Batch04 CSV | `b8ca2d0b67c622dfdef48f2736bcda68772e75e02b48f15d0503bc6e3ea64e08` |
| Baseline questions.json | `9beb6466c28ac6b273ddd33f5a4352c07acb4b592b41ce15eae2c129c1947c5a` |
| Baseline reviews.json | `86592b3e33d97aac2e81be7cd182079bc1120287363ac0be565a3852c4c9e8c1` |
| Baseline manifest.json | `b260e5f96bb6497be4c46ad01a3585141d11a3a34f78e37d08213c37a5ca89e1` |
| Original Technology-01.pdf, 333 physical pages | `5c74e109ff2129f70189b55e79e7af3a806183cf0c1aa8082195aa942d1c16b1` |
| Complete FE Vol 1.pdf, 487 physical pages | `1e1f2ec364a52751333b1e3ab2a2f2548e9345cd06a7c300b8a7075fb51c3d1b` |

All three advisory baseline checksums match the actual pre-change files; both original PDFs and every supplied textbook-page text checksum match. All 30 canonical IDs, transcript/content hashes, image references and image-byte hashes match their original records. Baseline status is 276 verified, 57 unresolved, zero approved.

**Record-index convention correction:** Batch 4 supplies zero-based `originalRecordIndex` values, unlike the one-based earlier artifacts. Each of its 30 indices was checked against the actual canonical ID at that zero-based position; no advisory byte was rewritten. Physical PDF pages remain one-based. In particular record index 181 is the new question on PDF p.182, not protected PDF p.181. The adapter uses this explicit Batch 4 convention and rejects a shifted/mixed index rather than guessing offsets.

## Full 30-question decision table

Historical pages are physical `Technology-01.pdf` pages. Textbook locations are **printed / physical PDF** pages; offsets vary. Canonical IDs retain prefix `HIST-TECH01-`; suffixes below identify the unchanged records. V/P/R denote verified/proposed/needs-review **mapping**, not permission to publish. Every row's answer was accepted; there are no newly withheld Batch 4 answers.

| Historical PDF | Canonical suffix | Accepted answer | Classification; textbook evidence | Mapping | Independent reconciliation / correction |
|---:|---|:---:|---|:---:|---|
| 182 | 2008A-Q021 | B | Ch.1, 3-1 CPU/clock generator; 47 / 52 | V | Clock controls CPU operation timing. Qualify frequency comparison to the same design/work; frequency alone does not rank different architectures. |
| 183 | 2008A-Q024 | C | Ch.5, 1-3-3 Hamming/ECC; 299 / 309, plus primary SECDED sources | R | Hamming family is the applicable listed method. Simultaneous SECDED specifically needs the extended overall-parity form; plain distance-3 Hamming is not sufficient. Exhaustive construction checked. |
| 185 | 2008A-Q027 | D | Ch.1, 5-5-2 RS-232C; 106 / 112 | V | Book explicitly links modems to serial RS-232C; retain historical PC context. |
| 189 | 2008S-Q018 | B | Ch.1, 3-4-1 AND/NOT; 61 / 66 | V | Trace all junctions: WXYZ rows for AB=00,01,10,11 are 1000,0010,0100,0001. Every cell of all four source alternatives compared. |
| 190 | 2008S-Q019 | D | Ch.1, 3-4-1 sequential circuit; 62 / 67 | V | Cross-coupled NAND latch, active-low inputs: 00 invalid,01 set,10 reset,11 hold. Solve feedback equations; do not copy NOR polarity. |
| 198 | 2007A-Q019 | B | Ch.1, 3-4-1 logic laws; 65 / 70 | V | AB + NOT B simplifies to A OR NOT B. All four original circuit paths evaluated. |
| 199 | 2007A-Q020 | D | Ch.1, 3-5-1 memory access plus CPU bus; 70 / 75 and 48 / 53 | P | Limited CPU-main-memory transfer rate is the bottleneck. Add actual shared-bus explanation; exact named bottleneck anchor remains pending. |
| 200 | 2007A-Q021 | B | Ch.1, 3-3-4 Interrupt; 59–60 / 64–65 | P | Check for eligible pending interrupts before continuing normal fetch in the ordinary instruction-cycle model. Add priority/handling evidence; exact boundary sequence remains contextual. |
| 206 | 2007S-Q006 | C | Uncertain; no established exact Venn passage | R | Independently read x-only, outside-x and all-y shading; OR memberships over all eight regions. Preserve full complement scopes and universal rectangle. |
| 208 | 2007S-Q018 | A | Ch.1, 3-4-1 sequential-circuit context; 62 / 67 | P | Active-high NOR latch: 00 hold,01 reset,10 set,11 invalid. Source is NOR, not the textbook's NAND example. |
| 209 | 2007S-Q019 | B | Ch.1, 3-3-3 addressing; **57–59 / 62–64** | V | Direct X2, indirect memory[X2], relative X1+X2, indexed X2+X4. Add the relative/direct/indirect pages; advisory p.62 alone does not cover all four. |
| 213 | 2007S-Q027 | C | Ch.1, **4-2 Optical Disc**; 88 / 94, plus Sony evidence | P | Greater rewrite endurance supported by manufacturer data, not the textbook alone. Correct advisory heading 4-1-3, which is magnetic-disk average access time. |
| 214 | 2007S-Q028 | B | Ch.1, 5-2-2 Printer; 100 / 106 | V | Explicit CMYK ink description; distinguish subtractive printing from RGB light. |
| 215 | 2007S-Q029 | A | Ch.1, 5-2-2 laser printer; 102 / 108 | V | Actual page begins with laser-printer dpi/ppm text before the next heading. Select both resolution and pages/minute. |
| 219 | 2022S-Q001 | A | Ch.1, 3-4-1 logic laws; 65 / 70 | V | NOT A AND (A OR NOT B) reduces to NOR. Source B complements its inner A too; every bar and all four truth rows checked. |
| 223 | 2022S-Q021 | D | Ch.1, 3-4-1 NOR/laws; **63,65 / 68,70** | P | Four-NOR network D gives XNOR. All options: A XOR,B AND,C OR,D XNOR. Improve contextual reference from introductory p.66 to actual NOR definition. |
| 224 | 2022S-Q022 | D | Ch.1, 3-4-1 logic laws; 65 / 70 | P | Exactly 30 of 32 tape patterns valid. D complements both invalid minterms; B leaves E uncomplemented. Test all 32 patterns against all options. |
| 228 | 2021A-Q021 | C | Ch.1, 3-4-1 logic laws; 65 / 70 | V | Parallel AND/OR outputs into OR reduce to A OR B. Trace shared input junctions. |
| 229 | 2021A-Q022 | C | Provisionally outside Vol.1; watts context 16 / 21 | R | RMS 100V ×10A ×PF1 ×1.5h =1500Wh. Book mentions power in watts but no exact energy calculation was found; outside placement stays proposed. |
| 230 | 2021S-Q001 | B | Ch.1, 3-4-1 distributivity; 65 / 70 | V | (x+y)(x+z)=x+yz; compare all eight assignments and exact source alternatives. |
| 232 | 2021S-Q022 | C | Ch.1, 3-4-1 NAND/NOR/laws; **63,65 / 68,70** | V | Stem asks NOT an implementation. A/B/D implement AB+CD; C implements ABCD. All 16 rows and input/output bubbles checked. |
| 234 | 2020A-Q002 | A | Ch.1, 3-4-1 contradiction; 65 / 70 | V | A reduces to zero; B is satisfiable,C is p,D tautology. Retain original parentheses and bars. |
| 237 | 2020A-Q022 | C | Ch.1, 3-4-1 NOT/De Morgan; **63,65 / 68,70** | V | NOT added separately to each OR input produces NAND. No extra inputs or unstated tied-input wiring are supplied for multi-input gate alternatives. |
| 239 | 2020S-Q019 | C | Ch.3, **2-2-3 Memory Management**, paging; 206 / 216 | R | Byte-addressed 2^32 space /4096-byte pages =2^20. Refine the advisory's broad OS heading to actual 2-2-3; virtual page count is not physical frame count. |
| 240 | 2020S-Q022 | D | Ch.1, 3-4-1 De Morgan; 65 / 70 | V | NAND(x,y) OR NOT z equals NOT(xyz); preserve the OR input bubble and compare all eight inputs. |
| 241 | 2020S-Q023 | B | Ch.1, 3-4-1 XOR/laws; 64–65 / 69–70 | V | (A OR B) AND NOT(AB) is XOR. C complements A alone inside its parentheses; complete AB complement appears in B. |
| 242 | 2019A-Q001 | B | Ch.1, 3-4-1 tautology; 65 / 70 | V | pq OR NOT p OR p NOT q =1. Other three alternatives each fail; enumerate all four inputs. |
| 243 | 2019A-Q024 | B | Ch.1, 3-4-1 NAND/laws; 63,65 / 68,70 | P | Original wire topology gives A=C=NOT(BC), B=NOT(AB), D=NOT(ABC). B alone matches reference; distinguish middle B,B from B,C NAND inputs. |
| 246 | 2019S-Q017 | C | Ch.3, 2-2-1 Job Management/Spooling; 198 / 208 | R | Explicit book definition: use fast auxiliary spool between main memory and slower I/O to improve throughput. |
| 247 | 2018A-Q002 | C | Uncertain; 2^n context 21 / 26 | R | Inclusive union count 8+4−2=10; enumerate all 16 strings. Contextual bit combinations do not establish an exact constrained-counting anchor. |

## Source-specific cautions and unresolved boundaries

**p.183, Hamming SECDED.** C names a coding family that includes extended Hamming. The [University of Michigan instructional construction](https://www.eecs.umich.edu/courses/eecs373.w05/lecture/hamming.html) labels its overall-parity (8,4) construction Hamming and establishes distance four. [Microchip's CoreEDAC guide](https://ww1.microchip.com/downloads/aemDocuments/documents/FPGA/ProductDocuments/UserGuides/ip_cores/directcores/CoreEDAC_HB.pdf), introduction and physical p.6, distinguishes ordinary Hamming from the SECDED extension. The source does not specifically restrict C to plain (7,4), and none of the other listed methods provides the requested correction/detection behavior. C is verified as the family answer with an explicit qualification: simultaneous SECDED needs extended overall parity; plain distance-three Hamming cannot guarantee both at once. The original wording is unchanged. The textbook's seven-bit example is classified correctly as error-control context, not falsely cited as proof of simultaneous SECDED.

An independent exhaustive construction used all 16 four-data-bit messages. The extended code has minimum distance four; all 128 single-bit corruptions have exactly the original codeword within distance one; all 448 two-bit corruptions have no codeword within distance one and are detected without miscorrection. The unextended code has distance three, with a concrete two-error word only one bit away from a different valid codeword. This counterexample is in the regression suite. Qualification is part of the saved worked explanation, not an inferred owner correction.

**p.213, DVD-RAM endurance.** The [Sony DVD Guide Glossary](https://www.sony.com.sg/support/resources/en_AP/html/Compatibility/DVDCharts/DVDGloss.html) compares approximately 100,000 recording cycles for DVD-RAM with approximately 1,000 for DVD-RW/+RW. This supports the historical durability choice C. The book establishes that these are rewritable optical formats; it does not supply their endurance comparison. The explanation does not promise real-world lifetime or treat double-sided capacity as dual-layer support. Exact textbook mapping remains proposed, and the incorrect optical-disc heading is corrected to 4-2.

**p.206, Venn shading.** Three separately bounded diagrams were enlarged: first shades only x outside y and z; second shades everything outside x, including outside all circles; third shades all y including overlaps. The independent OR is x·NOT y·NOT z OR NOT x OR y, matching only C across eight memberships. All source alternative bars were transcribed explicitly. No generic Venn teaching passage was established in the complete book, so classification stays uncertain; database set operations do not supply a substitute anchor.

**p.243, NAND-only topology.** Each network was traced from a high-resolution original render, retaining the tied inputs and branch wiring. In B the lower first-level gates invert B and C separately. In D the middle gate instead NANDs B and C, while the bottom still inverts C. Those lower branches reduce to B OR C versus C. At A=B=1,C=0, B/reference gives 0 and D gives 1. Complete eight-row source-option proofs confirm B alone. A and C happen to be equivalent to one another but are not equivalent to the target; this does not create duplicate correct choices.

**Classification limits.** p.229 remains provisionally outside Volume 1 with `classification.status: proposed`, null chapter/volume and no Chapter 1 mapping. The whole-book search found watts/power-consumption context on physical21/printed16, which is recorded; lack of an exact Wh calculation does not prove the broad subject absent. p.247 retains uncertain classification even though bit-combination context was found. Both p.247 and p.206 have verified self-contained answers without a verified chapter placement. The two Chapter 3 questions and Chapter 5 question remain outside Chapter 1 publication mappings. This milestone did not start converting those chapters.

**Seven protected reviews.** Historical pp.110,112,119,152,179,180,181 were not academically reinvestigated or modified. Their full review objects, not just answer statuses, match baseline. The retained numeric result for p.112 remains 1300, without a fabricated choice label. All other nonscope reviews also match baseline exactly.

## Visual fidelity and extraction

Rendered and manually inspected all 30 original question pages, plus enlarged regions for Venn shading, NAND-only topology, decoder truth tables, latch polarity, formula bars, NOR networks and tape patterns. Printed answer keys were visible, so these checks are not claimed as a controlled blind exam. Boolean proofs cover every assignment; multi-output proofs check every source-table cell; latch proofs solve cross-coupled gate equations and distinguish hold from forbidden equal-output states. The source's “unstable” latch label is explained as a forbidden noncomplementary condition with possible release race, rather than asserting indefinite voltage while both controls remain driven.

All **333 active original images** were independently decoded and compared to fresh 300-dpi RGB source renders. Text, vectors, embedded-image extent, crop geometry, pixel boxes, dimensions, hashes and answer-footer exclusion passed. **Zero images were recropped, redrawn or replaced.** The earlier p.45 crop/history remains intact. Seven initially partial raw transcripts now have complete source-bound reviewed descriptions/options: pp.190,206,208,223,232,240,243. Raw text and raw extraction statuses remain immutable; effective extraction becomes 318 complete /15 partial. All Batch 4 reviewed extractions are complete, without pretending contextual academic cautions have changed source wording.

## Pipeline, preservation and replay

Extended the existing `academic_qa.py` with `--batch 4`, rather than adding another review store. The adapter preserves earlier index conventions, implements Batch 4's checked zero-based indices, validates all three companion tables including CSV reasoning, validates both PDF identities and baseline snapshots, and verifies advisory and independent textbook-page checksums/excerpts against the actual full book. It reuses the previous snapshot/book validators, source-pixel validator, merge logic, manifest and gallery.

Existing Boolean choice proofs now support the explicit `not-equivalent` relation required by p.232. Added reusable complete-table and NAND/NOR feedback proof checks; an answer must match exactly one selected original option/table. This does not infer a diagram from an answer letter: the source topologies/tables were transcribed after visual inspection. Separate checked decisions carry source/image/content bindings and worked evidence; advisory `verified` mapping labels do not become approvals or answer authority on import.

Exactly the 30 scoped IDs are permitted. Seven protected source-page numbers are guarded independently of the advisory exclusion list and record-index convention. Unassigned/outside classifications require null chapters and pending mappings. All 276 old verified answers/explanations and every nonscope review are rechecked before writes. Existing FE owner-confirmed provenance, paper/subject uncertainty and approval objects remain unchanged.

The saved baseline or exact recorded applied snapshot is required for replay, together with unchanged advisory and decision hashes. Stale data, modified source images, altered companions and changed decisions are rejected. Earlier batches 1–3 cannot replay over Batch 4. Real integration checks confirmed read-only execution and repeat apply make zero review changes and preserve **all private file bytes and modification times**. Source/importer history and previous batches 1,2,3 are retained; no importer fingerprint migration or re-extraction was needed.

Byte-identical questions.json preserves every canonical ID, raw hash, printed key, source reference, image identity and student-progress compatibility. All metadata, page records, duplicate-report bytes and images match baseline. Every `src/` and `public/` file matches its saved hash, including published questions, explanations, concepts, guest-progress/Firebase code and textbook content. Fresh duplicate reconciliation reports zero reliable/ambiguous matches, zero conflicts and 333 distinct results under existing match rules. The current published catalog's dated questions cover 2024–2026; these Batch 4 historical occurrences have no compatible dated occurrence there. Undated/unconfirmed metadata is not guessed to force a match. Existing ITPEC Practice authority remains intact whenever a reliable published match exists.

Publication validation was **dry-run only**: zero approved inputs, additions, updates or conflicts. All 333 historical records remain unapproved and absent from public output. Tests of promotion behavior use isolated synthetic fixtures, not the real catalog.

Private inputs, checked decisions, original renders/contact sheets, preserved questions/reviews/manifest/pages/duplicate-report baseline, per-dimension changes/history, applied-state hashes and integrity report remain under ignored `.local/historical/technology-01/qa-batch4/`. The existing loopback review gallery was updated. No raw textbook crops, historical question records or source PDF files are committed. Reproducing private reconciliation on another machine requires these local artifacts and the original PDFs; public builds and synthetic tests do not.

## Validation and handoff

The following passed: 82 Vitest tests; 13 Batch 1, ten Batch 2, 12 Batch 3 and **14 new Batch 4** academic tests; seven extraction/approval tests; three isolated promotion tests. Astro/TypeScript reported zero errors, warnings or hints. Production build/data validation passed with unchanged 420 published records/images, 100 source-reader pages, 47 numbered figures and 81 spatial crops. Its existing large-client-chunk warning remains.

New tests cover zero-based record identity and page separation, source-image checksum rejection, all seven protected pages, companion reasoning/mapping consistency, preservation of 276 answers and all nonscope metadata/reviews, exact scope, idempotency and stale input/data rejection, NOT-implementation selection, every decoder cell, NAND/NOR latch polarity, exhaustive SECDED and plain-code counterexample, Venn membership, NAND topology counterexample, energy/page/string calculations, provisional classifications and blocked older-batch replay.

All **52 production-browser tests passed**, giving **193 passing tests** across the listed suites. Browser coverage includes source reading, dedicated questions, highlights, navigation, keyboard use, image enlargement, mobile bounds, reading-position restoration, bookmarks and progress/storage behavior. Playwright used normal Windows process permissions for local preview-server startup and teardown. No account/rules implementation changed; no live Firebase data was written.

```powershell
npm.cmd run questions:qa -- --batch 4          # Read-only source/snapshot validation
npm.cmd run questions:qa -- --batch 4 --apply  # Idempotent private replay; no approval/publication
npm.cmd run test:academic-batch4
npm.cmd run questions:reconcile -- --dry-run
npm.cmd run questions:publish -- --dry-run
npm.cmd run questions:review
```

Private real-data integrity script: `.local/historical/technology-01/qa-batch4/verify-integration.py`. Loopback gallery: `http://127.0.0.1:4319/`; example anchors `#HIST-TECH01-2008A-Q024` for SECDED and `#HIST-TECH01-2019A-Q024` for NAND topology.

Tracked changes are limited to `scripts/academic_qa.py`, `tests/test_academic_qa_batch4.py`, the npm test command, README and this completion report. Only the existing feature branch is committed/pushed; the implementation commit is supplied in the final handoff. Work stops for owner review of the qualifications, pending/provisional mappings and the 27 remaining unresolved records. No owner approval or publication decision has been granted.
