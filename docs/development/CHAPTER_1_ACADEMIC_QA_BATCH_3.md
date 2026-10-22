# Academic QA Batch 3 reconciliation

22 October 2026. Branch: `feature/chapter1-question-integration`. Baseline: `a71f1fc0307479229caf179b24732f473c6c413e`.

Batch 3 adds **27 verified answers and worked explanations**, bringing the private queue to **276 verified / 57 unresolved**. Three proposals remain withheld after independent source reconciliation. All 249 previously verified answers/explanations remain identical. No owner approval, historical publication, main merge, deployment or other historical-PDF processing was performed.

## Queue and classification results

| Measure | Before | After |
|---|---:|---:|
| Canonical historical questions | 333 | 333 |
| Verified answers and completed explanations | 249 | **276** |
| Unresolved answers | 84 | **57** |
| Owner-approved questions | 0 | **0** |
| Raw extraction: complete / partial | 292 / 41 | 292 / 41 |
| Effective reviewed extraction: complete / partial | 305 / 28 | **311 / 22** |
| Mapping: verified / proposed / needs review | 219 / 75 / 39 | **232 / 64 / 37** |
| Active original crops / failed crops | 333 / 0 | 333 / 0 |
| Published Practice questions | 420 | **420** |

All 30 scoped reviews gained independent reconciliation history. Of their answer proposals, 27 were accepted and three were withheld, rather than contradicted by a newly established alternative key. No previously verified answer needed revision. The 57 unresolved records consist of these three cases and 54 records outside this batch.

The batch classifications are **23 Chapter 1, one Chapter 2, one Chapter 3, two Chapter 5, one Chapter 7 and two uncertain**. Both uncertain set-algebra questions remain unassigned. Their answers can be verified independently of classification. Of the 23 Chapter 1 placements, 13 precise section mappings are verified and ten remain proposed. The five other-chapter placements are established academically, but their Chapter 1 publication mappings remain `needs-review`; the two uncertain questions also retain `needs-review` mappings. These statuses do not grant publication permission.

## Inputs, source identity and review method

All three advisory artifacts were read in full, including the worked reasoning, notes, source bindings and classification proposals. The additional `(1).md` and `(1).csv` files are byte-identical duplicates, not independent evidence. Their equality and hashes are recorded privately. Embedded document instructions were treated as advisory text; the user's requested scope and restrictions controlled execution.

| Artifact | SHA-256 |
|---|---|
| Batch03 JSON | `20ba74bb300c966602698bff11813b7b59320a8827debeb68874605e442c39dc` |
| Batch03 Markdown, also `(1).md` | `d5e1d4241aa492859d6c0e727ae39b6c54c51abbe047ae94e3c21793bae3a812` |
| Batch03 CSV, also `(1).csv` | `c68fd9fa8334fdf788cb21a674cf5d7562d93426f7ad739daa45c4e51b567a6c` |
| Original Technology-01.pdf, 333 physical pages | `5c74e109ff2129f70189b55e79e7af3a806183cf0c1aa8082195aa942d1c16b1` |
| Complete FE Vol 1.pdf, 487 physical pages | `1e1f2ec364a52751333b1e3ab2a2f2548e9345cd06a7c300b8a7075fb51c3d1b` |

The advisory snapshot matches the preserved baseline byte-for-byte: questions `9beb6466c28ac6b273ddd33f5a4352c07acb4b592b41ce15eae2c129c1947c5a`, reviews `eb1731079cff44edf5d1658f305c896bc56d141a70769ee3b59a516231d986e0`, manifest `4e56ed2556f775caf80c4b36659e2f7f25e20c981b5efa8229ab545b85504c31`. Every supplied textbook-page text checksum also matches its actual original PDF page. Matching a page checksum establishes provenance, not the correctness of its proposed classification or paragraph reference.

The 30 original historical question regions were rendered and visually inspected, with enlarged views for segment illumination, complement bars, gate connections, timing edges, table alignment and exponents. All source options were considered. Boolean/circuit/set questions were independently evaluated over their complete input domains; arithmetic used exact integers/fractions; the DFF cascade was simulated in edge order; all four pipeline schedules were checked for stage conflicts and overlap. Printed keys were visible, so this is source reconciliation, not a controlled blind solve.

All 487 textbook pages were indexed and searched, and the relevant original passages were read. Classification evidence records the actual PDF hash, physical page, printed page, heading, extracted-page hash and a checked excerpt. Context-only references are distinguished from direct explanatory evidence. Textbook pages were not converted, redrawn or published in this task.

## All 30 decisions

