# Chapter 1 crop-first fidelity review

**Published 21 October 2026 following owner approval:** https://itpecfetextbook.pages.dev. The approved feature branch was fast-forwarded into `main` and pushed. Application release commit: `41182c58cbef83650accbe80cc901ba1bbf163f8`; successful production deployment: `082700b9-e615-4b76-88d9-07394e06b286` (`https://082700b9.itpecfetextbook.pages.dev`). The validated build was uploaded directly while the connected GitHub deployment queue was delayed.

The production build passed all source, question, asset and publication-boundary checks for 24 static pages. `node scripts/verify-reading-preview.mjs https://itpecfetextbook.pages.dev --production` then passed against the canonical live domain: 7 readers, all 281 source asset hashes, 81 complete spatial crops, 14 restored prose fragments, 420 unchanged published questions and 52 contents links. The legacy cache redirect, guest answer/bookmark/return flow, original source text and checkpoints, UART paragraph repair, and 375/768/1024/1440-pixel layouts were verified with no browser errors. Live BCD screenshots were also visually inspected. Results and screenshots remain local in `.local/crop-first/production-review/`, including `production-check.json`, `bcd-desktop.png` and `bcd-mobile.png`. Firebase configuration and security rules were not changed or redeployed.

Reviewed 21 October 2026. Chapter 1 printed pages **13–111**, physical PDF pages **18–117**, including the unnumbered PDF 83 insertion, were visually scanned against the original PDF. **81 complete original regions on 43 pages** replace **301 broken text/image fragments**. The **47 numbered source figures** retain their existing complete original crops. No figures were redrawn or generated.

The first regression is **2-3-2 Numeric Data, printed page 32 / PDF 37**: the BCD example of `(2741)₁₀` is now one crop of the entire pink example box, including its instruction, decimal digits, four arrows, aligned four-bit groups, labels and border. Its PDF-point rectangle is `[88.74, 67.92, 506.52, 180.78]`, with three points of margin around the original frame. It is not a full-page screenshot. Original values remain aligned: `2 → 0010`, `7 → 0111`, `4 → 0100`, `1 → 0001`.

## Source and review method

Source: *New FE Textbook, Vol. 1, IT Fundamentals*, First Edition, April 2015. Local file: `D:\ITPEC Old Questions\database\raw\FE Vol 1.pdf`.

SHA-256: `1e1f2ec364a52751333b1e3ab2a2f2548e9345cd06a7c300b8a7075fb51c3d1b`. The existing owner-approved source-edition authorization is verified before integration. The immutable original source HTML, release metadata and 200 earlier source WebPs remain unchanged.

The complete chapter was inspected using 25 four-page survey sheets. Every new crop was reviewed using the local side-by-side gallery and 21 crop contact sheets. Review caught clipped bracketed box titles and the left edge of a fixed-point register; those boundaries were expanded and reviewed again before integration. A geometry guard now rejects cropped box titles, partial surrounding native paragraphs, numbered section headings, interactive exam concepts, duplicate ownership and page-sized crops.

The canonical page is rendered at **300 dpi**, including the original supplied PDF annotations, then cropped at the reviewed integer pixel bounds. Each WebP uses **lossless encoding**, and its decoded RGB pixels are compared exactly with a fresh render of the PDF. Image dimensions, encoded SHA-256, pixel SHA-256, byte size, PDF-point rectangle, integer pixel rectangle, printed/PDF page and source-block coverage are recorded. New assets total **2,274,972 bytes**. Rendering the whole page happens only within the local pipeline; readers receive the individual cropped boxes or spatial groups.

Examples that continue across source pages retain both complete source-page portions consecutively, with accurate page captions. Original open continuation borders are preserved; new borders or source explanations were not invented. These include normalization, XOR design, adder derivation and magnetic-disk worked examples.

## Reader integration

Each repaired region replaces its old visible fragments. Every historical source block ID remains as an empty checkpoint anchor within the new figure, preserving saved links and reading positions without displaying duplicate words or arrow-only fragments. Fourteen source prose runs that were accidentally embedded in old image fragments are restored directly from their original glyph ranges to selectable HTML. Their paragraph fragments are joined in source order and checked against recorded text hashes. Ordinary surrounding paragraphs, all 52 source contents headings and all interactive exam links remain native HTML.

