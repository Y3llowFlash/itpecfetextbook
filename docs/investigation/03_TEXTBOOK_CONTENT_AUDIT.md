# Textbook content audit

Date: **2026-10-21**. Source root: `D:\ITPEC Old Questions`. This distinguishes available source material from content already usable by a web reader.

## Verified facts

### Full textbook sources exist

The old repository contains both full English **New FE Textbook** volumes, not just chapter metadata. Both PDFs are tracked. Their colophons identify a first edition of April 2015, original Japanese copyright held by Infotech Serve Inc. (2013), and translation copyright held by Information-technology Promotion Agency, Japan (2015). No publication permission record or open redistribution/adaptation license was found among the inspected repository documentation. The repository's private visibility does not establish permission for redistribution from the new public repository.

| Exact local path | Content | Pages | Pages with extractable text | Extracted character count | Size |
|---|---|---:|---:|---:|---:|
| `D:\ITPEC Old Questions\database\raw\FE Vol 1.pdf` | IT Fundamentals | 487 | 484 | 889,669 | 8,207,454 bytes |
| `D:\ITPEC Old Questions\database\raw\FE Vol 2.pdf` | IT Strategy & Management | 423 | 421 | 835,001 | 5,081,119 bytes |
| **Total** | Two volumes | **910** | **905** | **1,724,670** | **13,288,573 bytes** |

Character counts describe extraction output, including headers/index/contents, not clean prose length. SHA-256 fingerprints and bookmark entries are in [audit evidence](evidence/local-audit-2026-10-21.json). PyMuPDF read all pages for extraction statistics and annotation counts. Representative page renders were visually inspected: Vol 1 PDF pages 21 and 29, and Vol 2 PDF page 16. The review confirmed mixed prose, figures, tables, colored emphasis and annotations. It was a representative extraction/structure check, not a page-by-page editorial review.

### Chapter structure

Bookmark starts establish these PDF page spans (one-based physical PDF pages, including chapter title pages):

| Volume | Chapter | PDF span |
|---|---|---|
| 1 | Hardware | 17–125 |
| 1 | Information Processing System | 126–192 |
| 1 | Software | 193–255 |
| 1 | Database | 256–297 |
| 1 | Network | 298–360 |
| 1 | Security | 361–411 |
| 1 | Data Structure and Algorithm | 412–459 |
| 2 | Corporate and Legal Affairs | 14–146 |
| 2 | Business Strategy | 147–200 |
| 2 | Information Systems Strategy | 201–235 |
| 2 | Development Technology | 236–312 |
| 2 | Project Management | 313–348 |
| 2 | Service Management | 349–383 |
| 2 | System Audit and Internal Control | 384–399 |

Both volumes also contain contents, introductory material and an index. Some bookmark labels abbreviate chapter names; the contents/body and existing application labels are better human-facing names. There is no existing structured textbook chapter/section content collection in `src/`, `docs/` or `public/`.

### Chapter 1: Hardware

Vol 1's contents on PDF page 2 provide the following outline. Printed page numbers below are the book's own numbers, not physical PDF pages.

| Top-level section | Printed start | Subsections available in source |
|---|---:|---|
| 1 Basic Configuration of Computers | 13 | History of Computers; Five Major Units of Computers |
| 2 Data Representation in Computers | 20 | Data Representation; Radix and Radix Conversion; Representation Form of Data |
| 3 Central Processing Unit and Main Memory Unit | 46 | Configuration of CPU; Main Memory Configuration; Instruction and Addressing; Circuit Configuration of ALU; High Speed Technologies |
| 4 Auxiliary Storage | 78 | Magnetic Disk; Optical Disc; Semiconductor Memory; Other Auxiliary Storage Media and Drives |
| 5 Input/Output Unit | 92 | Input Unit; Output Unit; Other Input/Output Units; Input/Output Control Methods; Input/Output Interfaces |
| Exercises | 112 | Source questions begin at physical PDF page 118 |

This is sufficient to design the initial hierarchy. Hardware has 38 mapped past questions in the current A corpus, but some lower-level section mappings need review. Chapter-level coverage is not evidence that every subsection has related questions.

### Figures, formulas, notes and annotations

The PDFs contain extractable text **and** raster/vector graphics. For example, Vol 1 PDF page 29 has a radix-conversion formula and number tables with vector drawing; page 50 contains a rotation-shift diagram with many raster elements. A plain text extraction loses superscript positioning, figure relationships and table layout. `get_images()` counts embedded image references rather than semantic figures, so its count must not be used as a “number of illustrations.”

Existing PDF annotations were found:

| Source | Annotation types / counts |
|---|---|
| Vol 1 | 712 Highlight, 61 Underline, 15 Text, 1 Square |
| Vol 2 | 546 Highlight, 53 Underline, 33 Ink, 2 Text, 1 Squiggly, 1 FreeText |

These provide possible learning-note/emphasis clues. They have no permanent concept IDs or question associations. Existing yellow highlights do not establish exam relevance or correctness; their provenance and intent have not been reviewed. Comment contents and author metadata were not copied into these reports.

All 460 A question records include editorial `notes`, topics and textbook-page references. Notes are concise mapping/solution clues, not full chapter prose or a complete explanation bank. Marketing/course data and recommendation copy include Myanmar-language text, but no complete structured Myanmar-language textbook was found in the requested repositories.

