# Morning / Subject A integration completion report

Historical metadata checkpoint. The subsequent [final approval preparation](FINAL_36_APPROVAL_PREPARATION.md) has integrated both validated accessibility transcriptions into native publication reviews. The overlay handoff prerequisite described below is therefore resolved; final owner publication approval is still absent.

Owner metadata confirmation is applied to **333 private historical reviews**: 333 Morning / Subject A, zero Evening / Subject B, zero unresolved metadata and zero conflicts. Evidence records explicit owner confirmation, the original instruction checksum, source checksum and exact scope. It does not claim paper/subject extraction from PDF pages.

All 333 immutable question records, canonical IDs, raw text, images, examination years/seasons/numbers and original source fields are unchanged. All 326 independent verification records and explanations, seven qualified owner-adjudication objects, classifications, mappings and academic histories are preserved exactly. The 420 published Practice records/images and production reader assets are unchanged. Preview progress continues to use the same question IDs, storage namespace and academic explanation revisions; no progress migration is required.

All 36 private pilot headers display confirmed FE / Morning / Subject A metadata. All original images, verified grading answers, summaries, worked steps, seven concept associations and reading-position restoration passed browser checks. Source-bound accessibility overlays for historical pages 22 and 28 remain resolved; only their full-review hash bindings changed after metadata-only preservation checks. Internal QA findings remain editor-only.

| Pilot readiness | Result |
|---|---:|
| Previous missing paper/subject blockers | 36 |
| Remaining metadata blockers | 0 |
| Corrected private projections technically ready for owner review | 36 |
| Additional content defects requiring repair in the selected set | 0 |
| Missing final owner publication approvals | 36 |
| Validated accessibility overlays to include in eventual final approval payload | 2 |
| Publication dry-run additions / updates / approved inputs | 0 / 0 / 0 |

The last distinction matters: the existing publisher reads native extraction reviews and does not merge preview overlays. Before eventual approval/promotion, the final source-bound payload must carry the two already validated transcriptions. This milestone neither discards the corrections nor grants approval to an older payload. All seven qualified owner cases remain grading/publication blocked; page 119 retains both A and D as valid, with no ordinary single-answer eligibility.

The full private 36-row table and per-record metadata, source, mapping, accessibility and approval results are in `.local/private-student-preview/metadata-integration/publication-readiness.md` and `.json`. The publisher was run with `--dry-run`; byte-and-mtime snapshots confirmed no protected source, review, approval, catalog or public asset writes. The readiness command's `--check` mode writes no reports either.

The refreshed complete classification audit lives in `.local/historical/technology-01/catalog-audit/metadata-reports/`. Original decisions/reports remain frozen. Recommendations remain 292 Hardware, 29 other Volume 1, three outside Volume 1 and nine uncertain. No classification recommendation was applied. Mapping totals remain 257 verified, 40 proposed and 36 needs-review; effective extractions remain 321 complete and 12 partial. Those broader repair queues are unchanged and are outside this pilot's publication readiness.

Engineering reuses the existing QA snapshot/history, manifest, source-pixel and gate validators. `academic_qa.py --metadata` validates the exact baseline or an identical applied state; `--apply` performs the authorized metadata-only reconciliation. Current audit/accessibility bindings are derived only after proving all non-metadata review fields identical. Prior metadata, original source history and all older academic/owner artifacts are retained. Engine-only refinement was separately rebound after proving the exact same 333 metadata outputs; the receipt is private. Repeated reconciliation makes zero review changes and rejects stale snapshots, sources, declarations or engine inputs.

Future import normalization records owner defaults or explicit evidence, preserves declared Evening / Subject B, and rejects contradictory source-specific instructions. Existing Practice synchronization code and answer-authority rules were not modified. No additional historical PDF was processed.

Validation: **147 Python tests, 82 application tests, 49 private browser tests and 52 production browser tests passed**. Production and private Astro/TypeScript checks passed without errors, warnings or hints. Production build/release validation passed with 420 original public questions/images; private build passed. All 333 original crops passed fresh source-pixel comparison; repeated private generation preserves identical projected data and asset hashes. Existing nonblocking chunk-size/terminal-color notices remain unchanged. No final test failures remain.

One intermediate private browser run had 48 passes and one temporary 404 while the repeat-build check replaced its local output. The build and browser run were then sequenced; the stable final run passed all 49 without changing assertions or content.

Changed implementation: `historical_metadata.py`, `metadata_integration.py`, metadata dispatch in `academic_qa.py`, historical import initialization, audit rebinding/report selection, private metadata projection/header, `pilot_readiness.py`, metadata/preview tests and these development reports. No production `src/` or `public/` file changed. Commit hash and clean feature-branch/push state are recorded in the private handoff and final response.

```powershell
python scripts/academic_qa.py --metadata
python scripts/catalog_audit.py --check
npm.cmd run questions:pilot:prepare
python scripts/pilot_readiness.py --check
npm.cmd run questions:pilot
```

Prepare the readiness report once with `python scripts/pilot_readiness.py` before using `--check`. Owner preview: **http://127.0.0.1:4324/**. All generated question material remains in ignored private workspaces; nothing is exposed through public assets. No owner publication approval, historical publication, main merge or deployment occurred. Stop for owner review.
