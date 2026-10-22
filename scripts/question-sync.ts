/** Read-only planning precedes every write. The Practice repository is never an output. */
import { readFile, readdir } from 'node:fs/promises';
import path from 'node:path';
import { deduplicate, digest, normalizeQuestion, selectPublished, webpDimensions } from './question-importer';
import type { Question } from '../src/lib/models';
import { writeQuestionSnapshot } from './question-snapshot';

export function planSync(existing: Question[], incoming: Question[]) {
  const byId = new Map(existing.map(q => [q.id, q]));
  const additions: string[] = [], updates: string[] = [], conflicts: { id: string; reason: string }[] = [];
  for (const q of deduplicate(incoming)) {
    const old = byId.get(q.id);
    if (!old) {
      // An examination occurrence under another ID must be reviewed, never added twice.
      const candidates = existing.filter(p => p.number === q.number && (p.examId === q.examId || (q.year !== null && p.year === q.year && p.season === q.season && p.paper === q.paper && p.subject === q.subject)));
      if (candidates.length) { conflicts.push({ id: q.id, reason: `Occurrence already uses ${candidates.map(p => p.id).join(', ')}` }); continue; }
      additions.push(q.id); byId.set(q.id, q); continue;
    }
    const oldCore = { ...old, review: undefined, source: { ...old.source, dataset: '', originalImagePath: '', documentPath: '' } };
    const newCore = { ...q, review: undefined, source: { ...q.source, dataset: '', originalImagePath: '', documentPath: '' } };
    if (JSON.stringify(oldCore) !== JSON.stringify(newCore)) {
      conflicts.push({ id: q.id, reason: old.correctAnswer !== q.correctAnswer ? `Authoritative answer retained: ${old.correctAnswer}; incoming: ${q.correctAnswer}` : 'Published content or verified metadata changed; owner review required' });
    } else if (JSON.stringify(old.source) !== JSON.stringify(q.source)) {
      // Safe source-location update: preserve all verified fields, IDs, review and answers.
      byId.set(q.id, { ...old, source: { ...q.source } }); updates.push(q.id);
    }
  }
  const ids = new Set(incoming.map(q => q.id));
  const retained = existing.filter(q => !ids.has(q.id)).map(q => q.id);
  return { questions: [...byId.values()].sort((a,b) => a.id.localeCompare(b.id)), additions, updates, conflicts, retained };
}

export async function syncQuestions(sourceRoot: string, outputRoot: string, dryRun = false) {
  const source = path.resolve(sourceRoot), output = path.resolve(outputRoot);
  if (source === output || output.startsWith(source + path.sep)) throw new Error('Output must be separate from the Practice source repository');
  const input = path.join(source, 'database/firebase_import');
  const files = (await readdir(input)).filter(n => /^questions_subject(?:A|B_[A-Za-z0-9]+)_firestore\.json$/.test(n)).sort();
  if (!files.length) throw new Error('No prepared Practice datasets found');
  const incoming: Question[] = [], assets = new Map<string, Buffer>(), sources = [];
  let skipped = 0;
  for (const file of files) {
    const bytes = await readFile(path.join(input, file));
    const rows = JSON.parse(bytes.toString('utf8').replace(/^\uFEFF/, ''));
    if (!Array.isArray(rows)) throw new Error(`Expected array: ${file}`);
    const published = selectPublished(rows); skipped += rows.length - published.length;
    const dataset = `database/firebase_import/${file}`;
    sources.push({ path: dataset, sha256: digest(bytes), records: rows.length, published: published.length });
    for (const row of published) {
      const imagePath = path.resolve(source, row.question_image_path || '');
      if (!imagePath.startsWith(path.join(source, 'database/builder/output_images') + path.sep)) throw new Error('Image outside approved Practice image directory');
      const image = await readFile(imagePath), sha = digest(image);
      const filename = `${row.question_id}.${sha.slice(0,12)}.webp`;
      incoming.push(normalizeQuestion(row, dataset, { src: `/questions/${filename}`, ...webpDimensions(image), sha256: sha }));
      assets.set(filename, image);
    }
  }
  const catalogFile = path.join(output, 'public/data/questions.json');
  let existing: Question[];
  try { existing = JSON.parse(await readFile(catalogFile, 'utf8')); } catch (error) { if ((error as NodeJS.ErrnoException).code !== 'ENOENT') throw error; existing = []; }
  const plan = planSync(existing, incoming);
  const report = { dryRun, additions: plan.additions, updates: plan.updates, conflicts: plan.conflicts, skippedUnpublished: skipped, retainedWithoutSourcePublication: plan.retained, unchanged: existing.length - plan.updates.length, total: plan.questions.length, mappingReviewRequired: plan.additions };
  // Any conflict prevents the whole write: no partially applied catalog and no answer changes.
  if (dryRun || plan.conflicts.length || (!plan.additions.length && !plan.updates.length)) return report;
  const writes=new Map<string,Buffer|string>();
  for (const id of plan.additions) {
    const q = plan.questions.find(p => p.id === id)!;
    writes.set(`public${q.image.src}`,assets.get(path.basename(q.image.src))!);
  }
  // Old records and images are deliberately retained. Revocation needs explicit review.
  const sourceTotal = sources.reduce((n,s) => n+s.published,0);
  const retainedSource = plan.retained.length ? [{ path: 'retained-approved-catalog', sha256: digest(JSON.stringify(existing.filter(q => plan.retained.includes(q.id)))), records: plan.retained.length, published: plan.retained.length }] : [];
  const manifest = { version: 1, policy: 'is_published === true', total: plan.questions.length, rejectedUnpublished: skipped, duplicatesRemoved: sourceTotal + plan.retained.length - plan.questions.length, sources: [...sources, ...retainedSource], questionIds: plan.questions.map(q=>q.id), images: plan.questions.map(q=>q.image.src), datasetHash: digest(JSON.stringify(plan.questions)) };
  writes.set('public/data/questions.json',JSON.stringify(plan.questions,null,2)+'\n');
  writes.set('public/data/import-manifest.json',JSON.stringify(manifest,null,2)+'\n');
  await writeQuestionSnapshot(output,writes);
  return report;
}
