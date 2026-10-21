import definitions from '../content/hardware-figures.json' with { type: 'json' };
import { editionLabel } from './lessons';

export const hardwareFigures = definitions;
const escape = (s: string) => s.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');

/** Render disjoint source pages faithfully, rather than implying an unverified continuous range. */
export function figurePageLabel(pages: number[]) {
  const groups: string[] = [];
  for (let i = 0; i < pages.length; i++) {
    const first = pages[i];
    let last = first;
    while (pages[i + 1] === last + 1) last = pages[++i];
    groups.push(first === last ? `${first}` : `${first}–${last}`);
  }
  return `${pages.length === 1 ? 'p.' : 'pp.'} ${groups.join(', ')}`;
}

/** Insert after the complete authored reading block, retaining its stable ID and nested markup. */
export function insertAfterReadingBlock(html: string, id: string, insertion: string) {
  if (!/^[a-z0-9-]+$/.test(id)) throw new Error('Unsafe figure insertion ID');
  const start = new RegExp(`<(?<tag>div|figure)\\b[^>]*\\bid="${id}"[^>]*>`).exec(html);
  if (!start?.groups) throw new Error(`Figure reading context is missing: ${id}`);
  const tag = start.groups.tag;
  const tokens = new RegExp(`<\\/?${tag}\\b[^>]*>`, 'g');
  tokens.lastIndex = start.index;
  let depth = 0;
  let token;
  while ((token = tokens.exec(html))) {
    depth += token[0].startsWith('</') ? -1 : 1;
    if (depth === 0) return html.slice(0, tokens.lastIndex) + insertion + html.slice(tokens.lastIndex);
  }
  throw new Error(`Unclosed figure reading context: ${id}`);
}

export function integrateFigures(html: string, lesson: string, artwork: Record<string, string>) {
  // Group same-context figures to preserve manifest order when inserted after one block.
  const groups = new Map<string, string[]>();
  for (const figure of hardwareFigures.filter((item) => item.lesson === lesson)) {
    const svg = artwork[figure.asset];
    if (!svg || figure.authorship !== 'authored-original' || figure.sourceReuse) throw new Error(`Unapproved/missing figure: ${figure.id}`);
    const markup = `<figure class="technical-figure" id="figure-${figure.id}" data-reading-block data-original-figure="${figure.id}" aria-labelledby="${figure.id}-caption">${svg}<figcaption id="${figure.id}-caption"><strong>${escape(figure.title)}.</strong> ${escape(figure.caption)}<span class="source-badge" data-figure-source="${figure.id}" title="${escape(editionLabel)}">Original textbook · ${figurePageLabel(figure.sourcePages)}</span></figcaption></figure>`;
    groups.set(figure.after, [...(groups.get(figure.after) || []), markup]);
  }
  for (const [after, markup] of groups) html = insertAfterReadingBlock(html, after, markup.join(''));
  return html;
}
