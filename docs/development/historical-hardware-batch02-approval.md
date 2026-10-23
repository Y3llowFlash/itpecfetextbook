# Batch 2 final approval package preparation

Feature branch: `feature/technology01-hardware-batch02`.
Prepared-batch baseline: `3e6c959c6941e68b61d29becbb79ffac0e26c23f`.
Inspected remote production baseline: `88577fed721e24ef5db9fbbe07bd7fe1e4910d19`.

Exactly the prepared 40 questions are final owner-review candidates, grouped by
all 21 concepts. All 40 remain unapproved. The 15 new source highlights are source
validated and await final owner editorial authorization. No academic, accessible
text, original image, native review, published question, existing approval or
student-progress record changed during this milestone.

## Existing architecture

The Release 1 `scripts/approval_candidates.py` builder, visible-content comparator,
publication fingerprints and owner-gallery renderer now support the explicit
second scope. The default first-release selector still requires its exact 36.
The earlier release package remains an unchanged historical artifact; it is not
regenerated against the newer public catalog or used as a current Batch 2 package.

The existing owner-gallery server accepts `--approval-candidates --batch2`. The
existing historical publisher accepts `--batch 2`. No approval-granting command,
alternate publisher or second review catalog was added.

The publisher obtains new concept definitions from the checked candidate package,
which matches the private preview. It validates their source fragments with the
same `scripts/historical-highlight.ts` gate used during preparation. This gate
allows legitimate unnumbered child labels inside the actual numbered subsection,
such as `(2) Pipeline control`, while rejecting a crossed numbered subsection,
unrecognized numbered heading, changed paragraph, nested link or duplicate
highlight. Original textbook wording is preserved.

## Private deliverables

All source content, question images and detailed reports remain local under:

`.local/historical/approval-candidates/technology-01-batch02/`

- `manifest.json`: exact native records/reviews, original images, accessible
  choices, verified answers/explanations, FE/Morning/Subject A metadata, exact
  mappings, bounded textbook passages, grading eligibility and fingerprints.
- `preparation-inputs.json` and `before/`: checksummed copies of the completed
  Batch 2 inputs, validated preview and complete native baseline.
- `index.html`: existing read-only owner gallery with 21 groups, 40 questions,
  complete technical checklist, original image links and individual blockers.
- `equality-report.json`: equality of every student-visible academic field and
  all 21 reviewed concept definitions with the validated private preview.
- `highlight-integration-report.json` and `highlight-integration-details.json`:
  all 15 highlight checks, actual source wording/pages, connected candidates and
  separately labeled supporting passages.
- `owner-review-checklist.json` and `candidate-fingerprints.csv`: complete
  per-question eligibility, fingerprints and remaining blockers.
- `completion-report.md`, `validation-results.json`, `idempotency-result.json`
  and `completion-integrity.json`: validation, repeatability and delivery receipts.

The final manifest SHA-256 is
`39bcc7b8ca0488bccfe61e5a66ab5ff7e61fa7e7310ff2b3089cc3449b85cea3`.
The candidate-set fingerprint is
`4a887d4730c7c8e4f5a43ff7585bbb0081fa0b4fbb81463e7fb348e1c3853cf0`.
Neither value constitutes owner authorization.

## Local review

```sh
python scripts/approval_candidates.py check --batch 2
node scripts/question-review-server.mjs --approval-candidates --batch2
```

Open `http://127.0.0.1:4330/`. Student comparison remains at port 4327, served by
`node scripts/private-student-preview-server.mjs --batch02`.

The owner server binds to loopback and serves only its fingerprinted HTML and the
40 original images. It rejects mutations, foreign Host/Origin headers, raw PDFs,
package JSON, native catalogs, other images and all previously released 36 images.
There are no approval controls, scripts, authentication or progress writes.

Preparation is deterministic and rejects changed original Batch 2 files, preview
content, native/source bindings, public records/assets or generated candidate
content. All native files and 333 original images retain their hashes and
modification times after repeated preparation. The first release's original
candidate manifest remains byte-identical.

## Verification

Passed: 185 Python tests, 91 application tests, 65 private student-preview browser
tests, four owner-gallery browser tests, 52 production browser tests and 11
existing historical-release browser tests. Application and private Astro/TypeScript
checks and both production/private builds passed. The unchanged production bundle
retains its existing large-chunk advisory.

All 40 crops were pixel-compared to the original PDF. Source cases on physical
pages 3, 32, 137, 186, 221, 300 and 311 were visually rechecked, including exponent
grouping, table rows, options and diagram connections. No new correction was
required and no independently verified answer or explanation was rewritten.

```sh
python -m unittest discover -s tests -p test_*.py
npm test
npm run check
npm run build
npm run test:e2e
npx playwright test --config=playwright.release.config.ts
npx playwright test --config=playwright.hardware-batch02.config.ts
npx playwright test --config=playwright.owner-batch02.config.ts
node node_modules/tsx/dist/cli.mjs scripts/publish-historical-questions.ts --dry-run --batch 2
```

The publisher dry run consumed only the existing 36 released approvals and
reported zero additions, zero updates and zero conflicts. No new approval was
granted. The public catalog remains 456 questions/images, with all 420 Practice
records and the first 36 historical records/approvals unchanged. The seven
qualified owner-adjudicated questions are excluded.

## Later explicit owner authorization

Remaining blockers are 40 owner publication authorizations and final owner
editorial authorization for 15 highlights affecting 26 candidates. There are zero
technical correction blockers. Source validation and technical eligibility grant
neither kind of authorization.

A later authorized release must use the existing native approval mechanism and
bind its receipt to the exact manifest SHA-256, candidate-set fingerprint and
each record's publication/context fingerprints. In addition to the existing
approval fingerprint, the publisher requires `candidateManifestSha256`,
`candidateSetFingerprint` and `approvalContextFingerprint` on any newly approved
record. New-highlight records also require `highlightEditorialAuthorization`
equal to the reviewed definition hash. This milestone provides no action that
grants those fields or approval.

Changing a question, image/source binding, answer, explanation, metadata, mapping
or accessible text invalidates the existing native publication fingerprint.
Changing the reviewed concept definition, source passage or package invalidates
the context/package binding. Re-review and fresh explicit owner authorization are
required after either kind of change. Reliable published Practice occurrences
retain their authoritative answers, explanations, IDs and progress identities.

No publication, merge, deployment, unrelated classification update, extra
historical PDF processing, Practice source edit or paid infrastructure is part of
this preparation milestone.
