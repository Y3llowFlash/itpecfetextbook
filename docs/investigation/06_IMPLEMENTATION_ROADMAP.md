# Implementation roadmap and decision report

Date: **2026-10-21**. This is a proposed sequence for the new standalone project. The existing practice repository remains a read-only source. **Phase 1 is complete when these investigation documents are delivered; application implementation requires the user's next approval.**

## Verified facts

- The new repository starts with a README and no application framework or feature code.
- The old repository supplies 460 processed A questions and 120 B questions, including 20 sample items, plus local crops, answer keys, mappings and reusable React services/components.
- Both full textbook PDFs exist, but no ready-to-import structured reader package exists. Publication basis and editorial conversion require preparation.
- Hardware has 38 mapped questions (33 High, five Medium). There are inconsistent section/page labels and no approved concept graph.
- Existing quizzes, guest progress, auth and cloud sync are implemented in code, but this investigation did not verify their live behavior. Full written question explanations and YouTube mappings remain gaps.
- No matching approved textbook prototype HTML was found in the two requested repositories. Its intended interaction/layout is specified by the user's brief.
- The architecture recommendation is static Astro pages with React practice components and local-first progress, with optional separate Firebase sync later. No framework has been installed and no cloud services have been provisioned.

## Assumptions

- Chapter 1: Hardware is the first public learning chapter; a complete small reading/practice/return flow is more useful for validation than a shell covering all 14 chapters.
- Start in English using the available source hierarchy; translation is separate unless subsequently requested.
- CET provisionally means chapter-end test. No official pass mark, timing or selection policy has been established.
- Work effort will depend mainly on permitted content reuse, editorial quality, formulas/figures, explanation writing and concept mapping. No evidence supports a fixed delivery date or budget estimate yet.

## Recommendations

### Phase 1 completion and approval boundary

Review the six reports and [reproducible local audit](evidence/local-audit-2026-10-21.json). Approve the intended framework/data approach and the scope of the Chapter 1 pilot before application work starts. The user's brief explicitly requires this stop. This phase has not copied the question bank into a public application, altered old data, deployed code or created infrastructure.

### Phase 2: Chapter 1 Hardware pilot

Implement this phase in the new repository after approval, using the following order.

| Step | Work | Dependencies | Reviewable completion evidence |
|---|---|---|---|
| 2.1 Content and UX baseline | Confirm permitted publication approach, exact source edition, pilot language, and prototype references. If original HTML remains unavailable, reconstruct the described layout as a new implementation and review it explicitly | Phase 1 approval; content publication evidence before reproduced material is shipped | Source/rights/attribution record; explicit prototype gap; pilot outline and layout states |
| 2.2 Isolated data snapshot | Copy only selected public-safe metadata, Hardware questions/images and source manifests; record original commit/path/hashes; normalize aliases and preserve IDs/AM/sample provenance | Reviewed source selection; new repo ignore rules before copying anything | 38 candidate Hardware IDs reconciled to source; answers verified; no credentials, tokenized upload reports or production paths as runtime dependencies |
| 2.3 Chapter structure and first prose | Define Hardware's five top-level sections and stable block/concept IDs; author/convert Basic Configuration and the first Data Representation slice; review tables/formulas/figures | Publication approach; block/source schema | Readable source-cited content in semantic HTML with stable links; editorial comparison against PDF pages |
| 2.4 Static reader and companion | Build left chapter navigation, central reader, right study companion, mobile drawer/collapsible help and public metadata | Approved layout and initial prose | Chapter/section readable without JavaScript; mobile layout and keyboard navigation usable; blue concept-action box absent |
| 2.5 Concept graph and first practice screen | Review bit shifts/two's complement/radix associations; derive exact question indexes/counts; adapt option, header, image and navigation components | Real concept edges and reviewed questions | Yellow inline link opens dedicated screen showing correct count, original exam label, navigation, answer feedback and a reviewed written explanation |
| 2.6 Reading-return flow | Persist section/block/mention/offset before leaving; retain practice context; restore on explicit return and browser Back | Stable blocks; reader/practice routing | Return reaches the same paragraph/highlight, including refresh and mobile-width scenarios; focus returns appropriately |
| 2.7 Guest progress and support | Add local attempts/bookmarks/reading pointer, local progress view, wrong-answer review, free-video candidates and optional course placement | Stable question/concept IDs and local schema | Entire learning loop works signed out; usable fallback when storage is blocked; verified free YouTube link where supplied or an honest no-YouTube state |
| 2.8 Complete Hardware content/review | Extend to CPU/main memory, auxiliary storage and I/O; review all 38 candidate question mappings and all five Medium entries; write required explanations | Pilot flow accepted; editorial capacity | Published subset is explicitly identified; all live highlight counts agree with navigation; gaps are visible rather than fabricated |

