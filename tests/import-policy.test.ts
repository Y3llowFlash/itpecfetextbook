// @vitest-environment node
import { afterEach, describe, expect, it } from 'vitest';
import { mkdtemp, mkdir, writeFile, readFile, readdir, rm } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { deduplicate, importQuestions, normalizeQuestion, selectPublished, webpDimensions } from '../scripts/question-importer';

const roots: string[] = [];
afterEach(async () => {
  for (const root of roots.splice(0)) {
    if (!path.resolve(root).startsWith(path.resolve(os.tmpdir()) + path.sep)) throw new Error('Unsafe test cleanup');
    await rm(root, { recursive: true, force: true });
  }
});
const image = Buffer.alloc(30);
image.write('RIFF', 0); image.write('WEBP', 8); image.write('VP8X', 12); image.writeUIntLE(15, 24, 3); image.writeUIntLE(7, 27, 3);
const row = { question_id: '2024A-A-Q009', is_published: true, exam_id: '2024A_FE_A', question_no: 9, year: 2024, season: 'A', subject: 'A', paper: 'A', format: 'subject_a', correct_answer: 'b', source_pdf: 'database/raw/exam.pdf', source_page_start: 8, source_page_end: 8, question_image_path: 'database/builder/output_images/question_images/a.webp', chapter: 'Chapter 1 Hardware', section: 'High speed memory', topic: 'Cache access time' };
const asset = { src: '/questions/example.webp', width: 16, height: 8, sha256: 'hash' };

describe('published-only import boundary', () => {
  it('accepts only literal true on the required snake-case flag', () => {
    const rows = [{ is_published: true }, { is_published: false, isPublished: true }, { is_published: 'true' }, { is_published: 1 }, { isPublished: true }, {}];
    expect(selectPublished(rows)).toEqual([rows[0]]);
  });
  it('refuses unpublished normalization even when the frontend alias is true', () => {
    expect(() => normalizeQuestion({ ...row, is_published: false, isPublished: true }, 'fixture.json', asset)).toThrow('Unpublished');
  });
  it('retains source identifiers, answer options and original mapping fields', () => {
    const q = normalizeQuestion({ ...row, answer_options: ['a', 'b', 'c', 'd', 'e', 'f'], correct_answer: 'f', mapped_page: 'PDF p75-76', confidence: 'High' }, 'fixture.json', asset);
    expect(q.id).toBe(row.question_id); expect(q.correctAnswer).toBe('f'); expect(q.options).toHaveLength(6);
    expect(q.mapping.mapped_page).toBe('PDF p75-76'); expect(q.source.pageStart).toBe(8);
    expect(() => normalizeQuestion({ ...row, correct_answer: 'z' }, 'fixture.json', asset)).toThrow('Invalid options');
  });
  it('deduplicates identical IDs and rejects conflicting answers', () => {
    const q = normalizeQuestion(row, 'fixture.json', asset);
    expect(deduplicate([q, q])).toHaveLength(1);
    expect(() => deduplicate([q, { ...q, correctAnswer: 'a' }])).toThrow('Conflicting duplicate');
  });
  it('extracts image dimensions and rejects invalid image data', () => {
    expect(webpDimensions(image)).toEqual({ width: 16, height: 8 });
    expect(() => webpDimensions(Buffer.from('not a WebP image'))).toThrow('Invalid WebP');
  });
  it('never reads/copies an unpublished image and removes a stale importer-owned image', async () => {
    const root = await mkdtemp(path.join(os.tmpdir(), 'itpec-import-test-')); roots.push(root);
    const source = path.join(root, 'source'), output = path.join(root, 'output');
    await mkdir(path.join(source, 'database/firebase_import'), { recursive: true });
    await mkdir(path.join(source, 'database/builder/output_images/question_images'), { recursive: true });
    await writeFile(path.join(source, row.question_image_path), image);
    const unpublished = { ...row, question_id: '2023A-AM-Q002', is_published: false, isPublished: true, question_image_path: 'database/builder/output_images/nonexistent-unpublished.webp' };
    const input = JSON.stringify([row, unpublished]);
    await writeFile(path.join(source, 'database/firebase_import/questions_subjectA_firestore.json'), input);
    await mkdir(path.join(output, 'public/questions'), { recursive: true });
    await writeFile(path.join(output, 'public/questions/stale.webp'), image);
    const report = await importQuestions(source, output);
    expect(report.total).toBe(1); expect(report.rejectedUnpublished).toBe(1);
    expect((await readdir(path.join(output, 'public/questions')))).toHaveLength(1);
    expect((await readFile(path.join(output, 'public/data/questions.json'), 'utf8'))).not.toContain('2023A-AM-Q002');
    expect(await readFile(path.join(source, 'database/firebase_import/questions_subjectA_firestore.json'), 'utf8')).toBe(input);
    // Reimporting a snapshot is deterministic and safely replaces its own files.
    expect((await importQuestions(source, output)).datasetHash).toBe(report.datasetHash);
  });
});
