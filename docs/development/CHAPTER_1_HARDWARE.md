# Chapter 1: Hardware completion

Date: **2026-10-21**. Scope: the five original Hardware sections, their 19 subsections and relevant deeper topics, plus the existing cache focus lesson. No other chapter or CET was implemented.

## Completed sections and printed references

Source: **New FE Textbook Vol.1 — IT Fundamentals, First Edition, April 2015**. Metadata is committed in `src/content/textbook-editions.json`. Its fingerprint and extracted printed footer labels are recorded in [page evidence](evidence/hardware-printed-pages.json). The read-only verifier checks the colophon and all printed labels 13–112; 112 is retained only as the exercise-boundary evidence, not published as an exercise lesson.

| Main section / route | Printed pages | Completed source subsections |
|---|---|---|
| Basic Configuration of Computers / `basic-configuration` | 13–19 | History of Computers (13–16); Five Major Units of Computers (16–19) |
| Data Representation in Computers / `data-representation` | 20–45 | Data Representation (20–23); Radix and Radix Conversion (23–28); Representation Form of Data (28–45) |
| Central Processing Unit and Main Memory Unit / `cpu-and-main-memory` | 46–77 | Configuration of CPU (46–49); Main Memory Configuration (49–52); Instruction and Addressing (52–61); Circuit Configuration of ALU (61–70); High Speed Technologies (70–77) |
| Auxiliary Storage / `auxiliary-storage` | 78–91 | Magnetic Disk (78–86); Optical Disc (86–88); Semiconductor Memory (89–90); Other Auxiliary Storage Media and Drives (90–91) |
| Input/Output Unit / `input-output` | 92–111 | Input Unit (92–97); Output Unit (97–103); Other Input/Output Units (103–104); Input/Output Control Methods (104–105); Input/Output Interfaces (105–111) |
| Retained Memory hierarchy & cache / `memory-and-cache` | 70–74 | Existing lesson, ID `fe-v1-ch01-memory-cache`, anchors and three-question practice preserved |

Ranges overlap when one printed page contains the end of one subsection and the start of another. Printed page 70 is physical PDF page 75, but printed page 78 is PDF page 84. Physical PDF page 83 is an unnumbered I2C insertion, so a global page offset would produce incorrect references.

The five main lessons preserve the original deeper sequence: character/numeric data, errors and shifts; memory devices/components/expansion; instruction types/execution/addressing/interrupts; logic/arithmetic circuits; memory/processor acceleration; disk capacity/recording/access; keyboard/paper/pointing/other input; display/printer/other output; and interface classification/types/drivers. There are 47 source-mapped headings across the new lessons. With four mapped headings in the old focus lesson and six lesson headers, the reading pages contain 57 subtle reference badges. Metadata contains the individual ranges. No source viewers, expandable panels, PDF links or page-search UI was added.

## Question mappings and explanations

All selected images were visually reviewed, and **all 23 answer letters were checked against their original answer PDFs**. IDs, exam dates, options, images and provenance remain unchanged. Only `is_published === true` records qualify. No unpublished image or record was introduced. Counts use distinct eligible IDs, not broad chapter associations.

| Reviewed concept | Published question IDs |
|---|---|
| Cache memory | `2024A-A-Q009`, `2025S-A-Q010`, `2026S-A-Q010` |
| Radix conversion | `2024S-A-Q001`, `2025S-A-Q002`, `2026S-A-Q002` |
| Floating-point representation | `2025A-A-Q001` |
| Signed integers and shifts | `2025A-A-Q002` |
| Bit masks | `2025S-A-Q001` |
| CPU registers | `2025S-A-Q009`, `2026S-A-Q009` |
| Interrupt priority | `2025A-A-Q008` |
| Bus transfer rate | `2026S-A-Q011` |
| Logic gates and equivalent circuits | `2024A-A-Q001`, `2024A-A-Q016`, `2024S-A-Q016`, `2025A-A-Q016`, `2026S-A-Q017` |
| Disk access time | `2024S-A-Q009`, `2025A-A-Q009` |
| Disk defragmentation | `2024A-A-Q010` |
| USB interfaces | `2024S-A-Q010` |
| 3D printing | `2025A-A-Q010` |

Added **20 explanations**, retaining the original three. Worked solutions include positional fractional weights, binary32 sign/exponent/fraction decoding, power-of-two algebra, the four-clock bus-transfer calculation, both complete HDD access calculations, and a nested-interrupt timeline. Circuit solutions derive the MUX's XOR function, a three-input NAND using De Morgan's law, and the complemented-input Boolean circuit. Distractor misconceptions are explained where the source supports them; accessible descriptions preserve diagram connections and timing events.

Relevant existing free Telegram resources are reused: memory/registers (`/101`), adder/logic fundamentals (`/64`) and select-line/MUX (`/178`) from the existing catalog. These are labeled topic help, not invented YouTube videos or asserted exact recordings of question solutions. Concepts without verified video mappings show a written takeaway and a link back to the relevant lesson, rather than to an unrelated cache example.

The snapshot remains **420 published questions and 420 original approved images**, with the previous 160 unpublished records excluded. Only the 23 reviewed Hardware questions receive public practice associations in this release. Foundational history/five-unit topics have no direct published-question associations and are not falsely highlighted.

## Original teaching material

Authored five substantive Markdown lessons. The prose is original explanatory writing, not raw source extraction. Examples, formulas and comparison tables cover the relevant source topics while distinguishing historical technologies from general engineering principles.

