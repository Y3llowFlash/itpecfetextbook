# Release 3 — exact owner-authorized Hardware expansion

This release adds exactly 40 independently verified historical questions and 14 source-bound highlights from the immutable final Batch 3 package prepared at `ec9f7de89eb9fe67c5f08fc6b8f8158801fbb9d9`. It preserves the previous 496 question payloads, explanations and images, all 76 previous historical approvals, and all 333 native academic histories. The remaining 217 historical records are unapproved and excluded, including all seven qualified owner-adjudicated cases.

The public catalog now contains 536 questions/images: 420 authoritative Practice records and 116 historical records. Forty new mappings cover 28 concepts; fourteen definitions are new. No duplicate exclusions, existing-record updates, academic edits, image replacements, progress migrations or Firebase production writes were needed.

## Authorization and reproducible gates

Candidate manifest SHA-256: `3d260fec5224408e642b1a405501097d423011a0e317b73e0224c302887e3721`.

Candidate-set fingerprint: `94f7afb532d4aaeb6eb367fcfe0fc8f03e77699121bd5883a4a82bf18f2ca6f2`.

The existing native `historical_questions.approve` mechanism grants each approval. Release authorization additionally binds the manifest, candidate set, per-question context, source content/image hashes and any new highlight definition. `scripts/release_3.py` validates this exact transition and rejects stale or expanded scope. It does not select, solve or approve other questions.

The mandatory publisher dry run returned 116 approved inputs, exactly 40 additions, zero updates and zero conflicts before public mutation. A fresh dry-run receipt is required by the existing publisher's non-dry-run Batch 3 gate. After publication, prepublication gates deliberately reject repeating the transition; `python scripts/release_3.py verify` validates the completed release instead.

The original approval package remains immutable. Preparation checks retain their original read-only rules and refuse rebinding after release. Explicit archival regression fixtures use the original unapproved reviews and 496-record baseline, while completed-release checks inspect real live approvals and public data. The archived galleries are read-only snapshots, not the current approval-status interface. They remain loopback-only and outside `dist`.

## Public integrity

`docs/development/evidence/historical-release-3.json` binds every new public question, answer, mapping and image. Production validation recursively checks Releases 1 and 2 on their unchanged original subsets, then validates Release 3 and all 14 definitions. Existing Practice authority and qualified-answer safeguards remain intact. Original book HTML, source crops, account code, guest keys and authentication configuration are unchanged.

The built release contains 53 pages and 536 question images. Closed asset allowlists and an additional private-ID scan exclude source PDFs, editorial archives, native reviews and the 217 unapproved records.

## Local verification and operational evidence

Validation includes 221 Python tests, 98 application tests, 40 release-browser tests covering all 40 new questions and 28 associations, 72 frozen student-preview tests, five read-only owner-gallery tests, 52 general browser tests, twelve emulator rules tests, and six emulator account tests including Release 3 cross-device answer/bookmark synchronization. Astro/TypeScript reports zero diagnostics. `npm run build` validates all source/image bindings and the production boundary.

Release 2 count assertions were updated to exact Release 3 counts while preserving earlier receipt assertions. A local test-output collision deleted archived review screenshots; all 22 were recovered byte-for-byte against frozen hashes, and new browser outputs now live outside the frozen package. An Astro preview-lock collision was resolved by running account and production-preview suites sequentially. No gate was weakened and no real student data was changed. The build retains the existing large-chunk warning; emulator CLI MOTD/config fetch warnings were nonfatal.

Git integration uses a fresh `origin/main` check and fast-forward merge if ancestry permits. Cloudflare's existing GitHub/main production workflow performs deployment; no new project, infrastructure, DNS or Firebase setting is required. Before rollout, deployment `009f2d5a-7eeb-435c-9bdf-424fb57ddd6c` at `540ddf145cc60fbf223a7bc960d89012a06f4cb6` is preserved as the rollback reference.

Actual Git integration, provider deployment identity, full asset-manifest comparison, direct HTTPS observations and live-browser outcomes are recorded separately in `.local/releases/historical-40-batch03/completion-report.md`. Deployment, asset integrity and live UI evidence must be assessed separately; transport failures alone do not justify rollback or a claim of full UI verification.
