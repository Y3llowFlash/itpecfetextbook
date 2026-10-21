# Local figure extraction and review

Source inputs are read-only. Generated source images, page text, contextual previews and galleries are always written under the ignored **`.local/figures/`** directory. Nothing in that directory is an application asset. No publication permission for textbook crops or third-party illustrations is assumed.

The verified source is `D:\ITPEC Old Questions\database\raw\FE Vol 1.pdf`. Python 3 with **PyMuPDF** and **Pillow** is required (`python -m pip install pymupdf Pillow` if absent). This run used PyMuPDF 1.27.2.3 and Pillow 11.1.0. The source SHA-256 must match the committed edition evidence. Production builds require only the existing Node dependencies; Python and the old repository are not build requirements.

## Commands

Run from the repository root:

```powershell
# Render the entire chapter for page-level identification, including vector content.
python scripts/figures.py survey

# Render one selected physical PDF page to WebP or PNG.
python scripts/figures.py render --pdf-page 68 --dpi 180 --format png

# Crop a manually selected complete region, in PDF points (not pixels).
python scripts/figures.py render --pdf-page 68 --crop 100 80 470 330 --dpi 180 --format png

# Check edition, printed/PDF pairs, region boundaries and review coverage.
python scripts/figures.py validate

# Propose expanded boundaries when a seed crop cuts text or image fragments.
python scripts/figures.py suggest-bounds

# Inspect proposals before adopting them into the editorial JSON manifest.
python scripts/figures.py --manifest .local/figures/suggested-manifest.json review

# Render all approved editorial regions and both local comparison galleries.
python scripts/figures.py review

# Regenerate only original public SVGs and their source/author/hash manifest.
node scripts/author-hardware-figures.mjs
node scripts/figure-inventory-report.mjs

# Automated checks; browser tests require a production build first.
python -m unittest discover -s tests -p test_figure_pipeline.py
npm run check
npm test
npm run build
npm run test:e2e
npm run test:accounts
```

The Python figure commands accept `--source` and `--manifest` before the subcommand. Default manifest: `docs/development/figures/chapter1-inventory.json`. The source file must remain the verified edition. `--dpi` accepts 72–600. Coordinates are `[x0, y0, x1, y1]`, PDF points, top-left origin; 72 points equal one inch. Printed pages are recorded separately. PDF page 83 is unnumbered, so there is no universal page offset.

## Review loop

1. Use `survey` to locate the complete figure and supporting caption on the full page. Catalog tables and relevant examples as well as numbered diagrams. Record a page review even when there is no independent figure.
2. Choose a seed rectangle around the full teaching region in the inventory JSON. Retain labels, arrows, legends, equations and related captions. Select all parts of a multipart figure. Keep per-page crops for a cross-page explanation.
3. Use `suggest-bounds` when labels or image fragments meet the boundary. It writes **a local candidate**, never silently changes editorial approval. The source PDF contains some connectors and glyphs as tiny image fragments, so inspecting only large embedded images is insufficient.
4. Inspect `.local/figures/gallery.html`: each high-resolution crop has a linked full-page contextual image with its exact boundary drawn in red. `review` rejects severed word/image boxes. **The detector is not a semantic figure detector and cannot prove completeness**: inspect vector strokes, neighboring components and captions visually. A complete row wholly outside a seed would not trigger a boundary warning. Prefer a little surrounding prose over a severed diagram.
5. Follow each region’s link to its new original in `.local/figures/originals.html`, or to the existing lesson equivalent. The original gallery links back to every source region. Compare the technical meaning, signal polarity, units and labels. Do not assume an annotation or source example is error-free.
6. Recreate simple figures with the deterministic SVG authoring script. No source PDF, crops or raster images are inputs to that script. Update original alt text, caption, immediate reading block, edition/source regions and generated asset hash. Keep a source reuse proposal editorial-only until publication permission is confirmed.
7. Regenerate the human-readable inventory and run validation/build/browser checks. Do not move crops or either editorial gallery into `public/`.

The pipeline rasterizes **the whole PDF page display list with a clipping rectangle**, preserving vector paths, text and raster components together. It does not rely on image-object extraction. It exports quality-94 WebP previews (180 DPI by default) or optimized lossless PNG; it also produces page-context previews. A standalone selected-page crop is a trial export; the reviewed manifest drives the full gallery.

## Publication boundary

`src/content/hardware-figures.json` approves only newly authored SVGs, with SHA-256, nonempty descriptions, source-region IDs and verified printed pages. `scripts/validate-figures.ts` rejects source reuse, unmapped or changed artwork, external references, embedded raster images and scripts. Production verification requires all approved figures and uses an exact public-image allowlist: the existing approved exam images plus favicon. New teaching figures are inline vectors, so they request no additional images or cloud services.

The editorial manifest is metadata only and is not bundled into the application. Public source badges retain the existing minimal style. Multiple source pages are displayed as disjoint ranges when necessary, for example `pp. 46, 55–57`, rather than inventing a continuous reference.

Browser checks cover named SVGs with `title`/`desc`, caption references, unique document IDs, 14px minimum rendered figure text at 320px, text bounds within the viewBox, horizontal fit, static HTML, keyboard practice return and a reading checkpoint on a new figure. Screenshots are generated for every original figure at mobile width and all five desktop lessons. These targeted checks are not a claim of a comprehensive WCAG audit or physical-device testing.