Four new original visual explanations are built from semantic HTML: the five-unit data path, IEEE binary32 fields, the fetch/decode/execute path and a pipeline timing table. The prior memory-hierarchy diagram remains. Further tables cover truth values, signed formats, register roles, addressing modes, memory devices, optical storage, input recognition, printing and I/O control. These have readable mobile layouts with internally scrolling tables where necessary. No protected source prose or textbook figures were copied into public assets.

## Navigation and progress

All five navigation entries now open complete lessons. The chapter page has a reviewed concept-practice index. Each lesson has an in-page outline, appropriate practice links, completion control and previous/next navigation. Three-column desktop styling, the study companion and mobile reader remain intact.

The old cache ID and anchors are unchanged. The main section IDs remain `fe-v1-ch01-s01` through `s05`. Reading validation now checks exact allowed route/section-ID pairs. Reading return uses the actual route, offset, anchor and clicked concept; cross-section session pointers cannot redirect a reader to an unrelated lesson. The dashboard includes all five main completion states and routes new bookmarks to their actual concept practice.

Google accounts retain guest migration, UID isolation, immutable attempt IDs, tombstones and offline retry. Browser testing found an account-restoration race that could clear an answer chosen immediately after navigation. Answer controls now wait for an explicitly restored account to settle, avoiding an assignment to the wrong local identity; guest reading and practice remain available without Firebase.

## Firebase deployment, separate from the website release

The existing Firestore rules allowed reading checkpoints only for the cache route. Extended this to the six exact verified route/section pairs. Unknown paths, external paths, mismatched IDs, Anonymous tokens and cross-user access remain denied. No owner-only requirement was relaxed.

**Rules were deployed separately after 12 emulator tests passed**, using only `--only firestore:rules --project itpec-textbook`. Live ruleset: `5ff273ba-fd72-4047-b59a-9bd576eb3671`. A subsequent read-only audit confirmed exact agreement with the tested local file. Added only the verified `itpecfetextbook.pages.dev` domain to the existing Google Auth authorized-domain list, so the already-deployed preview can use Google sign-in. No production student accounts or test progress were created. Billing remains disabled; no paid services or infrastructure were introduced.

## Verification executed

- Astro/TypeScript: no errors, warnings or hints.
- Unit/component tests: **47 passing**, including printed labels, source edition, 19-subsection structure, published-only counts, numerical/circuit solutions and route safety; existing guest/sync tests also pass.
- Firebase rules/SDK emulator tests: **12 passing**, including six valid reading routes, rejected route/ID combinations and two-device new-section progress.
- Production Chromium tests: **19 passing**, including five new 320px lesson layouts, badges, navigation, wrong/correct answers, bookmarks, completion, exact return, browser Back, static HTML and all original regressions.
- Account Chromium scenarios: **3 passing**, including guest migration, offline recovery, cross-tab sign-out, account switching and new-section reading/bookmark/completion on another device.
- Production build: **23 static HTML routes**, plus sitemap; validates all 420 published records and image hashes, every reviewed mapping/explanation, each source heading and badge, and exclusion of PDF/editorial/credential/emulator material.
- Visual review: inspected mobile/desktop CPU and I/O reading layouts, typography, reference badges, wrapped navigation and truth tables. Automated screenshots cover all five main sections at 320px; existing tests cover other viewport sizes.

The optional account vendor bundle retains its advisory Vite size warning; this does not block the build. Tests use Chromium rather than physical Safari/Firefox devices. Rules and account tests use the separate demo emulators, with production Auth/Firestore APIs blocked in browser tests. A transient emulator startup interruption and an Auth-restoration race were resolved before the passing runs.

## Editorial and mapping gaps

- 3D printing/fused filament fabrication is a modern exam extension. No precise occurrence in this 2015 edition was established, so no dedicated printed-page reference was fabricated for that extension. Its general output/printer context has a verified section reference.
- The stack-pointer exam association is taught alongside register roles; the source's CPU register list does not establish a precise dedicated SP paragraph. No separate SP page badge is invented.
- The unnumbered I2C insertion is recorded in source evidence and is not assigned a printed page or copied into this chapter.
- Original exam-reading checklists and recaps in the cache focus lesson are editorial teaching material, not source subsections, so they receive no fabricated individual page mapping.
- Existing free-video links are catalog-backed topic resources. Many concepts have no verified matching video, so written help remains the fallback. No additional videos were invented.
- The textbook's protected exercise pages/CET are not reproduced or implemented. Other chapters remain outside scope.

## Cloudflare release verification

Read-only Pages API inspection confirmed GitHub `Y3llowFlash/itpecfetextbook`, production branch **main**, automatic deployments enabled, root directory empty, build command **npm run build**, output **dist**, and **Node 24**. The only configured production variable name was `NODE_VERSION`; emulator mode is not enabled. Existing successful production deployment was commit `fb53d14` before this release.

The cached Wrangler login had expired; normal Wrangler CLI authentication refreshed it and enabled the read-only project audit. No Pages settings were changed. Release consists of the requested commit/push to main, allowing the existing Git integration to build. The final completion message records the resulting commit and Cloudflare deployment state after the push. Direct preview HTTP checks from this environment experienced connection resets; deployment status is independently available through Cloudflare's authenticated API.

Before pushing, `npm run build` checked publication eligibility and the actual output inventory. Raw source PDFs, extraction text, visual review crops, temporary authoring files and OAuth/session data remain outside public output and Git. The old repository was used read-only.
