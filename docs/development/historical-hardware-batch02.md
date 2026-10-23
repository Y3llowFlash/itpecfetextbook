# Hardware expansion Batch 2: private preparation

Base: `88577fed721e24ef5db9fbbe07bd7fe1e4910d19` on remote main.
Branch: `feature/technology01-hardware-batch02`.

This milestone prepares 40 additional questions across 21 Hardware concepts. All
remain unapproved. Fifteen new paragraph highlights exist only in the ignored
preview application. Production remains at 456 questions, including the unchanged
first 36 historical questions. The seven qualified owner cases are excluded.

## Reuse and boundaries

`scripts/hardware_batch02.py` orchestrates the existing native review schema,
academic QA source/image validators, catalog-audit evidence validator,
publication-readiness gate, publication fingerprints and private student adapter.
It provides only `prepare` and `check`; it cannot grant approval or publish.

The original 36-question selector and its seven-concept assertions are unchanged.
The shared adapter now accepts an explicit later-batch scope and association
callback. The existing loopback server accepts `--batch02` to select the new
allowlist. The default first-pilot command retains its original behavior.

Only the selected native reviews' classification, mapping and extraction
dimensions are updated, with previous/new values and source-bound preparation
history. Academic answers, explanations, metadata, approvals, original transcripts
and image bytes are preserved. All other 293 native reviews remain identical to
the released baseline, including the 36 approved records. An initial private draft
is retained locally with a supersession receipt recording a corrected exponent
grouping; it grants no approval.

The older advisory classification ledger is validated against its actual preserved
pre-metadata snapshot. Its stale reports are not rebound to current reviews. The
40 decisions are separately validated against current source images, complete
Volume 1 page text/checksums, printed page labels, exact numbered headings and
actual website fragments. Classification annotations increase from 146 to 179;
only 33 previously missing annotations are added, alongside seven selected
annotations rechecked. Nonselected advisory recommendations remain unapplied.

## Local artifacts

Private inputs and all generated material live under:

`.local/historical-batches/technology01-hardware-batch02/`

- `before/`: frozen native records, reviews, manifest and gallery.
- `decisions.json`: 40 reviewed editorial decisions, passages and concept fragments.
- `baseline-guard.json`: public/source/input fingerprints.
- `review-diff.json`: exact previous/revised editorial values for every selected ID.
- `candidate-recommendation.json`: full future candidate recommendation, statuses,
  grading eligibility, accessible text, answers, explanations and fingerprints.
- `inventory.csv` and `completion-report.md`: complete 40-question inventory,
  repairs, page evidence, distribution, deferred cases and remaining queue.
- `preview/manifest.json`: exact 40 additions plus 36 published references and
  hash-allowlisted delivery assets.
- `preview/app/`: isolated application with disposable progress and no Firebase.

These files, historical question images and textbook evidence are deliberately
absent from Git and production assets. The versioned script requires the existing
local editorial workspace; it cannot infer or recreate missing private decisions.

## Preparation and review

```sh
python scripts/hardware_batch02.py prepare
python scripts/hardware_batch02.py check
node scripts/private-student-preview-server.mjs --batch02
```

Open `http://127.0.0.1:4327/`. The concept walkthrough shows separate addition and
published-reference counts. Practice has a collection selector and collection
badges. The usual image enlargement, answer feedback, explanation, keyboard
navigation and precise reading return are reused.

Progress uses `itpecTextbook:privateHardwareBatch02:`. Reset removes only this
namespace, preserving production guest/account data and the earlier private pilot.
The server binds to loopback, requires its exact Host/Origin, accepts GET/HEAD only,
serves exact fingerprinted assets, blocks private ledgers/PDFs and excludes all
unselected historical images. Student pages contain no editorial histories.

`prepare` rejects changed source, decisions, public files or live review snapshots.
Repetition recomputes the same bounded updates from the frozen baseline, without
appending history repeatedly or invalidating existing approvals. `check` rejects
stale implementation, preview sources, generated data or delivery assets.

## Validation

```sh
python -m unittest discover -s tests -p test_*.py
npm test
npm run check
npm run build
npm run test:e2e
npx playwright test --config=playwright.hardware-batch02.config.ts
```

The private browser suite checks all 40 original images, accessible choices,
grading and unchanged worked explanations; all 21 reading/highlight/return paths;
76 image hashes; collection comparison; literal exponent grouping; neutral
diagram descriptions; 320px enlargement; keyboard use; reset and real-progress
isolation; no cloud requests; and private transport restrictions.

The existing native approved export still contains exactly the released 36, with
none of the new 40. The production build validates the same 456 public records and
image hashes. The older full-catalog release snapshot checker intentionally
predates these authorized private repairs; it is not weakened or overwritten.

Completed validation: 171 Python tests (including 14 new preparation regressions),
86 Vitest tests, 52 production browser tests and 65 private Batch 2 browser tests.
Application Astro/TypeScript checks reported zero errors/warnings/hints; the private
application check did likewise. Production and private builds passed. The unchanged
production bundle retains its existing large-chunk advisory. A private reset
namespace defect found during the first browser pass was corrected and the full
65-test suite then passed.

## Later authorization

The recommendation is not an approval package or publication authorization. A
later explicitly authorized milestone must use the existing approval-candidate
and publisher architecture to bind the final student-visible records and reviewed
concept definitions/highlights, compare them to this preview, and obtain separate
owner authorization for those exact fingerprints. Any later academic, mapping or
accessible-description change must invalidate that authorization. Reliable Practice
occurrences retain their authoritative answers and identities.

No merge, deployment, public catalog edit or owner approval is part of this work.
