# Chapter 1 source publication

The project owner reviewed the complete local source preview, approved it and explicitly requested publication on `https://itpecfetextbook.pages.dev/`. The approval and exact source fingerprint are recorded in [chapter1-publication.json](editorial/chapter1-publication.json). This release supersedes the previous local-only publication boundary for the Chapter 1 reader content.

## Published content

- The five main Hardware routes now render the complete source edition, printed pages 13–111: 100 physical PDF pages including the unnumbered insertion. Original paragraphs, headings, terminology, formulas, tables, illustrations and source sequence are retained.
- The earlier summarized lesson bodies and 40 simplified replacement SVGs are no longer imported by the public reader. Historical files remain in Git; they are not public page content.
- The existing memory/cache URL renders the original source pages 70–74 as an excerpt. It contains the same source material as that part of the full CPU section.
- All 47 numbered figures, additional illustrations, complex tables and notation use the verified original source renderings. Two hundred deduplicated, lossless WebP assets total **2,989,060 bytes**. The release script compares every decoded RGB pixel against its source PNG before accepting optimization.
- Semantic text and feasible tables reflow in the existing three-column design. Wide original figures and tables scroll within their own containers on phones. Images retain intrinsic dimensions, lazy loading, alt text and full-size links. Printed-page badges stay minimal; no PDF viewer or editorial panels were added.

Public reader content is committed as `src/content/source-hardware/*.html`; `src/content/hardware-source-release.json` records the edition/revision, all source pages and block references, text hashes, annotation references and asset hashes. `public/textbook/hardware/` contains only the exact approved image files. The build works without Python, the PDF or the ignored local dataset.

## Learning and account behavior

Original-source quotes receive the existing yellow exam links as a separate annotation layer. Eleven exact inline anchors connect 21 published questions; all 13 reviewed concepts and 23 Hardware questions remain available through existing practice navigation. The two concepts without exact source phrases remain practice topics without invented textbook words. The bank remains exactly 420 strictly published records and original exam images; IDs, publication flags, explanations and free-video mappings are unchanged.

The six existing section URLs and IDs remain valid. Versioned source block IDs use the `fev1-201504-ch1-r1-` prefix and the existing reading-record format, so the deployed owner-scoped Firestore rules already accept them. No Firebase configuration, data migration or rule widening was needed. Guest checkpoints, Google account migration, offline outboxes, completion/bookmark history and cross-device source restoration use the existing progress system.

Cache practice now returns to either the full CPU source section or the memory/cache source excerpt, according to the actual clicked highlight. Unrelated reading checkpoints are rejected as practice return destinations. Older removed summary blocks retain the existing scroll-position fallback. Shared legacy practice anchors are deduplicated, preserving source text while keeping existing explanation links usable. The progress companion now derives its cache count from the published bank instead of applying a chapter-wide count to that single topic.

## Verification

Completed verification covers:

- **57** application unit/component tests, including approved source hashes, native text integrity, all 100 page references and cross-section concept return.
- **27** production browser tests: full source block order, original figures, mobile bounds, readable source image scale, static reading without JavaScript, exam answers/bookmarks/completion, keyboard navigation, browser Back and source reading restoration.
- **3** account browser scenarios against local demo emulators: Google sign-in and guest migration, two-device/offline/account-switch behavior, and original-source figure/reading checkpoint restoration on another device.
- **12** Firestore security and real SDK synchronization tests against local demo emulators.
- Astro/TypeScript checks and production build validation. The existing bundle-size advisory remains.

The build verifies native source text hashes after rendering, exact source block order, every numbered figure, all 200 approved asset hashes and all 420 unchanged published exam images. Only explicit approved reader routes/assets are allowed. Raw extraction JSON, full-page PDF renders, source comments, crop-review galleries, comparison pages, extra crops and credentials remain excluded. Publication permission for the reader did not turn the whole editorial workspace into a public folder.

The [conversion report](CHAPTER_1_SOURCE_CONVERSION.md) retains the editorial fidelity evidence and remaining semantic-review queue. Complex formulas and raster cells remain visually exact original material; this release does not claim completed accessible transcription of every special-font equation or raster table. It uses the source preview approved by the owner, without silently replacing or correcting textbook content.

## Regeneration and deployment

```powershell
npm.cmd run editorial:validate
npm.cmd run editorial:release
npm.cmd run check
npm.cmd test
npm.cmd run build
npm.cmd run test:e2e
npm.cmd run test:rules
npm.cmd run test:accounts
```

The release generator uses only the fingerprinted local Chapter 1 dataset and the recorded publication approval. It generates the committed public bundle; it does not deploy by itself. Cloudflare Pages builds `main` with Node 24, `npm run build` and `dist`. The source release is committed and pushed to `main`; the delivery message records the resulting commit and verified deployment status. No infrastructure or Firebase deployment is needed.
