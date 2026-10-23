# Private accessibility corrections: historical PDF pages 22 and 28

Both descriptions were checked visually against freshly rendered original `Technology-01.pdf` pages and the unchanged question crops. Only accessible diagram descriptions and the defective option transcription are corrected. Academic answers, summaries, worked steps, takeaways, image bytes, canonical IDs, progress keys and publication statuses are preserved.

| Physical PDF page | Corrected accessible content | Validation |
|---|---|---|
| 22 | Directed instruction-storage sequence, position of main memory outside the processor, and both components inside the processor boundary | Original labels, both right-pointing arrows and enclosing box checked visually |
| 28 | Both input branches, upper AND/lower OR gates, final OR connections, branch dots and crossing without a junction; removed trailing diagram input labels from option D | Original gate shapes, wiring, absence of inversion bubbles and all four option expressions checked visually |

The private correction ledger is `.local/private-student-preview/accessibility-repairs.json`. It retains before/after accessible fields, structured diagram evidence and original PDF/content/review/image checksum bindings. The pipeline rejects stale bindings, an expanded repair scope, unrelated choice edits and academic fields in the correction payload. The two preserved findings are resolved only with matching validated repair hashes; their original pending history is archived in `accessibility-review/findings-before.json`.

The overlay applies to the private preview projection. All 333 original academic review objects and preserved audit snapshots remain unchanged. Any future publication preparation must explicitly consume the validated corrections; the public catalog has not been modified. Preparation and integrity checking require the ledger and findings as private inputs.

Editorial findings and their former warning text stay in the editor-only manifest/report. They are excluded from student props and practice screens. Build checks reject leaked QA notices; browser checks cover the accessible transcript, exact option D label, enlarged-image alternative text, and denial of requests for private correction/history files.

Validation for this repair:

- 133 Python tests passed, including 15 preview tests covering source/snapshot binding, allowed field changes, resolution gating, repeatability and preservation.
- 49 private browser tests passed, including all 36 original image hashes/answers/worked explanations, the two corrected transcriptions, mobile enlargement and reading restoration.
- Production and private Astro/TypeScript checks passed with zero errors, warnings or hints.
- Production build passed with the existing 420 public questions and matching images. No private historical data was added.
- All 36 source crops passed fresh PDF pixel comparison. Repeated private generation preserved identical projected data and asset hashes.
- All 1,491 protected original catalog/source/application files retained their bytes and modification times; 326 independently verified answers and seven qualified owner adjudications remain intact, with zero publication approvals.

Full before/after text, bindings, source renders, screenshots and a focused integrity report remain under `.local/private-student-preview/accessibility-review/`. The private visual gallery and 36-question completion report have been updated. Nothing was published, deployed or merged into main.
