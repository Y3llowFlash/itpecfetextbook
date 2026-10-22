# Academic QA Batch 5 completion report

22 October 2026. Branch: `feature/chapter1-question-integration`. Baseline: `080ff731f9bd80085dd9ca88f4d939cca8bd1986`.

Independently accepted **all 20 Batch 5 answers**, with **zero rejected and zero newly withheld**. The private queue now has **326 verified answers / 7 unresolved** and 326 worked explanations. The remaining unresolved records are exactly the seven protected disputes; their review objects are unchanged. All 306 previously verified answers, explanations, evidence and provenance remain identical. This completes the requested final regular verification batch, not publication approval.

No owner approval, historical publication, public question-catalog change, main merge, deployment, other historical-PDF processing or original Practice repository modification was performed. Work stops for owner review.

## Final queue, mapping and extraction totals

| Measure | Before | After |
|---|---:|---:|
| Canonical historical records | 333 | 333 |
| Verified answers / completed explanations | 306 | **326** |
| Unresolved answers | 27 | **7** |
| Owner-approved records | 0 | **0** |
| Raw extraction complete / partial | 292 / 41 | 292 / 41 |
| Effective reviewed extraction complete / partial | 318 / 15 | **321 / 12** |
| Mapping verified / proposed / needs review | 249 / 48 / 36 | **257 / 40 / 36** |
| Original active images / crop failures | 333 / 0 | 333 / 0 |
| Published Practice questions / images | 420 / 420 | **420 / 420** |

Batch classifications: **12 Chapter 1, two Chapter 2, four Chapter 3 and two uncertain**. The mixed cache/virtual-memory question on p.282 retains a **proposed** Chapter 3 classification, with Chapter 1 context separately recorded. The two uncertain records retain null chapter/volume and pending mapping. All six other-chapter records retain `needs-review` Chapter 1 publication mappings. Among the 12 Chapter 1 records, eight section mappings are verified and four remain proposed. No new public highlight or concept was created.

Explicit classification annotations across the entire private catalog currently record 113 Chapter 1, six Chapter 2, 12 Chapter 3, three Chapter 5, one Chapter 7, three outside-Volume-1 and eight uncertain records. Another 187 retain earlier reviews without a separate `classification` annotation. These are annotation counts, not a new classification audit of earlier records or permission to publish. Earlier data was preserved.

## Input and baseline verification

Read all three artifacts completely, including every answer, worked rationale, source note, classification proposal and methodological limitation. Embedded instructions were treated as advisory document content; the user's scope and restrictions controlled this task. Matching the printed key was a consistency check, not the independent verification method.

| Input | SHA-256 |
|---|---|
| Batch 05 JSON | `428782e873ecc01f6f96243b9ff7c5d5d045396bc2cf141d20c681d03a185bfb` |
| Batch 05 Markdown | `fb591c397cc8b1ef6f0cd149eaf2eec0b3fe4fafa2a264ab0f710ba3fa616b63` |
| Batch 05 CSV | `0e22819a0917b461643061eaf20429e4ab1ca7ea67ef8a0d5e954340b8e47ec1` |
| Baseline questions.json | `9beb6466c28ac6b273ddd33f5a4352c07acb4b592b41ce15eae2c129c1947c5a` |
| Baseline reviews.json | `7e9ca4930d1e63a0f23afa46b78063d682b8413bed3427221b8a95dc116cd66a` |
| Baseline manifest.json | `a8b9db06e3b8faa98fae72afd9b4e8e2de781e1c3fd4b533ffbceef43d06dd03` |
| Original Technology-01.pdf, 333 physical pages | `5c74e109ff2129f70189b55e79e7af3a806183cf0c1aa8082195aa942d1c16b1` |
| Complete FE Vol 1.pdf, 487 physical pages | `1e1f2ec364a52751333b1e3ab2a2f2548e9345cd06a7c300b8a7075fb51c3d1b` |

All baseline/source hashes match actual bytes. All 20 canonical IDs, content hashes, original statuses, image paths and image-byte hashes match the current records. Supplied textbook-page hashes and normalized excerpts match the actual original book pages; excerpt presence alone was not treated as proof that it teaches the proposed concept. Independently selected evidence points to the relevant text, rather than merely copying a page's opening excerpt.

