import { readFile, readdir, stat } from 'node:fs/promises';
import path from 'node:path';
import { digest } from './question-importer';
import { hardwareLessons } from '../src/lib/lessons';
import {CPU_PATH,CACHE_HEADING} from '../src/lib/reading-routes';
import { concepts } from '../src/lib/catalog';
import { validateSourceRelease, sourceAssets } from './source-release';
import { assertPublicationBoundary, assertApprovedPublicFile } from './publication-boundary';
import {coverAssets,validateLandingAssets,validateLandingPage} from './landing-assets';
const root = path.resolve('dist');
const source = await readFile('public/data/questions.json');
const built = await readFile(path.join(root, 'data/questions.json'));
if (digest(source) !== digest(built)) throw new Error('Built question data differs from the validated snapshot');
const questions = JSON.parse(built.toString());
if (questions.some((q: { is_published: unknown }) => q.is_published !== true)) throw new Error('Unpublished record in production output');
const expected = new Set(questions.map((q: { image: { src: string } }) => path.basename(q.image.src)));
const images = await readdir(path.join(root, 'questions'));
if (images.length !== expected.size || images.some((filename) => !expected.has(filename))) throw new Error('Extra or missing question image in production output');
const reader = await readFile(path.join(root, 'chapters/hardware/cpu-and-main-memory/index.html'), 'utf8');
const legacyReader=await readFile(path.join(root,'chapters/hardware/memory-and-cache/index.html'),'utf8');
if(!legacyReader.includes('data-legacy-reader')||!legacyReader.includes(`${CPU_PATH}#${CACHE_HEADING}`)||legacyReader.includes('class="reader-prose source-book"'))throw new Error('Legacy cache route must link to the canonical source subsection without duplicating the reader');
if (!reader.includes('data-source-release="fev1-201504-ch1-r1"') || !reader.includes('data-concept="cache-memory"')) throw new Error('Source reader content/highlight missing');
for (const lesson of hardwareLessons.slice(0,5)) {
  const html = await readFile(path.join(root, 'chapters/hardware', lesson.slug, 'index.html'), 'utf8');
  if (!html.includes(`data-section-id="${lesson.id}"`) || !html.includes('class="source-badge"')) throw new Error(`Missing lesson/page badge: ${lesson.slug}`);
  if (/Planned for a later update|Coming later/.test(html)) throw new Error(`Incomplete chapter navigation in ${lesson.slug}`);
}
for (const concept of concepts) {
  const html = await readFile(path.join(root, 'practice', concept.id, 'index.html'), 'utf8');
  for (const id of concept.questionIds) if (!html.includes(id)) throw new Error(`Missing reviewed practice question ${id}`);
}
const publicFiles = await readdir(root, { recursive: true });
const allowedHtml=new Set(['index.html','404.html','progress/index.html','practice/index.html','chapters/hardware/index.html',
  ...hardwareLessons.map((lesson)=>`chapters/hardware/${lesson.slug}/index.html`),
  ...concepts.map((concept)=>`practice/${concept.id}/index.html`)]);
if (publicFiles.some((name) => /\.(?:pdf|env|py|mjs)$/.test(name) || name.includes('hardware-review'))) throw new Error('Source/editorial material leaked into public output');
// Closed asset allowlist: published exam images, favicon and the approved
// hash-verified source illustrations. Raw editorial exports remain excluded.
for (const name of publicFiles) {
  if((await stat(path.join(root,name))).isDirectory())continue;
  assertApprovedPublicFile(name,allowedHtml,expected as Set<string>,new Set(sourceAssets.keys()),new Set(coverAssets.keys()));
  assertPublicationBoundary(name, /\.(?:html|json|js|css)$/.test(name)?await readFile(path.join(root,name),'utf8'):undefined,allowedHtml);
  if (/\.(?:webp|png|jpe?g|gif|avif|svg)$/i.test(name) && name !== 'favicon.svg' && !sourceAssets.has(name.replaceAll('\\','/')) && !coverAssets.has(name.replaceAll('\\','/')) && !(name.startsWith(`questions${path.sep}`) && expected.has(path.basename(name)))) throw new Error(`Unapproved public illustration: ${name}`);
  if (/chapter1-inventory|gallery\.html|originals\.html|(?:^|[\\/])crops(?:[\\/]|$)|suggested-manifest/.test(name)) throw new Error('Editorial source material in public output');
}
const progress = await readFile(path.join(root, 'progress/index.html'), 'utf8');
if (!progress.includes('noindex,follow')) throw new Error('Private progress route is indexable');
for (const name of await readdir(path.join(root, '_astro'))) {
  if (!/\.(js|css)$/.test(name)) continue;
  const content = await readFile(path.join(root, '_astro', name), 'utf8');
  if (/itpec-fe-practice|demo-itpec-textbook|firebasestorage\.googleapis\.com|BEGIN (?:RSA )?PRIVATE KEY|free-video-/.test(content)) throw new Error(`Production dependency or credential/placeholder found: ${name}`);
}
await validateSourceRelease(root);
await validateLandingAssets(root);await validateLandingPage(root);
console.log(`Production verified: ${questions.length} published records; ${images.length} approved exam images; approved Chapter 1 source reader; private progress metadata.`);
