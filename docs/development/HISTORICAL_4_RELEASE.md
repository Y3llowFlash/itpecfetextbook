# Release 4 — exact owner-authorized Hardware expansion

Release 4 adds exactly 40 independently verified historical questions and two
source-bound highlights from the final Batch 4 approval package at
`9eb77e143b0134e8192187eed8d613f4c54c0766`. It preserves all previous 536 public
question records, images and explanations, 116 prior historical approvals, and all
333 native academic histories. The other 177 historical questions remain private
and unapproved, including all seven qualified adjudications.

The public catalog contains 576 question/image pairs: 420 authoritative Practice
records and 156 historical records. Batch 4 spans 20 Hardware concepts, reuses 18
unchanged highlight definitions and adds `display-memory` and
`cache-write-policies`. No duplicate exclusions, prior-record updates, academic
rewrites, image replacements or progress migrations were needed.

## Exact authorization and publication gates

Candidate manifest SHA-256:
`abe86bab2c0226e9e1139f581a13ddd01ee43fd37529b250a080ffe7107261b0`.

Candidate-set fingerprint:
`bd1bd946d17cbf8a95a0a334b14a509d51cbdc4b192234580fe95adedc8186cc`.

The explicit owner instruction authorizes these exact 40 fingerprint-bound
questions and both reviewed highlights, the safe main merge and existing Pages
production deployment. Its verbatim text and hash are frozen privately with the
native before-snapshot and original package artifacts. No authorization is inferred
for any other question or feature.

`scripts/release_4.py` follows the existing Release 3 orchestration and reuses the
native `historical_questions.approve`, candidate/preview comparator, independent
verification, source-image and paragraph gates, context fingerprints and existing
TypeScript publisher. Each approval binds the manifest, candidate set, exact
question/context fingerprint and original content/image hashes. The three records
associated with new highlights also bind the owner editorial definition hash.

Every gate checks the frozen final package against its original Git implementation
at `9eb77e1`; no prepared fingerprint or student-visible content was refreshed.
All 40 original crops were pixel-compared against Technology-01 again at freeze.
The 13 complex source cases and existing accessible repairs remain unchanged.

The mandatory prepublication dry run returned 156 approved inputs, exactly 40
additions, zero updates and zero conflicts. A fresh hash-bound successful dry run
is required before the existing publisher can mutate public files. A completed
release is validated with `python scripts/release_4.py verify`; prepublication gates
deliberately reject repeating the already-applied transition.

The approval gate caught generic summary regeneration recounting three effective
extraction repairs already present before authorization. Only approval objects had
changed. Before publication, the exact frozen manifest was retained with only its
approval count updated. A regression rejects other manifest-summary changes. No
source, answer, extraction or mapping gate was bypassed.

## Highlights and preservation

- Display memory: heading 5-2-1, printed p.98 / physical p.104, two questions.
- Cache write policies: heading 3-5-1, highlight context printed p.71 / physical
  p.76; direct teaching printed p.72 / physical p.77, one question. The original
  context and teaching roles are preserved separately.

`docs/development/evidence/historical-release-4.json` binds the final public
questions, worked explanations, mappings, images and highlight definitions.
Application/build validation recursively verifies Releases 1–3 on their unchanged
subsets, then the exact Release 4 append. Existing textbook source HTML/crops,
student-facing components, Firebase/auth configuration, guest storage keys,
bookmarks and reading checkpoints are unchanged.

The production build contains 55 pages and exactly 576 approved question images.
Closed public-asset checks and a separate scan exclude the 177 private IDs, source
PDFs, native review JSON and editorial approval packages. Archived owner/student
galleries remain read-only local snapshots of the unapproved review milestone.
Their archival checks do not pretend current live approvals are absent; real
publication checks always inspect the live native catalog.

## Validation and deployment evidence

Validation covers 249 Python academic/release tests, 101 application tests, 64
archived private-preview browser checks, five read-only owner-gallery checks (one
Batch 3-only case skipped), 52 general application browser checks and 60 Release
1–4 browser checks, including all 40 new questions and 20 associations. Twelve
local rules tests and seven demo-emulator account tests cover guest migration,
cross-device answers/bookmarks, offline recovery and reading checkpoints, including
Release 4. Astro/TypeScript and the production/source/asset build gates must pass
before production integration. Exact exit codes and final results are retained in
the ignored release workspace.

Catalog count and navigation assertions were extended to the exact approved
Release 4 set while retaining earlier receipt and explanation checks. One private
reading-return failure under concurrent browser load passed in the complete
isolated rerun without application changes. Account and production previews are
run sequentially because Astro shares a preview lock. A Windows emulator startup
interruption passed on retry. The existing large-chunk advisory and nonfatal
Firebase CLI configuration-fetch warnings remain documented.

Integration uses fresh remote-main evidence and a fast-forward-only merge when
ancestry permits, without force push. The existing GitHub/main Cloudflare Pages
workflow deploys the merged revision. No new project, infrastructure, DNS,
Firebase setting or real student data is changed. Current Release 3 deployment
`8def6de1-a59f-4459-8359-b5703a3dd566` remains the predecessor reference.

The actual pushed/deployed commit, Cloudflare deployment ID, provider asset
manifest, direct HTTPS evidence and live browser results are recorded in
`.local/releases/historical-40-batch04/PRODUCTION-HEALTH-REPORT.md` and
`completion-report.md`. Do not infer live verification from local tests or provider
deployment success alone.

## Carried Release 3 operational uncertainty

Release 3's 52 deployed HTML hash differences remain unexplained. Actual HTML and
live UI verification were transport-blocked, with similar failures on the earlier
healthy deployment. They have not been classified as harmless, and no confirmed
application regression or evidence warranting automatic rollback has been found.
The owner explicitly authorized Release 4 with this risk documented. New deployment
identity, content assets, successful live retrievals, blocked transport and remaining
HTML uncertainty are reported separately; production progress is never reset to
perform verification.
