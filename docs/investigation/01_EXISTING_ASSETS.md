# Existing assets and repository state

Investigation date: **2026-10-21 (Asia/Rangoon)**. Phase 1 is investigation and planning only. No application features were implemented.

## Verified facts

### Evidence and verification limits

Local working copies are the primary evidence. Paths in the asset tables below are relative to **`D:\ITPEC Old Questions`**, unless marked otherwise. The new project is **`D:\ITPEC_FE_TEXTBOOK`**.

“Implemented” means the route, component, service, and relevant data were traced in source. It does **not** mean that production behavior, Google sign-in, remote image availability, or cross-device synchronization was exercised. No production Firestore reads/writes, imports, deployments, or billing changes were performed. Existing rules tests were inspected but not run; they clear emulator data and need a deliberately isolated test environment. The local Subject A validator was run read-only with bytecode writing disabled and passed. Independent checks covered both subjects, including all answer PDFs.

Reproducible counts, exact schemas, source workbook paths, file hashes, and source-PDF paths are recorded in [local audit evidence](evidence/local-audit-2026-10-21.json). The supporting [audit script](evidence/audit_local_resources.py) only reads files and prints metadata; it does not import Firebase libraries. These are investigation aids, not an application data importer.

### Local versus GitHub

| Repository | Local state at start | GitHub comparison on investigation date |
|---|---|---|
| `Y3llowFlash/itpecfetextbook` | Branch `main`, HEAD `80b1e6499f02b08224b470140a4f36a4b95393af`; clean; only `README.md` tracked | Connector reports public repository, default branch `main`. Compare HEAD to live GitHub `main`: identical, 0 ahead/behind, no changed files |
| `Y3llowFlash/itpecbyharu` | Branch `design/interactive-landing`, HEAD `aee4d8d7d8879fe06176198d337a413bafe13a9d`; no tracked modifications; 803 tracked paths | Connector reports private repository, default branch `main`. Compare local HEAD to live GitHub `main`: identical, 0 ahead/behind, no changed files. Remote branch search finds no `design/interactive-landing` branch |

