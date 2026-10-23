# Confirmed historical FE paper/subject policy

The owner's explicit **Morning / Subject A Metadata Integration** instruction of 23 October 2026 supersedes the earlier unknown-metadata proposal below. All 333 imported `Technology-01.pdf` questions are FE / Morning / Subject A. This is owner-confirmed information, not independently extracted paper/subject text.

The existing historical schema uses `examType: FE`, `paper: AM`, `subject: A`, `status: verified`, with owner-confirmation evidence. Existing Practice records retain their original paper values. Future explicitly declared Subject B uses the existing `B` paper/subject values and displays Evening / Subject B in the private header. No current historical record is Subject B.

New approved historical imports default to FE / Morning / Subject A. Explicit Subject B or source-specific metadata is preserved; contradictory declarations stop reconciliation. Year, season, filename and topic never select a subject. Initial reviews distinguish owner defaults, explicit owner declarations and source-specific evidence. Raw source fields remain separate.

The confirmation is bound to instruction SHA-256 `7789861b24ca233e1c0a22264029f9d7ff066eebf46e2edb6650425ab31da928`, the Technology-01 source checksum, all 333 canonical IDs and the `deccd08` snapshot. Prior metadata remains in history. No academic verification, grading eligibility, placement approval or publication approval is conferred.

All seven qualified owner decisions retain their restrictions, including both valid answers on page 119. Practice synchronization and authoritative-answer rules remain unchanged. See [metadata integration completion report](MORNING_METADATA_INTEGRATION.md).

## Earlier proposal, retained as superseded history

This proposal changes no metadata or publication rule. The 36-question local preview preserves `paper: null`, `subject: null`, FE owner-confirmation provenance, year, season, question number and source bindings. The live gate still requires evidenced paper and subject values plus separate owner publication approval.

| Consideration | Option A: retain the current strict requirement | Option B: separately approve documented unknown values |
|---|---|---|
| Source accuracy | Keep paper/subject pending until reliable source or explicitly evidenced owner confirmation establishes them. No guessing from dates, topics or filenames. | Introduce explicit provenance states such as `established`, `source-not-established` and `awaiting-review`. Unknown must be deliberately reviewed and source-bound, rather than silently treating missing data as complete. |
| Grading | Preserve independently verified answer evidence. Missing occurrence metadata continues to block publication even when a local answer can be checked correctly. | Metadata uncertainty does not verify an answer. Retain all academic, extraction, mapping and qualified-owner grading gates; the seven disputed selections remain outside this pilot. |
| Duplicate matching and Practice authority | Require reliable occurrence identity and source-image/content evidence before applying published Practice authority. Keep unresolved matches for review. | Never equate unknown with another paper/subject or use a nullable wildcard to merge records. Require additional occurrence/image evidence and manual review when paper identity is ambiguous. Preserve existing canonical IDs and Practice authority; no automatic rekeying or progress migration. |
| UI labels | Show FE (owner-confirmed), year, season and Q number; omit unknown fields or say “Paper/subject not established.” | Use the same truthful labels. Do not display Morning, Subject A, Technology or an invented exam edition. Clearly document what is and is not established. |
| Publication approval | Existing source-bound metadata and separate per-record publication approval remain mandatory. | Requires a separately approved policy, schema/validator changes, explicit owner acceptance of documented uncertainty, fresh publication fingerprints and per-record approval. Unknown metadata alone must never authorize publication. |
| Engineering implications | No gate/model changes; investigate evidence in a later milestone. | Design and test provenance-aware nullable metadata across validation, matching, UI, import, approval fingerprints and progression compatibility before any promotion. Preserve published records' stricter established identities. |

**Recommendation for this milestone:** retain Option A. Use the private preview to inspect student behavior while the owner considers whether Option B warrants a separate implementation proposal. Preview inclusion, answer submission and screenshots are not publication approval. No policy choice has been applied.