Batch 5's zero-based record indices and explicit per-entry/scope conventions are validated. Historical source pages remain one-based. Exactly 20 unique IDs are required independently of the advisory's declared count; changing that count cannot expand or shrink the authorized batch. Both companions must contain all 20 matching rows, including CSV reasoning, target chapters, keys, mapping statuses and flags.

## Complete 20-question reconciliation table

Historical pages below are physical `Technology-01.pdf` pages. Textbook locations are **printed / physical PDF** pages. IDs retain prefix `HIST-TECH01-`; suffixes identify the unchanged records. Mapping V/P/R means verified/proposed/needs-review. Every answer below was independently accepted; none was owner-approved.

| Historical PDF | Canonical suffix | Accepted | Classification; textbook evidence | Mapping | Independent result / qualification |
|---:|---|:---:|---|:---:|---|
| 249 | 2018A-Q024 | C | Ch.1, 5-2-1 Display context; 97 / 103 | P | Active-low 0x92=10010010 lights a,c,d,f,g only; b,e,dot OFF. All four original drawings compared. Descriptions are editorial visual transcriptions. |
| 250 | 2018A-Q025 | A | Ch.2, 4-2-2 Code Design; 161 / 170 | R | 8000(1.2)^3=13824; 26²=676 <13824 ≤26³=17576. Minimum three letters. Future-growth code capacity is explicit book context. |
| 259 | 2016S-Q001 | D | Ch.1, 2-2 radix; 24–25 / 29–30 | V | 0.B1 hex =177/256 =2^-1+2^-3+2^-4+2^-8. Negative exponent positions checked in every source option. |
| 267 | 2014A-Q010 | C | Ch.3, 2-2-3 virtual address translation; 206 / 216; Ch.1 weighted-time context 71 / 76 | R | (199/200)·1+(1/200)·40 =1.195 cycles. Times are complete hit/miss translation latencies. No exact TLB passage found. |
| 274 | 2013S-Q014 | B | Ch.1, 3-5-1 weighted access/multilevel cache; 71–72 / 76–77 | V | Service probabilities .95,.025,.025 yield 3.7 cycles under complete serving-level latencies. Incremental-cost interpretation gives 4.0 and is explicitly distinguished. |
| 275 | 2013S-Q015 | B | Ch.3, 2-2-4 I/O-management context; 209 / 219; seek context 83 / 89 | R | Increasing requests 110,120,140, then 90,80,70,60: total 120 cylinders. Reverse at last pending request; preserve distinct 2013 occurrence. |
| 276 | 2013S-Q029 | C | Ch.2, 5-1-2 PCM; 170–171 / 179–180 | R | Mono 44100·16·3600/8=317520000 bytes. Closest option 320Mbytes under decimal MB or MiB; no stereo/compression assumption. |
| 279 | 2012S-Q004 | C | Uncertain; no exact constrained-counting passage | R | Recurrence f(n)=f(n−1)+f(n−2), f(0)=1,f(1)=2 gives 21. Independent enumeration of all 64 six-bit strings confirms 21 without adjacent ones. |
| 280 | 2011A-Q001 | C | Ch.1, 2-2 radix; 24 / 29 | V | 753 base 8=491; A6 base 16=166; difference 325. Other actual-radix choices represent 333,321,309. |
| 281 | 2011A-Q004 | C | Uncertain; no exact flow-rate passage | R | Net rate 1/20+1/30−1/40=7/120 tank/min; time 120/7≈17.142857min. Nearest 17.1; drain remains negative. |
| 282 | 2011A-Q012 | C | **Proposed Ch.3**, 2-2-3 virtual storage; 206 / 216, with Ch.1 cache context 71–72 / 76–77 | R | Probabilities .95,.0495,.0005; ns/ms converted toµs give 5.002395µs, closest 5.0. Cumulative alternative 5.0025µs selects the same choice. |
| 294 | 2009A-Q001 | B | Ch.1, 2-2 radix; 24 / 29 | V | 3A.5C hex=3735/64=58.359375. Source fraction numerators/denominators checked; all four compared exactly. |
| 296 | 2009A-Q008 | D | Ch.1, 3-4-1 XOR; 61,64 / 66,69 | V | Original 1101 XOR0001 XOR0101 XOR1101=0100. New middle key1110 alone produces1111; all candidate key outputs checked. |
| 303 | 2009S-Q003 | B | Ch.1, 2-2 binary-weight context; 24 / 29 | P | For all n≥1, alternating 2n-bit x obeys x+x/2=2^(2n)−1. Algebraic proof plus n=1..16 checks; exact fraction bar/exponents preserved. |
| 313 | 2008A-Q023 | B | Ch.1, 3-1 address-bus context; 48 / 53, main-memory selection 51 / 56 | P | Source highest/lowest 3FFFFFF/3000000 contains 35E3C03 and spans 16MiB inclusive. Other ranges have wrong capacity. Proposed concept is memory-address-map, not CPU registers. |
| 315 | 2008S-Q001 | A | Ch.1, 2-2 radix; 24–25 / 29–30 | V | 2A.4C hex=2707/64. Set-bit powers 5,3,1,−2,−5,−6 match only A. |
| 320 | 2007A-Q003 | B | Ch.1, 2-2 binary-weight context; 24 / 29 | P | Same proven alternating-bit identity as p.303, with its own source, exam year/season and canonical ID. No deduplication across occurrences. |
| 325 | 2007A-Q028 | D | Ch.1, 4-1-2 blocking/IBG; 81–82 / 87–88 | V | 6000 data bytes+400 gap; four whole blocks/track, 500 blocks total,125 tracks. A block cannot cross tracks. |
| 326 | 2007A-Q029 | B | Ch.3, 2-2-4 I/O-management context; 209 / 219; seek context 83 / 89 | R | Independently calculate the 120-cylinder path. Same numerical requests as p.275, separate 2007 examination occurrence. |
| 327 | 2007S-Q001 | D | Ch.1, 2-2 radix; 24 / 29 | V | 0.248 hex=2/16+4/256+8/4096=73/512. Source alternatives 31/32,31/125,31/512,73/512 compared exactly. |