Images preserve aspect ratio. Wide examples scroll within their own focusable, labelled region on narrow screens and can be opened at full resolution with **Enlarge**, including keyboard navigation. Captions retain the minimal printed-page reference; physical PDF and printed references are also embedded as source metadata. The three-column reader, dedicated question screens, mobile contents/tools, guest progress and Firebase synchronization remain in place.

No PDF viewer or reference panel was added. Full-page context images, source extraction data, comparison sheets and the gallery stay in ignored `.local/`; the production asset allowlist accepts only the approved hash-verified regional WebPs.

## Reproduce and inspect

Requires the existing editorial dependencies in `scripts/requirements-editorial.txt`, plus the local source PDF and extracted `chapter.json` dataset. If the dataset is absent, first run `npm.cmd run editorial:convert` with the matching source edition.

```powershell
npm.cmd run editorial:spatial -- build
npm.cmd run editorial:spatial -- verify
# Refresh local review links for an integration preview without rerendering:
npm.cmd run editorial:spatial -- review --reader-origin https://40c559c4.itpecfetextbook.pages.dev
# After reviewing .local/crop-first/gallery.html and its source context:
npm.cmd run editorial:spatial -- publish
npm.cmd run build
```

`build` writes local previews, a manifest, contact sheets and the gallery. `verify` independently rerenders the source and checks geometry, ownership and every crop's pixels. `publish` repeats verification and copies only the regional WebPs and static application manifest; it does not deploy. It prunes obsolete hashed files only inside this pipeline's own `public/textbook/hardware-spatial/` folder. Add or adjust a selected region in `editorial/chapter1-spatial-crops.json`; coordinates use PDF points with a top-left origin. `scripts/figures.py render` also supports individual page/region inspection.

Local visual gallery: `.local/crop-first/gallery.html`. Application manifest: `src/content/hardware-spatial-crops.json`. The source crop is shown beside its original page with a red boundary in the gallery; source context pages are never reader assets.

## Executed verification

| Check | Result |
| --- | --- |
| `python scripts/spatial_crops.py build` | 81 original regions generated and compared with fresh 300-dpi source pixels; all 100 pages inventoried |
| `python scripts/spatial_crops.py publish` | Pixel/geometry verification repeated; 81 optimized regional WebPs integrated |
| `npm.cmd run check` | 0 errors, warnings or hints |
| `npm.cmd test` | 67 tests passed across 14 files |
| `npm.cmd run test:e2e -- --output=.local/crop-first/e2e` | 39 browser tests passed |
| `npm.cmd run test:accounts` | 3 account/emulator tests passed, including cross-device reading checkpoint restoration |
| `npm.cmd run build` | 24 static pages; source coverage, native text, approved asset hashes, question bank and publication boundary passed |
| `node scripts/verify-reading-preview.mjs https://40c559c4.itpecfetextbook.pages.dev` | Passed: 7 reader routes, all 281 source asset hashes, 81 crops, 14 recovered prose fragments, 420 unchanged questions, 52 contents links, practice/bookmark/return flow, and 375/768/1024/1440-pixel viewports; no browser errors |
| `python scripts/spatial_crops.py review --reader-origin https://40c559c4.itpecfetextbook.pages.dev` | Fresh source-pixel verification passed; local gallery refreshed with the verified reader preview links |
| `git diff --check` | Passed |

Browser coverage includes every new crop decoding at 375 and 1440 pixels, correct aspect ratio, readable minimum image scale, container bounds, alt text, keyboard-focusable scroll regions, BCD arrow-key panning and full-resolution image opening. The BCD regression also restores a previously saved fragment checkpoint to the full box. Existing checks cover 320-1280-pixel layouts, no-JavaScript reading, contextual tools, question answering, bookmarks, browser history and exact reading offsets. Account tests use local emulators, including guest migration, two devices, offline recovery, account switching and sign-out isolation. No new Firebase infrastructure or deployed security rules were needed.

