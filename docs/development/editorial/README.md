# Local source edition workflow

This corrects the earlier summary-first architecture. Source characters, source terminology, original illustrations and original sequence are conversion inputs; existing study-guide prose and replacement SVGs are not. Only Chapter 1 is in scope. The owner has approved publication of the source edition, which now replaces the summarized public lessons.

## Reproduce and open

Python 3.11+ and Node 24+ are required. Tested with PyMuPDF 1.27.2.3 and Pillow 11.1.0. From `D:\ITPEC_FE_TEXTBOOK`:

```powershell
python -m pip install -r scripts/requirements-editorial.txt
npm.cmd ci
npm.cmd run editorial:convert
npm.cmd run editorial:validate
npm.cmd run editorial:preview
```

Open **http://127.0.0.1:4340/**. Stop the server with Ctrl+C. It binds only to loopback and never exposes the repository root. No PDF reader, credentials, Firebase SDK or external fonts are served by this local server. Practice links intentionally open the existing public application in another tab.

The conversion defaults to `D:\ITPEC Old Questions\database\raw\FE Vol 1.pdf`, rendered at 180 DPI. Override the source path or DPI:

```powershell
python scripts/editorial_convert.py convert --source "D:\ITPEC Old Questions\database\raw\FE Vol 1.pdf" --dpi 180
python scripts/editorial_convert.py preview
node scripts/editorial-server.mjs --port 4345
```

`preview` rebuilds HTML/manifests from the existing local dataset without rerendering the PDF. An output override must remain beneath `.local/editorial/`; public, source-code, external and deployment-output destinations are rejected. A different PDF edition fails the fingerprint check. Port changes use a separate browser storage origin.

## Local deliverables

All paths below are under **`.local/editorial/chapter-1/`**, ignored by Git:

| Path | Purpose |
|---|---|
| `chapter.json` | Complete source text/glyphs/fonts/positions, content blocks, region associations, image/vector inventory and supplied PDF annotations |
| `raw/pdf-NNN.json` | Unmodified per-page extraction, physical/printed provenance and source text hash |
| `page-manifest.json` | All 100 physical pages, verified printed labels, original page renders and hashes |
| `figure-manifest.json` | Every original region, coordinates, captions, original pixels, table cells, figure numbers and review flags |
| `outline.json` | Original headings, levels and source block references |
| `annotations.json` | Separate exact-quote exam annotation layer; does not rewrite source blocks |
| `library/*.png` | Complete original source regions, including captions/labels and complex notation |
| `assets/*.png` | Original visual assemblies placed in reading order in the responsive reader |
| `cells/*.png` | Original source table cells, including undecodable symbols |
| `pages/*.png` | Canonical full source-page renderings, used only for comparison and pixel verification |
| `reader/pdf-NNN.html` | Responsive three-column source reader for each source page |
| `compare/pdf-NNN.html` | All 100 side-by-side PDF-rendering/digital comparisons |
| `assets.html` | Crop review gallery with source coordinates, captions, page links and unresolved flags |
| `source-annotations.html` | Text comments already present in the supplied PDF, separate from book prose |
| `validation-report.json`, `validation.html` | Detailed coverage/pixel results and linked review queue |
| `index.html` | Start/resume, source outline and editorial tools |

Source page boundaries provide provenance and previous/next navigation, not a fixed page-sized reading canvas. Paragraphs, headings and lists reflow. Feasible source grids become semantic tables with original superscripts and merged cells; undecodable/raster cells and complex mathematics preserve original pixels. Wide figures and tables can scroll within their own container on phones; figures also open at full resolution. The source material is never replaced by newly invented drawings or guessed equations.

## Pipeline and data model

1. Verify the exact source SHA and printed-label evidence in `../evidence/hardware-printed-pages.json`. Physical pages 18–117 contain printed 13–111, including unnumbered PDF 83. There is no single global page offset.
2. Extract every source character with its PDF block/line indices, glyph box/origin and font attributes. Preserve the raw text separately. Running headers, footers and whitespace remain in the dataset as `page-furniture`, rather than cluttering the responsive reader.
3. Start with the metadata-only crop seeds in `chapter1-regions.json`. Supplement with source table grids, raster objects, equations with special fonts/spatial notation and remaining technical vector clusters. This is full-page rendering, not embedded-image extraction alone.
4. Expand region boundaries to retain intersecting complete source words and image/connector objects. Keep uncertain semantic boundaries flagged. Full regions remain in the library; narrative beside visuals reflows independently in the reader where possible.
5. Render a canonical source page once, then make lossless PNG crops from that exact frame. Store file hashes, pixel hashes, DPI and PDF-point bounds (top-left origin, 72 points/inch). Repeated conversion removes obsolete generated crops from its fixed local folders.
6. Assign every source glyph exactly once to a block through `lineRanges` and `glyphOwners`. Join PDF layout lines into paragraphs without changing source characters; retain explicit `reflowJoins` provenance. Geometric ordering and original PDF indices are both retained for review.
7. Render native source HTML plus original visual assemblies, source outline, page navigation, local restoration, exam annotations and comparison tools. Do not use public replacement diagrams as input.
8. Independently reextract the source, audit HTML text and glyph ownership, account for every embedded image object, check original annotations, verify complete word/image crop boundaries, and compare crop pixels with canonical source pages. Compare canonical pages with fresh PDF renders using the recorded small antialias tolerance; observed results are in the report.

One source region can contain several formulas or include a table inside a numbered illustration; overlapping regions can become one reader assembly. Counts in the report therefore distinguish inventoried regions from rendered blocks. Paragraph boundaries, inferred headings and grid reading order are editorial interpretations, not a claim that automatic extraction has resolved every semantic ambiguity. Background rules, highlight shapes and other PDF markup remain in the source-page/vector audit; source comments are not silently incorporated into textbook prose.

## Verification and publication boundary

```powershell
npm.cmd run test:editorial
npm.cmd run check
npm.cmd test
npm.cmd run build
npm.cmd run test:e2e
```

Install the Chromium browser with `npx.cmd playwright install chromium` if needed. Editorial browser tests require the generated dataset, visit every page, and check representative 320px and desktop comparisons, original figure scale, table rows/superscripts, annotations, local restoration, no external requests and reading without JavaScript. Screenshots/traces stay under `.local/editorial-test-results/`.

`npm run build` never calls Python or the converter. It works without the PDF or local dataset. Build verification permits only the known public HTML routes, two published question JSON files, the 420 approved exam images, favicon and exact hash-verified source assets listed in the approved release manifest. It rejects editorial markers, raw extraction datasets, additional crops, source preview routes and PDFs. Negative tests cover accidental copies and disguised editorial HTML/JS. The local server rejects traversal, symlink escapes, unsupported file types and writes.

The owner-approved release uses `chapter1-publication.json` and `npm.cmd run editorial:release`. After `editorial:validate` passes, the release script generates six source HTML sections in `src/content/source-hardware/`, optimized lossless WebPs in `public/textbook/hardware/`, and `src/content/hardware-source-release.json`. It verifies that WebP decoding retains every original RGB pixel. Commit these approved outputs; Cloudflare builds from them without requiring the PDF or Python. Do not copy raw datasets, full page renderings, comparison galleries or source comments into public output. The [publication report](../CHAPTER_1_SOURCE_PUBLICATION.md) describes this implemented release; earlier local-only reports remain historical evidence.