Start development with a small coherent example: a Data Representation paragraph about shifts and/or two's complement linked to `2025A-A-Q002` (correct answer c) and other individually reviewed applicable questions. Preserve `2023A-AM-Q002` as a separate legacy source (answer d), resolving its source publication discrepancy through the new release's editorial decision. Basic Configuration provides the first reading section even where no suitable exam question has been mapped yet. Do not force a yellow practice link into every paragraph.

The first slice must include **one real reviewed explanation**, working question navigation and precise return to reading. Showing only a correct-answer letter or a video button does not satisfy the explanation requirement. Use image fallback initially while progressively adding accurate question/choice text for accessibility. Free YouTube recommendations require actual provided/discovered links and review; Telegram candidates must retain their platform label. Course suggestions stay optional and subordinate to free support.

### Phase 3: Section practice, Chapter 1 CET and progress

Agree the CET definition, learning objectives, source types, count, timing, pass/feedback and retake policy before coding it. Use a versioned assessment definition and a frozen question selection per attempt; preserve official exam provenance and distinguish authored/textbook exercises. Confirm any source exercise answer/solution before including it in scored assessment content.

Add practice by section using the union of approved concept/question edges, and clearly labeled broad chapter practice if needed. Build guest dashboard summaries from deduplicated attempts, with transparent “latest” versus “all attempts” semantics. Recommend free lessons after a meaningful struggle signal without presenting an unvalidated accuracy number as official exam readiness. Add local export/import/reset and deletion behavior. Extend first to a completed, reviewed Hardware learning experience before scaling all chapters.

### Phase 4: Optional Google sign-in and cloud backup

Use a **new, separate Firebase project** only after the sync design and emulator tests are reviewed. Retain the free Spark plan initially, using Auth/Firestore without Cloud Storage, Functions, App Hosting, or billing linkage. Configure only the new site's allowed domains. The app must still build and support guest learning when Firebase is disabled or unavailable.

Adapt the old provider wiring while replacing the global mixed guest/user cache and snapshot counter merges. Add UID-scoped state, explicit device-progress merge, stable attempt IDs, delta/outbox synchronization, retries, bookmark deletion tombstones and a sync status. Minimize profile data. Test two devices, repeated uploads, offline recovery, account switching, sign-out, cross-user denial, malformed private records, deletion and quota failures. Provide distinct controls for cloud progress deletion and Auth account deletion, with local-device handling explained.

All emulator tests must use a dedicated demo/test project and explicit emulator endpoints. Do not reuse the old tests' production-like project IDs or run routines that clear resources against production. New deploy configuration must reject the old Firebase project/bucket identifiers. Authentication testing and deployment are later explicit work; none is part of this investigation.

### Phase 5: Additional chapters and Subject B

Use the proven content/mapping pipeline for remaining IT Fundamentals chapters, then Strategy & Management. Retain volume/edition IDs because chapter numbers repeat. Prioritize mapped modern-topic gaps and review Medium/Low associations rather than presenting broad chapter matches as exact section evidence.

Import the rest of the approved 580-record candidate corpus into static release data as coverage grows. For B, retain long stitched-image handling, variable option counts, 20 sample questions as a distinct source kind, and the conservative exact/similar video mapping. The existing B map covers 2024/2025 dated papers; review 2026S and any new concepts explicitly. Keep raw 2023 PM PDFs as unprocessed backlog until a separate processing/editorial task is approved.

### Phase 6: Launch readiness and independent hosting

Use a static host for chapter HTML, versioned question JSON and local image assets. Cloudflare Pages Free is the initial candidate; Firebase Hosting Spark is an alternative if one-vendor operation is preferred. Validate current plan limits and Myanmar mobile-network behavior before launch. Domain purchase/renewal and DNS/deployment changes are separate authorized launch actions.

