import { readFile, readdir } from 'node:fs/promises';
import path from 'node:path';
import { digest, webpDimensions } from './question-importer';
import { concepts, explanationMap, publishedQuestions, questionsForConcept } from '../src/lib/catalog';
import { hardwareLessons, lessonPath } from '../src/lib/lessons';
import sourceEvidence from '../docs/development/evidence/hardware-printed-pages.json';
import { validateSourceRelease } from './source-release';
import release from '../src/content/hardware-source-release.json';
import { applyQuestionHighlights } from '../src/lib/question-highlights';
import { presentSourceHTML } from '../src/lib/reader-presentation';
import { validateHistoricalRelease } from './historical-release-integrity';
import historicalRelease from '../docs/development/evidence/historical-release-36.json';

const root = path.resolve('.');
const questions = await publishedQuestions();
const raw = JSON.parse(await readFile(path.join(root, 'public/data/questions.json'), 'utf8'));
validateHistoricalRelease(raw, [...explanationMap.values()], concepts, historicalRelease);
if (questions.length !== raw.length || new Set(questions.map((q) => q.id)).size !== questions.length) throw new Error('All published records must be unique and explicitly is_published === true');
const manifest = JSON.parse(await readFile(path.join(root, 'public/data/import-manifest.json'), 'utf8'));
if (manifest.policy !== 'is_published === true' || manifest.total !== questions.length || manifest.datasetHash !== digest(JSON.stringify(questions))) throw new Error('Import manifest does not match the published snapshot');
if (manifest.sources.reduce((sum: number, source: { published: number }) => sum + source.published, 0) - manifest.duplicatesRemoved !== questions.length) throw new Error('Published source totals do not reconcile');
const imageNames = await readdir(path.join(root, 'public/questions'));
if (imageNames.length !== questions.length) throw new Error('Unexpected images in the public question directory');
for (const question of questions) {
  if (question.review?.sources.some(source=>source.kind==='historical-pdf') && (question.review.reviewStatus!=='approved' || question.review.publicationStatus!=='published' || !question.review.approvalFingerprint || question.review.extractionQuality!=='complete')) throw new Error(`Unapproved historical record: ${question.id}`);
  if (!question.options.includes(question.correctAnswer) || !question.source.questionPdf || !question.source.pageStart) throw new Error(`Invalid published record ${question.id}`);
  const image = await readFile(path.join(root, 'public', question.image.src));
  const dimensions = webpDimensions(image);
  if (digest(image) !== question.image.sha256 || dimensions.width !== question.image.width || dimensions.height !== question.image.height) throw new Error(`Image mismatch: ${question.id}`);
}
for (const concept of concepts) {
  if (!hardwareLessons.some((lesson) => lesson.id === concept.sectionId && lessonPath(lesson) === concept.sectionUrl)) throw new Error(`Invalid concept reading destination: ${concept.id}`);
  const lesson = hardwareLessons.find((lesson) => lesson.id === concept.sectionId)!;
  if (!release.unanchoredConcepts.includes(concept.id) && !applyQuestionHighlights(presentSourceHTML(await readFile(`src/content/source-hardware/${lesson.slug}.html`, 'utf8')),concepts,questions).includes(`data-concept="${concept.id}"`)) throw new Error(`Concept lacks an exact source annotation: ${concept.id}`);
  const linked = questionsForConcept(concept, questions);
  if (new Set(concept.questionIds).size !== concept.questionIds.length || linked.length !== concept.questionIds.length || !linked.length) throw new Error(`Missing/unpublished concept question: ${concept.id}`);
  for (const question of linked) {
    const explanation = explanationMap.get(question.id);
    if (!explanation || explanation.answer !== question.correctAnswer || !explanation.steps.length || question.options.some((id) => !explanation.optionText[id])) throw new Error(`Missing or inconsistent explanation: ${question.id}`);
    if (!concept.mappingEvidence.some((edge) => edge.questionId === question.id && edge.reviewedAgainst.includes('original question image'))) throw new Error(`Unreviewed mapping: ${question.id}`);
  }
  for (const video of concept.videos) {
    const url = new URL(video.url);
    if (url.protocol !== 'https:' || !['t.me', 'www.youtube.com', 'youtube.com', 'youtu.be'].includes(url.hostname)) throw new Error('Unapproved video link');
  }
}
const printed = new Set(sourceEvidence.pages.map((page) => page.printedPage).filter((page) => page !== null));
for (const lesson of hardwareLessons) {
  if (lesson.editionId !== sourceEvidence.editionId || !release.lessons.some(entry=>entry.id===lesson.id&&entry.slug===lesson.slug)) throw new Error(`Lesson edition/ID mismatch: ${lesson.slug}`);
  for (const reference of [lesson, ...lesson.headings]) {
    const [first, last = first] = reference.pages;
    if (!Number.isInteger(first) || last < first || first < 13 || last > 111) throw new Error(`Invalid printed range: ${lesson.slug}`);
    for (let page = first; page <= last; page++) if (!printed.has(page)) throw new Error(`Unverified printed page: ${page}`);
  }
}
const linkedIds = new Set(concepts.flatMap((concept) => concept.questionIds));
if (explanationMap.size !== linkedIds.size) throw new Error('Unassociated or duplicate explanations');
console.log(`Validated ${questions.length} published questions, ${imageNames.length} matching image hashes, ${hardwareLessons.length} lessons, and ${concepts.length} concepts linking ${linkedIds.size} distinct reviewed questions.`);
await validateSourceRelease();