Screenshots: `.local/crop-first/e2e/source-spatial-BCD-complet-1796d-and-old-reading-checkpoints/bcd-375.png` and `bcd-1440.png`; representative images for all five sections at both widths are alongside the test outputs. Crop images and source comparisons were visually inspected in addition to automated checks.

## Repaired-region inventory

The website locations below preserve the original section and checkpoint anchors. Each listed crop contains the entire source box or spatial unit on that source page; separate continuation entries together preserve a multi-page example.

Verified preview: **https://40c559c4.itpecfetextbook.pages.dev**. Implementation commit: **`7cebe3de00aa0bfed5cfbc68c47bc06d9f5dac2d`**, pushed on **`feature/chapter1-crop-first-fidelity`**. The connected Cloudflare build also succeeded for that commit at `https://8dba34ca.itpecfetextbook.pages.dev`. The locally built preview above was independently checked in the browser. These preview results preceded the approved production publication recorded above.

Hosted screenshots and the machine-readable browser check are local at `.local/crop-first/hosted-review/`, including `bcd-desktop.png`, `bcd-mobile.png`, `bcd-tablet.png`, `bcd-small-tablet.png` and `preview-check.json`. The gallery and source comparison pages remain local; no full-page review images were deployed.

| Repaired region | Printed page | PDF page | Original visual | Website location |
| --- | --- | --- | --- | --- |
| spatial-p18-01 | 18 | 23 | Main and auxiliary memory: complete persistence comparison box with data-flow arrows | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/basic-configuration/#fev1-201504-ch1-r1-pdf-023-b003-l00-text-0) |
| spatial-p20-01 | 20 | 25 | Two electrical states: current flowing or not, and high or low voltage, connected by two-way arrows | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-025-b005-l06-text-0) |
| spatial-p21-01 | 21 | 26 | Information amount: n bits, one byte, and a 16-bit word, with the original powers and bit patterns | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-026-visual-002) |
| spatial-p22-01 | 22 | 27 | Information theory: occurrence probability and information amount in the original complete callout | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-027-b002-l00-text-0) |
| spatial-p22-02 | 22 | 27 | Large-number prefixes: kilo, mega, giga, tera and peta, with decimal and binary powers | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-027-b005-l00-text-0) |
| spatial-p23-01 | 23 | 28 | Small-number prefixes: milli, micro, nano and pico, with their decimal powers | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-028-b002-l00-text-0) |
| spatial-p23-02 | 23 | 28 | Decimal place-value expansion of 362.9, including the original base notation and explanation | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-028-visual-004) |
| spatial-p24-01 | 24 | 29 | Binary place-value expansion of 101.1 into decimal 5.5 | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-029-visual-001) |
| spatial-p24-02 | 24 | 29 | Octal place-value expansion of 317.5 into decimal 207.625 | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-029-visual-003) |
| spatial-p24-03 | 24 | 29 | Hexadecimal place-value expansion of 1A6.E into decimal 422.875 | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-029-visual-005) |
| spatial-p25-01 | 25 | 30 | Binary-to-octal grouping: aligned groups of three bits, arrows, padding zeros and the resulting octal digits | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-030-visual-003) |
| spatial-p25-02 | 25 | 30 | Binary-to-hexadecimal grouping: aligned groups of four bits, arrows, padding zeros and the hexadecimal result | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-030-visual-004) |
| spatial-p26-01 | 26 | 31 | Worked binary-to-decimal conversion of 1001101.101, with every digit aligned to its power and contribution | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-031-b003-l00-text-0) |
| spatial-p27-01 | 27 | 32 | Worked decimal-to-binary conversion of 77.625, including both division and multiplication columns and reading-order arrows | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-032-b002-l00-text-0) |
| spatial-p27-02 | 27 | 32 | Original radix-conversion procedures for integer and fractional parts, kept together in their complete box | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-032-b005-l00-text-0) |
| spatial-p27-03 | 27 | 32 | Worked decimal-to-octal conversion of 67.6875, with division and multiplication columns and reading-order arrows | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-032-visual-002) |
| spatial-p28-01 | 28 | 33 | Decimal, binary and octal representations of 67.6875 with the aligned three-bit groups | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-033-visual-001) |
| spatial-p28-02 | 28 | 33 | Recurring binary fractions: complete explanation and repeated multiplication loop for decimal 0.2 | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-033-b004-l00-text-0) |
| spatial-p30-01 | 30 | 35 | JIS character-code lookup for J, I and S: character, table position, binary code and hexadecimal code in aligned columns | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-035-visual-001) |
| spatial-p32-01 | 32 | 37 | BCD representation of decimal 2741: digits 2, 7, 4 and 1 align above four downward arrows and the groups 0010, 0111, 0100 and 0001. Complete original example box. | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-037-b002-l00-text-0) |
| spatial-p32-02 | 32 | 37 | Zoned-decimal representation of positive 672 and negative 1905, including all zone bits, sign bits, digit labels and the example explanation | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-037-b004-l00-text-0) |
| spatial-p33-01 | 33 | 38 | Packed-decimal representation of positive 672 and negative 1905, including digit groups, sign nibbles and the example explanation | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-038-b002-l00-text-0) |
| spatial-p34-01 | 34 | 39 | Fixed-point storage positions and the aligned radix-point indicator | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-039-visual-001) |
| spatial-p34-02 | 34 | 39 | Representation of decimal 89 as an eight-bit fixed-point value: full example and register layout | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-039-b005-l00-text-0) |
| spatial-p34-03 | 34 | 39 | Signed-magnitude representation of positive and negative 89, including the highlighted sign bits and both aligned register rows | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-039-b009-l00-text-0) |
| spatial-p35-01 | 35 | 40 | Complements: complete callout with the decimal 614 and binary 01101101 subtraction examples, reference values and results | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-040-b002-l00-text-0) |
| spatial-p35-02 | 35 | 40 | Twos-complement representation of positive and negative 89, including the subtraction and both signed register layouts | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-040-b011-l00-text-0) |
| spatial-p36-01 | 36 | 41 | Worked subtraction of 10 from 15 using twos complement: both stages, carries, register rows and discarded carry annotation | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-041-b003-l00-text-0) |
| spatial-p37-01 | 37 | 42 | Eight-bit signed-magnitude and twos-complement ranges compared side by side, preserving positive and negative zero and both negative limits | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-042-visual-001) |
| spatial-p37-02 | 37 | 42 | Range of signed values representable by n bits in twos-complement notation, with the original superscripts | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-042-b012-l00-text-0) |
| spatial-p37-03 | 37 | 42 | Thirteen storage positions for the sign and decimal digits of 456000000000 | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-042-b015-l00-text-0) |
| spatial-p37-04 | 37 | 42 | Scientific-notation conversion of 456000000000 to 0.456 times ten to the twelfth power | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-042-visual-004) |
| spatial-p38-01 | 38 | 43 | Floating-point sign, fraction and exponent aligned with their stored decimal digits and explanatory labels | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-043-visual-001) |
| spatial-p38-02 | 38 | 43 | Original basic floating-point formula, preserving sign, fraction, radix and superscript exponent | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-043-b008-l00-text-0) |
| spatial-p38-03 | 38 | 43 | Single-precision 32-bit floating-point layout: sign 1 bit, exponent 8 bits and fraction 23 bits, with the complete source heading | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-043-b011-l00-text-0) |
| spatial-p38-04 | 38 | 43 | Double-precision 64-bit floating-point layout: sign 1 bit, exponent 11 bits and fraction 52 bits, with the complete source heading | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-043-b017-l01-text-0) |
| spatial-p39-01 | 39 | 44 | Exponent bias comparison table: Excess 127 for IEEE 754 and Excess 64 for IBM, including all grouped headers | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-044-visual-001) |
| spatial-p39-02 | 39 | 44 | Normalization example: first source-page portion, with the seven stored fraction digits and its complete explanation | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-044-b012-l00-text-0) |
| spatial-p40-01 | 40 | 45 | Normalization example: continuation on the next source page, with normalized form and aligned stored digits | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-045-b002-l00-text-0) |
| spatial-p40-02 | 40 | 45 | Complete worked IEEE 754 single-precision encoding of decimal 1234.625: conversion, normalization, biased exponent and final 32-bit layout | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-045-b005-l00-text-0) |
| spatial-p41-01 | 41 | 46 | Loss of trailing digits: complete floating-point addition with aligned values, underlining and the ignored-value annotation | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-046-visual-002) |
| spatial-p42-01 | 42 | 47 | Cancellation of significant digits: complete binary subtraction example, aligned operands and unreliable-digit annotation | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-047-visual-001) |
| spatial-p42-02 | 42 | 47 | Overflow and underflow: minimum and maximum values, representable range, baseline and directional labels together | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-047-b006-l01-text-0) |
| spatial-p42-03 | 42 | 47 | Absolute error: the complete original boxed formula with absolute-value bars | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-047-visual-003) |
| spatial-p43-01 | 43 | 48 | Relative error: the complete original boxed fraction, including numerator, denominator and absolute-value bars | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-048-b003-l01-text-0) |
| spatial-p43-02 | 43 | 48 | Arithmetic left shift by two bits: complete example with source and result registers, arrows, discarded bits and inserted zeros | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-048-visual-002) |
| spatial-p44-01 | 44 | 49 | Computation rules of arithmetic shifts, including powers of two and the complete original callout | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-049-b003-l00-text-0) |
| spatial-p44-02 | 44 | 49 | Logical-shift rules: complete original callout | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-049-b006-l00-text-0) |
| spatial-p44-03 | 44 | 49 | Comparison of arithmetic and logical right shifts by two bits: both register diagrams, arrows, sign extension, inserted zeros and results | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-049-b009-l00-text-0) |
| spatial-p45-01 | 45 | 50 | Circular right shift by two bits: complete example box with the returning-bit arrows and explanation | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-050-b003-l00-text-0) |
| spatial-p61-01 | 61 | 66 | Logic-operation truth table: complete grouped input headers and AND, OR, NOT and XOR results | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/cpu-and-main-memory/#fev1-201504-ch1-r1-pdf-066-visual-001) |
| spatial-p65-01 | 65 | 70 | Main logical laws: complete aligned expressions including associative, distributive, absorption and De Morgans laws | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/cpu-and-main-memory/#fev1-201504-ch1-r1-pdf-070-b002-l01-text-0) |
| spatial-p65-02 | 65 | 70 | Logical design of an XOR circuit: first source-page portion of the derivation and explanation | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/cpu-and-main-memory/#fev1-201504-ch1-r1-pdf-070-b013-l00-text-0) |
| spatial-p66-01 | 66 | 71 | Logical design of an XOR circuit: continuation with the original expression, circuit, connectors and output labels | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/cpu-and-main-memory/#fev1-201504-ch1-r1-pdf-071-b002-l00-text-0) |
| spatial-p66-02 | 66 | 71 | Alternative XOR circuit: complete original derivation, circuit diagram, crossover connectors and labels in one example box | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/cpu-and-main-memory/#fev1-201504-ch1-r1-pdf-071-visual-003) |
| spatial-p67-01 | 67 | 72 | Four aligned one-bit binary additions, including the X and Y labels, plus signs, horizontal rules and carry digits | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/cpu-and-main-memory/#fev1-201504-ch1-r1-pdf-072-visual-001) |
| spatial-p67-02 | 67 | 72 | Half-adder truth table: complete original grouped input, carry and sum headers and all four rows | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/cpu-and-main-memory/#fev1-201504-ch1-r1-pdf-072-b003-l04-text-0) |
| spatial-p68-01 | 68 | 73 | Full-adder truth table: complete original grouped inputs X, Y and carry-in, with all eight carry and sum result rows | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/cpu-and-main-memory/#fev1-201504-ch1-r1-pdf-073-b002-l00-text-0) |
| spatial-p68-02 | 68 | 73 | Full-adder carry and sum derivation: complete first source-page portion with the aligned terms and original operators | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/cpu-and-main-memory/#fev1-201504-ch1-r1-pdf-073-b014-l00-text-0) |
| spatial-p69-01 | 69 | 74 | Full-adder sum derivation: final expression continued from printed page 68 | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/cpu-and-main-memory/#fev1-201504-ch1-r1-pdf-074-visual-001) |
| spatial-p69-02 | 69 | 74 | Dividing a three-bit addition into two two-bit additions: complete explanation, aligned sums, carry combination and arrows | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/cpu-and-main-memory/#fev1-201504-ch1-r1-pdf-074-b004-l00-text-0) |
| spatial-p71-01 | 71 | 76 | Cache average-access-time example: complete input table, miss probability, weighted formula and original 95-nanosecond result | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/cpu-and-main-memory/#fev1-201504-ch1-r1-pdf-076-b003-l00-text-0) |
| spatial-p80-01 | 80 | 86 | Disk storage-capacity example: complete first source-page portion with the specification table and introductory explanation | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/auxiliary-storage/#fev1-201504-ch1-r1-pdf-086-b008-l00-text-0) |
| spatial-p81-01 | 81 | 87 | Disk storage-capacity example: complete continuation with track, cylinder and drive calculations | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/auxiliary-storage/#fev1-201504-ch1-r1-pdf-087-b002-l02-text-0) |
| spatial-p81-02 | 81 | 87 | Variable-length recording: source explanation, records, blocks, inter-block gaps and aligned track layout together | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/auxiliary-storage/#fev1-201504-ch1-r1-pdf-087-b006-l01-text-0) |
| spatial-p82-01 | 82 | 88 | Sector recording: source continuation with record blocks, sector boundaries and track layout together | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/auxiliary-storage/#fev1-201504-ch1-r1-pdf-088-b002-l00-text-0) |
| spatial-p82-02 | 82 | 88 | Disk recording-area example: complete first source-page portion with the specification table, block and sector calculations | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/auxiliary-storage/#fev1-201504-ch1-r1-pdf-088-b008-l00-text-0) |
| spatial-p83-01 | 83 | 89 | Disk recording-area example: complete continuation through blocks, sectors, tracks and rounded cylinder count | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/auxiliary-storage/#fev1-201504-ch1-r1-pdf-089-visual-001) |
| spatial-p83-02 | 83 | 89 | Disk reading sequence: seek and rotational search, first source-page portion of the original box | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/auxiliary-storage/#fev1-201504-ch1-r1-pdf-089-b006-l00-text-0) |
| spatial-p84-01 | 84 | 90 | Disk reading sequence: data-transfer explanation, continuation of the original box from printed page 83 | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/auxiliary-storage/#fev1-201504-ch1-r1-pdf-090-b002-l00-text-0) |
| spatial-p84-02 | 84 | 90 | Disk access-time diagram: complete seek, rotational latency, transfer, waiting and total-access intervals | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/auxiliary-storage/#fev1-201504-ch1-r1-pdf-090-visual-001) |
| spatial-p84-03 | 84 | 90 | Average disk access time: complete original boxed formula | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/auxiliary-storage/#fev1-201504-ch1-r1-pdf-090-b006-l08-text-0) |
| spatial-p84-04 | 84 | 90 | Average seek and rotational-latency explanation: first source-page portion of the original box | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/auxiliary-storage/#fev1-201504-ch1-r1-pdf-090-b010-l00-text-0) |
| spatial-p85-01 | 85 | 91 | Average rotational latency and data-transfer rate: complete source continuation with both original fractions and explanations | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/auxiliary-storage/#fev1-201504-ch1-r1-pdf-091-b002-l00-text-0) |
| spatial-p85-02 | 85 | 91 | Worked disk access-time example: first source-page portion with the 2000-byte request and complete specification table | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/auxiliary-storage/#fev1-201504-ch1-r1-pdf-091-b010-l00-text-0) |
| spatial-p86-01 | 86 | 92 | Worked disk access-time example: complete continuation with rotation, latency, transfer and total-access-time calculations | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/auxiliary-storage/#fev1-201504-ch1-r1-pdf-092-b002-l00-text-0) |
| spatial-p94-01 | 94 | 100 | One-dimensional barcode and two-dimensional QR-code comparison: full original box with both explanations, code illustrations and captions | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/input-output/#fev1-201504-ch1-r1-pdf-100-b004-l02-text-0) |
| spatial-p98-01 | 98 | 104 | Display-resolution standards: complete original caption, VGA, SVGA, XGA and SXGA table | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/input-output/#fev1-201504-ch1-r1-pdf-104-visual-002) |
| spatial-p98-02 | 98 | 104 | Worked VRAM-capacity calculation for a 1280 by 1024 RGB display: complete example, explanation and intermediate equations | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/input-output/#fev1-201504-ch1-r1-pdf-104-b016-l00-text-0) |
| spatial-p106-01 | 106 | 112 | Star, cascade and daisy-chain connections: full original box with all three explanations, device labels, hubs, connectors and terminator | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/input-output/#fev1-201504-ch1-r1-pdf-112-b002-l01-text-0) |
| spatial-p110-01 | 110 | 116 | Bluetooth standards: full original box with connection limits, speed, range explanation and class-distance table | [Source location](https://40c559c4.itpecfetextbook.pages.dev/chapters/hardware/input-output/#fev1-201504-ch1-r1-pdf-116-b002-l01-text-0) |

## Full source-page scan

All 100 entries were visually reviewed. The per-page counts refer to rendered source visual blocks outside the new replacements, not unique files or numbered figures.

| Printed page | Physical PDF page | Repaired regions | Retained original visual blocks |
| --- | --- | --- | --- |
| 13 | 18 | Existing source layout retained | 1 |
| 14 | 19 | Existing source layout retained | 1 |
| 15 | 20 | Existing source layout retained | 2 |
| 16 | 21 | Existing source layout retained | 1 |
| 17 | 22 | Existing source layout retained | 1 |
| 18 | 23 | spatial-p18-01 | 1 |
| 19 | 24 | Existing source layout retained | 0 |
| 20 | 25 | spatial-p20-01 | 1 |
| 21 | 26 | spatial-p21-01 | 1 |
| 22 | 27 | spatial-p22-01, spatial-p22-02 | 1 |
| 23 | 28 | spatial-p23-01, spatial-p23-02 | 2 |
| 24 | 29 | spatial-p24-01, spatial-p24-02, spatial-p24-03 | 2 |
| 25 | 30 | spatial-p25-01, spatial-p25-02 | 2 |
| 26 | 31 | spatial-p26-01 | 0 |
| 27 | 32 | spatial-p27-01, spatial-p27-02, spatial-p27-03 | 0 |
| 28 | 33 | spatial-p28-01, spatial-p28-02 | 1 |
| 29 | 34 | Existing source layout retained | 0 |
| 30 | 35 | spatial-p30-01 | 1 |
| 31 | 36 | Existing source layout retained | 0 |
| 32 | 37 | spatial-p32-01, spatial-p32-02 | 0 |
| 33 | 38 | spatial-p33-01 | 1 |
| 34 | 39 | spatial-p34-01, spatial-p34-02, spatial-p34-03 | 0 |
| 35 | 40 | spatial-p35-01, spatial-p35-02 | 0 |
| 36 | 41 | spatial-p36-01 | 0 |
| 37 | 42 | spatial-p37-01, spatial-p37-02, spatial-p37-03, spatial-p37-04 | 0 |
| 38 | 43 | spatial-p38-01, spatial-p38-02, spatial-p38-03, spatial-p38-04 | 0 |
| 39 | 44 | spatial-p39-01, spatial-p39-02 | 0 |
| 40 | 45 | spatial-p40-01, spatial-p40-02 | 0 |
| 41 | 46 | spatial-p41-01 | 1 |
| 42 | 47 | spatial-p42-01, spatial-p42-02, spatial-p42-03 | 0 |
| 43 | 48 | spatial-p43-01, spatial-p43-02 | 1 |
| 44 | 49 | spatial-p44-01, spatial-p44-02, spatial-p44-03 | 0 |
| 45 | 50 | spatial-p45-01 | 0 |
| 46 | 51 | Existing source layout retained | 1 |
| 47 | 52 | Existing source layout retained | 0 |
| 48 | 53 | Existing source layout retained | 1 |
| 49 | 54 | Existing source layout retained | 1 |
| 50 | 55 | Existing source layout retained | 2 |
| 51 | 56 | Existing source layout retained | 1 |
| 52 | 57 | Existing source layout retained | 0 |
| 53 | 58 | Existing source layout retained | 1 |
| 54 | 59 | Existing source layout retained | 1 |
| 55 | 60 | Existing source layout retained | 2 |
| 56 | 61 | Existing source layout retained | 2 |
| 57 | 62 | Existing source layout retained | 2 |
| 58 | 63 | Existing source layout retained | 4 |
| 59 | 64 | Existing source layout retained | 2 |
| 60 | 65 | Existing source layout retained | 0 |
| 61 | 66 | spatial-p61-01 | 0 |
| 62 | 67 | Existing source layout retained | 3 |
| 63 | 68 | Existing source layout retained | 4 |
| 64 | 69 | Existing source layout retained | 1 |
| 65 | 70 | spatial-p65-01, spatial-p65-02 | 0 |
| 66 | 71 | spatial-p66-01, spatial-p66-02 | 0 |
| 67 | 72 | spatial-p67-01, spatial-p67-02 | 1 |
| 68 | 73 | spatial-p68-01, spatial-p68-02 | 0 |
| 69 | 74 | spatial-p69-01, spatial-p69-02 | 1 |
| 70 | 75 | Existing source layout retained | 1 |
| 71 | 76 | spatial-p71-01 | 1 |
| 72 | 77 | Existing source layout retained | 2 |
| 73 | 78 | Existing source layout retained | 2 |
| 74 | 79 | Existing source layout retained | 0 |
| 75 | 80 | Existing source layout retained | 3 |
| 76 | 81 | Existing source layout retained | 1 |
| 77 | 82 | Existing source layout retained | 0 |
| Unnumbered insert | 83 | Existing source layout retained | 1 |
| 78 | 84 | Existing source layout retained | 1 |
| 79 | 85 | Existing source layout retained | 2 |
| 80 | 86 | spatial-p80-01 | 0 |
| 81 | 87 | spatial-p81-01, spatial-p81-02 | 0 |
| 82 | 88 | spatial-p82-01, spatial-p82-02 | 0 |
| 83 | 89 | spatial-p83-01, spatial-p83-02 | 0 |
| 84 | 90 | spatial-p84-01, spatial-p84-02, spatial-p84-03, spatial-p84-04 | 0 |
| 85 | 91 | spatial-p85-01, spatial-p85-02 | 0 |
| 86 | 92 | spatial-p86-01 | 0 |
| 87 | 93 | Existing source layout retained | 0 |
| 88 | 94 | Existing source layout retained | 0 |
| 89 | 95 | Existing source layout retained | 0 |
| 90 | 96 | Existing source layout retained | 0 |
| 91 | 97 | Existing source layout retained | 0 |
| 92 | 98 | Existing source layout retained | 2 |
| 93 | 99 | Existing source layout retained | 3 |
| 94 | 100 | spatial-p94-01 | 1 |
| 95 | 101 | Existing source layout retained | 2 |
| 96 | 102 | Existing source layout retained | 1 |
| 97 | 103 | Existing source layout retained | 0 |
| 98 | 104 | spatial-p98-01, spatial-p98-02 | 1 |
| 99 | 105 | Existing source layout retained | 0 |
| 100 | 106 | Existing source layout retained | 2 |
| 101 | 107 | Existing source layout retained | 1 |
| 102 | 108 | Existing source layout retained | 2 |
| 103 | 109 | Existing source layout retained | 0 |
| 104 | 110 | Existing source layout retained | 0 |
| 105 | 111 | Existing source layout retained | 0 |
| 106 | 112 | spatial-p106-01 | 0 |
| 107 | 113 | Existing source layout retained | 0 |
| 108 | 114 | Existing source layout retained | 0 |
| 109 | 115 | Existing source layout retained | 0 |
| 110 | 116 | spatial-p110-01 | 0 |
| 111 | 117 | Existing source layout retained | 0 |
