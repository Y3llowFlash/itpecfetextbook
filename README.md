# ITPEC FE Textbook

A free, static textbook with real ITPEC FE question practice. The first milestone contains one complete **Hardware → Memory hierarchy & cache** lesson, three related-question explanations, and browser-local guest progress.

Built with **Astro, React and TypeScript**. Output is compatible with static Cloudflare Pages hosting. This repository does not provision or deploy infrastructure.

## Run locally

Requires Node.js 24 or later and npm.

```powershell
npm.cmd ci
npm.cmd run dev
```

Open `http://127.0.0.1:4321/`. On shells without PowerShell's script restriction, `npm` can be used instead of `npm.cmd`.

Useful routes:

- `/chapters/hardware/` — chapter structure and the available lesson.
- `/chapters/hardware/memory-and-cache/` — complete static lesson.
- `/practice/cache-memory/` — real questions, answer checking and explanations.
- `/progress/` — local reading, attempts, completion and bookmarks.

## Check and build

```powershell
npm.cmd run check
npm.cmd test
npm.cmd run build
npx.cmd playwright install chromium
npm.cmd run test:e2e
npm.cmd run preview
```

`check` runs Astro diagnostics and TypeScript. Unit/component tests cover publication filtering, duplicates, answer explanations, persistence failures, navigation and reading restoration. End-to-end tests run against the production build in a fresh headless browser, including 320, 375, 414, 768 and 1280 pixel viewports. The build validates data/assets before rendering and verifies the final public output afterward. Preview serves the production `dist/` directory, normally on port 4321. E2E uses its own temporary preview on port 4322 and stops it on completion.

Astro CLI telemetry is disabled by the local wrapper. No Firebase configuration or credentials are required. The pilot sends no learning data to a server.

## Published-question import

The imported snapshot is committed, so ordinary development and builds **do not need the old repository**.

To intentionally refresh it from a read-only source checkout:

```powershell
npm.cmd run import:questions -- --source "D:\ITPEC Old Questions"
npm.cmd run validate:data
npm.cmd test
npm.cmd run build
```

Alternatively, set `ITPEC_SOURCE_DIR` and run `npm.cmd run import:questions`. The source must contain the processed `database/firebase_import/questions_subject*_firestore.json` files and referenced local images under `database/builder/output_images/`.

The importer:

1. Selects **only `is_published === true`**. Camel-case `isPublished`, truthy strings and numbers never override this policy.
2. Preserves original IDs, dates, subject/paper, answer/options, chapter/section/topic mappings and PDF/page provenance.
3. Copies only the selected records' local images, adding SHA-256 filenames and intrinsic dimensions.
4. Deduplicates identical IDs and fails on conflicting records.
5. Validates all inputs before replacing its own `public/questions/` directory and `public/data/` output files. Treat `public/questions/` as generated; do not put hand-authored files there.
6. Produces `public/data/import-manifest.json` with source hashes, included IDs, publication totals and image inventory. It never writes to the source checkout or connects to Firebase.

Current snapshot: **420 published questions** (300 A + 100 dated B + 20 sample B); **160 unpublished records excluded**. There are exactly 420 public question images. All included IDs are listed in the import manifest. The pilot UI exposes only these three reviewed cache-memory questions:

| Original ID | Source | Answer |
|---|---|---|
| `2024A-A-Q009` | 2024 Autumn Subject A, Q9 | b |
| `2025S-A-Q010` | 2025 Spring Subject A, Q10 | c |
| `2026S-A-Q010` | 2026 Spring Subject A, Q10 | d |

The other published records are available as static release data for later reviewed mappings. They are not given invented concepts or explanations. No unpublished AM questions or images are included in the application build.

## Edit content

| Location | Purpose |
|---|---|
| `src/content/hardware/memory-and-cache.md` | Editable original lesson prose, headings, persistent reading blocks and concept links |
| `src/content/chapters.json` | Hardware's five-part structure and availability |
| `src/content/concepts.json` | Explicit concept/question associations, evidence and video mappings |
| `src/content/explanations.json` | Original answer reasoning, option text and accessible image descriptions |
| `src/components/` | React learning components and Astro navigation/overview |
| `src/lib/` | TypeScript models, guest storage, derived counts and reading return |
| `scripts/` | Read-only-source importer and release/build checks |
| `public/data/`, `public/questions/` | Generated published-only snapshot and local images |

Concept counts are derived from distinct published question IDs. Add an association only after checking the original image, source mapping and answer. Add a complete explanation whose answer matches the source key; validation rejects missing or inconsistent pilot explanations.

Keep section and reading-block IDs stable when editing prose. The return flow stores the block's viewport offset and clicked concept before leaving, restores after fonts/layout settle, and supports explicit return and browser Back. A pixel-scroll fallback covers removed anchors.

The prose and memory-hierarchy diagram were written for this project. No raw textbook PDF extraction or third-party textbook figure is included. The existing PDF chapter structure informed the outline. Exam images retain original exam attribution and source-page references; these materials are not claimed as original project authorship.

## Guest progress and future accounts

Progress uses the namespaced local key `itpecTextbook:guest:v1`, with stable attempt, question and section IDs. It tracks submitted attempts, latest correctness per question, bookmarks, section completion, last reading position and current practice question. Retrying preserves attempt history. A duplicate attempt ID does not count twice.

Storage-denied/quota failures leave an in-memory learning session available with a clear message. Corrupt or unknown-version data is preserved rather than overwritten. Progress can be downloaded as JSON. File restore and multi-tab simultaneous-edit conflict resolution are not part of this milestone. Clearing browser data or using another device does not retain local progress.

After meaningful activity, a dismissible reminder explains future free account backup. It does not display a nonfunctional sign-in button or force registration. `ProgressSyncAdapter` in `src/lib/models.ts` defines the future interface; there is **no Firebase SDK, Auth setup, Firestore connection, cloud sync or server-side personal data** in this release.

## Free help

Incorrect answers show a relevant free memory-hierarchy lesson from the existing catalog, clearly labeled as an external **Telegram** topic lesson. It is not presented as an exact question solution. No YouTube URL was invented. The component supports a reviewed YouTube mapping with click-to-load, privacy-enhanced embedding when one is supplied. A missing video mapping falls back to a written takeaway and textbook example. The 1% paid course appears only as an optional secondary disclosure.

## Scope

This is the first Hardware learning experience, not a completed 14-chapter textbook. Further Hardware lessons, CET, Firebase accounts/sync and deployment are intentionally deferred. See [milestone report](docs/development/MILESTONE_1.md) for verification and limitations, and [investigation reports](docs/investigation/06_IMPLEMENTATION_ROADMAP.md) for the prior evidence.
