# Release 5: forty authorized Hardware questions

Release 5 publishes exactly the forty candidates and one flip-flop highlight reviewed at preparation commit `e136255243198e4867a67ee7be49b20cf8d466c6`. The owner explicitly authorized publication, safe main integration and deployment. The authorization text and detailed operational evidence remain private under `.local/releases/historical-40-batch05/`.

The reviewed manifest SHA-256 is `1618204cf7a991ec6cabb482c8badebe8b5c77125a9f3515faa6f8cc56fe4e39`; its candidate-set fingerprint is `681e50824fafdd0b18e4519ad4ac651348e3479deb301c08837ab6d3aec2c1c2`. Neither the package nor its student-visible payload was regenerated for release.

The public catalog now contains 616 question/image pairs: 420 authoritative Practice questions and 196 historical questions. All previous 576 records, answers, explanations and image bytes are preserved. The 156 prior approvals are unchanged; only the forty authorized candidates received new approvals. All 333 academic histories and all seven qualified owner adjudications are preserved. The remaining 137 historical records are private and unapproved.

## Existing approval and publication architecture

`scripts/release_5.py` reuses the established release transition. It freezes the exact owner authorization, candidate package, prior public payload, native reviews and original image bindings. Approval uses `historical_questions.approve`; each receipt binds the publication fingerprint, candidate manifest/set/context fingerprints, source/image hashes and authorization provenance. The three questions using the new highlight additionally bind its definition hash.

The publisher requires the native approval and exact final package gates. A non-dry-run publication additionally requires a successful, fresh dry run bound to the same review bytes, publisher implementation and manifest. The authorized dry run contains exactly forty additions, zero updates/conflicts and one new source highlight. Unapproved records, changed reviewed content or duplicate exclusions block publication.

The sanitized `evidence/historical-release-5.json` binds all forty published records, explanations, images, mappings, the one highlight and unchanged predecessor fingerprints. The public validator recursively checks Releases 1–4 before checking Release 5. Existing concept definitions retain their wording and placements; only authorized question associations are appended. No student progress keys, Firebase production configuration, authentication code, separate Practice repository or unrelated textbook content is changed.

## Frozen review evidence

The original private Batch 5 preview and read-only owner gallery remain immutable historical review artifacts. Their native preparation snapshot contains unapproved candidates by design. Release-aware delivery validates those archived bytes rather than pretending the live approved catalog is still the preparation baseline.

Preparation regression tests use explicit frozen fixtures for original-state assertions. Live release/publication validators always inspect the actual current native/public records and never use these test fixtures. Separate negative regressions exercise missing/stale approval/context/highlight bindings, academic edits, protected records, prior approvals, source images and stale dry runs.

## Local verification and deployment

The established Python, application, private/owner browser, production/release browser, account-emulator, rules, type and production-build checks are required before integration. Release-specific browser coverage includes every one of the forty additions and all sixteen concept associations. The final private validation report records results and any retried assertions.

The production deployment uses the existing GitHub-connected Cloudflare Pages project `itpecfetextbook`, production branch `main`, and `npm run build` → `dist`. A successful main push alone is insufficient: authenticated deployment identity, build outcome and asset bindings must be checked against the actual main commit.

All private source PDFs, native reviews, owner authorization text, galleries and unapproved images stay outside public assets. Build checks scan all generated assets for private paths/IDs and validate every approved image hash.

## Operational uncertainty

Release 4's 54 unexplained provider/local HTML hash differences remain unresolved. Previous HTTPS resets/timeouts also affected earlier healthy deployments. This is not proof of harmless transformation or of an application regression.

Release 5 verification separates deployment identity, catalog/image/non-HTML integrity and live behavior. New HTML differences must be reported separately; timeouts before application content are blocked checks, never passing UI tests. Bounded live attempts retain certificate verification and use isolated guest contexts without production Firebase writes. A confirmed content-integrity failure or reproducible application defect requires stopping unsafe operations; transport failures alone do not justify automatic rollback.

The private completion and production-health reports record the actual main/deployment IDs, exact provider bindings, live results, unresolved HTML differences and rollback assessment. No production state is described as fully verified if live interactions remain blocked.