Check real rendered HTML, canonical URLs, sitemap, robots/404 behavior, heading structure and private-route indexing. Verify responsive reading, long-image zoom, visible focus, screen-reader descriptions, reduced motion, explanation accuracy, link accessibility and graceful no-video states. Cache immutable assets by hash; ensure updates keep or migrate active session versions rather than losing reading/progress state. Keep a reversible release artifact and a documented rollback. Offline/PWA caching and analytics can be evaluated afterward; do not copy the old site's tracking script automatically.

### Verification appropriate to each implementation phase

| Area | Meaningful checks | Expected result |
|---|---|---|
| Data integrity | Unique IDs, original provenance, local answer-PDF comparisons, explicit publication status, valid options, image hashes/dimensions | No silent renumbering, duplicate records or four-choice assumptions for B |
| Mapping/counts | A question linked to two concepts; a concept in multiple sections; chapter unions; unpublished/pending edges; no-match concepts | Distinct eligible ID count matches exactly what the learner can navigate |
| Reader return | Explicit return, Back/Forward, refresh, font/image layout changes, mobile resize, changed/removed anchor | Correct section and nearest stable block; useful focus restoration |
| Quiz/explanations | Correct/wrong choices, previous/next/jump, final question, reload, source labels, explanation revision | Answers and explanations correspond to original IDs; session position remains valid |
| Guest persistence | Storage permitted/blocked/full, reload, local reset/export/import | Reading/practice remains available; persistence limitations are clear |
| Sync/privacy | Two accounts/devices, duplicate events, sign-in race, sign-out, denied cross-user access, deletion, network/quota failure | No cross-account cache merge; idempotent sync; local work retained |
| Public delivery | Read page HTML with JS disabled; generated links/404/sitemap; static dependencies and secrets scan | Useful public reading and no dependency on old production services |

Run checks when their feature exists. Do not start a full old-project build, upload or deployment merely to verify planning documents. Phase 1 verification consists of local read-only audits, source tracing, GitHub commit comparisons and document/evidence consistency checks.

### Decisions still needed at the relevant phase

- Approve the architecture and Chapter 1 pilot scope now, before implementation.
- Confirm the publication approach for textbook prose/figures and whether the original prototype can be supplied later. Neither gap blocks completing Phase 1.
- Define CET and the first lesson language/content standards before assessment implementation.
- Supply or approve specific YouTube lessons, including whether clearly labeled Telegram fallbacks are acceptable while YouTube coverage grows.
- Choose hosting and authorize project/domain/deployment work when the reviewable pilot is ready; no billable resources are assumed.

## Concise decision report

| Question | Decision |
|---|---|
| What can we reuse immediately? | Existing local question IDs, verified answer keys, 580 image crops, registry/source metadata, 14-chapter outline and lecture catalogs as **review candidates**. Use these in an isolated, reviewed snapshot |
| What must be adapted? | Snake/camel JSON schemas, publication rules, section/page mappings, static data delivery, React quiz/review UI, lecture matching, guest storage, auth wiring and cloud merge/security behavior |
| What must be built from scratch? | Structured web textbook/content workflow, stable blocks, concept glossary and many-to-many graph, yellow concept annotations, dedicated concept-practice context/reading return, complete written explanations, YouTube mapping and CET specification/data/UI |
| Where is canonical processed question data? | A: `D:\ITPEC Old Questions\database\firebase_import\questions_subjectA_firestore.json`, upstream master in `database\sorted\`. B: six `questions_subjectB_*_firestore.json` files in the same import directory. Registry-selected workbooks are the rebuild sources; production Firestore is not needed for reuse |
| Can existing textbook content be imported? | Technically yes: two full English PDFs (910 pages). They require editorial conversion, figure/formula handling, source/page indexing and an established publication basis; no finished MDX/HTML package exists |
| What is the safest, lowest-cost architecture? | Independent static Astro + reusable React components; own-hosted content/images; guest local progress; later optional Google Auth/Firestore in a separate Spark project. Avoid a runtime server and Firebase Storage for this initial design |
| What should we build first? | A Chapter 1 Hardware reading/practice/return slice with a real explanation, accurate reviewed concept count, mobile/keyboard support and guest persistence, then complete Hardware before expanding |

**Stop here and obtain approval before implementing application features, as required by the Phase 1 brief.**