## Mathematical and source-image interpretation

All 20 original source question pages were rendered and manually inspected, with enlarged individual views for seven-segment choices, radix subscripts, negative superscripts, fractions, address-map columns and the XOR cascade. Printed keys were visible, so this is not claimed as a controlled blind solve. Keys were confirmed only after independent calculations and comparison of the actual source alternatives.

**p.249:** The original explicitly states zero turns an LED on. P0..P6 map to a..g and P7 to the decimal dot. The common-anode polarity must not be copied from superficially similar active-high questions. Reviewed descriptions label themselves as editorial transcriptions of image-only choices; raw image-only option strings remain untouched.

**pp.259,280,294,303,315,320,327:** Exact rational arithmetic avoids floating-point rounding. Source minus signs belong in negative exponents where shown; radix subscripts identify each choice's base; fraction bars separate full numerators and denominators. For pp.303/320, x=2(4^n−1)/3, so 3x/2=4^n−1 for every positive n. Finite numerical cases are regressions, not the proof of an infinite identity. All four original formula alternatives are evaluated. No generated/redrawn mathematics replaces the original crop.

**p.274:** The source says data in L1/L2/main memory can be accessed using 1/10/100 cycles. The independent verification uses those as complete latencies for the serving level, consistent with the actual textbook example's mutually exclusive hit/miss weighted average. L2's miss probability is conditional on reaching L2. This gives .95·1+.025·10+.025·100=3.7. If those numbers instead meant incremental serial costs, 1+.05·10+.025·100=4.0; the saved explanation explicitly records that alternative. Neither the matching key nor the absence of 4.0 from the choices alone is evidence for the latency convention.

**p.282:** Convert 2ns to .002µs, 10ns to .01µs and 10ms to 10000µs. The disk probability is .05·.01=.0005, not .05. Complete-latency averaging gives 5.002395µs; adding sequential lookup overhead gives 5.0025µs, still closest to 5.0. The answer is robust to that small timing-model difference. Its Chapter 3 placement remains tentative because the problem spans virtual memory and Chapter 1 cache timing.

**pp.275/326:** The conditions specify increasing requests first, reversal only once no requests remain in that direction, and no new arrivals. The explicit path 100→110→120→140→90→80→70→60 moves 120 cylinders. No physical end-of-disk travel is introduced. The textbook provides seeking and OS I/O-management context, not an exact named disk-scheduling algorithm passage. The distinct 2013S/2007A identities, original question numbers, hashes, images and source references are preserved. The analogous 2009S/2007A pair on pp.303/320 is also retained separately.

