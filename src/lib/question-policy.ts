import type { Question } from './models';

export type SourceMembership = 'itpec-practice' | 'historical-pdf';
export interface QuestionSource {
  kind: SourceMembership; filename: string; sha256?: string; pages: number[];
  printedAnswer?: string; sourceId?: string;
}
export interface QuestionReview {
  examType: string | null;
  sources: QuestionSource[];
  answerVerification: 'unverified' | 'verified' | 'conflict' | 'needs-review';
  mappingStatus: 'verified' | 'proposed' | 'needs-review';
  extractionQuality: 'complete' | 'partial' | 'failed';
  reviewStatus: 'needs-review' | 'approved';
  publicationStatus: 'unapproved' | 'published';
  mappings: { chapterId: string; sectionId: string; subsectionId: string; conceptId: string; headingNumber: string }[];
  approvalFingerprint?: string;
  discrepancies?: { authoritativeAnswer: string; printedAnswer: string; sourceId: string }[];
}
export const FILTER_KEY = 'itpecTextbook:questionFilters:v1';
export interface QuestionFilters { from: number | null; to: number | null; source: 'all' | SourceMembership; unanswered: boolean }
export const DEFAULT_FILTERS: QuestionFilters = { from: null, to: null, source: 'all', unanswered: false };
export function parseFilters(value: unknown): QuestionFilters {
  const v = value && typeof value === 'object' ? value as Partial<QuestionFilters> : {};
  const year = (n: unknown) => Number.isInteger(n) && Number(n) >= 1900 && Number(n) <= 2200 ? Number(n) : null;
  return { from: year(v.from), to: year(v.to), source: v.source === 'itpec-practice' || v.source === 'historical-pdf' ? v.source : 'all', unanswered: v.unanswered === true };
}
export function questionSources(q: Question): SourceMembership[] {
  return q.review ? [...new Set(q.review.sources.map(s => s.kind))] : ['itpec-practice'];
}
export function publishedYears(questions: Question[]): number[] {
  return [...new Set(questions.filter(q => q.is_published === true && Number.isInteger(q.year)).map(q => q.year!))].sort((a,b) => a-b);
}
export function filterQuestions(questions: Question[], filters: QuestionFilters, answered: ReadonlySet<string>): Question[] {
  if (filters.from !== null && filters.to !== null && filters.from > filters.to) return [];
  return [...new Map(questions.filter(q => q.is_published === true &&
    (filters.from === null || (q.year !== null && q.year >= filters.from)) &&
    (filters.to === null || (q.year !== null && q.year <= filters.to)) &&
    (filters.source === 'all' || questionSources(q).includes(filters.source)) &&
    (!filters.unanswered || !answered.has(q.id))).map(q => [q.id, q])).values()];
}
export function questionLabel(q: Question) {
  if (q.sourceKind === 'sample') return q.examLabel || 'FE-B sample';
  return `${q.year ?? 'Year unknown'} ${q.season === 'S' ? 'Spring' : q.season === 'A' ? 'Autumn' : q.season} · ${q.paper === 'AM' ? 'Morning' : `Subject ${q.subject}`}`;
}

export interface MatchCandidate {
  id: string; examType: string | null; year: number | null; season: string | null; number: number;
  contentSha256?: string; imageSha256?: string; answer: string | null;
}
export function matchOccurrence(incoming: MatchCandidate, catalog: MatchCandidate[]) {
  const occurrence = catalog.filter(q => incoming.year !== null && incoming.season && q.year === incoming.year && q.season === incoming.season && q.number === incoming.number);
  const candidates = occurrence.filter(q => incoming.examType && q.examType === incoming.examType);
  const identical = (q: MatchCandidate) => Boolean((incoming.contentSha256 && incoming.contentSha256 === q.contentSha256) || (incoming.imageSha256 && incoming.imageSha256 === q.imageSha256));
  if (candidates.length === 1 && identical(candidates[0])) return { status: 'matched' as const, canonicalId: candidates[0].id, answer: candidates[0].answer, conflict: incoming.answer !== candidates[0].answer };
  if (occurrence.length || catalog.some(q => identical(q))) return { status: 'needs-review' as const, candidateIds: [...new Set([...occurrence, ...catalog.filter(identical)].map(q => q.id))] };
  return { status: 'distinct' as const };
}
