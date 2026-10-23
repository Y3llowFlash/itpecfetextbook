# Hardware Batch 5: combined private preparation and final candidates

This milestone prepares forty independently verified Technology-01 questions across sixteen Hardware concepts. Fifteen published highlight definitions are reused; one unchanged sequential-circuit paragraph supplies a new flip-flop highlight. All candidates remain private and unapproved. Production remains at 576 question/image pairs and 156 historical approvals.

The feature branch is `feature/technology01-hardware-batch05`, based on main `ab642bcb96e32a47e4d28ee68b1352190c8da0c5`. No application content or assets are changed. Private native records, source review, candidate manifests, screenshots, source PDFs and reports live under ignored `.local` folders and are intentionally absent from clones.

## Reuse and integrity

`hardware_batch05.py` adapts the existing Batch 2 reconciliation gates and Batch 3 preview generator. Only selected classification, mapping and accessible extraction reviews can change. All academic answers, explanations, metadata/provenance, existing approvals, protected adjudications and immutable source records are preserved. Exact passages and source associations must pass the existing textbook/highlight validators. Source images are pixel-compared with the original PDF.

`approval_batch05.py` is an adapter to `approval_candidates.py`: it reuses its candidate builder, visible-content equality, publication/context fingerprints, source-review validator and read-only gallery. Preparation proceeds directly from the checked preview to the final package without an intermediate preparation commit. The frozen baseline and implementation hashes identify the inputs; the final feature commit is recorded in the ignored completion receipt.

The final source ledger binds images, raw transcripts, accessible payloads, native reviews and the new highlight. Literal source defects and editorial linearizations remain separate. Missing or stale evidence fails closed. Repeated preparation validates frozen output without refreshing hashes. Candidate/context fingerprints change if student-visible content, answer, explanation, description, metadata, mapping, image or highlight changes.

The publisher supports `--batch 5 --dry-run` and rejects Batch 5 non-dry-run before reading or mutating source data. It requires the exact final package and accepts only the forty candidates plus the 156 already released historical IDs. No approval operation or Release 5 deployment implementation is added.

## Local review

Run from the repository root, in separate terminals:

```powershell
node scripts/private-student-preview-server.mjs --batch05
node scripts/question-review-server.mjs --approval-candidates --batch5
```

Student preview: `http://127.0.0.1:4340/`.
Final owner gallery: `http://127.0.0.1:4342/`.

Both servers validate the package before serving, bind loopback, restrict Host/Origin, allow GET/HEAD only and hash-check an explicit asset allowlist. Unselected images, raw PDFs and native review JSON are denied. The preview contains forty private additions and 179 clearly labeled unchanged published references. It uses a distinct disposable progress namespace and excludes Firebase/authentication runtime. The owner gallery has no scripts, forms or approval controls.

## Reproducible private handoff

```powershell
python scripts/hardware_batch05.py check
python scripts/approval_candidates.py check --batch 5
python scripts/batch05_report.py
node node_modules/tsx/dist/cli.mjs scripts/publish-historical-questions.ts --batch 5 --dry-run
```

Private workspace: `.local/historical-batches/technology01-hardware-batch05/`.

- `completion-report.md`, `inventory.csv`: exact IDs, examination identities, textbook references, selection rationale and owner handoff.
- `review-diff.json`, `editorial-repairs.md`: exact before/after editorial, mapping and classification repairs, including explicit labels for previously missing accessible fields.
- `coverage-analysis.json`, `excluded-deferred.json`, `highlight-inventory.json`: complete coverage analysis, exclusions and reused/new/deferred highlights.
- `preservation-report.json`: all 333 academic histories, 156 approvals, seven protected cases and public-file integrity.
- `final-approval/manifest.json`, `source-review.json`: exact publication/context/set fingerprints and per-source review.
- `final-approval/equality-report.json`, `eligibility-report.json`: preview equality and per-question readiness/blockers.
- `validation/`, `validation-results.md`, `completion-receipt.json`: tests, unchanged production-build comparison, final commit and clean-tree receipt.

The original import manifest is preserved byte-for-byte. Effective review totals are computed separately: 326 complete and seven partial extractions; 265 verified, 32 proposed and 36 needs-review mappings. Academic totals remain 326 independently verified and seven qualified owner adjudications. All 177 unpublished historical records remain private/unapproved, including the forty candidates.

## Validation and later authorization

Focused regressions cover exact selection, stale snapshots, source fidelity, literal gate topology and latch polarity, numeric interpretation, answer neutrality, protected records, prior approval preservation, progress isolation, idempotency and owner/package fingerprint binding. Browser suites exercise every selected question and concept, the final owner gallery, privacy, mobile enlargement, keyboard navigation and reading return. Existing application, production browser, account-emulator, rules, type-check and build suites remain required.

The publication dry run must show 156 approved inputs, zero additions, zero updates and zero conflicts. The deterministic production build must match the Release 4 local asset baseline byte-for-byte. Exact test counts and results are in the private validation report.

A later explicitly authorized milestone must bind owner approval to the exact manifest SHA-256, candidate-set fingerprint, each publication/context fingerprint, and the new highlight definition hash for its three associated questions. Any changed candidate/context requires re-review and new authorization. This milestone grants no approval, publication, merge or deployment.

The 54 unresolved provider/local HTML hash differences and transport-blocked production UI verification remain open operational risks. They are not proved harmless. No application regression is established; this milestone preserves prior evidence and uses local production regressions without another network investigation, deployment or rollback.
