# Level selection landing page

Implemented and reviewed on 22 October 2026, on `feature/level-selection-landing`. The new root page is a static three-level bookshelf based on the owner's approved reference. FE opens the existing `/chapters/hardware/` entry; IP and AP display “Coming soon” with disabled buttons and no links. The header retains the existing `fe.` mark and yellow dot. No About ITPEC link, waitlist, extra textbook route or account requirement was added.

## Original assets

All seven PNG attachments were recovered from the owner's previous message and saved without byte changes under `design-references/`. The three selected fronts are:

| Level | Original resource | Native size | Original SHA-256 |
| --- | --- | --- | --- |
| FE | `fe-vol-1.png` — New FE Textbook Vol. 1, IT Fundamentals | 595 × 842 | `e1fa138fe89bfef5faa7a76efcc3a9d9e9d5e67e94296f1799ac56a3145a724f` |
| IP | `ip-main-2017.png` — New IT Passport Examination Preparation Book, main 2017 edition | 595 × 840 | `1aaa2585e8477f12f5a51a7b9f204c5445e80cb852523e546861c478a84c76bd` |
| AP | `ap-vol-1.png` — AP Exam Preparation Book, Volume 1 | 595 × 842 | `041764924b2a32dd503e52cee9093a742b3f38d9a3a8954b9e8b77186ce5bb4a` |

The FE Volume 2, IP syllabus supplement and AP Volume 2 remain available as design resources. The approved reference is stored separately as `landing-reference.png`; it is not used as a flattened webpage image. All six original covers and the reference were visually inspected.

`npm.cmd run prepare:covers` runs the reusable Pillow preparation script. It exports 320-pixel and native-width lossless WebPs for each selected cover, preserving the full artwork and aspect ratio. Native-size decoded RGBA pixels equal the original PNG pixels exactly. All six files total **151,414 bytes**. `src/content/book-covers.json` records original and optimized hashes, dimensions and sizes. Build verification accepts only these six exact approved paths and hashes; unused covers, the reference and other design resources are excluded from the public build.

## Presentation and performance

Astro renders semantic HTML with the existing Newsreader and IBM Plex Sans fonts and design tokens. A separate landing stylesheet keeps the FE reader's presentation intact. The centered heading, warm ivory/beige lighting and FE–IP–AP order follow the approved reference. The reference's About ITPEC button is deliberately omitted as directed in the brief.

`BookMockup.astro` places the supplied image on a CSS front face. Separate spine, back-board and page-edge layers use CSS perspective and `translateZ`, with restrained binding highlights, directional lighting and contact shadows. Images are never cropped or stretched to a shared aspect ratio; the IP book retains its distinct 595:840 proportions. FE has a gentle hover lift and a visible keyboard focus ring. IP and AP are desaturated and muted, while their availability labels remain readable. Reduced motion removes movement. No 3D library, React hydration, Firebase startup or client JavaScript is loaded on the landing page.

Desktop widths from 1024 pixels show three books in a single row. Tablet shows FE first with the two unavailable levels below. Mobile uses one column with a large FE cover and action first. Seven viewport sizes were rendered and reviewed: **320, 375, 414, 768, 1024, 1440 and 1536 pixels**. A visual comparison prompted tighter desktop hero spacing so that the primary action sits within the reference-sized viewport.

Measured Chromium WCAG contrast ratios: muted copy against the darkest background 4.92:1; main text 11.43:1; available badge 7.38:1; primary action 15.91:1. Keyboard operation, visible focus, alt text, disabled controls, no-JavaScript access and reduced motion were checked.

## Routes and preservation

Only `/` changes from the duplicate Chapter 1 entry into level selection. Both FE book and Open Textbook action link to `/chapters/hardware/`. Existing reader, chapter, subsection, practice and progress URLs remain intact. The existing reader logo already links to `/`, so it now returns to level selection without changing the reader layout.

The source release validator now checks the five existing section routes plus `/chapters/hardware/`; the root route is separately validated as static level selection. No source validation was relaxed on the remaining readers. The closed publication allowlist was extended with the six explicitly approved cover paths, retaining its rejection of raw editorial data and unknown assets. Sitemap and canonical settings already include the root and existing textbook entry.

Chapter 1 source text, all 47 numbered original figures, all 81 crop-first repairs, formulas, tables, 420 published question records and images, concept mappings, explanations and videos remain unchanged. Guest progress, Google Authentication, Firestore synchronization, Firebase configuration and security rules were not modified. No old ITPEC Practice repository or backend infrastructure was touched.

Tests verify FE entry, browser Back to level selection, the existing reader logo returning home, answering/bookmarking before and after home navigation, source deep links, and exact saved reading-checkpoint restoration. Visiting the static landing page does not initialize or reset the progress store.

## Executed checks

| Command / check | Result |
| --- | --- |
| `python scripts/prepare_book_covers.py` | Three selected originals, six lossless responsive variants; decoded pixel checks passed |
| `npm.cmd run check` | 0 errors, warnings or hints |
| `npm.cmd test` | 69 tests passed across 15 files |
| `npm.cmd run test:e2e -- --output=.local/landing/e2e` | 49 tests passed, including 39 existing FE checks and 10 new landing checks |
| `npm.cmd run test:e2e -- tests/e2e/landing.spec.ts --output=.local/landing/final-e2e` | All 10 landing checks passed again after final CSS spacing refinements; seven refreshed viewport screenshots |
| `npm.cmd run test:e2e -- tests/e2e/landing.spec.ts -g 'returning home' --output=.local/landing/checkpoint-e2e` | Additional home/checkpoint/Back regression passed |
| `npm.cmd run build` | 24 static pages; source, question, asset, landing structure and publication-boundary checks passed |

Firebase emulator suites were not rerun for this milestone because authentication, account synchronization, progress schemas and rules were unchanged. Existing browser tests exercise the complete guest learning flow. Production retains the previously published FE reader until the owner approves this separate landing milestone.

## Review locally

Run `npm.cmd run preview -- --port 4344` after the production build and open `http://127.0.0.1:4344/`. FE enters the existing chapter. Stop the server before running Playwright, because Astro permits one preview server per workspace.

Final screenshot examples:

- Desktop/reference size: `.local/landing/final-e2e/landing-level-bookshelf-or-23b54-responsive-layout-at-1536px/landing-1536.png`
- Desktop: `.local/landing/final-e2e/landing-level-bookshelf-or-5fae0-responsive-layout-at-1440px/landing-1440.png`
- Small desktop: `.local/landing/final-e2e/landing-level-bookshelf-or-5faa1-responsive-layout-at-1024px/landing-1024.png`
- Tablet: `.local/landing/final-e2e/landing-level-bookshelf-or-668f0--responsive-layout-at-768px/landing-768.png`
- Mobile: `.local/landing/final-e2e/landing-level-bookshelf-or-2c990--responsive-layout-at-375px/landing-375.png`

The result is ready for owner review. This milestone does not merge into `main`, publish to production, or begin IP/AP textbook development.
