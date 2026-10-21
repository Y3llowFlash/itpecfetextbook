# Hardware pilot completion report

Date: 2026-10-21. Scope: the first complete Hardware learning experience. No production deployment or Firebase provisioning.

## Implemented

- Static Astro chapter/lesson pages, SEO metadata, sitemap, real 404 and noindex private progress route.
- React practice and progress components with TypeScript models, readable original Markdown content and an original semantic memory-hierarchy diagram.
- Left chapter navigation, central reader and right companion; narrow layouts use a chapter disclosure and place study help below the reader.
- A yellow inline cache-memory highlight connected to three verified published questions, with original images, accessible descriptions/options, explicit submission, correct/incorrect feedback, worked explanations, previous/next and numbered navigation, bookmarks and image enlargement.
- Stable block/offset reading capture, explicit return and browser Back with focus restoration after fonts/layout settle. The return destination is restricted to the known same-origin lesson.
- Local guest attempts, latest correctness, section completion, bookmarks, current question and last reading location. Storage failures retain a usable in-memory session and show a message; corrupt stored data is preserved. Duplicate attempt IDs are idempotent.
- A dismissible future-account reminder after meaningful activity, local JSON export and a clean `ProgressSyncAdapter` interface. No Firebase implementation is present.
- Concept-specific external Telegram help after an incorrect answer, a written fallback for missing mappings, and a click-to-load YouTube-capable component for future real mappings. Optional paid-course information is secondary.

## Existing resources reused

The source was `D:\ITPEC Old Questions`, commit `aee4d8d7d8879fe06176198d337a413bafe13a9d`. The implementation reused processed published JSON, original question IDs/answer keys, original local WebP crops, chapter/section/topic metadata, PDF/page provenance, the Hardware chapter outline and the real `memory-hierarchy` Telegram lesson from `src/data/lectureResources.js`.

Normalization, variable-choice handling, guest learning and recommendation behavior informed the new components. The old Firebase-bound services and large `App.jsx` were not copied into the new runtime. All lesson prose, diagram, explanations, storage code and application components were authored in this repository. No source textbook PDF prose extraction or third-party textbook figure was published.

## Real pilot questions

| ID | Original paper | Answer | Verified concept connection |
|---|---|---|---|
| `2024A-A-Q009` | 2024 Autumn Subject A, Q9 | b | Cache miss ratio and weighted access time; 360 ns |
| `2025S-A-Q010` | 2025 Spring Subject A, Q10 | c | Equal effective access times; shared hit ratio approximately 0.83 |
| `2026S-A-Q010` | 2026 Spring Subject A, Q10 | d | Cache miss fetches data from main memory in the question's model |

Each original image was inspected and compared with the existing topic/notes and answer key. Explanations preserve the question's timing assumptions; the 2024A main-memory time already includes the cache check. The 2025S hit-ratio algebra is independently checked by substitution.

The three-question count is derived from distinct published IDs. The full imported snapshot contains 420 published records for future reviewed use; the UI does not pretend that all 420 have pilot lessons or explanations. All included IDs and source fingerprints are in [the import manifest](../../public/data/import-manifest.json).

## Published-only verification

The importer checks the literal snake-case flag `is_published === true` before reading or copying any image. It rejects truthy strings/numbers and does not fall back to camel-case `isPublished`. A dedicated fixture includes an unpublished row whose camel-case flag is true and whose image does not exist; import succeeds without reading that image and does not output its ID.

Independent comparison with all seven old prepared JSON files confirmed **420 exact matching published IDs**, **zero excluded IDs**, and **zero excluded image filenames** in public output. The 160 excluded records are not copied into the release. Exactly 420 public image files occupy 33,992,598 bytes. The build checks their SHA-256 hashes/dimensions, rejects stale/extra images, and verifies that the final `dist/data/questions.json` matches the validated snapshot.

The importer stages/validates inputs before replacing only its own generated output, deduplicates identical records, rejects conflicting IDs and verifies generated paths remain within the intended output directory. Reimporting the test fixture is deterministic. Ordinary builds use the committed snapshot and require no access to the old repository.

## Validation

- Astro diagnostics and TypeScript: zero errors, warnings or hints.
- Vitest: 23 unit/component tests covering import policy, ID conflicts, original mappings, option counts, image metadata, deterministic refresh, attempts/retries, bookmarks/completion, corrupted/denied/quota-limited storage, derived counts, numerical reasoning, real practice interaction and reading restoration.
- Production build: six pages plus sitemap, static reading text/highlight present, private progress indexing disabled, 420 published records and 420 matching images, no old Firebase bucket/client dependency or video placeholders in bundles.
- Playwright: **11 passing browser tests** cover the production-build learning flow, exact explicit reading return and browser Back, reload persistence, blocked storage, no-JavaScript reading, keyboard answers, image dialog/Escape, no external runtime requests, and 320/375/414/768/1280 pixel layouts. The full learning-flow test also checks for browser/console errors, including hydration errors. Screenshots are generated under ignored `test-results/` for review.
- The interactive browser connector was unavailable; isolated headless Chromium tests were used for the local application. Screenshots were inspected directly. Safari/Firefox and physical-device/network testing remain outside this milestone's verification.

## Run and review

```powershell
npm.cmd ci
npm.cmd run dev
```

Open `http://127.0.0.1:4321/chapters/hardware/memory-and-cache/`. Follow the yellow highlight, answer a question, navigate, bookmark, return to the highlighted paragraph, mark the section complete and open Your progress. Detailed test, build, preview and import commands are in [README](../../README.md).

## Deliberately unfinished

Further Hardware sections and all other chapters, CET, Firebase sign-in/cloud synchronization, production deployment, progress-file restore, simultaneous multi-tab edit conflict resolution and a verified YouTube catalog remain unfinished. The current relevant video is a real cataloged Telegram topic lesson; it is not relabeled as YouTube or an exact question solution. The missing original prototype HTML was not invented as evidence; the supplied layout/interaction requirements were implemented directly.

No old repository code/data was changed or deployed. Guest progress remains local. Accounts are not required. This milestone stops at the single complete Hardware learning flow for review.
