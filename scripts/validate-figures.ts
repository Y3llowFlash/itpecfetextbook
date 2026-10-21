import { readFile, readdir } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import inventory from '../docs/development/figures/chapter1-inventory.json';
import evidence from '../docs/development/evidence/hardware-printed-pages.json';
import { hardwareFigures } from '../src/lib/figures';
import { hardwareLessons } from '../src/lib/lessons';

export async function validateFigures() {
  if (inventory.sourceReuseAuthorized !== false || inventory.editionId !== evidence.editionId) throw new Error('Unexpected source publication policy/edition');
  const regions = new Map(inventory.regions.map((region) => [region.id, region]));
  if (regions.size !== inventory.regions.length || inventory.pageReview.length !== 99) throw new Error('Incomplete/duplicate figure inventory');
  for (let printedPage = 13; printedPage <= 111; printedPage++) {
    const review = inventory.pageReview.find((page) => page.printedPage === printedPage);
    if (!review || review.pdfPage !== evidence.pages.find((p) => p.printedPage === printedPage)?.pdfPage) throw new Error('Incorrect page review');
    const expected = inventory.regions.filter((region) => region.printedPage === printedPage).map((r) => r.id).sort();
    if (JSON.stringify([...review.regions].sort()) !== JSON.stringify(expected)) throw new Error('Figure inventory/page review mismatch');
  }
  const ids = new Set(hardwareFigures.map((f) => f.id));
  if (ids.size !== hardwareFigures.length) throw new Error('Duplicate original figure ID');
  const assets = await readdir('src/assets/hardware');
  if (assets.length !== hardwareFigures.length || assets.some((name) => !hardwareFigures.some((f) => f.asset === name))) throw new Error('Unapproved figure asset');
  for (const figure of hardwareFigures) {
    if (!/^[a-z0-9-]+\.svg$/.test(figure.asset) || figure.authorship !== 'authored-original' || figure.sourceReuse || !figure.alt || !figure.caption || figure.editionId !== evidence.editionId) throw new Error(`Unapproved original: ${figure.id}`);
    const lesson = hardwareLessons.find((lesson) => lesson.slug === figure.lesson);
    const content = await readFile(`src/content/hardware/${figure.lesson}.md`, 'utf8');
    if (!lesson || !content.includes(`id="${figure.after}"`)) throw new Error(`Missing immediate figure context: ${figure.id}`);
    const svg = await readFile(`src/assets/hardware/${figure.asset}`, 'utf8');
    if (createHash('sha256').update(svg).digest('hex') !== figure.sha256 || svg.length > 20000 || /<(?:image|foreignObject|script|style)\b|\b(?:href|onload|onclick)\s*=/i.test(svg)) throw new Error(`Unsafe/changed/raster figure: ${figure.id}`);
    if (!svg.includes(`aria-labelledby="${figure.id}-title ${figure.id}-desc"`) || !svg.includes('<desc ') || !svg.includes('<title ')) throw new Error('Inaccessible SVG');
    const refs = figure.sourceRegions.map((id) => regions.get(id));
    if (!refs.length || refs.some((r) => !r || r.disposition !== 'recreated' || r.equivalent !== figure.id || r.printedPage === null)) throw new Error('Unreviewed original/source mapping');
    const pages = [...new Set(refs.map((r) => r!.printedPage))].sort((a,b) => a! - b!);
    if (JSON.stringify(pages) !== JSON.stringify(figure.sourcePages)) throw new Error('Incorrect figure page badge');
  }
  for (const region of inventory.regions) {
    if (evidence.pages.find((page) => page.pdfPage === region.pdfPage)?.printedPage !== region.printedPage || region.crop.length !== 4 || region.crop[0] < 0 || region.crop[1] < 0 || region.crop[2] > 595.23 || region.crop[3] > 842 || region.crop[0] >= region.crop[2] || region.crop[1] >= region.crop[3]) throw new Error(`Invalid source crop metadata: ${region.id}`);
    if (region.disposition === 'recreated' && !ids.has(region.equivalent)) throw new Error(`Missing recovered visual: ${region.id}`);
    if (region.disposition === 'existing-equivalent') {
      const slug = region.equivalent === 'memory-hierarchy' ? 'memory-and-cache' : region.section;
      if (!(await readFile(`src/content/hardware/${slug}.md`, 'utf8')).includes(`id="${region.equivalent}"`)) throw new Error(`Missing existing equivalent: ${region.id}`);
    }
  }
  console.log(`Figures verified: ${inventory.pageReview.length} printed pages reviewed; ${regions.size} editorial regions; ${hardwareFigures.length} original SVGs, matching hashes and page references.`);
}
