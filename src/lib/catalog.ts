import { readFile } from 'node:fs/promises';
import path from 'node:path';
import definitions from '../content/concepts.json';
import explanations from '../content/explanations.json';
import type { Concept, Explanation, Question } from './models';

export const concepts = definitions as Concept[];
export const explanationMap = new Map(explanations.map((entry) => [entry.questionId, entry as Explanation]));
export async function publishedQuestions(): Promise<Question[]> {
  const data = JSON.parse(await readFile(path.resolve('public/data/questions.json'), 'utf8')) as Question[];
  return data.filter((question) => question.is_published === true);
}
export function questionsForConcept(concept: Concept, questions: Question[]) {
  const ids = new Set(concept.questionIds);
  return [...new Map(questions.filter((q) => q.is_published === true && ids.has(q.id)).map((q) => [q.id, q])).values()];
}
export function examTitle(question: Question) {
  if (question.sourceKind === 'sample') return 'FE-B sample';
  return `${question.year} ${question.season === 'S' ? 'Spring' : 'Autumn'} · ${question.paper === 'AM' ? 'Morning' : `Subject ${question.subject}`}`;
}
