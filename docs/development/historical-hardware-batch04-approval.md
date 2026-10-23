# Batch 4 final owner-review package

Preparation baseline: `4bfdd608def68e511aa0a55fa748c575459c1334`.
Production baseline: `7debddd041e73ee943e4e83d0a39b299338fbf09`.
Branch: `feature/technology01-hardware-batch04`.

Exactly 40 prepared questions across 20 Hardware concepts are frozen as final
publication candidates. All are technically eligible; all remain unapproved.
Eighteen existing highlight definitions are unchanged. Two new highlights passed
original-book source review, but have no owner editorial authorization. No required
academic or accessible-content repair remains in this package.

## Reused architecture and immutable preparation

`scripts/approval_candidates.py --batch 4` extends the existing native candidate
builder, source review, preview comparator, gallery and approval fingerprints.
The publisher dry run now requires this exact final package. Non-dry-run Batch 4
publication is still rejected before source access or mutation. No approval writer,
alternative publisher or student application feature is added.

The original preparation inputs, completed receipt and native snapshot were frozen
before changing publisher integration. That change updates an implementation hash
tracked by the preview. The existing preparation engine revalidated the preview:
only its implementation field changed; all native objects, other preparation
artifacts, preview source files and delivered preview asset bytes remained equal.
The original manifest is retained separately. Missing/stale original evidence or a
changed prepared candidate fingerprint fails validation rather than being refreshed.

Every candidate retains its original publication fingerprint from completed
preparation. Separate dimension hashes bind verification, explanation, extraction,
metadata, classification and mapping. Its context fingerprint also binds the exact
concept, source support, highlight and final editorial review. The set fingerprint
binds all 40 candidates, 20 definitions, two highlight reviews and both PDF sources.
The final manifest SHA-256 binds the whole review package identity.

## Source review

All 40 original question crops were pixel-compared again with Technology-01.
Final visual reinspection covered physical pages 40, 58, 97, 111, 147, 195, 216,
222, 265, 283, 287, 289 and 333, including options, tables, wiring, units and notation.
The effective extraction repairs on pages 111, 283 and 287 remain present. No image,
academic answer, explanation or examination identity changed in this milestone.

Page 111's literal source typo `bimary` remains in the raw transcript and image;
the previously validated accessible correction is recorded separately. The source
option's unmatched parenthesis is also retained literally, with the existing
accessible grouping clarification distinguished from source wording. This is
already qualified in the preserved verified explanation, not a new answer change.

The two source-validated proposed highlights are:

| Concept | Book source | Questions |
|---|---|---|
| Display memory | Heading 5-2-1, printed 98 / physical 104 | 2 |
| Cache write policies | Heading 3-5-1; highlight context printed 71 / physical 76; direct teaching printed 72 / physical 77 | 1 |

Each exact original paragraph, page identity, subsection, source checksum and
question association is bound. Cache context and direct teaching retain their
separate roles. Original wording is unchanged; no question-specific selected answer
or computed result was inserted. The owner-only gallery deliberately shows answers.

## Private artifacts and launch

All private outputs are under
`.local/historical-batches/technology01-hardware-batch04/final-approval/`:

- `manifest.json` and `package-fingerprints.json`: exact candidates and bindings.
- `before/`, `preparation-inputs.json`, `preview-revalidation.json`: frozen inputs
  and implementation-only revalidation evidence.
- `source-review.json`, `highlight-integration-report.json`: individual source
  checks, both highlight reviews and explicit absent owner approvals.
- `equality-report.json`: student-visible candidate/preview equality.
- `owner-review-checklist.json`, `eligibility-report.json` and CSV: separate
  readiness dimensions, precise placements, fingerprints and remaining blockers.
- `index.html`: read-only gallery grouped by 20 concepts, two highlight cards,
  direct links to 13 complex source cases and private textbook concept links.
- `completion-report.md`, `preservation-evidence.json`, `validation-results.md`
  and `completion-receipt.json`: full decision table, checks, risks and commit.

```sh
python scripts/approval_candidates.py check --batch 4
node scripts/question-review-server.mjs --approval-candidates --batch4
```

Open `http://127.0.0.1:4338/`. The student preview concept links use port 4336:

```sh
node scripts/private-student-preview-server.mjs --batch04
```

The existing loopback server allows only GET/HEAD, the exact Host/Origin, gallery
HTML and these 40 hash-bound images. Raw PDFs, native JSON, other questions and
mutation routes are denied. CSP blocks scripts and connections. No approval action,
authentication, Firebase or progress runtime is delivered. Private files remain
ignored by Git and absent from production assets. A fresh clone needs the existing
private evidence workspace; it cannot reconstruct missing evidence from assumptions.

## Preservation and validation

All 536 published question/image pairs, 116 existing historical approval objects,
333 native histories, 326 independently verified answers/explanations and seven
qualified adjudications are unchanged. The seven qualified cases are excluded.
The 217 unpublished historical questions remain private. All production source and
public files are fingerprint-preserved, including progress, bookmarks, reading
checkpoints, Practice filters, landing behavior and Firebase configuration.

Validation includes 239 Python tests, 98 application tests, 64 private student
browser checks, five final-gallery browser checks (one Batch 3-only case skipped),
52 local application browser checks and 40 local release checks. Astro/TypeScript,
production build and closed-asset validation pass. The final validation receipt
records isolated emulator checks and a byte comparison against all 913 deterministic
Release 3 build assets. These are local tests, not live production verification.

The existing publisher dry run has 116 previously approved inputs and zero
additions, updates or conflicts. It grants no new approval. All 40 candidates need
final owner publication authorization; the three using new highlights also need
owner editorial authorization bound to their exact definitions.

## Later explicit authorization and production risk

A later owner authorization must identify the exact manifest SHA-256, candidate-set
fingerprint, each publication/context fingerprint and both new-highlight definition
hashes. Use the existing native approval fields and package/context authorization
mechanism only after that separate authorization. Revalidate immediately before
approval and publication dry run. Any change to student-visible content, source,
mapping, accessibility, image or highlight invalidates the old authorization and
requires review. This milestone accepts no approval transition.

Release 3 still has 52 unexplained deployed HTML hash differences. Transport
failures blocked actual live HTML and browser verification, including against the
previous healthy deployment. They are neither proven harmless nor confirmed
application defects. Existing evidence does not warrant rollback. This risk does
not block private preparation but must be explicitly accounted for before any later
Batch 4 production release. No equivalent failing network investigation was repeated.

No approval, publication, merge, deployment, hosting change, real student-data write,
additional historical PDF processing or separate Practice repository edit occurred.
