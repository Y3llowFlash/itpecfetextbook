# 36-question private student preview

23 October 2026. Branch: `feature/chapter1-question-integration`. Completed audit checkpoint: `0d28d36f0a206caf899c337c4d26d059bfdf7e4a`; underlying audit input baseline: `db83363`. The older input baseline is legitimate: its source/review fingerprints still match the live private state at the completed audit commit.

Implemented a student-facing, **loopback-only preview of exactly 36 historical questions**. All 36 original images render, each existing verified answer can be submitted, all existing worked explanations match their private reviews, and all 36 associations reuse seven existing reviewed concepts. No question, source explanation or academic/classification record was rewritten. There are no excluded associations or newly created source highlights in this selected set.

| Concept | Questions | Representative owner walkthrough |
|---|---:|---|
| Logic gates and equivalent circuits | 24 | Existing Logic circuit highlight, multiple question navigation, diagrams and accessible choices |
| Radix conversion | 6 | Existing Radix conversion highlight, fractional/exponent notation, original image enlargement |
| USB interfaces | 2 | Existing USB highlight, text-only choices and navigation |
| CPU registers | 1 | Existing Register highlight, source diagram and single-question return |
| Cache memory | 1 | Existing Cache memory highlight, miss behavior and worked explanation |
| Disk access | 1 | Existing access-time entry, defragmentation's effect on efficient access |
| Disk defragmentation | 1 | Existing defragmentation highlight and direct source explanation |
| Total | **36** | All canonical IDs and exact references are in the private completion report |

## Launch and owner inspection

From `D:\ITPEC_FE_TEXTBOOK`:

```powershell
npm.cmd run questions:pilot:prepare
npm.cmd run questions:pilot
```

Open **http://127.0.0.1:4324/**, choose **Open Chapter 1**, then navigate to one of the seven existing concepts. The private home page also links directly to each existing passage and concept's question set. Choose an option, check the answer, inspect the verified explanation, navigate between related questions, then use **Return to textbook** to restore the source reading position. The preview home has a **Reset preview progress** action that clears only its own namespace.

`questions:pilot:prepare` validates the original private records, preserved audit reports and supplied shortlist, compares all 36 crops against freshly rendered original PDF pixels, then checks/builds the isolated application. A fresh clone requires the original private catalog, full source PDFs, audit artifacts and the two owner-provided review inputs; ordinary production development does not. Preserved copies of the supplied Markdown notes and CSV are under `.local/private-student-preview/inputs/`. Notes are advisory context; CSV fields are independently checked rather than treated as approval.

`questions:pilot` validates the prepared site before starting its read-only server. It refuses stale records, reviews, images, inputs, implementation files or generated assets. Run `npm.cmd run questions:pilot:check` for a separate integrity check. Stop the foreground server with Ctrl+C when inspection is finished.

The private `.local/private-student-preview/` workspace contains:

- `completion-report.md`: all 36 canonical IDs, concept associations, original question pages, existing highlight pages, topic-support pages, routes, walkthroughs, test results and publication blockers.
- `manifest.json`: exact source/review snapshot, input hashes, 36 selected IDs, immutable image bindings, actual source-paragraph/anchor bindings and allowlisted delivery assets.
- `walkthrough.json`: seven concrete representative question IDs and reading/practice URLs.
- `review-gallery.html`: local visual gallery with full-size screenshot links, including seven concepts and mobile Boolean/radix views.
- `seven-concept-contact-sheet.jpg`: compact overview; use the full screenshots to inspect text and figures.
- `generation-integrity.json`: repeated-build byte comparison and preservation results.
- `accessibility-repairs.json`: validated before/after transcriptions for historical pages 22 and 28, bound to the original content, review, image and PDF checksums.
- `app/`: ignored source copy and static build; never used by the production build.
- `handoff.json`: final commit, branch, readiness state and owner-inspection URL.

Full private question tables, screenshots, source data and generated preview files are not committed or placed in production assets.

### Two resolved private accessibility findings

Fresh visual comparison with the original PDF and pixel-matched crops resolved both findings. Historical **p.22** now describes the arrow sequence and processor boundary. Historical **p.28** now describes the complete gate wiring, branch dots and unconnected crossing; the stray input labels were removed from accessible option D. Images, canonical IDs, grading answers and every verified explanation remain unchanged.

Corrections are a private, source-bound accessibility overlay; the original academic review objects and audit snapshots remain byte-for-byte intact. Preserve both `accessibility-repairs.json` and `review-findings.json` with the private inputs. Preparation rejects missing/stale repair evidence, changes outside the two accessible fields, unrelated choice edits, and resolutions without matching validated repairs. The manifest retains the resolved findings and correction history for editors. Internal QA notices and findings are not serialized into student props or rendered in practice screens. See [repair validation report](PRIVATE_ACCESSIBILITY_REPAIRS.md).

## Source placement review

Selection is the exact 36 `priorityAfterMandatoryRepairs === true` records, cross-checked against the supplied CSV and current canonical IDs, original source pages, dates, academic status, extraction bindings and verified mappings. Each is independently verified, accessible-review complete, unapproved, non-adjudicated and issue-free in the preserved audit. The supplied concept distribution matches exactly.

Each association checks actual TOC subsection membership, section ID, concept ID, route and an existing unique source-highlight fragment. The manifest binds the original paragraph and anchor bytes; it separately lists the **highlight's printed/physical page** and **topic-support passages**. A heading-name match alone cannot create an association or a highlight.

The disk-access pilot asks why defragmentation improves file access. Its established access-time entry remains in 4-1-3, with explicit supporting defragmentation teaching at **printed p.85 / physical p.91**. This is a qualitative access-performance question; it is not mislabeled as a numeric seek/latency calculation. The separate defragmentation concept retains its own existing question and original highlight. No duplicate highlight or reclassification is introduced.

