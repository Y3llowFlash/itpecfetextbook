# Phase 8: final private inventory and other-chapter dependencies

Baseline: `5800c9e0ca0069649aa6404f672a827eb8c192db` (Release 7).
Branch: `feature/technology01-phase08-other-chapters`.

This milestone audits the remaining 66 Technology-01 records. It grants no
approval and changes no application content. The 687 published question/image
pairs, 267 historical approvals and all 333 native academic histories are frozen.
The seven qualified owner-adjudicated cases remain protected within the 25
Hardware deferrals.

## Result and dependency

| Original private category | Count | Phase 8 result |
|---|---:|---|
| Hardware | 25 | Separate follow-up queue; no expansion of candidate scope |
| Other Volume 1 chapters | 29 | Source-reviewed dossiers; all deferred |
| Uncertain | 9 | Remain unassigned pending direct teaching evidence |
| Provisionally outside Volume 1 | 3 | Remain private; no claims about unreviewed books |

The 29 other-chapter records distribute across the actual textbook as follows:

| Chapter | Actual title | Records | Direct topic teaching | Context only |
|---|---|---:|---:|---:|
| 2 | Information Processing System | 11 | 11 | 0 |
| 3 | Software | 12 | 8 | 4 |
| 5 | Network | 5 | 2 | 3 |
| 7 | Data Structure and Algorithm | 1 | 1 | 0 |

Only Hardware has implemented source-reader routes, source HTML and precise
anchors. The native publication gate and publisher also explicitly require
Hardware. Implementing these other chapters is substantive source-conversion
work. The task explicitly requires deferral in this situation. No substitute
Hardware links, invented anchors or relaxed publication gates are introduced.

**Final eligible candidates: zero.** The final package explicitly records
`publicationReady: false` and
`preparationStatus: blocked-no-implemented-other-chapter-routes`. Its empty-set
fingerprint is an integrity receipt, not authorization for a later changed set.
There are no individual future approval fingerprints. Candidate-to-preview
equality applies to zero additions and does not certify the 29 deferred dossiers
as release-ready questions.

All 29 dossiers have original-image-bound accessible reviews. Fifteen private
editorial overlays (ten other-chapter, five Hardware) preserve native images,
raw transcripts and academic objects. They are not applied to the native review
database. Two Hardware explanation concerns remain separate academic blockers;
the existing answers and explanations are preserved.

The complete 487-page textbook text was indexed and searched. Relevant question
and textbook diagrams were visually reviewed; this is not a claim of manually
viewing all 487 pages. Source passages retain physical/printed page identities
and source/text hashes. Contextual support is explicitly distinguished from
teaching the tested method. Highlight plans remain deferred without source HTML
bindings; no public highlight definitions change.

## Existing architecture

`scripts/phase08.py` validates a frozen native/public baseline and source-bound
audit artifacts, then adapts the existing preview and approval-candidate system.
`scripts/phase08_report.py` renders private reports and the read-only gallery.
The existing publisher supports an exact-package Phase 8 dry run and rejects
every non-dry Phase 8 invocation before reading private input. This is not a
second approval system or a transition that enables other-chapter publication.

All private outputs live under the ignored directory
`.local/historical-batches/technology01-phase08/`. Original source materials,
question dossiers, approval payloads, galleries and screenshots must remain
outside public assets and Git.

```powershell
python scripts/approval_candidates.py check --batch 8
node node_modules/tsx/dist/cli.mjs scripts/publish-historical-questions.ts --batch 8 --dry-run
node scripts/private-student-preview-server.mjs --phase08
node scripts/question-review-server.mjs --approval-candidates --phase08
```

Student reference preview: `http://127.0.0.1:4352/`.
Read-only owner audit: `http://127.0.0.1:4354/`.

The reference preview contains 290 unchanged published Hardware questions and
zero new private questions. It explicitly distinguishes these from the 687
sitewide public records. The owner gallery contains the complete 66-record
audit, grouped by actual chapter. It is not a claim of 66 approval candidates.
Both servers bind loopback, verify hashes and allowed roots, reject mutations
and foreign origins, and use `no-store`/`noindex`. Preview progress has a separate
local-storage namespace and no production Firebase connection.

Preparation rejects stale source, review, implementation, payload and preview
bindings. Repeating preparation must preserve artifact bytes. A later chapter
implementation requires a fresh reviewed preparation baseline and separate
owner authorization; the Phase 8 empty package cannot approve it.

## Verification and next work

Regression evidence is private under `validation/`, with the detailed completion
report at `COMPLETION-REPORT.md`. Coverage includes exact scope and protected
records, source-image fidelity, source passages, classification independence,
accessible overlays, stale bindings, idempotency, publication rejection,
preview isolation, browser keyboard/mobile behavior and existing account/guest
progress. Production build outputs are compared byte for byte with the baseline.

Validation passed: 373 Python tests (including 21 Phase 8 tests), 119 application
unit tests, 12 emulator rule tests and 219 browser checks. Four owner-gallery
cases for other batches were intentionally skipped. The 21 Phase 8 Python tests
and 12 Phase 8 browser checks were repeated after a gallery navigation wrapping
fix. Root Astro checked 143 files and the private preview checked 41 files, with
no diagnostics; TypeScript passed. The production build has 56 pages, the private
reference build 57. All 1,067 production assets remain byte-identical. Repeated
preparation preserves all 874 preview/final-package files. Publisher dry run:
267 prior approved inputs, zero additions, updates or conflicts.

The most efficient next milestone is source-faithful Chapter 2 conversion and
verified navigation/anchors for its eleven directly supported dossiers, followed
by the smallest chapter-aware extensions to the existing publication framework.
Seven contextual-only records still need stronger teaching evidence. Hardware,
uncertain and outside queues remain separate.

Release 7's 55 unexplained provider/local HTML mismatches and transport-blocked
live HTML/UI verification remain unresolved. Phase 8 performs no new production
probes, deployment, rollback or cloud configuration changes.

Feature commits use the `[CF-Pages-Skip]` prefix because the existing Cloudflare
project automatically builds all preview branches. Cloudflare documents this
prefix as skipping its deployment; other CI is not suppressed. See the official
[Git integration documentation](https://developers.cloudflare.com/pages/configuration/git-integration/github-integration/#skipping-a-build-via-a-commit-message).
No Cloudflare settings are changed.