**p.296:** Source box order A,B,C, every internal key and both old/new outputs were checked against the actual image. XOR cancellation isolates only the changed B key. The original 0101 key is retained as original data and is tested to produce 0100; the proposed replacement 1110 is separately tested to produce 1111. No original source key is overwritten.

**p.313:** Source table order is highest then lowest. Range B is the only listed range with both the correct inclusive capacity and the stated address inside it. Aligned decoding is a useful interpretation, but one interior address plus capacity does not uniquely determine an arbitrary unaligned window in general. The explanation makes no such stronger claim. The proposed concept tag is memory-address-map; no existing CPU-register highlight is reused.

**p.325:** Floor whole blocks per track before rounding track count upward. Dividing a global byte total would allow a block to straddle tracks against the source condition. Even omitting a trailing gap after the last block cannot fit a fifth 6000-byte block with four 400-byte intervening gaps into 30000 bytes.

## Classification corrections and limits

The complete 487-page book was indexed and searched; relevant original passages were read. Code Design on printed 161 explicitly discusses future growth exhausting a code space, supporting Chapter 2 for p.250. PCM and its worked data-amount calculation span printed 170–171, supporting Chapter 2 for p.276. Virtual-memory address translation and backing storage support Chapter 3 context for pp.267/282; OS I/O management supports Chapter 3 context for the two disk schedulers. Literal TLB/disk-scheduling teaching passages were not found, and no exact anchor was fabricated.

The hexadecimal/binary grouping explanation on printed 25 supplements positional weights on printed 24. Multilevel cache on printed 72 supplements the weighted-average example on printed 71. Main-memory address selection on printed 51 supplements address-bus context on printed 48. These are evidence refinements; exact proposed mappings remain pending where the specific formula or diagram is absent.

General no-adjacent-ones combinatorics and tank rates remain unassigned, even though their answers are verified. Binary positional-weight identities are retained only as proposed mappings under radix context. The p.282 chapter-level status is proposed rather than presenting a mixed-topic placement as established. No Chapter 2/3/general-mathematics question is inserted into Chapter 1 public concepts.

## Preservation, image fidelity and reproducibility

All **333 active original crop files** passed decoded RGB comparison with fresh 300-dpi original-PDF renders, including geometry, dimensions, pixel/content hashes, source text, vector/embedded-image extent and answer-footer exclusion. **Zero crops were regenerated, redrawn or replaced.** The earlier p.45 repair/history is retained. Three raw-partial records in this batch, pp.249,259,280, now have complete source-bound reviewed descriptions/options. Raw records remain byte-identical, so the effective extraction improvement is separate from immutable raw status. Twelve partial reviewed extractions remain across the full catalog despite 326 verified answers; verification is not equivalent to extraction/publication readiness.

Real integration checks confirmed:

- The complete questions.json bytes are unchanged: 333 IDs, original keys, content hashes, raw text, region/image metadata, source references and FE provenance preserved.
- All 306 earlier verified review objects, including explanations, evidence, academic history and metadata, are unchanged. Every nonscope review is identical to baseline, including all seven protected records.
- The remaining unresolved pages are precisely 110,112,119,152,179,180,181. Their previous review states were not academically reinvestigated or altered. p.112's stored numeric result remains 1300 without a fabricated choice identity.
- All metadata and approval objects, pages.json and duplicate-report bytes are unchanged. FE remains owner-confirmed; exact paper/subject remains pending. All 333 approvals are unapproved.
- Source/importer history and prior batches 1–4 remain recorded. Editorial staging revisions/history are retained privately; the applied snapshot binds the final decision fingerprint.
- Read-only execution and repeat apply produce zero review changes and preserve every private file's bytes **and modification time**. Manifest totals match a fresh derivation. Distinct-exam pairs remain distinct.
- Every src/public file matches its saved hash. Existing question IDs, guest/account progress schemas, bookmarks, reading checkpoints, Firebase synchronization, explanations and textbook content are untouched.
- Fresh duplicate reconciliation gives zero reliable/ambiguous matches, 333 distinct results and zero conflicts. Current published dated occurrences cover 2024–2026, so these older Batch 5 occurrences do not match by exam identity. No metadata is guessed; published Practice answers remain authoritative whenever reliable matches exist.
- Publication **dry-run only** reports zero approved inputs, additions, updates or conflicts. No historical record or crop enters public output.