### Exercises, solutions and CET

Exercise starts are present for all 14 chapters: Vol 1 PDF pages 118, 189, 250, 293, 354, 406 and 455; Vol 2 pages 134, 196, 231, 307, 345, 379 and 396. They have not been extracted into a structured assessment bank.

Both PDF outlines contain an “Explanations and Answers” entry that points to **page 1**. Text searches did not locate a corresponding solution heading, the PDFs have no embedded attachments, and the tails contain indexes/colophons. A standalone usable textbook-solution supplement is therefore **not verified**. Do not treat that bookmark as proof of available exercise solutions. Exam answer-key PDFs are a separate resource and match the 580 processed answers.

No implemented CET route, CET schema, chapter-end scoring policy, or dedicated CET question dataset was found in the app/source assets. Practice/mock exam routes are implemented, but they are not evidence of an approved CET assessment design.

### Page references require an edition-aware map

Physical and printed numbering differ and the offset changes within a volume. Vol 1 PDF page 21 shows printed page 16; PDF page 100 shows printed page 94; the Hardware exercises start at PDF page 118 / printed page 112. Existing JSON stores mixed human-readable references such as `FE Vol 1 PDF p75-76 / textbook p70-71`.

Do not apply one global offset. Preserve the exact source PDF fingerprint, physical page number, printed page label and original raw mapping string. Later conversion should add block-level coordinates or source spans for verification.

### Prototype availability

Neither `D:\ITPEC_FE_TEXTBOOK` nor `D:\ITPEC Old Questions` contains a matching approved textbook prototype HTML. The HTML found consists of the practice SPA entrypoint, its build entrypoint and 13 generated crop-review pages. The old untracked `src/components/landing/LandingExperience.jsx` implements a practice-site landing/demo question, not a textbook reader with a chapter navigation rail and study companion.

The approved UX is known from the user's brief: left chapter navigation, central reader, right companion, inline yellow concept links, dedicated related-question screens, counts/navigation/explanations/free video, reading-position return, optional accounts and dashboard. The removed blue concept-action box should remain absent. Exact prototype CSS, dimensions, responsive behavior and event/state implementation remain unavailable; none has been invented here.

## Assumptions

- English content is the starting source language; Myanmar translations would be a separate editorial scope.
- “CET” is provisionally treated as a chapter-end test. Its intended expansion, assessment rules, pass threshold, retake behavior and relationship to textbook exercises need product agreement before that feature is implemented.
- The 2015 volumes are useful foundations. Their alignment with newer exam concepts is incomplete: the current mapping explicitly flags blockchain as not visibly named in the source, and other modern-topic updates need editorial review.
- Technical extraction is feasible, but rights to publicly reproduce/adapt these exact volumes and third-party figures have not been established by this investigation. This is a source-evidence gap, not a conclusion about permission being granted or denied.

## Recommendations

### Import strategy

1. Record the intended edition and source fingerprints. Establish the allowed publication approach before shipping reproduced prose/figures. If direct adaptation is not available, author original explanations using the reviewed chapter outline and topic coverage, retaining source references for internal review.
2. Convert a **small Chapter 1 slice first**, with persistent section/block IDs. Preserve headings, paragraphs, tables, formulas, figure captions and source references. Start with Basic Configuration for the reading shell and Data Representation for a question-connected flow.
3. Extract text with layout coordinates into an editorial staging format. Remove running headers/footers, join line wraps carefully, and correct hyphenation, symbols and reading order. Do not publish raw PDF extraction as finished Markdown.
4. Catalog each needed figure, separating content from PDF annotations. Recreate or export approved figures at readable resolution with captions, alt text and intrinsic dimensions. Represent simple tables and formulas semantically where practical.
5. Review the converted content beside the source page. Add original worked examples and reviewed answer explanations. Keep textbook exercise IDs separate from official past-exam IDs.
6. Add explicit concept annotations after the prose is stable. Resolve question mappings against the original exam image and answer PDF; keep confidence/review state on the association, not just the whole question.

### Missing content and infrastructure

| Missing deliverable | Why it is needed for the pilot |
|---|---|
| Web-ready chapter and section text | The existing frontend loads question metadata/images; it has no reader content pipeline |
| Stable block IDs and source-page index | Deep links, highlights, editorial verification and exact reading return |
| Reviewed concept glossary and question associations | Accurate concept counts and useful targeted practice |
| Structured question/choice text where feasible | Accessibility, search and readable mobile practice; image fallback remains useful |
| Written answer explanations | Correct-answer letters and mapping notes do not explain why distractors are wrong |
| YouTube lesson catalog and mapping review | Existing real resources are Telegram links, with one known accessibility concern |
| CET specification and reviewed bank | Source exercise pages alone do not define assessment behavior or verified scoring |
| Approved prototype file or a reviewed reconstruction | Only the UX description is currently available |
| Content rights/attribution record and edition policy | Public source publication and future revisions need a documented basis |

The answer to “Can existing textbook content be imported?” is **technically yes, as an editorial conversion from the two PDFs**. There is no ready-made MDX/HTML textbook package to import directly. Content review, figures/formulas, publication basis and source mapping are the main preparation work.
