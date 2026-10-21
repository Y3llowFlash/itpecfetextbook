import { createHash } from 'node:crypto';
import { readFile, readdir, mkdir, writeFile, rename, rm } from 'node:fs/promises';
import path from 'node:path';
import type { Question } from '../src/lib/models';

type Row = Record<string, any>;
export const digest = (data: Buffer | string) => createHash('sha256').update(data).digest('hex');

function ownedPath(outputRoot: string, relative: string) {
  const target = path.resolve(outputRoot, relative);
  const inside = path.relative(outputRoot, target);
  if (!inside || inside.startsWith('..') || path.isAbsolute(inside)) throw new Error('Unsafe generated-output path');
  return target;
}

export function selectPublished(rows: Row[]): Row[] {
  // This exact flag is the publication authority. Never fall back to isPublished.
  return rows.filter((row) => row.is_published === true);
}

export function webpDimensions(buffer: Buffer) {
  if (buffer.toString('ascii', 0, 4) !== 'RIFF' || buffer.toString('ascii', 8, 12) !== 'WEBP') throw new Error('Invalid WebP');
  const kind = buffer.toString('ascii', 12, 16);
  let width = 0, height = 0;
  if (kind === 'VP8X') {
    width = 1 + buffer.readUIntLE(24, 3); height = 1 + buffer.readUIntLE(27, 3);
  } else if (kind === 'VP8 ') {
    width = buffer.readUInt16LE(26) & 0x3fff; height = buffer.readUInt16LE(28) & 0x3fff;
  } else if (kind === 'VP8L') {
    const bits = buffer.readUInt32LE(21); width = 1 + (bits & 0x3fff); height = 1 + ((bits >>> 14) & 0x3fff);
  }
  if (!width || !height) throw new Error('Unsupported WebP dimensions');
  return { width, height };
}

export function normalizeQuestion(row: Row, dataset: string, image: Question['image']): Question {
  const id = String(row.question_id || '');
  if (!/^(?:\d{4}[AS]-(?:A|B|AM)|SAMPLE-B)-Q\d{3}$/.test(id)) throw new Error(`Invalid question ID: ${id}`);
  if (row.is_published !== true) throw new Error(`Unpublished question rejected: ${id}`);
  const options = row.answer_options || row.answerOptions || ['a', 'b', 'c', 'd'];
  const answer = String(row.correct_answer || '').toLowerCase();
  if (!Array.isArray(options) || !options.length || new Set(options).size !== options.length || !options.every((s) => /^[a-z]$/.test(s)) || !options.includes(answer)) throw new Error(`Invalid options/answer: ${id}`);
  if (!row.exam_id || !Number.isInteger(row.question_no) || !row.source_pdf || !row.source_page_start || !row.source_page_end) throw new Error(`Incomplete provenance: ${id}`);
  const mappingFields = ['book', 'chapter', 'chapter_name', 'section', 'topic', 'mapped_volume', 'mapped_chapter', 'mapped_section', 'mapped_topic', 'mapped_page', 'related_textbook_pages', 'confidence', 'notes', 'website_tag', 'tags'];
  const mapping = Object.fromEntries(mappingFields.filter((key) => key in row).map((key) => [key, row[key]]));
  return {
    id, examId: row.exam_id, number: row.question_no, year: row.year == null ? null : Number(row.year), season: row.season || '',
    subject: row.subject, paper: row.paper, format: row.format,
    sourceKind: row.exam_id === 'FE_B_SAMPLE' ? 'sample' : 'past_paper', examLabel: row.exam_label || '',
    correctAnswer: answer, options, is_published: true,
    chapter: row.chapter || '', section: row.section || '', topic: row.topic || '', mapping, image,
    source: { dataset, questionPdf: row.source_pdf, pageStart: row.source_page_start, pageEnd: row.source_page_end,
      originalImagePath: row.question_image_path, documentPath: row.firestore_path || `questions/${id}` },
  };
}

export function deduplicate(questions: Question[]) {
  const byId = new Map<string, Question>();
  for (const question of questions) {
    const previous = byId.get(question.id);
    if (previous && JSON.stringify(previous) !== JSON.stringify(question)) throw new Error(`Conflicting duplicate: ${question.id}`);
    byId.set(question.id, question);
  }
  return [...byId.values()].sort((a, b) => a.id.localeCompare(b.id));
}

export async function importQuestions(sourceRoot: string, outputRoot: string) {
  const source = path.resolve(sourceRoot), output = path.resolve(outputRoot);
  if (source === output || output.startsWith(source + path.sep)) throw new Error('Output must be separate from source');
  const inputDirectory = path.join(source, 'database', 'firebase_import');
  const files = (await readdir(inputDirectory)).filter((name) => /^questions_subject(?:A|B_[A-Za-z0-9]+)_firestore\.json$/.test(name)).sort();
  if (!files.length) throw new Error('No prepared question datasets found');
  const staged = ownedPath(output, '.local/question-import');
  const finalImages = ownedPath(output, 'public/questions');
  const finalQuestions = ownedPath(output, 'public/data/questions.json');
  const finalManifest = ownedPath(output, 'public/data/import-manifest.json');
  await rm(staged, { recursive: true, force: true });
  await mkdir(path.join(staged, 'questions'), { recursive: true });
  const questions: Question[] = [];
  const sources: { path: string; sha256: string; records: number; published: number }[] = [];
  let rejected = 0;
  for (const file of files) {
    const bytes = await readFile(path.join(inputDirectory, file));
    const rows = JSON.parse(bytes.toString('utf8').replace(/^\uFEFF/, '')) as Row[];
    if (!Array.isArray(rows)) throw new Error(`Expected array: ${file}`);
    const published = selectPublished(rows);
    rejected += rows.length - published.length;
    const dataset = `database/firebase_import/${file}`;
    sources.push({ path: dataset, sha256: digest(bytes), records: rows.length, published: published.length });
    for (const row of published) {
      const imagePath = path.resolve(source, row.question_image_path || '');
      if (!imagePath.startsWith(path.join(source, 'database', 'builder', 'output_images') + path.sep)) throw new Error('Image path outside approved source directory');
      const imageBytes = await readFile(imagePath);
      const hash = digest(imageBytes);
      const filename = `${row.question_id}.${hash.slice(0, 12)}.webp`;
      const question = normalizeQuestion(row, dataset, { src: `/questions/${filename}`, ...webpDimensions(imageBytes), sha256: hash });
      questions.push(question);
      await writeFile(path.join(staged, 'questions', filename), imageBytes);
    }
  }
  const unique = deduplicate(questions);
  const manifest = { version: 1, policy: 'is_published === true', total: unique.length,
    rejectedUnpublished: rejected, duplicatesRemoved: questions.length - unique.length, sources,
    questionIds: unique.map((q) => q.id), images: unique.map((q) => q.image.src), datasetHash: digest(JSON.stringify(unique)) };
  // Replace only importer-owned directories, after every input has passed validation.
  await mkdir(path.join(output, 'public', 'data'), { recursive: true });
  await writeFile(path.join(staged, 'questions.json'), JSON.stringify(unique, null, 2) + '\n');
  await writeFile(path.join(staged, 'manifest.json'), JSON.stringify(manifest, null, 2) + '\n');
  await rm(finalImages, { recursive: true, force: true });
  await rename(ownedPath(output, '.local/question-import/questions'), finalImages);
  await rename(ownedPath(output, '.local/question-import/questions.json'), finalQuestions);
  await rename(ownedPath(output, '.local/question-import/manifest.json'), finalManifest);
  return manifest;
}