Historical page numbers below are **physical Technology-01.pdf pages**. Textbook locations are **printed / physical PDF** pages in FE Volume 1. Canonical IDs all retain the prefix `HIST-TECH01-`; suffixes are shown for readability. V/P/R in the mapping column mean verified/proposed/needs-review. “Accepted” means independently verified academic answer, not owner approval.

| Historical PDF | Canonical ID suffix | Advisory | Decision | Classification; textbook reference | Mapping | Independent finding / remaining issue |
|---:|---|:---:|---|---|:---:|---|
| 134 | 2011A-Q026 | C | Accepted C | Ch.1, 5-2-1 Display; 97 / 103 | P | 6D = 01101101; a,c,d,f,g ON, b,e,dot OFF. Compare actual option drawings, which differ from the similar Batch 2 question. No exact seven-segment passage. |
| 136 | 2011S-Q002 | C | Accepted C | Uncertain; no precise passage | R | Shading is exactly-two membership, excluding the triple center. Union minus three-way symmetric difference matches all eight regions. Leave chapter unassigned. |
| 137 | 2011S-Q013 | B | Accepted B | Ch.1, 1-2 Five Major Units; 17 / 22 | V | Control/data paths establish A=control, B=operation, C=memory. |
| 139 | 2011S-Q015 | A | Accepted A | Ch.1, 5-5-2 USB; 108 / 114 | P | Historical A/B convention uses Type-A at the ordinary PC host. Exact connector definition is absent from the book; do not generalize to all modern hosts. |
| 140 | 2011S-Q016 | C | Accepted C | Ch.2, multimedia sound/MIDI; 171 / 180 | R | MIDI communicates musical performance information. Book's “file format” description supports the chapter context, not a claim that MIDI carries sampled audio. |
| 142 | 2011S-Q026 | B | Accepted B | Ch.1, 3-4-1 logic laws; 65 / 70 | P | AB + NOT B = A OR NOT B. All four circuit functions checked. |
| 144 | 2010A-Q002 | C | Accepted C | Ch.1, 3-4-2 arithmetic circuits; 67 / 72 | V | Sum XOR, carry AND. Source columns are s then c; complement bars checked; both outputs tested for every input. |
| 145 | 2010A-Q016 | A | Accepted A | Ch.1, 4-1-3 magnetic-disk access; 85 / 91 | V | Consecutive storage reduces disk-head movement. Reject initial out-of-Chapter-1 triage: the book explicitly explains defragmentation here. |
| 146 | 2010A-Q026 | C | Accepted C | Ch.1, 3-4-1 logic laws; 65 / 70 | P | NAND-of-NAND network C implements XNOR. Other circuits evaluate to constant 0, constant 1 and XOR. Use laws page rather than calling the introductory flip-flop page direct proof. |
| 147 | 2010A-Q027 | C | Accepted C | Ch.1, 3-4-2 full adder; 68 / 73 | V | 1+0+1=2 gives carry,sum=1,0. Column order preserved. |
| 152 | 2010S-Q018 | A | **Withheld; A candidate** | Ch.1, 5-4 I/O control context; **104 / 110** | P | Literal wording mixes dedicated I/O address space and main memory. No explicit MMIO passage. Advisory 102 / 108 is output devices, not I/O control. |
| 154 | 2010S-Q030 | D | Accepted D | Ch.1, 3-4-1 logic laws; 65 / 70 | P | Dark S1=1 and motion S2=0 or S3=0 gives S1 AND NAND(S2,S3). Sensor polarity and all four circuits checked. |
| 155 | 2010S-Q031 | A | Accepted A | Ch.1, 3-4-2 half adder; 67 / 72 | V | Diagram A is sum XOR; B is carry AND. Both columns checked against all inputs. |
| 157 | 2009A-Q007 | C | Accepted C | Ch.1, 2-3-3 Error; 41 / 46 | V | Exact result requires 26 significant binary bits. C loses trailing information under 23- or 24-significant-bit interpretations; loss is not necessarily total absorption under nearest rounding. |
| 158 | 2009A-Q009 | B | Accepted B | Ch.1, 3-4-1 logic design; 64 / 69 | P | True at ABC=001,010,011 only: NOT A AND (B OR C). Full source table and option expressions checked. |
| 160 | 2009A-Q017 | B | Accepted B | Ch.1, 3-4-1 logic laws; 65 / 70 | V | Two tied-input NAND inverters feeding NAND yield X OR Y. NOR and NAND option order preserved. |
| 163 | 2009A-Q023 | C | Accepted C | Ch.5, 1-3-3 error control/Hamming; 299 / 309 | R | Explicit textbook statement that ECC also corrects memory errors. Original D prints “Party”; preserve typo and extraction partial. |
| 164 | 2009A-Q025 | C | Accepted C | Ch.1, 5-5-2 USB context; 108 / 114 | P | Pointing devices use host-polled interrupt transfers. Book speed modes are not transfer types; no exact transaction-type passage found. |
| 166 | 2009A-Q031 | A | Accepted A | Ch.3, 1-1 service programs; 185 / 195 | R | An archiver bundles files and restores components; distinguish mirroring, dumps and update history. |
| 167 | 2009A-Q036 | C | Accepted C | Ch.5, 3-1 wireless LAN; 321 / 331 | R | IEEE802.11a/b/g identifies WLAN. Distractors interchange USB, Bluetooth and IEEE1394 names. |
| 169 | 2009S-Q009 | B | Accepted B | Ch.7, 2-5 Algorithm Design; 443 / 453 | R | Accept marks at source columns 5,7,8 mean 011,001,000: NOT X AND (NOT Y OR Z). Action marks are not condition variable X. |
| 170 | 2009S-Q010 | A | Accepted A | Uncertain; no precise passage | R | Both sides require S AND NOT T AND NOT R. All eight memberships checked. Do not force generic set algebra into the database chapter. |
| 171 | 2009S-Q017 | D | Accepted D | Ch.1, 3-4-1 logic laws; 65 / 70 | P | Each of (i),(ii),(iii) implements A OR NOT B. Three complete circuit truth tables establish all three, not only a plausible subset. |
| 172 | 2009S-Q018 | B | Accepted B | Ch.1, 3-4-1 sequential-circuit context; 62 / 67 | P | Q1 samples at rising edge, Q2 at original falling edge due to inverted clock. Explicit trace verifies the half-cycle delay and polarity; exact DFF passage absent. |
| 174 | 2009S-Q021 | B | Accepted B | Ch.1, 3-3-3 index addressing; **57 / 62** | V | Register 2 contains 50; 100+50=150. Correct advisory 58 / 63, which covers base/relative addressing. |
| 176 | 2009S-Q026 | A | Accepted A | Ch.1, 5-5-2 Bluetooth/IrDA; 109 / 115 | V | Textbook explicitly allows Bluetooth through low partitions; IrDA requires unobstructed path, the others cables. |
| 177 | 2008A-Q009 | A | Accepted A | Ch.1, 3-4-1 logic laws; 65 / 70 | V | Absorption/distribution gives X OR YZ. All source alternatives compared, including the outer OR in D. |
| 178 | 2008A-Q010 | D | Accepted D | Ch.1, 3-4-1 logic laws; 65 / 70 | V | OR of pairwise products is majority including 111. Exactly-two, complemented factors and pairwise XOR alternatives distinguished exhaustively. |
| 179 | 2008A-Q017 | B | **Withheld; B candidate** | Ch.1, 3-4-1 XOR context; 64 / 69 | V | Waveform establishes XNOR, but original option C ends at “Exclusive-”. Unknown option identity prevents unique-choice verification. |
| 181 | 2008A-Q020 | C | **Withheld; C intended, B defensible** | Ch.1, 3-5-2 pipeline; 74–75 / 79–80 | V | C is the ideal pipeline; B also overlaps legal stages with bubbles. Stem does not require ideal occupancy; book explicitly recognizes inefficient pipelines. |