`academic_qa.py --batch 5` reuses the existing architecture. It enforces 20 unique advisory IDs and exact decision scope, validates zero-based record conventions, both PDFs, all source/content/image bindings, baseline snapshots and all companion fields, and checks advisory/independent textbook excerpts against actual pages. Earlier batches retain their 30-record scope and original indexing conventions. Protected-page checks are independent of advisory exclusions. Separate answer, explanation, classification, mapping, extraction, metadata and approval statuses remain intact.

Added a small exact-arithmetic proof evaluator for rational/radix values, exponent sums, integer XOR, rounding boundaries and source-option comparison. It uses fixed operations and Fraction arithmetic; it executes no advisory code. All four choices are compared with exact equality or an explicit nearest-choice rule. The finite-case evaluator supplements, rather than replaces, the algebraic argument for alternating-bit identities. Existing Boolean, table, latch and source-pixel validators remain in use.

Only the preserved advisory baseline or its exact hash-bound applied state permits replay with unchanged inputs. Changed advisory/decision files, altered source data/images or stale live snapshots fail before writes. Batches 1–4 cannot replay over Batch 5. Baselines, original renders/contact sheets, checked decisions, changes/history, applied-state fingerprints, editorial revision archive and integrity report remain under ignored `.local/historical/technology-01/qa-batch5/`. The existing loopback gallery reflects the reviewed options, source images and blockers. These private materials are not committed; a fresh clone needs them and the original PDFs to reproduce private reconciliation. Public builds/tests do not require private data.

## Validation, changed files and handoff

Passed: 82 Vitest tests; 13 Batch 1, 10 Batch 2, 12 Batch 3, 14 Batch 4 and **15 new Batch 5** academic regressions; seven extraction/approval tests; three isolated promotion tests. Astro/TypeScript checks report zero errors, warnings or hints. Production build/data validation passes with the unchanged 420 published records/images, 100 source-reader pages, 47 numbered figures and 81 spatial crops. Its existing client-chunk-size warning remains.

The new tests cover exact 20-record scope, source/checksum/index conventions, companion reasoning consistency, preservation of 306 complete reviews and all seven disputes, stale snapshots/inputs, idempotency, source-pixel fidelity, rational fractions/exponents/radices, active-low LEDs, XOR original/new keys, cache timing models and units, disk path and distinct occurrence IDs, inclusive address ranges, block/track boundaries, general-math classification independence and approval gates. Existing unit/browser suites cover progress and practice compatibility. Promotion tests use isolated synthetic fixtures.

All **52 production-browser tests passed**, bringing the total to **208 passing tests**. The local preview ran with normal Windows process permissions. Browser coverage includes source-reader navigation, dedicated questions, highlights, image enlargement, keyboard use, mobile bounds, reading-position restoration, bookmarks and progress/storage behavior. No live account data was written.

Tracked files: `scripts/academic_qa.py`, `tests/test_academic_qa_batch5.py`, `package.json`, `README.md`, and this report. No dependency, application or public-catalog changes. Only the existing feature branch is committed/pushed. The final commit hash is supplied in the final handoff and saved in the private `completion-handoff.json`; the private completion-report copy includes that hash.

```powershell
npm.cmd run questions:qa -- --batch 5          # Read-only validation
npm.cmd run questions:qa -- --batch 5 --apply  # Idempotent private replay; no approval/publication
npm.cmd run test:academic-batch5
npm.cmd run questions:reconcile -- --dry-run
npm.cmd run questions:publish -- --dry-run
npm.cmd run questions:review
```

Private real-data check: `.local/historical/technology-01/qa-batch5/verify-integration.py`. Loopback gallery: `http://127.0.0.1:4319/`, with anchors such as `#HIST-TECH01-2013S-Q014` and `#HIST-TECH01-2009A-Q008`.

**Remaining publication blockers:** owner adjudication of the seven protected disputes; precise pending/provisional mappings and classifications; source-defect/extraction issues; reliable paper/subject metadata; required source/passage bindings for any new public highlight; and separate fingerprint-bound owner approval. 326 academic verifications do not satisfy these separate gates. No approval or publication is granted here, and no further batch or dispute investigation is started.