Other placements retain their existing passages: register definitions at physical p.52, cache miss handling at p.75, logic/truth-table laws within 3-4-1, radix conversion within 2-2, and USB teaching at pp.113–114. All actual original diagrams, tables, mathematical layouts and symbols remain in the exact source images. Accessible text uses the existing private reviews plus the two validated accessibility corrections; worked explanations remain exactly as verified.

## Isolation and unchanged production behavior

The implementation copies the existing reader, practice, navigation, image dialog and progress components into an **ignored application root**. Small explicit templates adapt only that copy's data/account boundary. Original `src/`, `public/`, textbook source bytes, public catalog helpers, publication validators and reconciliation modules remain unchanged.

Private question projections explicitly retain **`is_published: false`**, **`publicationStatus: unapproved`**, **`paper: null`** and **`subject: null`**. The preview's isolated catalog/filter adapter recognizes this private marker; the production published-only filter is unchanged. Unknown metadata is displayed truthfully as **Paper/subject not established**, alongside FE, year, season and question number. No Morning/Subject A/Technology value is inferred.

Historical images are **not copied into any production asset directory**. The local server streams only the 36 allowlisted original files from their existing private image paths, checking their exact hashes on delivery. It serves the exact private build allowlist, rejects unselected original images, and never serves raw PDFs, raw catalog/review JSON, arbitrary filesystem paths or the audit workspace. Host/origin checks, GET/HEAD-only delivery, no-store/noindex headers and a CSP restricting connections to the same loopback origin provide additional local boundaries. The server binds only to `127.0.0.1`.

All disposable keys use **`itpecTextbook:privatePilot36:`**, covering guest attempts, reading returns and filters. The private account/analytics modules contain no production Firebase SDK/configuration or opt-in reads. Sign-in, migration and synchronization are absent. Browser checks seed genuine guest/account/return keys and confirm they remain intact after answering, navigation and preview reset; network checks show no external requests. The preview does not require a student-progress migration or a backend.

All **333 original question/review objects**, **326 independent answers**, **seven qualified owner adjudications**, prior evidence, IDs, checksums, provenance and approvals remain unchanged. All **1,491 protected source/review/application files** retain their original bytes and modification times. The public release remains **420 questions / 420 images**, 100 reader source pages, 47 numbered figures and 81 spatial crops. No ITPEC Practice repository file was modified.

## Validation

```powershell
npm.cmd run test:pilot-selection
npm.cmd run test:pilot
npm.cmd run questions:pilot:check
```

The real-data browser suite requires a prepared private preview. Synthetic Python selection tests do not require private inputs. Private tests use port 4325; owner inspection uses 4324. Production tests use the existing port 4322 and production `dist/`.

| Check | Result |
|---|---|
| Full Python suite | **128 passed**, including ten new selection/projection/non-promotion regressions |
| Application Vitest | **82 passed** |
| Production Astro / TypeScript | **0 errors, warnings or hints** |
| Private application Astro / TypeScript | **0 errors, warnings or hints** |
| Production build/release validation | Passed; unchanged 420 public question/image bindings and original reader release |
| Production-preview browser suite | **52 passed** |
| Private student preview browser coverage | **47 passed** in the final complete run |
| Source pixel fidelity | **36/36** original crops compared successfully; no regeneration or replacement |
| Repeated private generation | Identical site/image allowlist bindings and projected question/concept/explanation bytes |
| Original catalog/source/public preservation | **1,491 protected files unchanged** |

Every selected question's image is decoded and hash-checked, its canonical ID and truthful metadata checked, its verified answer submitted, and its summary and every worked step compared with the original private review. Seven walkthroughs verify unique existing source highlights, exact related counts and reading-position restoration. Additional checks cover wrong-answer feedback, retry, persistent year/source filters, unanswered counts, single/multiple-question navigation, keyboard controls, mobile Boolean images and all six radix originals at 320px. Boundary checks reject an actual unselected historical image, unknown routes, raw PDFs/catalog/reviews, wrong hosts/origins and POSTs.

Eight initial private browser assertions failed because tests counted both source and recap practice links, and expected retry to erase immutable attempt history. The tests were corrected to select the source highlight and respect the existing unanswered-history rule. All eight passed on focused rerun; no verified evidence, production behavior or assertion timeout was changed. The final mobile and asset-boundary checks also passed. Existing nonblocking build chunk-size and terminal-color warnings are unchanged.

## Metadata and publication decision

See [paper/subject policy options](PRIVATE_PILOT_METADATA_POLICY.md) for the separate owner decision. **Option A** retains independently evidenced paper/subject values; **Option B** would require an explicitly approved, provenance-aware unknown-metadata policy and related matching/schema/UI/validator work. Neither option has been newly applied; the existing strict publication gate remains intact.

Every pilot record still needs reliable paper/subject evidence and separate final owner publication approval. Both flagged accessibility cases are resolved in the private projection. Any future publication preparation must explicitly carry these source-bound corrections forward; this milestone does not promote them into the public catalog. Preview inclusion and answer submission grant no approval. All seven qualified owner disputes and the 41 other/outside/uncertain catalog records remain outside this preview. Published ITPEC Practice authority remains unchanged for reliably matched occurrences.

Tracked implementation: `scripts/private_student_preview.py`, `scripts/private-student-preview-server.mjs`, six non-public build templates in `scripts/private-preview/`, focused Python/browser tests, `playwright.pilot.config.ts`, package commands, README and the two preview/policy reports. Only validated implementation changes are committed/pushed to `feature/chapter1-question-integration`. No main merge, deployment, publication, owner approval or bulk application of the 333 audit proposals is performed. Final commit details are supplied in the handoff; work stops for owner inspection.
