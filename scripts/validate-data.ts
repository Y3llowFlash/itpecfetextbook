import { readFile, readdir } from 'node:fs/promises';
import path from 'node:path';
import { digest, webpDimensions } from './question-importer';
import { concepts, explanationMap, publishedQuestions, questionsForConcept } from '../src/lib/catalog';

const root = path.resolve('.');
const questions = await publishedQuestions();
const raw = JSON.parse(await readFile(path.join(root, 'public/data/questions.json'), 'utf8'));
if (questions.length !== raw.length || new Set(questions.map((q) => q.id)).size !== questions.length) throw new Error('All published records must be unique and explicitly is_published === true');
const manifest = JSON.parse(await readFile(path.join(root, 'public/data/import-manifest.json'), 'utf8'));
if (manifest.policy !== 'is_published === true' || manifest.total !== questions.length || manifest.datasetHash !== digest(JSON.stringify(questions))) throw new Error('Import manifest does not match the published snapshot');
if (manifest.sources.reduce((sum: number, source: { published: number }) => sum + source.published, 0) - manifest.duplicatesRemoved !== questions.length) throw new Error('Published source totals do not reconcile');
const imageNames = await readdir(path.join(root, 'public/questions'));
if (imageNames.length !== questions.length) throw new Error('Unexpected images in the public question directory');
for (const question of questions) {
  if (!question.options.includes(question.correctAnswer) || !question.source.questionPdf || !question.source.pageStart) throw new Error(`Invalid published record ${question.id}`);
  const image = await readFile(path.join(root, 'public', question.image.src));
  const dimensions = webpDimensions(image);
  if (digest(image) !== question.image.sha256 || dimensions.width !== question.image.width || dimensions.height !== question.image.height) throw new Error(`Image mismatch: ${question.id}`);
}
for (const concept of concepts) {
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
console.log(`Validated ${questions.length} published questions, ${imageNames.length} matching image hashes, and ${concepts.length} concept with ${concepts[0].questionIds.length} reviewed questions.`);