GitHub evidence: [new repository commit](https://github.com/Y3llowFlash/itpecfetextbook/commit/80b1e6499f02b08224b470140a4f36a4b95393af), [practice repository commit](https://github.com/Y3llowFlash/itpecbyharu/commit/aee4d8d7d8879fe06176198d337a413bafe13a9d). Access to the private repository is required for the second link.

The old workspace contains untracked `src/components/landing/LandingExperience.jsx`, `src/components/landing/landing.css`, `tokens.css`, `.hallmark/log.json`, and five cache database files under the literal directory `%SystemDrive%/ProgramData/Microsoft/Windows/Caches/`. The landing JSX includes an interactive transcription of `2023A-AM-Q002`; searches found no import of that component or its CSS in the active app entrypoints. `.hallmark/log.json` describes a practice landing design dated 2026-09-07. These local files are not included in the remote commit comparison.

Ignored local resources include installed dependencies, `.env`, logs, browser-debug state, and `database/secrets/`. Credential contents were not inspected or copied. The core exam registry, processed question JSON, image crops, and both textbook PDFs are **tracked** (`git ls-files --error-unmatch` confirmed representative paths). There is no repository `AGENTS.md` found in either project, and no tracked `LICENSE*` in the old repository. Other local branches and a separate old-project worktree exist; this investigation targets the two requested working directories and current GitHub default branches, not every historical branch.

### Reusable data and processing assets

| Asset and exact path | Format / current status | Dependencies and suitability |
|---|---|---|
| `database/builder/exam_registry.json` | JSON; 13 registered sets with paper, IDs, counts, PDF/workbook/crop paths | Best entrypoint for provenance and source selection. Reuse metadata in a versioned snapshot; preserve legacy AM and sample distinctions |
| `database/firebase_import/questions_subjectA_firestore.json` | JSON array, 460 records; full current Subject A prepared export | Strong import source for a new static adapter. Snake-case fields; publication flags need independent review |
| `database/sorted/questions_import_subjectA.json`, `master_subjectA_question_bank.xlsx`, `master_subjectA_question_bank.csv` | Parallel 460-row processed master outputs | XLSX requires openpyxl/pandas for existing tools. Same meaningful values as prepared A JSON; some empty strings become null in the latter |
| `database/firebase_import/questions_subjectB_{2024A,2024S,2025A,2025S,2026S,sample}_firestore.json` | Six exact JSON filenames expanded by braces; 20 records each | No unified B master JSON. Adapter must deduplicate camel/snake aliases and retain variable answer counts |
| Registry-selected workbooks in `database/sorted/` | XLSX, 13 active first sheets; 580 rows combined; backups and reviewed variants also exist | Use the registry paths, not newest filename or every file in the directory. Exact selected names are in report 02 and audit evidence |
| `database/builder/output_images/question_images/subject_a/{2023A,2023S,2024A,2024S,2025A,2025S,2026S}/qNNN.webp` | 460 cropped question images | Reusable local assets; copy approved files into the new project's own hosting, with provenance and hashes |
| `database/builder/output_images/question_images/subject_b/{2024A,2024S,2025A,2025S,2026S,sample}/qNNN.webp` | 120 images, including stitched multi-page questions | Long-image mobile/zoom handling needs adaptation. Total A+B image size: 41,246,360 bytes |
| `database/firebase_import/storage_upload_manifest.json`, `storage_subjectB_{2024A,2024S,2025A,2025S,2026S,sample}_manifest.json` | Local-to-Storage path manifests, 460 + 120 entries | Reuse path mapping knowledge. Do not preserve dependency on old bucket download tokens |
| `database/builder/crop_manifest/*_crop_manifest.csv` | 13 CSV crop-coordinate/review manifests; all 580 rows marked approved | Useful validation history, including source page ranges. These are stored review claims, not a fresh visual review of every crop |
| `database/builder/crop_overrides/2026S_FE_B.json` | JSON manual crop override | Preserve if reproducing Subject B cropping; 2026S B has one manual crop, 2023S AM has two in its CSV |
| `database/builder/review_html/*_review.html` | 13 generated crop-review pages | Local QA pages, not the requested textbook UX prototype |
| `database/raw/` | 31 PDFs: two textbooks, registered exams/answers, and unprocessed 2023 PM papers | Original evidence and answer keys; no need to upload to Firebase. Details in reports 02/03 |
| `database/firebase_import/upload_report_subjectA.json`, `upload_report_subjectB_{2024A,2024S,2025A,2025S,2026S,sample}.json` | Historical upload reports | A latest report covers 60 writes, not proof of all 460 live A records. Six B reports each record 20 successful writes. Reports do not prove current production contents |
| `database/firebase_import/subjectB_{2024A,2024S,2025A,2025S,2026S,sample}_upload_dry_run_report.json` | Historical preparation reports | Evidence of prior checks only. Do not execute upload scripts even in dry mode during this phase |
| `database/sorted/itpec_fe_2024A_mapping_review.md` | Markdown editorial mapping notes | Useful review context, but it says no low-confidence mappings while the current export contains one; current rows take priority |

### Implemented learning infrastructure

| Asset and exact path | Verified implementation | Dependencies / reuse judgment |
|---|---|---|
| `src/components/quiz/QuestionWorkspace.jsx` | Image/code reference pane, answer controls, previous/next, flag/save, feedback metadata, image zoom callback | React, Motion, `OptionCards`, motion helpers and CSS. Adapt props/styles for the textbook practice screen. It does not render full written answer explanations |
| `src/components/quiz/OptionCards.jsx` | Selection and correct/wrong answer states | React/Motion; variable letters supplied by parent. Reusable presentation |
| `src/components/quiz/QuizHeader.jsx`, `QuestionNavigationDrawer.jsx` | Quiz header and numbered navigation/filter/status UI | React/Motion and existing CSS. Extract with keyboard/focus review |
| `src/App.jsx` (`QuizScreen`, `ChapterQuizPage`, `ChaptersPage`, `ResultPage`, `RetryWrongPage`, `ProgressPage`) | Quiz state, timers, chapter practice, review, diagnosis and progress routes are wired | React Router, Firebase services and several internal helpers. Large 4,494-line integration file; selectively extract pure logic, not the whole app |
| `src/services/questionService.js` | Firestore published/exam queries, snake/camel normalization, Storage URL resolution, chapter filtering | Firebase Web SDK. Replace query/image transport with static files; preserve ID and variable-option semantics. `ChapterQuizPage` can fetch the full bank twice |
| `src/services/progressService.js` | Guest local progress, topic stats, wrong-question tracking, paper status, streaks, capped session history | Browser localStorage, `itpec:guestProgress:v1`, 50 sessions. Useful logic; add textbook locations, stable attempts and storage failure handling |
| `src/services/userProgressService.js` | User profile, guest/cloud merge, Firestore reads and batched saves | Firebase; `users/{uid}` plus learning/profile, topicStats, wrongQuestions, paperProgress, sessions. Adapt rather than copy conflict and account-boundary behavior |
| `src/services/savedQuestionService.js` | Guest saved questions and signed-in merge/write/remove | Local key `itpec:saved_questions:v1`; Firestore `users/{uid}/saved_questions`. Add deletion tombstones and UID-scoped local state |
| `src/services/authService.js`, `src/context/AuthContext.jsx` | Google popup sign-in/out; auth subscription; initial hydrate and sign-in sync; local fallback messaging | Firebase Auth and progress services. Useful provider wiring. Popup success/live authorized domains not tested |
| `src/firebase.js` | Firebase initialization from six `VITE_FIREBASE_*` fields; missing values throw at module load | SDK exports auth/db/storage. New static guest pages must not depend on Firebase configuration merely to load |
| `src/data/lectureResources.js`, `src/utils/lectureRecommendation.js` | 43 Subject A lessons; tags/keyword matching then chapter fallback | All 43 catalog URLs are Telegram. Reuse catalog as candidates, not as verified YouTube mappings |
| `src/data/subjectBLectureResources.js`, `src/utils/subjectBLectureRecommendation.js` | 20 sample-video resources, exact-ID and restricted similar-question matching | Depends on `database/analysis/subject_b_sample_similarity_map.json`. Reuse conservative matching rules; verify private-link accessibility |
| `database/analysis/subject_b_sample_similarity_map.json`, `subject_b_sample_question_taxonomy.md`, `subject_b_sample_similarity_report.md` | Curated sample taxonomy, 80 dated-paper classifications, 25 similar-match edges and exclusions | JSON is imported by runtime JS. Adapt into standalone content data; expand for 2026S explicitly |
| `src/components/SmartLectureCTA.jsx`, `src/utils/telegramLinks.js` | Correct/wrong/weak-area suggestions, mock-mode suppression, session display cap, Telegram app/web URLs | React/Motion; sessionStorage. Useful recommendation behavior; future free YouTube recommendations need new mappings |
| `src/data/courses.js`, `fullCourse.js`, `subjectAOldQuestion.js`, `subjectBCourse.js`; `src/components/courses/` | Existing course content and page components | Reference optional next-step offers; design a restrained placement after free learning support |
| `firestore.rules`, `storage.rules`, `tests/security-rules.test.js` | Public official content/read rules; owner-only private documents; official content writes denied; emulator assertions exist | Firebase emulators, `@firebase/rules-unit-testing`. Reuse security intent and tests, add schema/size validation and isolation tests |
| `index.html`, `src/App.jsx` (`SeoHead`), `public/sitemap.xml`, `public/robots.txt` | SPA shell, browser-updated metadata and SEO route listings | No pre-render plugin/server in Vite config. Reuse metadata ideas; generate real public chapter HTML in the new app |
| `docs/ui_v2_component_inventory.md`, `ui_v2_redesign_blueprint.md`, `ui_v2_implementation_plan.md` | Historical practice-site audit and plans | Helpful navigation, not proof of completed features or the approved textbook prototype |

### Processing tools

All paths below are under `database/builder/scripts/` unless stated. These were read, not executed, except the validator.

| Tool | Current function | Dependencies / future adaptation |
|---|---|---|
| `builder_common.py` | Registry loader, chapter constants, column aliases, stable IDs and paths | pandas; central reusable conventions. Some helper functions create directories when called |
| `crop_subject_a.py`, `crop_subject_b.py` | Locate PDF question boundaries, crop and stitch images, preserve overrides | PyMuPDF, Pillow, registry and manifests. Useful offline tools; rerunning writes output files |
| `generate_review_html.py` | Generate crop-review HTML | Builder helpers and local images. Writes files |
| `update_excel_with_image_paths.py` | Add crop metadata to source workbook with backup | pandas/openpyxl. Mutates workbooks; do not run against old repo |
| `build_master_subject_a_bank.py` | Enrich and validate source A rows; write XLSX/CSV/JSON master | pandas/openpyxl, registry; enforces A answer letters a-d and chapter labels |
| `prepare_firebase_import.py`, `prepare_subject_b_firebase_import.py` | Produce local Firebase payloads/manifests | pandas and builder helpers. Writes prepared files; replace Firebase payload output with versioned static output in a copied pipeline |
| `run_2025s_pipeline.py` | Orchestrate crop, workbook update, master and import preparation | Multiple mutating local steps; do not run in old repo |
| `validate_registered_exams.py` | Read-only **Subject A** registry/workbook/manifest/import validation | pandas/openpyxl. Despite its broad name it iterates only registered Subject A exams. Ran with `python -B`; passed |
| `audit_subject_a_questions.js` | Live Firestore question auditing through Admin SDK | Credentials/Firebase Admin; not used. Prefer local deterministic checks for this project |
| `upload_subject_a_to_firebase.js`, `upload_subject_b_to_firebase.js` | Upload images and merge documents into old `questions` collection | Firebase Admin, service-account path or supported auth, bucket configuration. Production mutation tools; do not copy active defaults into the new app |
| `database/build_2025s_subjecta_map.py` | Older exam-specific workbook mapping generator | pandas/openpyxl; inspect as historical reference, not the current canonical bank |

The old `package.json` specifies React `^19.2.3`, React Router `^7.10.1`, Vite `^7.3.0`, Firebase `^12.15.0`, Firebase Admin `^14.0.0`, Motion `^12.42.2`, Tailwind `^4.3.1`, and Lucide. These are manifest ranges, not a recommendation to install latest versions. Python requirements are unpinned (`pymupdf`, `pillow`, `pandas`, `openpyxl`, `firebase-admin`). Firebase Admin belongs only in any future offline tooling, never the public app bundle.

## Assumptions and unresolved evidence

- The old site's deployed release and live database may differ from the checked-out code and historical reports. Their current state was not inspected.
- The approved three-column textbook prototype may exist outside the two requested repositories. No matching HTML was found within them. `index.html`, `dist/index.html`, and crop-review HTML do not implement that prototype.
- Existing PDF annotations may reflect a learner's study work; their authorship, accuracy and publication rights are not established by file presence.

## Recommendations

Reuse a reviewed, versioned **copy** of the question/export/image/registry resources. Keep the new runtime independent of the old repository, production Firebase project, image bucket and deployment configuration. Preserve original IDs and original page references while introducing separate textbook/concept IDs. Selectively adapt quiz and recommendation components, and build textbook reading/content infrastructure separately. Reports [02](02_EXAM_DATA_AUDIT.md) and [03](03_TEXTBOOK_CONTENT_AUDIT.md) detail data and content readiness; [04](04_ARCHITECTURE_OPTIONS.md) compares the application architecture.
