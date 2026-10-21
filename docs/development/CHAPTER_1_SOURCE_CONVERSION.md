# Chapter 1 faithful source conversion

**Publication update:** the owner subsequently approved this preview and requested publication. The [source publication report](CHAPTER_1_SOURCE_PUBLICATION.md) describes the resulting release. The local-only boundary below records the previous phase, not the current publication status.

Verified 21 October 2026. This report supersedes earlier statements that a summarized, independently authored Hardware chapter constituted a completed textbook conversion. Those lessons and their replacement diagrams remain the public fallback. The source edition is a separate, unpublished local editorial conversion.

## Outcome and scope

The reusable converter and local source reader cover printed pages **13–111**, physical PDF pages **18–117**: **99 numbered pages plus the unnumbered insertion at PDF 83**. All five main divisions, 19 numbered source subsections and deeper extracted headings are retained in the source sequence. The original terminology, errors and legacy statements are preserved; no corrective paraphrases or new textbook paragraphs were substituted.

Source: *New FE Textbook, Vol. 1, IT Fundamentals*, First Edition, April 2015, `D:\ITPEC Old Questions\database\raw\FE Vol 1.pdf`. SHA-256: `1e1f2ec364a52751333b1e3ab2a2f2548e9345cd06a7c300b8a7075fb51c3d1b`. The source file and old repository were read-only inputs. No question bank, publication flags, Firebase configuration or security rules were changed.

| Identified material | Result |
|---|---:|
| Physical source pages and side-by-side comparisons | 100 each |
| Original source text lines / source characters, including whitespace | 5,066 / 156,493 |
| Native paragraph blocks | 681 |
| Native list items / headings | 214 / 160 |
| Inventoried figure regions | 77, including all 47 numbered figures |
| Inventoried table regions | 29: 26 source grids and 3 curated raster/unruled tables |
| Original table cell crops | 437 |
| Inventoried formula/notation regions | 152 |
| Additional image-fragment / vector regions | 24 / 20 |
| Original image objects accounted for | 1,986 |
| Original vector objects inventoried | 4,929 |
| Existing PDF highlights/comments/underlines retained separately | 407 |

Counts distinguish source-region inventory from responsive assemblies. Overlaps are displayed together rather than repeating labels. The reader has 78 figure blocks, 15 table blocks, 91 formula blocks and 15 additional visual blocks, totaling 199 visual assemblies. Some tables/formulas belong inside numbered figures. Formula-region counts are not a count of individual algebraic statements. Paragraphs embedded in original visuals remain in those source regions and their exact character ranges; 681 is the count of native paragraph blocks, not a claim that all source paragraphs have already been independently classified.

## Deliverables and opening the preview

The [workflow](editorial/README.md) documents the converter, dependencies, schema, controls and reproduction commands. The [interactive plan](editorial/INTERACTIVE_INTEGRATION.md) describes the working source-quote annotation layer and the future approved-edition adapter. [Crop seeds](editorial/chapter1-regions.json) and [sanitized audit metadata](editorial/chapter1-audit.json) contain provenance and counts without reproduced book prose or figures.

From `D:\ITPEC_FE_TEXTBOOK`, run:

```powershell
npm.cmd run editorial:preview
```

Open **http://127.0.0.1:4340/**. The complete generated edition already exists locally at `.local/editorial/chapter-1/`. Its entry page links the source reader, original crop gallery, all 100 PDF-versus-digital comparisons and the detailed validation/review queue. Source comments can be reviewed at `/source-annotations.html`. Use `npm.cmd run editorial:convert` and `npm.cmd run editorial:validate` to regenerate and verify it against the original PDF.

The central reader uses native responsive paragraphs, headings and lists; feasible grids use semantic HTML. Complex source figures and spatial/special-font notation use exact original rendered PNGs with source associations and full-resolution links. On small screens, wide figures and tables scroll inside their own containers to retain label size. The PDF page image appears only in the separate editorial comparison view, not as the central reading experience. Original source crops include the actual vacuum-tube photographs and technical illustrations, rather than substitute drawings.

## Verification and fidelity

Automated source verification passed for all 100 pages:

- Exact fresh extraction of every source character, font and position; each source glyph belongs to exactly one digital block. Raw source text is also independently hashed per page.
- Native rendered HTML retains the original words; only layout whitespace reflows. Exam question-count badges are excluded from source-text comparison. No source prose is summarized or rewritten.
- All 47 numbered figures are present. Every embedded source image object has a responsive visual owner. Inventoried crop boundaries do not cut intersecting source words or image/connector objects; objects outside the physical paper are clipped to the visible source page.
- Region, reader-assembly and cell PNGs match their canonical source-page pixels exactly. Fresh source-page render comparisons passed the recorded antialias tolerance, with observed maximum mean channel difference **0.0** for this run.
- All printed-page pairs match verified footer evidence. PDF 83 remains explicitly unnumbered; later page references use the changed offset.
- Existing PDF annotations retain their original metadata and comment contents, separate from textbook prose. Non-content page rules, backgrounds and markup remain in the vector inventory and full-page comparison renders.
- Exact source quotes anchor 11 exam concepts to 21 published questions. The companion retains all 13 existing concepts and 23 reviewed Hardware questions. Bit masks and 3D printing remain explicitly unanchored; no matching source words were invented.

Visual inspection covered contact sheets of all 77 original figure regions and representative desktop/mobile comparisons, including CPU/main-memory, register addressing, logic circuits, table prefixes, insertion, storage and input/output pages. It caught clipped main-memory, register, hierarchy and gate labels; the corrected crops retain their complete source objects. Automated browser navigation checks every page's block order against the dataset. This is not a claim that all 100 pages have received a complete human semantic transcription audit.

Completed checks: **55 application unit/component tests**, **6 converter tests**, **1 local-server boundary test**, **16 editorial browser tests**, and **26 public production browser tests**. Astro/TypeScript checking passed with **0 errors, warnings or hints**. The production build and asset/publication checks passed. The existing build emits its bundle-size advisory. Account/rules emulator suites were not rerun because the account client, rules, schema and public learning flow did not change; the public browser suite still verifies guest learning, question return and reading restoration.

## Uncertainties and remaining editorial work

No source page, source text character or numbered figure is missing from the local dataset. This is complete source preservation with a reviewable responsive conversion, **not a certified publication-ready semantic edition**.

The local review report retains 130 semantic-math transcription flags, including 31 undecoded special-font cases, and 26 table-grid reading-order flags. Such material uses original pixels, avoiding corrupted or guessed Unicode/MathML. Raster/unruled tables retain all original visual cell contents but still need complete accessible cell transcription. Automatic fragment/vector grouping has 24 image-boundary and 20 vector-boundary review candidates. The 101 curated seeds retain conservative caption/boundary review flags; geometric integrity checks do not establish semantic crop approval. Several original regions include surrounding source prose, intentionally favoring completeness. Paragraph segmentation, inferred heading levels and side-by-side teaching layouts remain reviewable against the full original pages.

The source edition has separate local reading restoration. It links to the existing public practice/progress/account system, whose guest and Firestore behavior is preserved. Cloud synchronization of source-edition reading positions is a future adapter change described in the integration plan; it was not enabled for unpublished content.

## Git and deployment boundary

Only scripts, tests, metadata-only crop seeds, reports and documentation enter Git. The full source dataset, comment text, page renders, original crops, manifests containing source captions, galleries and test screenshots remain ignored under `.local/`. Neither Astro nor Cloudflare imports them.

Before pushing, the authenticated read-only Cloudflare audit confirmed the GitHub project `Y3llowFlash/itpecfetextbook`, production branch `main`, automatic deployments enabled, Node 24, build command `npm run build`, output `dist`, empty root and no production emulator setting. The production build rejects source-edition markers, PDFs, reproduced datasets, unexpected HTML/JSON and all images outside the approved 420 exam-image/favicon allowlist. Negative tests cover accidental and disguised copies. The unchanged public fallback is the only material eligible for automatic deployment.

The implementation is committed and pushed to `main`; the exact commit and resulting Cloudflare status are reported in the delivery message. This phase stops at Chapter 1 local conversion and verification. Reproduced material remains unpublished pending authorization and editorial review.
