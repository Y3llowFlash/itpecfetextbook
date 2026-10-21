# Chapter 1 figure recovery and integration

Date: **2026-10-21**. Scope: Chapter 1 Hardware only, printed **13–111** of **New FE Textbook Vol.1, IT Fundamentals, First Edition April 2015**. The old repository was read-only. No source publication permission was assumed.

## Delivered

1. [Human-readable figure inventory](figures/CHAPTER_1_INVENTORY.md), with a row for every selected region and its website context/equivalent. It covers all **47 numbered figures, 1-1 through 1-47**, plus tables, photographs, worked visual examples and relevant annotations.
2. [Editorial manifest](figures/chapter1-inventory.json): **130 complete teaching regions**, physical/printed page pairs, PDF-point crop coordinates, baseline comparison, review decision and equivalent. It also records an explicit review for every one of the **99 numbered pages**. Related examples can share a region; 130 is not a count of separately numbered figures.
3. [Reusable local pipeline](../../scripts/figures.py) and [workflow instructions](figures/README.md): selected-page rendering, manual region selection, conservative boundary suggestions, full-display-list rasterization/clipping, WebP/PNG export, validation, red-boundary page contexts and comparison galleries.
4. **40 newly authored SVGs** integrated immediately after their relevant explanations, plus expanded prefix, Boolean-law and full-adder truth tables. [Public original-artwork manifest](../../src/content/hardware-figures.json) records authorship, SHA-256, descriptions, captions, source-region IDs, edition and printed references.
5. Local review galleries: **`.local/figures/gallery.html`** for all 130 source regions, and **`.local/figures/originals.html`** for the 40 public originals with links back to their source evidence. These galleries and all source crops remain ignored, nonpublic editorial material. The pipeline regenerates both.
6. Automated source/asset/build/browser checks and this report. Runtime output remains static Astro, with React limited to the existing interactive features.

## Integrated original diagrams

| Lesson | New SVGs | Main recovered teaching roles |
|---|---:|---|
| Basic Configuration | 4 | Switching-device integration; computer forms versus roles; separate data/control paths among five units; volatile working memory versus persistent storage |
| Data Representation | 11 | Pattern branching/byte; radix grouping; integer/fraction conversion directions; recurring fractional remainders; representation tree; character lookup; decimal packing; signed ranges; normalized binary32/binary64 fields; precision/range errors; shifts/rotation |
| CPU and Main Memory | 13 | CPU/IR/PC/decoder/ALU paths; clock and bus roles; charge versus feedback memory; selected memory address; instruction fields; addressing/dereference chain; six gate symbols; active-low NAND latch; XOR construction; two-half-adder full adder; cache paths; interleaved banks; pipeline stalls |
| Auxiliary Storage | 3 | Track/sector/head/cylinder geometry; records/blocks/gaps; seek/rotation/transfer timing |
| Input/Output | 9 | Input-processing-output; key bounce; paper recognition versus image capture; relative/absolute input; pixel grid/RGB depth; impact print mechanism; plotter/projector; programmed/DMA transfer; star/cascade/daisy chain |

The existing five-unit flow, instruction-cycle flow, binary32 field diagram, pipeline timing table and cache hierarchy remain. Some new drawings expand their spatial details rather than replacing stable reading anchors. Existing original tables and arithmetic explanations cover **35** source regions; **92** regions map to the new original SVGs; **3** remain editorial-only.

## Technical and editorial review

Reviewed all 100 physical chapter pages, including the unnumbered insertion, through rendered survey sheets. Reviewed all 130 selected regions in crop contact sheets and inspected corrected boundaries on individual high-resolution examples. The crop helper caught fragmented image objects used for connectors/glyphs, not just conventional photographs. Manual review also caught a complete prefix row outside an initial crop, and the missing top of a half-adder diagram; their final crops retain the complete region. Automated bounds alone cannot prove semantic completeness.

Reviewed all 40 recreated figures in mobile screenshots, with individual checks of CPU paths, gate inputs, distinct adder carry paths, XOR wiring, memory models and source-appropriate latch polarity. The source uses a **NAND active-low SR latch**, not a NOR active-high latch. The new labels `S_n`, `R_n` make its convention explicit; the truth cases were independently evaluated. The full-adder table was checked against integer addition for all eight inputs. Independent checks also cover radix examples, signed ranges, blocking space and rotation timing.

Important adaptations/exclusions:

- The margin additions on printed 49/50 depict a TTL NAND implementation and a clocked JK circuit. They are neither DRAM-cell drawings nor confirmed licensed assets. They remain local editorial evidence. Simple original memory-retention and NAND-latch diagrams teach the relevant chapter concepts.
- The physical-page-83 inserted exam screenshot is unnumbered and excluded from public figures. No printed page is invented.
- Historical product photographs are replaced by conceptual schematics/role illustrations. The release does not recreate product likenesses or publish source photographs.
- Existing interface comparisons explain families, topology and version-dependent behavior; legacy rate tables are not copied as universal current specifications.
- The original numeric-error diagram correctly separates tiny-magnitude underflow from signed range overflow, rather than repeating misleading source wording.
- Equivalents preserve the teaching concept and necessary labels, not every source sample value, decorative detail or page layout. No raw figure reuse is approved or included.

## Layout, accessibility and performance

Figures use responsive inline SVG with `viewBox`, intrinsic dimensions, document-unique marker IDs, named `title`/`desc`, semantic `figure`/`figcaption`, and minimal printed-reference badges. Disjoint source pages are shown honestly (for example **pp. 46, 55–57**). Labels remain at least **14px rendered size at 320px**; browser tests reject text outside the viewBox. Captions use the existing interface font and palette. Color is not the sole carrier of gate, bank or signal meaning.

The three-column desktop layout, mobile navigation, yellow highlights, dedicated practice screens and cache lesson are preserved. No PDF viewer or source-reference panel was added. The new figures total **85,942 SVG bytes** before transport compression (approximately **23,647 bytes** if each SVG is individually Brotli-compressed); actual whole-page compression differs. They are inline, so there are **no additional illustration requests**, no layout shift from image loading, no image CDN and no new cloud reads/writes.

Each new figure has a stable `figure-{id}` reading block. A cross-device test exposed an existing identity-restoration race: a resume request could inspect the guest store before the remembered Google account loaded, then a native fragment scroll could replace the saved checkpoint. The reader now waits for identity restoration, suppresses checkpoint capture during that restoration and verifies the checkpoint owner before applying the stored viewport offset. Guest mode still initializes no Firebase session without the existing explicit opt-in marker.

## Executed verification

- Astro/TypeScript: **0 errors, 0 warnings, 0 hints**.
- Unit/component tests: **53 passing**, including asset/source/hash reconciliation, complete page-review coverage, disjoint reference labels, nested-block insertion, rejection of missing artwork, independent arithmetic/latch truth cases and all displayed full-adder rows.
- Python pipeline tests: **5 passing**, covering severed captions, fragmented connectors, conservative expansion, unchanged complete regions and rejection of invalid crops before export.
- Production Chromium: **26 passing** after visual/connector refinements; includes every new diagram at 320px, accessible names/descriptions, source labels, unique IDs, text size/bounds, mobile fit, all five desktop lesson screenshots, no-JavaScript content, figure checkpoint resume, keyboard practice return and the original learning-flow regressions.
- Account Chromium/emulator scenarios: **3 passing**, including migration, offline recovery, account switching, cross-tab sign-out, new-section progress and the new exact figure-position resume between two signed-in contexts. Production Auth/Firestore APIs are blocked in these scenarios.
- Read-only source verification: **130 crop boundaries**, printed/PDF page pairs and all 99 numbered-page review records pass. Rendered the chapter survey, the complete 180-DPI WebP gallery and a selected physical page/region as PNG.
- Production build: **23 static HTML routes**, all 40 approved originals present, all 420 published question/image records validated, all 23 reviewed Hardware questions retained. The build rejects changed/unapproved artwork, raster-in-SVG, external/scripted artwork, source PDFs, crop galleries and non-allowlisted public images.

The Vite advisory about the optional account vendor chunk remains. Accessibility checks are targeted SVG semantics/readability/keyboard checks, not a comprehensive WCAG certification. Chromium was used rather than physical Safari/Firefox devices. No Firestore rules or production Firebase settings changed during this phase, so no security-rule deployment is required.

The initial browser run caught one clipped binary64 label, corrected before the passing run. The new signed-in figure test caught the identity race described above, which was corrected before final verification. Emulator/browser preview processes were run sequentially because Astro tracks one preview per workspace. The temporary sandbox/preview startup failures were not counted as passing tests.

## Publication and release

Before push, read-only Cloudflare inspection confirmed GitHub `Y3llowFlash/itpecfetextbook`, branch **main**, auto deployments enabled, **Node 24**, command **npm run build**, output **dist**, and no production emulator setting. Normal Wrangler CLI refreshed its existing login for this inspection; no Pages configuration changed.

Source crops, survey images/text, contextual previews, comparison galleries, temporary curation scripts and account/emulator review data remain under ignored `.local/` or `test-results/`. Only metadata, original SVGs, application changes, reusable scripts, tests and documentation are committed. Build validation checks the actual output, not just source filenames. No raw textbook crops are deployed. The completion message records the commit and resulting automatic Cloudflare deployment status.
