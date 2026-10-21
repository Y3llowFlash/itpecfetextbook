# Chapter 1 reading and navigation refinement

Baseline: `0f243ef`. Review branch: `feature/chapter1-reading-navigation`.
Scope: Chapter 1 interface and navigation only. Production remains on `main`; this branch is prepared for review before merging.

Implementation commit: `cc54ba36c584d29b48e84cfe98c24370a2b6d3c9`.
Verified preview: https://f38e2dc9.itpecfetextbook.pages.dev/ (branch alias: https://feature-chapter1-reading-nav.itpecfetextbook.pages.dev/).
No automatic preview appeared after the push, so the verified production build was uploaded with Wrangler using the feature branch explicitly. Cloudflare confirmed environment `preview`, that implementation commit, and successful deployment. The production deployment remains `0ae0ac1b` at baseline `0f243ef`.

## Reading experience

The home and Chapter 1 routes now show `CHAPTER 1`, `Hardware`, and the original content beginning on printed page 13. The duplicate landing introduction, Start button, inline contents overview, separate Memory & Cache entry, repeated source-edition introduction, and header/footer slogans have been removed. Section routes begin with their original source heading and a small chapter breadcrumb. Printed page badges and figure captions use `p. …`; the edition remains identified at the end of each section.

The warm background, typefaces, restrained yellow highlights, source colors, three-column desktop layout, and existing question interface remain. Figures retain their original pixels and full-size links. Tables and large figures scroll within the reading column. On mobile and tablet, native Contents and Study tools disclosures preserve reading space; the study panel starts closed below 78rem.

## Source contents and navigation

`src/content/hardware-toc.json` contains exactly 52 numbered source headings: 5 main sections, 19 subsections, and 28 deeper entries. Original names, numbering, order, printed references, and source block IDs come from the existing release manifest. Main sections begin on printed pages 13, 20, 46, 78, and 92. Original numbering uses forms such as `3-5-1`; no replacement outline was invented.

Generate navigation metadata with `npm run generate:reader-toc`. The normal production build runs the same generator in `--check` mode and rejects stale metadata. Neither operation edits source HTML or images.

Native fragment links provide browser history and non-JavaScript navigation. A passive, animation-frame scroll handler updates `aria-current="location"` and the study context without adding history entries. Ancestor section groups expand without opening the outer mobile Contents disclosure. Selecting a subsection closes mobile Contents and focuses its original heading. Reader headings use one scroll offset, avoiding the inherited combination of document padding and heading margin. Initial fragment positioning waits for the existing fonts; saved checkpoints and history restoration retain their own restoration behavior.

## Memory & Cache compatibility

The primary reading location is now `3-5-1 High Speed Memory Access`, printed page 70:

`/chapters/hardware/cpu-and-main-memory/#fev1-201504-ch1-r1-pdf-075-b005-l00-text-0`

The old `/chapters/hardware/memory-and-cache/` route replaces itself with that location, preserving query parameters and valid original source fragments. Without JavaScript it exposes an ordinary link to the canonical subsection. It is excluded from the primary contents and sitemap.

Historical reading records are normalized when read, preserving source block IDs and exact offsets where available. Older authored-guide anchors fall back to the real source heading. Existing records are not destructively rewritten. The old completion ID `fe-v1-ch01-memory-cache` represents completion of this subsection; it does not mark the entire CPU section complete. Completed subsections remain visible on Progress. The legacy schema and Firestore allowlist remain intact.

The existing three cache questions, answers, explanations, videos, bookmarks, question IDs, and evidence mappings remain unchanged. Only the cache concept's reading destination was updated. Historical authored lesson files remain in the repository.

## Contextual study tools

The panel follows the current numbered source heading and shows its number, title, page, completion, and saved resume link. Related questions are calculated from the actual published question mappings for that heading and its descendants, with distinct question counts. Related bookmarks link through a concept that actually contains that question. Existing mapped video URLs appear only for relevant headings. Empty question/video/bookmark groups are omitted. The Progress page has no fixed cache recommendation; the Practice index groups available questions under original source sections.

Context data is computed during static generation. Scrolling changes local interface state only. Completion, attempts, bookmarks, reading checkpoints, and account sync reuse the existing stores and synchronization path; no new Firestore reads, listeners, services, dependencies, billing settings, or deployed rules were added.

## Preservation and publication checks

The source release JSON, all six immutable source HTML fragments, all 200 approved source assets, all 420 published question records and images, answer explanations, publication flags, Firebase configuration, and Firestore rules are unchanged from the baseline. The five main readers still cover all 100 physical source pages and all 47 numbered figures. Build verification checks every source block and native text hash on the five readers and both chapter entry routes, checks approved image hashes, and rejects source/editorial material outside the existing publication boundary. The compatibility route is checked separately to prevent another duplicate reader.

## Executed verification

Executed on 2026-10-21:

| Command | Result |
| --- | --- |
| `npm run check` | 0 errors, warnings, or hints |
| `npm test` | 63 passed, 13 files |
| `npm run test:e2e -- --output=.local/reading-refinement-e2e` | 33 passed |
| `npm run test:rules` | 12 passed against local Auth/Firestore emulators |
| `npm run test:accounts` | 3 passed against local Auth/Firestore emulators |
| `npm run build` | 24 static pages; source, question, asset, and publication checks passed |
| `git diff --check` | Passed |
| `node scripts/verify-reading-preview.mjs https://f38e2dc9.itpecfetextbook.pages.dev` | Passed: 7 readers, all 200 source hashes, all source text hashes, published bank, 52 contents links, guest practice and 4 viewport sizes; no browser errors |

Browser coverage includes original hierarchy and page references, section/subsection links, scrolling selection, native Back/Forward, keyboard disclosure/link/focus behavior, legacy cache URLs and historical checkpoints, related question/video counts, blocked storage, guest persistence, exact source-figure offsets, question answers/explanations/navigation/zoom, and non-JavaScript readers. Layout checks cover 320, 375, 414, 768, 1024, 1280, and 1440px across the suite and preview verification. Account scenarios cover Google popup sign-in, guest migration, legacy subsection completion across devices, offline retry, multiple tabs, account isolation, and exact cross-device source-figure restoration.

Screenshots and traces are local, outside the public build:

- `.local/reading-refinement-e2e/`: browser regression screenshots.
- `test-results/accounts/`: emulator account screenshots.
- `.local/reading-review/`: hosted preview desktop/mobile/tablet screenshots and `preview-check.json` recording the verified URL and checks.

Hosted screenshots were visually reviewed: `desktop.png`, `cache-desktop.png`, `mobile.png`, `mobile-tools.png`, and `tablet.png` in `.local/reading-review/`. Original figures, readable source text, current-section selection, and the collapsed mobile controls were retained. The implementation is ready for review and merge; merging and production publication remain a separate step.

Run the hosted preview verification after Pages finishes building the branch:

```powershell
node scripts/verify-reading-preview.mjs https://DEPLOYMENT.itpecfetextbook.pages.dev
```

This verifies seven source reader URLs, all 200 image hashes, the unchanged published question bank, original native text hashes, the cache redirect/context, guest answer/bookmark/return behavior, and responsive disclosures. It writes local review artifacts. Real Google credentials are not used by this automated preview check; account behavior is exercised with the emulators. Existing Firebase authorized-domain settings are unchanged. Vite still reports the existing optional Firebase bundle size warning; it does not fail the build.

No merge, production deployment, Firebase rule deployment, Chapter 2 work, CET implementation, or changes to the old Practice project are included.

## Follow-up: word-by-word prose on the unnumbered insertion

The owner reported the serial-transmission explanation displaying one word per paragraph. The source PDF's physical page 83 stores each prose word as a separate PDF text object, often with a different PDF block ID. The conversion retained all characters and coordinates but rendered these 235 objects as independent HTML paragraphs. The previous text/hash and image checks did not detect this incorrect paragraph structure.

Visual comparison with the PDF confirms five prose paragraphs: I²C, PCI Express, SPI, UART, and the concluding paragraph. `scripts/generate_prose_repairs.py` verifies the original words and bounding boxes, groups the reviewed prose by baseline positions and paragraph gaps, and emits `src/content/hardware-prose-repairs.json`. Its five groups contain 50, 56, 48, 57, and 24 original word objects. The helper rejects separate columns and non-prose objects. A scan of the 100 source pages for consecutive runs of at least ten one/two-word prose blocks found only this page; short diagram/table labels are not automatically joined.

The static reader renderer uses that metadata to put the original words inside five semantic paragraphs. Every original word ID, reading checkpoint anchor, source block attribute, and word remains present. Source HTML inputs, release hashes, figures, approved assets, questions, and account data are unchanged. Production builds need only committed metadata; they do not need the PDF or local editorial workspace. Build verification now checks both native text integrity and this paragraph structure, so merely preserving all words is insufficient to pass.

Local verification after the fix: `npm run check` passed with no diagnostics; `npm test` passed 64 tests; the full browser suite passed 36 tests; `python -m unittest discover -s tests -p test_editorial_converter.py` passed 8 tests; `python scripts/generate_prose_repairs.py --check` and `npm run build` passed. New browser tests check normal paragraph wrapping at 375, 1024, and 1440px and exact restoration of original word-level reading checkpoints. Desktop and mobile screenshots were visually compared against the source. No Firebase schema, rule, SDK or synchronization code changed in this repair.

The review branch alias is https://feature-chapter1-reading-nav.itpecfetextbook.pages.dev/. Hosted checks also verify the five paragraph text hashes and capture `uart-desktop.png`, `uart-mobile.png`, and tablet variants under `.local/reading-review/`. The earlier immutable preview URL above records the initial refinement before this follow-up.
