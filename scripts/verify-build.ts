import { readFile, readdir } from 'node:fs/promises';
import path from 'node:path';
import { digest } from './question-importer';
const root = path.resolve('dist');
const source = await readFile('public/data/questions.json');
const built = await readFile(path.join(root, 'data/questions.json'));
if (digest(source) !== digest(built)) throw new Error('Built question data differs from the validated snapshot');
const questions = JSON.parse(built.toString());
if (questions.some((q: { is_published: unknown }) => q.is_published !== true)) throw new Error('Unpublished record in production output');
const expected = new Set(questions.map((q: { image: { src: string } }) => path.basename(q.image.src)));
const images = await readdir(path.join(root, 'questions'));
if (images.length !== expected.size || images.some((filename) => !expected.has(filename))) throw new Error('Extra or missing question image in production output');
const reader = await readFile(path.join(root, 'chapters/hardware/memory-and-cache/index.html'), 'utf8');
if (!reader.includes('Why do computers need several kinds of memory?') || !reader.includes('data-concept="cache-memory"')) throw new Error('Static reader content/highlight missing');
const progress = await readFile(path.join(root, 'progress/index.html'), 'utf8');
if (!progress.includes('noindex,follow')) throw new Error('Private progress route is indexable');
for (const name of await readdir(path.join(root, '_astro'))) {
  if (!/\.(js|css)$/.test(name)) continue;
  const content = await readFile(path.join(root, '_astro', name), 'utf8');
  if (/itpec-fe-practice|demo-itpec-textbook|firebasestorage\.googleapis\.com|BEGIN (?:RSA )?PRIVATE KEY|free-video-/.test(content)) throw new Error(`Production dependency or credential/placeholder found: ${name}`);
}
console.log(`Production verified: ${questions.length} published records; ${images.length} approved image files; static reader and private progress metadata; no old Firebase dependencies.`);
