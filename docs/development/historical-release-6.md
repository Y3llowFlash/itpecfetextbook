# Release 6: forty authorized Hardware questions

Release 6 publishes exactly the forty candidates reviewed at preparation commit `2ec36dc239112ff40dc3bcfc53372517d231e56f`. The owner explicitly authorized their approval, publication, safe main integration and existing Cloudflare Pages deployment. Authorization text and detailed operational evidence remain private under `.local/releases/historical-40-batch06/`.

The immutable manifest SHA-256 is `da136fd278ebd826a25560def1f461412fbd84f175f767792388d9afabef2364`; the candidate-set fingerprint is `1111f8755de6ab6f554a7882b4683e7dfacc35a3fbf8fab1995d941c09108148`. Neither the original candidate manifest nor its student-visible content is regenerated during release. Thirteen existing concept highlights are reused. No highlight definition or source wording is added or changed.

The resulting catalog contains 656 question/image pairs: 420 authoritative Practice questions and 236 historical questions. All previous 616 records, answers, explanations and image bytes remain unchanged. The 196 earlier approvals remain unchanged; only the forty authorized candidates receive new approvals. All 333 academic histories and seven qualified adjudications are preserved. The remaining 97 historical questions stay private and unapproved, including the multiple-valid-answer case that cannot use ordinary single-answer grading.

## Existing pipeline and release gates

`scripts/release_6.py` extends the established release transition. It freezes the exact authorization, immutable candidate package, prior public payload, native reviews, original images and confirmed predecessor deployment. Approval calls `historical_questions.approve` and binds each record to its publication/context fingerprints, candidate manifest/set fingerprints, source/image hashes and explicit authorization provenance.

Publication requires an exact source-bound native gate and a fresh successful dry run. The dry-run receipt binds the native review bytes, publisher implementation and final manifest. It must contain exactly forty additions, 236 approved inputs, zero updates/conflicts and zero new highlights. An unauthorized, stale, altered, duplicate or out-of-scope payload fails closed.

The sanitized `evidence/historical-release-6.json` binds the forty published records, explanations, images and mappings, and all predecessor fingerprints. Production validation recursively verifies Releases 1–5 before checking Release 6. Existing concept definitions retain their exact wording and placement; only the authorized question associations are appended. No source PDF, private gallery, raw review history or unapproved crop enters the public build.

## Frozen private preparation

The original Batch 6 student preview and read-only gallery remain immutable review evidence with their original unapproved labels and 616-question baseline. The servers expose these as historical preparation artifacts through the same archival mechanism used in prior releases. They do not pretend that the live native reviews remain unapproved. Preparation regression tests retain their original assertions against explicit frozen snapshots; production approval and publication gates inspect real current data and never enter those test fixtures.

The release checks exact candidate-to-public equality, original source pixels, complete accessible descriptions and options, verified answers/explanations, existing source-highlight bindings, old record/image preservation and exclusion of every unapproved record. Browser coverage exercises all forty new questions across thirteen concepts, keyboard/mobile enlargement, grading, filters, reading return, bookmarks and guest persistence. Account and rules tests use isolated demo emulators and retain all prior-release progress cases. Guest keys, schemas, authentication and production Firebase configuration are unchanged.

## Production evidence and operational risk

The previous production baseline is `cd5fa89136dbd04d60ad0ccb7044eac923e08cd0`, deployment `c7e638e4-0b9c-4f2f-8f47-582800fae202`. Deployment identity must be established from authenticated Cloudflare evidence after a normal main push; local build success alone is insufficient.

The private release report separately classifies deployment identity, catalog/image/non-HTML integrity, HTML integrity and live browser behavior. It records the actual Release 6 provider/local HTML differences and compares their path set to Release 5's unresolved 55 differences. Those earlier differences have not been shown harmless. Bounded HTTPS/browser attempts retain certificate validation and never treat a transport timeout as a passed application workflow. A genuine release-specific defect blocks further rollout; matching transport failures on an earlier healthy deployment alone do not justify rollback.

No progress reset, destructive data migration, separate Practice repository change, DNS/hosting/Firebase configuration change or new infrastructure belongs to this release. Full test results, any diagnostics, git integration, deployment evidence, precise HTTP failures and final health classifications remain in the ignored release workspace.
