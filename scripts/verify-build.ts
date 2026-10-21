import { readFile, readdir, stat } from 'node:fs/promises';
import path from 'node:path';
import { digest } from './question-importer';
import { hardwareLessons, pageLabel } from '../src/lib/lessons';
import { concepts } from '../src/lib/catalog';
import { hardwareFigures, figurePageLabel } from '../src/lib/figures';
import { assertPublicationBoundary, assertApprovedPublicFile } from './publication-boundary';
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
for (const lesson of hardwareLessons) {
  const html = await readFile(path.join(root, 'chapters/hardware', lesson.slug, 'index.html'), 'utf8');
  if (!html.includes(`data-section-id="${lesson.id}"`) || !html.includes(`Original textbook · ${pageLabel(lesson.pages)}`)) throw new Error(`Missing lesson/page badge: ${lesson.slug}`);
  for (const heading of lesson.headings) if (!html.includes(`data-source-ref="${heading.id}"`)) throw new Error(`Missing printed reference: ${heading.id}`);
  if (/Planned for a later update|Coming later/.test(html)) throw new Error(`Incomplete chapter navigation in ${lesson.slug}`);
  for (const figure of hardwareFigures.filter((f) => f.lesson === lesson.slug)) {
    if (!html.includes(`data-original-figure="${figure.id}"`) || !html.includes(`Original textbook · ${figurePageLabel(figure.sourcePages)}`) || !html.includes(`id="${figure.id}-desc"`)) throw new Error(`Missing original diagram/source/description: ${figure.id}`);
  }
}
for (const concept of concepts) {
  const html = await readFile(path.join(root, 'practice', concept.id, 'index.html'), 'utf8');
  for (const id of concept.questionIds) if (!html.includes(id)) throw new Error(`Missing reviewed practice question ${id}`);
}
const publicFiles = await readdir(root, { recursive: true });
const allowedHtml=new Set(['index.html','404.html','progress/index.html','chapters/hardware/index.html',
  ...hardwareLessons.map((lesson)=>`chapters/hardware/${lesson.slug}/index.html`),
  ...concepts.map((concept)=>`practice/${concept.id}/index.html`)]);
if (publicFiles.some((name) => /\.(?:pdf|env|py|mjs)$/.test(name) || name.includes('hardware-review'))) throw new Error('Source/editorial material leaked into public output');
// Exact asset allowlist: new teaching figures are inline vectors; the existing
// published exam images and favicon are the only public image files.
for (const name of publicFiles) {
  if((await stat(path.join(root,name))).isDirectory())continue;
  assertApprovedPublicFile(name,allowedHtml,expected as Set<string>);
  assertPublicationBoundary(name, /\.(?:html|json|js|css)$/.test(name)?await readFile(path.join(root,name),'utf8'):undefined,allowedHtml);
  if (/\.(?:webp|png|jpe?g|gif|avif|svg)$/i.test(name) && name !== 'favicon.svg' && !(name.startsWith(`questions${path.sep}`) && expected.has(path.basename(name)))) throw new Error(`Unapproved public illustration: ${name}`);
  if (/chapter1-inventory|gallery\.html|originals\.html|(?:^|[\\/])crops(?:[\\/]|$)|suggested-manifest/.test(name)) throw new Error('Editorial source material in public output');
}
const progress = await readFile(path.join(root, 'progress/index.html'), 'utf8');
if (!progress.includes('noindex,follow')) throw new Error('Private progress route is indexable');
for (const name of await readdir(path.join(root, '_astro'))) {
  if (!/\.(js|css)$/.test(name)) continue;
  const content = await readFile(path.join(root, '_astro', name), 'utf8');
  if (/itpec-fe-practice|demo-itpec-textbook|firebasestorage\.googleapis\.com|BEGIN (?:RSA )?PRIVATE KEY|free-video-/.test(content)) throw new Error(`Production dependency or credential/placeholder found: ${name}`);
}
console.log(`Production verified: ${questions.length} published records; ${images.length} approved image files; static reader and private progress metadata; no old Firebase dependencies.`);
