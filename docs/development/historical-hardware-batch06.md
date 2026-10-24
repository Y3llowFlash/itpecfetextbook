# Hardware Batch 6: private preparation and final owner candidates

This milestone prepares forty independently verified Technology-01 Hardware questions across thirteen existing concepts, with no new highlight proposals. Every candidate remains private and unapproved. The public catalog remains at 616 question/image pairs and 196 historical approvals.

The branch is `feature/technology01-hardware-batch06`, created from fetched main `cd5fa89136dbd04d60ad0ccb7044eac923e08cd0`. Only reusable adapters, regressions and this sanitized document belong in Git. Native reviews, original crops, source passages, exact IDs/fingerprints, galleries, screenshots and reports remain under ignored `.local` directories.

## Existing workflow and safety gates

`hardware_batch06.py` reuses the Batch 2 editorial reconciliation gates and Batch 3 disposable preview adapter. `approval_batch06.py` reuses the established candidate builder, visible-content comparator, publication/context fingerprints, source-review validation and read-only owner gallery. The publisher accepts `--batch 6 --dry-run` through the exact package gate; Batch 6 non-dry-run publication fails before source access. No approval command or Release 6 transition is implemented.

The exact source-reviewed ledger is required. It binds immutable source/image/raw-transcript hashes, the original review snapshot and literal textbook passages with verified printed/physical page labels. Only the selected classification, mapping and accessible extraction reviews can change. All academic verification objects, worked explanations, owner metadata, previous approvals, protected adjudications and other 293 review objects are preserved. Existing Practice occurrence/image collisions are rejected without overriding authoritative Practice answers.

Repeated preparation validates existing output and rejects stale source, snapshot, implementation, candidate, preview or gallery bindings. It never silently refreshes fingerprints. The final manifest includes per-dimension, publication, context and candidate-set fingerprints, complete preview equality and grading eligibility. These are future approval candidates, not owner approvals.

The final source ledger distinguishes immutable source wording from editorial linearization. A missing-parenthesis defect is retained in original/literal evidence while balanced accessible notation is explicitly identified as editorial. Circuit descriptions trace all comparable branches without stating derived functions or winning choices before submission. No original image or academic answer is rewritten.

## Selection and source limitations

Coverage analysis spans all published Hardware concepts and authoritative numbered textbook subsections. The selection includes cache write policies and memory hierarchy with low prior historical counts, as well as varied Boolean/circuit, memory, addressing, interrupt, radix and shift applications. Broad cache recommendations are narrowed where a more precise existing concept applies.

Bitwise questions use actual logical-operation teaching plus radix weights; their supplied operators are applied per bit. The unrelated existing shift/bit-masks anchor is not used. A selector-circuit question is placed as an application of the drawn basic gates; the book is not claimed to provide a named multiplexer-design lesson. These distinctions and exact source fragments are exposed in the private owner evidence.

Specialized deferrals were investigated against the complete PDF and its rendered figures. Actual daisy-chain teaching is in an intact spatial crop. UART teaching exists in an unnumbered insert. A JK circuit inset exists in the memory-device material, but its clock/table scope cannot be inferred from generic bistable prose. Figure-bound highlights, unnumbered insert placements and required secondary-chapter support are documented as separate capability proposals. This milestone introduces no broad mapping architecture change and does not fabricate direct passages. Unsupported register-indirect, biased-order, timing, endurance and decoder placements remain deferred. The seven qualified owner-adjudicated cases remain excluded and unchanged.

## Private review

From the repository root, launch in separate terminals:

```powershell
node scripts/private-student-preview-server.mjs --batch06
node scripts/question-review-server.mjs --approval-candidates --batch6
```

Student preview: `http://127.0.0.1:4344/`.
Read-only final owner gallery: `http://127.0.0.1:4346/`.

The preview separates 616 sitewide published questions from 219 published Hardware collection references and forty new private additions, for 259 preview questions. Collection/source/year/unanswered counts are independent. All private attempts, bookmarks and reading returns use `itpecTextbook:privateHardwareBatch06:`. No Firebase/authentication runtime or real-progress migration is included. Reset controls affect only this disposable namespace.

Both servers bind loopback, restrict Host/Origin, serve GET/HEAD only and verify explicit asset hashes. Raw PDFs, native/private JSON and unselected images are denied. The final gallery groups all forty candidates by thirteen concepts, provides direct textbook-preview links and has no scripts, forms, approval actions or progress writers.

## Reproducible checks and handoff

```powershell
python scripts/hardware_batch06.py check
python scripts/approval_candidates.py check --batch 6
node node_modules/tsx/dist/cli.mjs scripts/publish-historical-questions.ts --batch 6 --dry-run
```

The dry run must contain 196 existing approved inputs, zero new approvals, zero additions, zero updates and zero conflicts. Public question/image files, source reader, progress/auth code, all 196 approval objects and all prior private release evidence are hash guarded. The local production build must equal the Release 5 local baseline byte-for-byte.

Private workspace: `.local/historical-batches/technology01-hardware-batch06/`.

- `completion-report.md`, `inventory.csv`: complete per-question handoff, exact source identities and source placements.
- `coverage-analysis.json`, `excluded-deferred.json`, `highlight-inventory.json`: coverage and explicit exclusions/deferrals.
- `review-diff.json`, `editorial-repairs.md`: exact before/after selected editorial changes.
- `final-approval/manifest.json`, `source-review.json`, `equality-report.json`, `eligibility-report.json`: exact reviewed future approval package.
- `preservation-report.json`, `validation/`, `validation-results.md`, `completion-receipt.json`: preservation, test/build/dry-run evidence and final pushed feature commit.
- `draft-01-owner-concept-links/`, `gallery-link-revalidation.json`: preserved initial diagnostic package and explicit revalidation after adding owner-gallery links. Student/source/academic/native/public bytes and candidate-set fingerprint remain unchanged; the final manifest is newly bound to the corrected gallery implementation.

A separate explicit owner authorization must bind the exact final manifest SHA-256, candidate-set fingerprint and every publication/context fingerprint before any approval or publication. Any material content, explanation, accessible description, metadata, mapping, source/image or highlight change requires renewed review. This milestone grants no approval and does not merge or deploy.

Release 5's 55 provider/local HTML differences and transport-blocked live UI checks remain unresolved. They are not assumed harmless. Existing evidence is preserved; no production probe, deployment, rollback, hosting/DNS/Firebase change or new infrastructure is performed for Batch 6.