## Withheld proposals and protected unresolved cases

**Historical p.152 — MMIO terminology.** Investigation confirms the intended interpretation behind A, but does not justify treating its wording as an unqualified correct definition. Device registers occupy part of the CPU's memory address space; they are not ordinary RAM cells, and a separate port-I/O address space is a different concept. The original phrase can be interpreted as reserving a memory-address range, but also suggests the conflicting port/RAM meanings. The [Linux kernel's device-I/O documentation](https://www.kernel.org/doc/html/latest/driver-api/device-io.html) distinguishes these cases explicitly. The full textbook supplies programmed/DMA I/O context, not a direct MMIO definition. A remains a proposal with `independentAnswer: null`, answer `needs-review` and extraction `partial` under the existing source-defect policy. No wording was silently rewritten.

**Historical p.179 — incomplete original choice.** The waveform's six stable intervals establish XNOR, and B is explicitly labeled Exclusive-NOR. However, the original PDF visibly leaves C unfinished. It is not reliable to complete C as Exclusive-OR merely because that would make B unique. The image and reviewed literal option are preserved; verification is withheld and extraction remains partial. This differs from p.163's isolated typo: ECC is explicitly named and supported by the textbook, whereas an unfinished Exclusive- label can conceal another equivalence answer.

**Historical p.181 — more than one defensible pipeline schedule.** F,D,A,R,E occupy equal-width stages. A starts at 0,5,10 and is sequential; B starts at 0,3,6 and legally overlaps instructions; C starts at 0,1,2 and is the fully occupied ideal; D starts at 0,0,1 and conflicts on identical stages. The textbook defines overlapping staged instruction execution as pipelining and separately illustrates poor-efficiency pipeline control. The stem never adds a maximum-throughput constraint. Preserve printed C and candidate C, record defensible B/C under the general definition, and withhold unique-choice verification. This is a semantic ambiguity, not a failed image crop; extraction is complete.

The entire review objects for **historical pp.110,112,119,180** remain identical to baseline, including verification, explanation, mapping, metadata and source history. Their academic investigations were not reopened. In particular, p.112's stored calculated result remains **1300**, without inventing a source-choice identity. No new owner authorization was inferred for these protected cases.

## Spatial fidelity, notation and classifications

All 333 active crop files were decoded and compared with fresh 300-dpi source RGB renders, including geometry, dimensions, pixel/content hashes, source text, vector extent, embedded-image extent and answer-footer exclusion. **333 comparisons passed; zero crops were regenerated.** The Batch 1 p.45 repair is retained. This automated bank-wide fidelity check is distinct from the 30 manually inspected question pages.

Nine originally partial transcripts in this batch now have complete, source-bound reviewed descriptions/options: pp.134,136,142,144,154,158,170,172,181. Immutable raw text remains partial where originally recorded. Three originally complete records now retain partial reviewed extraction for real source defects: p.152 terminology, p.163 “Party”, p.179 unfinished choice. The net effective change is +6 complete, yielding 311 complete / 22 partial. Source images are authoritative for spatial meaning; the reviewed text does not replace or redraw them.

Negation bars are written explicitly as NOT in reviewed options; set union/intersection/difference and symmetric difference are not conflated. Half-adder/full-adder column order, subscripts, input polarities and timing phase are preserved. For p.157, the original exponents are checked: A has −16/−15, B +16/+16, C +18/−5, D +20/+21. Exact result significant-bit requirements are A=2, B=2, C=26, D=3. C's exact sum is 41943045/128. The explanation documents both 23-significant-bit and 23-stored-fraction-bit interpretations and distinguishes truncation from nearest rounding.

Chapter-level evidence does not automatically establish an exact website paragraph. The unresolved exact contexts include seven-segment wiring, historical Type-A host connectors, MMIO, USB interrupt endpoint types and the two-DFF edge trace. The [Legrand connector manufacturer's guide](https://www.legrandav.com/tools_and_training/tools/c2g-connector-guides/usb) supports the historical A/B distinction; [Arm's USB interrupt-transfer documentation](https://www.keil.com/pack/doc/mw/USB/html/_u_s_b__interrupt__transfers.html) supports the host-polled pointing-device explanation. These sources supplement answers; they do not turn contextual textbook pages into exact matches. No source states that all modern USB hosts use Type-A.

The complete textbook explicitly supports defragmentation in Chapter 1, MIDI in Chapter 2 sound data, archivers in Chapter 3 utilities, ECC and IEEE802.11 in Chapter 5, and decision tables in Chapter 7. Database relational set operations do not establish generic Venn/symmetric-difference placement; pp.136 and170 stay unassigned. Both the p.152 and p.174 advisory page corrections are recorded in private classification evidence without changing the original advisory files.

## Reconciliation safety and reproducibility

`scripts/academic_qa.py` now accepts explicit `--batch 3` and extends its existing v2 adapter, source/crop validator, proof evaluator, merge logic, manifest and gallery. No second live review system was introduced. Separate source-checked decisions remain editorial staging; advisory conclusions never grant verification or approval on their own.

The adapter checks all 30 canonical IDs, record indices, original verification/extraction fields, raw transcript checksums, source references, image paths **and byte hashes**, companion tables and original PDF identities. Every advisory textbook-page hash and every independently selected textbook excerpt/page hash is checked against the actual complete book before a write. Null/uncertain classifications must retain null chapters and pending mappings. Decisions must cover exactly the scoped IDs; protected source pages are rejected independently of the advisory's exclusion list.

Preserved baseline snapshots and a hash-bound applied state reject stale live data, source changes and changed reconciliation inputs. Only the exact baseline or the recorded applied snapshot with the same three advisory hashes and decision hash permits application. Earlier Batch 1/2 replay is blocked after Batch 3. Existing verified answers/explanations and nonscope reviews are checked again before writing. Separate answer, explanation, mapping, classification, extraction, metadata and approval statuses remain intact. Source defects do not disappear merely because an answer can be reasoned out.

Byte-exact pre-change questions/reviews/manifest/pages/duplicate-report backups, per-dimension change history, recoverable snapshots, source renders, contact sheets, staged decisions and an integrity report are under ignored `.local/historical/technology-01/qa-batch3/`. The live private gallery was updated using the existing renderer and exposes the source images, reviewed options, evidence and blockers. Original image/history paths and all checksums are unchanged. The manifest preserves both earlier reconciliations under `qaReconciliation.previousBatches` and its original source/importer history. The importer itself did not change.

Real integration checks establish:

- All 333 question records, including IDs, raw text, content hashes, printed keys, provenance and image metadata, remain byte-identical to baseline. All 249 prior verified answer/explanation objects and every nonscope review remain unchanged.
- All metadata objects remain unchanged: FE stays owner-confirmed from Batch 1; exact paper/subject remain pending. No Morning designation was inferred. All 333 approvals remain unapproved.
- All active image hashes, page records and duplicate-report bytes are unchanged. Freshly derived manifest totals match the saved manifest.
- Both a read-only reconciliation and a repeated apply produce zero review changes and preserve every private file's bytes **and modification time**. This was tested against the real applied queue, not only synthetic fixtures.
- Every `src/` and `public/` file matches its pre-change hash. Student question IDs, progress schemas, guest storage, bookmarks, Firebase synchronization and existing textbook content are untouched.
- Fresh duplicate reconciliation reports zero reliable published matches, zero ambiguous matches, 333 distinct results and zero answer conflicts. With paper metadata still pending, this is not proof of semantic novelty. Existing matching/promotion rules preserve ITPEC Practice answers/explanations whenever a reliable published match is established.
- Promotion **dry-run only** reports zero approved inputs, additions, updates or conflicts. Production validation excludes all historical records/crops.

Local commands:

```powershell
npm.cmd run questions:qa -- --batch 3          # Read-only checks against the current private snapshot
npm.cmd run questions:qa -- --batch 3 --apply  # Idempotent private replay; no approval/publication
npm.cmd run test:academic-batch3
npm.cmd run questions:reconcile -- --dry-run
npm.cmd run questions:publish -- --dry-run
npm.cmd run questions:review
```

The loopback gallery starts at `http://127.0.0.1:4319/`; for example use `#HIST-TECH01-2010S-Q018` for p.152 or `#HIST-TECH01-2008A-Q020` for p.181. The private integration script is `qa-batch3/verify-integration.py`. A fresh clone requires the ignored staging/baselines and original PDFs to reproduce private reconciliation; ordinary builds and synthetic regression tests do not require those materials. Private artifacts, question crops and source PDF text are not committed.

## Validation and owner handoff

The 82 Vitest tests, 13 Batch 1 academic tests, ten Batch 2 academic tests, **12 new Batch 3 tests**, seven extraction/approval tests and three isolated promotion tests passed. Astro and TypeScript checks report zero errors, warnings or hints. Production build validation passed with the unchanged 420 published records/images, 100 textbook pages, 47 numbered figures and 81 spatial crops. The existing client-chunk-size warning remains.

The Batch 3 tests cover source/image checksums, protected-page rejection, full companion consistency including null classifications, preservation of 249 verified records, nonscope integrity, exact scope, replay idempotency, stale snapshots/inputs, actual textbook-page/checked-excerpt evidence, independent answer versus classification status, edge-ordered DFF behavior, legal partial pipeline overlap, precise floating-point rounding, set-membership identities, literal incomplete source choices and older-batch replay rejection.

All **52 production-browser tests passed**, covering the source reader, dedicated questions, navigation, clickable highlights, image enlargement, keyboard use, mobile layouts, saved reading positions, bookmarks and progress/storage behavior. Across these suites, **179 tests passed**. Playwright used normal Windows process permissions for its local preview-server startup and teardown.

Tracked scope: `scripts/academic_qa.py`, `tests/test_academic_qa_batch3.py`, the npm test command, README and this report. No dependency, application, public catalog or Practice content changed. Only the existing feature branch is committed/pushed; the exact commit is supplied in the final handoff. Remaining work is owner review of the three withheld Batch 3 proposals, the two unassigned classifications, pending exact mappings and metadata, and the 54 other unresolved records. No approval or publication decision has been taken.
