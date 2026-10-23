/** Validate the owner-authorized published payload without private source files. */
import { createHash } from 'node:crypto';

export function canonical(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`;
  if (value && typeof value === 'object') return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${canonical((value as Record<string, unknown>)[key])}`).join(',')}}`;
  return JSON.stringify(value);
}
export const checksum = (value: unknown) => createHash('sha256').update(canonical(value)).digest('hex');

export function validateHistoricalRelease(questions: any[], explanations: any[], concepts: any[], receipt: any) {
  if (receipt.schema !== 'itpec-historical-release-v1' || receipt.authorizedCount !== 36 || receipt.records.length !== 36 || receipt.excludedUnapproved !== 297) throw Error('Invalid first historical release authorization scope');
  const ids = new Set<string>(receipt.records.map((r: any) => r.id));
  const historical = questions.filter(q => q.format === 'historical' || q.review?.sources.some((s: any) => s.kind === 'historical-pdf'));
  if (ids.size !== 36 || historical.length !== 36 || historical.some(q => !ids.has(q.id)) || questions.length !== receipt.total || receipt.total !== 456) throw Error('Unauthorized historical publication');
  const practice = Object.fromEntries(questions.filter(q => !ids.has(q.id)).map(q => [q.id, q]));
  if (Object.keys(practice).length !== 420 || checksum(practice) !== receipt.practiceRecordsSha256) throw Error('Original authoritative Practice catalog changed');
  const counts: Record<string, number> = {};
  for (const approved of receipt.records) {
    const q = questions.find(q => q.id === approved.id), e = explanations.find(e => e.questionId === approved.id);
    if (!q || !e || checksum(q) !== approved.questionSha256 || checksum(e) !== approved.explanationSha256 || checksum(q.review.mappings) !== approved.mappingSha256 || q.review.approvalFingerprint !== approved.approvalFingerprint || q.image.sha256 !== approved.imageSha256) throw Error(`Published approval payload changed: ${approved.id}`);
    if (q.correctAnswer !== e.answer || q.paper !== 'AM' || q.subject !== 'A' || q.review.examType !== 'FE' || q.review.reviewStatus !== 'approved' || q.review.publicationStatus !== 'published') throw Error(`Invalid grading/metadata/approval: ${approved.id}`);
    const links = concepts.filter(c => c.questionIds.includes(approved.id));
    if (links.length !== 1 || links[0].id !== approved.conceptId || q.review.mappings[0].conceptId !== approved.conceptId) throw Error(`Approved concept placement changed: ${approved.id}`);
    counts[approved.conceptId] = (counts[approved.conceptId] || 0) + 1;
  }
  if (checksum(counts) !== checksum(receipt.conceptCounts)) throw Error('Seven-concept authorization distribution changed');
}
