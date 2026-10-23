# Batch 3 final owner-review package

Preparation baseline: `e08aaa20a72996d6bb57aa8641488c2f674a4bc9`.
Production baseline: `540ddf145cc60fbf223a7bc960d89012a06f4cb6`.
Branch: `feature/technology01-hardware-batch03`.

The exact 40 prepared questions are frozen as native publication candidates,
grouped by 28 concepts. All 14 proposed highlights passed individual original-book
review and the existing paragraph/heading gate. All 40 candidates are technically
eligible for owner review, zero require content corrections, and all remain
unapproved. Source validation is separate from owner editorial or publication
approval; neither has been granted.

## Existing architecture and exact bindings

`scripts/approval_candidates.py --batch 3` extends the established candidate builder,
student-visible comparator, source associations, read-only gallery and publication
fingerprints. The shared package validator retains its earlier Batch 2 wrapper and
defaults. No importer, practice UI, approval writer or alternative publisher is added.

The native publication fingerprint binds the immutable question, original image,
reviewed transcription, metadata, mapping and academic answer/explanation. The
approval-context fingerprint additionally binds the exact concept definition,
highlight passage, source support and final editorial review. The candidate-set
fingerprint binds all 40 entries, all concept definitions, the 14 highlight reviews
and both original PDF checksums. The manifest also records the feature commit,
completed preparation identity, native snapshot and current implementation hashes.
Any later owner authorization must bind the manifest SHA-256 as well as these
candidate/set/context and new-highlight definition fingerprints.

The publisher's existing Batch 3 dry-run route now requires this exact package.
Missing, stale, modified, expanded or newly approved inputs fail closed. Batch 3
without `--dry-run` is still rejected before publication inputs are accessed. This
milestone does not permit an approval transition, even in publisher-check mode.

## Original preview and source review

The original completed Batch 3 manifest, data, reports and native snapshot were
archived before changing publisher integration. That integration changes an
implementation fingerprint tracked by the preview engine. The full existing
preparation engine therefore revalidated/rebuilt the preview; every native object,
generated preview source and delivered asset byte remained equal to the archived
preview. The original completion artifacts were restored byte for byte. A separate
receipt binds the original and current manifests. Stale-input checks were not
disabled, and an existing receipt cannot silently be refreshed.

All 40 original question images and transcriptions were rechecked. All 40 crops
were pixel-compared with the source PDF. All 14 highlight passages, printed/physical
page labels, subsection ownership, associated questions, continuation context and
lack of question-specific answer annotations were reviewed individually.

The switch-bounce definition remains in the original keyboard note, with the
repeat-versus-chattering qualification intact and corroborating 5-3 support. Touch
sensing, memory hierarchy, superscalar and portable-flash evidence retain their
original continuation pages and figures. Historical Bluetooth range and CPU-clock
performance qualifications remain in the preserved explanations.

Literal raw extraction and original option wording are kept separately from
neutral editorial clarifications. Page 155 uses full gate names in the source;
parenthetic standard abbreviations already present in the reviewed preview are
explicitly identified as clarifications. The page 75 typo “cash memory” remains
literal. No academic answer, worked explanation, image or accessible preview field
was rewritten for this milestone.

## Private artifacts and launch

The package uses the existing native manifest/gallery format and is stored under:

`.local/historical-batches/technology01-hardware-batch03/final-approval/`

This keeps the new workspace outside the preparation guard's frozen earlier
approval-package directories. Those earlier files remain byte-identical.

- `manifest.json`: exact 40 candidates, 28 definitions, 14 highlight reviews,
  source/native/feature/implementation bindings and all approval fingerprints.
- `before/`, `preparation-inputs.json`, `preview-revalidation.json`: original
  preparation snapshots and byte-equality evidence.
- `source-review.json`, `highlight-integration-report.json`: individual question
  and highlight editorial evidence; all owner-approval flags remain false.
- `equality-report.json`, `owner-review-checklist.json`: every visible-content
  comparison, independent readiness dimension, blocker and fingerprint.
- `completion-report.md`: all 40 canonical IDs, examinations, source pages,
  placements, fingerprints and the complete 14-highlight decision table.
- `preservation-evidence.json`, `validation-results.md`: protected catalog/review
  hashes, production-build privacy, test/build results and final commit receipt.
- `index.html`: the read-only owner gallery, grouped into 28 concepts, with a
  separate 14-highlight index and literal-versus-editorial source details.

All source-derived artifacts and original images remain private and ignored by
Git. A fresh clone requires the existing frozen private workspace; missing evidence
is rejected rather than reconstructed.

```sh
python scripts/approval_candidates.py check --batch 3
node scripts/question-review-server.mjs --approval-candidates --batch3
```

Open `http://127.0.0.1:4334/`. Set `QUESTION_REVIEW_PORT` to an unused loopback port
if necessary. The existing server serves only the gallery HTML and these exact
40 original images. It checks byte hashes, exact Host/Origin and GET/HEAD methods,
uses no-store/noindex and a CSP with no script or connection permission, and rejects
package JSON, raw PDFs, other questions and mutation endpoints. There are no
approval controls, authentication or student-progress writes.

The byte-equivalent student preview remains at port 4332, launched with
`node scripts/private-student-preview-server.mjs --batch03`.

## Validation and preservation

- 212 Python tests passed, including 12 new final-package regressions for scope,
  stale source review, native/visible/metadata/image changes, context fingerprints,
  withheld findings, unchanged approvals and byte-idempotent regeneration.
- 95 application tests passed across 20 files.
- 72 Batch 3 student-preview browser tests, five final owner-gallery tests and
  52 local production browser tests passed.
- Five guest/account cross-device tests passed using only local demo Firebase
  Auth/Firestore emulators, including both existing historical releases.
- Astro/TypeScript checks and production/private builds passed with no type
  diagnostics. The existing production chunk-size advisory remains.
- The production build still contains exactly 496 approved records and images;
  none of the 40 unapproved IDs, image bindings or new private concept routes is
  present. No private gallery/package data enters the public build.
- All 333 native review objects are byte-identical to this milestone's starting
  snapshot, preserving 326 independent answer/explanation objects, seven qualified
  adjudications and 76 previous owner approvals. All `src/` and `public/` files and
  earlier private release/approval evidence remain unchanged.
- Publisher dry run: 76 existing approved inputs, zero new approved inputs, zero
  additions, updates or conflicts.

The earlier full-native release snapshots remain frozen at their own milestones;
they are not rebound to the subsequently authorized private Batch 3 repairs.
Current release preservation is checked against all 496 original public file
bindings, the exact 36/40 earlier release ID sets and all 76 existing approval
fingerprints. No check is weakened to accommodate an unrelated change.

No publication approval, historical publication, merge, production deployment,
Practice-repository edit, paid infrastructure or real-progress reset occurred.
The final manifest SHA-256, candidate-set fingerprint and pushed feature commit
are recorded in the private validation/completion receipt for explicit owner review.
