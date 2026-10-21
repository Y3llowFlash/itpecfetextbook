# ITPEC FE Textbook

A free, static reading and practice application. Chapter 1 publishes the owner-approved source edition: complete original text, illustrations, tables and notation across printed pages 13–111. The source edition replaces the summarized public lessons. Thirteen reviewed concepts link 23 published questions with explanations. Guest learning works locally; optional Google accounts back up progress.

Built with **Astro, React and TypeScript**. Cloudflare Pages publishes the validated static `dist/` output from `main`.

The [source publication report](docs/development/CHAPTER_1_SOURCE_PUBLICATION.md) describes the approved release and validation. Follow the [editorial workflow](docs/development/editorial/README.md) to regenerate source content or open the private comparison tools.

## Run locally

Requires Node.js 24 or later and npm.

```powershell
npm.cmd ci
npm.cmd run dev
```

Open `http://127.0.0.1:4321/`. On shells without PowerShell's script restriction, `npm` can be used instead of `npm.cmd`.

Useful routes:

- `/chapters/hardware/` — chapter structure and the available lesson.
- `/chapters/hardware/basic-configuration/` — computer history and the five major units.
- `/chapters/hardware/data-representation/` — bits, bases, character/numeric formats, errors and shifts.
- `/chapters/hardware/cpu-and-main-memory/` — CPU, memory, addressing, interrupts, circuits and high-speed techniques.
- `/chapters/hardware/auxiliary-storage/` — magnetic, optical and semiconductor storage.
- `/chapters/hardware/input-output/` — input/output devices, control methods and interfaces.
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
npm.cmd run test:rules
npm.cmd run test:accounts
npm.cmd run preview
```

`check` runs Astro diagnostics and TypeScript. Unit/component tests cover publication filtering, duplicates, answer explanations, persistence failures, navigation and reading restoration. End-to-end tests run against the production build in a fresh headless browser, including 320, 375, 414, 768 and 1280 pixel viewports. The build validates data/assets before rendering and verifies the final public output afterward. Preview serves the production `dist/` directory, normally on port 4321. E2E uses its own temporary preview on port 4322 and stops it on completion.

Emulator tests require Java 21 or newer. `test:rules` runs security rules and real SDK synchronization tests. `test:accounts` builds a separate demo application under ignored `.local/account-dist/` and tests Google sign-in, migration, two-device/offline sync and sign-out in Chromium. It never replaces the production `dist/`. Both commands start/stop local Auth and Firestore emulators using `demo-itpec-textbook`; test accounts and records never reach production. The popup test permits Google's static popup JavaScript while blocking production Auth/Firestore APIs.

Astro CLI telemetry is disabled by the local wrapper. Firebase's public web configuration defaults to the verified `itpec-textbook` app. Optional Astro `PUBLIC_FIREBASE_*` overrides are listed in `.env.example`; never put Admin credentials in public environment variables. Production builds always target `itpec-textbook`. `PUBLIC_FIREBASE_USE_EMULATORS=true` selects only `demo-itpec-textbook`, and runtime use is restricted to loopback hosts. Analytics runs in supported production browsers and is skipped for development, loopback previews and emulator builds. No learning records are sent as custom Analytics events.

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

Current snapshot: **420 published questions** (300 A + 100 dated B + 20 sample B); **160 unpublished records excluded**. There are exactly 420 public question images. All included IDs are listed in the import manifest. Chapter 1 exposes 23 directly reviewed Hardware questions across 13 concepts; the retained cache-memory set is:

| Original ID | Source | Answer |
|---|---|---|
| `2024A-A-Q009` | 2024 Autumn Subject A, Q9 | b |
| `2025S-A-Q010` | 2025 Spring Subject A, Q10 | c |
| `2026S-A-Q010` | 2026 Spring Subject A, Q10 | d |

The [Chapter 1 report](docs/development/CHAPTER_1_HARDWARE.md) lists all 23 linked IDs. Other published records remain static release data for later reviewed mappings. They are not given invented concepts or explanations. No unpublished AM questions or images are included in the application build.

## Edit content

| Location | Purpose |
|---|---|
| `src/content/source-hardware/*.html` | Approved complete source text, semantic tables, original visuals and versioned reading blocks |
| `src/content/hardware-source-release.json` | Source edition, page/block manifest and exact approved asset hashes |
| `public/textbook/hardware/` | Optimized lossless source illustrations and notation |
| `src/content/hardware/*.md` | Historical authored fallback; no longer rendered by the public reader |
| `src/content/hardware-lessons.json` | Stable lesson IDs/routes, ordered subsection headings and verified printed-page ranges |
| `src/content/textbook-editions.json` | Source volume, edition and PDF fingerprint; source bytes are not published |
| `src/content/chapters.json` | Hardware's five-part structure and availability |
| `src/content/concepts.json` | Explicit concept/question associations, evidence and video mappings |
| `src/content/explanations.json` | Original answer reasoning, option text and accessible image descriptions |
| `src/components/` | React learning components and Astro navigation/overview |
| `src/lib/` | TypeScript models, guest storage, derived counts and reading return |
| `scripts/` | Read-only-source importer and release/build checks |
| `public/data/`, `public/questions/` | Generated published-only snapshot and local images |

Concept counts are derived from distinct published question IDs. Add an association only after checking the original image, source mapping and answer. Add a complete explanation whose answer matches the source key; validation rejects missing or inconsistent pilot explanations.

Minimal badges show **printed textbook page numbers**, with volume/edition on the section badge. References are checked against committed footer-label evidence; the PDF has an unnumbered insertion, so one global offset is unsafe. To reverify against the read-only source, run `python scripts/verify-textbook-source.py` (requires PyMuPDF). Ordinary builds need neither Python nor the old repository. Only the approved rendered source content and listed assets enter public output; raw extraction, annotation metadata and review galleries stay local.

Keep section and reading-block IDs stable when editing prose. The return flow stores the block's viewport offset and clicked concept before leaving, restores after fonts/layout settle, and supports explicit return and browser Back. A pixel-scroll fallback covers removed anchors.

The current reader publishes the original textbook prose and illustrations with the owner's explicit approval. These source materials and past-exam images are attributed to their originals and are not claimed as project authorship. The source dataset and comparison tools remain available locally for editorial verification.

The earlier 40 authored SVG replacements and summary lessons remain historical repository resources; the public reader does not import them. The published source reader contains all 47 numbered figures, additional illustrations, original tables and notation. Its 200 lossless WebPs total approximately 3 MB and load lazily. Existing lesson routes and section IDs remain stable; source reading-block IDs include the release revision.

## Guest progress and optional accounts

Progress uses the namespaced local key `itpecTextbook:guest:v1`, with stable attempt, question and section IDs. It tracks submitted attempts, latest correctness per question, bookmarks, section completion, last reading position and current practice question. Retrying preserves attempt history. A duplicate attempt ID does not count twice.

Storage-denied/quota failures leave an in-memory learning session available with a clear message. Corrupt or unknown-version data is preserved rather than overwritten. Progress can be downloaded as JSON. File restore is not implemented. Clearing browser data or using another device does not retain unsynced local progress.

Guests never use Anonymous Authentication, create cloud records or read/write Firestore. Google sign-in is voluntary from `/progress/#account` or a dismissible prompt after meaningful learning activity. Auth/Firestore code loads only after explicit sign-in or restoration of a previously chosen account.

Account progress uses `itpecTextbook:account:{uid}:v1` locally and `users/{uid}/progress/{recordId}` in Firestore. Guest migration merges with existing account history and consumes the guest source rather than copying it into future accounts. A durable ownership claim protects interrupted migrations. Attempts are immutable records keyed by attempt ID; bookmarks and completed sections retain removal tombstones, resolving conflicts by logical clock and device ID. Reading checkpoints synchronize periodically; raw scroll events only update local storage. Practice navigation and reminder dismissal remain device-local.

Changes debounce for 2.5 seconds; foreground polling uses an incremental server-timestamp/document-ID cursor every minute and pauses while hidden. Transactions upload only pending records in chunks of 100, preserve newer cloud state, and make retries idempotent. Offline/network/quota errors retain the local outbox and show sync status. Retry backoff caps at five minutes; `Sync now` and reconnect/focus also retry. Sign-out immediately clears the active account view and reading-return pointer across tabs. Synced caches are cleared; unsynced data remains isolated under its original UID until that account returns.

See [Firebase security and integration report](docs/development/FIREBASE_INTEGRATION.md) for the audit, deployed rules, conflict policy, test coverage and limitations.

## Free help

Incorrect answers show a relevant free memory-hierarchy lesson from the existing catalog, clearly labeled as an external **Telegram** topic lesson. It is not presented as an exact question solution. No YouTube URL was invented. The component supports a reviewed YouTube mapping with click-to-load, privacy-enhanced embedding when one is supplied. A missing video mapping falls back to a written takeaway and textbook example. The 1% paid course appears only as an optional secondary disclosure.

## Scope

Only Chapter 1 is published as the approved source edition; other chapters and CET remain deferred. Complex notation and raster tables retain original pixels, with the semantic-review queue still available locally. Cloudflare Pages is connected to `main`, using Node 24, `npm run build` and `dist`. A push deploys automatically after production validation. Earlier fallback and local-only milestone reports are historical records.
