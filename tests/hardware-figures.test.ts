// @vitest-environment node
import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { validateFigures } from '../scripts/validate-figures';
import { figurePageLabel, hardwareFigures, insertAfterReadingBlock, integrateFigures } from '../src/lib/figures';
import inventory from '../docs/development/figures/chapter1-inventory.json';

describe('reviewed Hardware figures', () => {
  it('reconciles every source region, printed/PDF page, author approval and asset hash', async () => {
    await expect(validateFigures()).resolves.toBeUndefined();
    expect(inventory.pageReview.map((p) => p.printedPage)).toEqual(Array.from({length:99},(_,i)=>i+13));
    expect(inventory.regions.filter((r) => r.disposition === 'editorial-only').map((r) => r.id)).toEqual(['hw-p049-02','hw-p050-01','hw-unnumbered-i2c']);
  });
  it('keeps disjoint source pages distinct instead of implying unseen pages', () => {
    expect(figurePageLabel([46,55,56,57])).toBe('pp. 46, 55–57');
    expect(figurePageLabel([51])).toBe('p. 51');
    expect(figurePageLabel([24,25,28])).toBe('pp. 24–25, 28');
  });
  it('inserts outside a complete nested block without changing reading anchors', () => {
    const html='<div id="kept" data-reading-block><div>nested</div><p>explanation</p></div><h2>Next</h2>';
    expect(insertAfterReadingBlock(html,'kept','<figure>new</figure>')).toBe(html.replace('</div><h2>','</div><figure>new</figure><h2>'));
    expect(()=>insertAfterReadingBlock(html,'missing','x')).toThrow('missing');
    expect(()=>insertAfterReadingBlock(html,'kept|unsafe','x')).toThrow('Unsafe');
  });
  it('requires available original artwork and attaches accessible captions and source references', () => {
    const figures=hardwareFigures.filter((f)=>f.lesson==='auxiliary-storage');
    const html=figures.map((f)=>`<div id="${f.after}" data-reading-block>Explanation</div>`).join('');
    expect(()=>integrateFigures(html,'auxiliary-storage',{})).toThrow('Unapproved/missing');
    const assets=Object.fromEntries(figures.map((f)=>[f.asset,readFileSync(`src/assets/hardware/${f.asset}`,'utf8')]));
    const rendered=integrateFigures(html,'auxiliary-storage',assets);
    for(const figure of figures) {
      expect(rendered).toContain(`aria-labelledby="${figure.id}-caption"`);
      expect(rendered).toContain(`data-original-figure="${figure.id}"`);
      expect(rendered).toContain(`Original textbook · ${figurePageLabel(figure.sourcePages)}`);
    }
  });
  it('checks the independent numeric examples and distinguishes NAND latch input polarity', () => {
    expect(parseInt('101101',2)+parseInt('101',2)/8).toBe(parseInt('55',8)+5/8);
    expect(parseInt('2D',16)+10/16).toBe(45.625);
    expect(2**4).toBe(16); expect((0b1000 ^ 0b1111)+1).toBe(8);
    expect(512-5*100).toBe(12);
    expect(60000/7200/2).toBeCloseTo(4.166666667);
    for (const a of [0,1]) for (const b of [0,1]) for (const carryIn of [0,1]) {
      const s1=a^b, c1=a&b, sum=s1^carryIn, carry=c1|(s1&carryIn);
      expect(carry*2+sum).toBe(a+b+carryIn);
    }
    // Stable cross-coupled NAND states: Q=!(S_n & Qbar), Qbar=!(R_n & Q).
    for (const [s,r,q,qbar] of [[1,1,0,1],[1,1,1,0],[0,1,1,0],[1,0,0,1],[0,0,1,1]]) {
      expect(Number(!(s&qbar))).toBe(q); expect(Number(!(r&q))).toBe(qbar);
    }
    expect(hardwareFigures.find((f)=>f.id==='sr-latch')!.alt).toContain('active-low');
    expect(hardwareFigures.find((f)=>f.id==='sr-latch')!.caption).toContain('00 forces both outputs high');
  });
  it('checks all displayed full-adder truth rows against integer addition',()=>{
    const source=readFileSync('src/content/hardware/cpu-and-main-memory.md','utf8');
    const table=source.split('<table id="full-adder-truth">')[1].split('</table>')[0];
    const rows=[...table.matchAll(/<tr>((?:<td>[01]<\/td>){5})<\/tr>/g)].map(match=>[...match[1].matchAll(/<td>([01])<\/td>/g)].map(cell=>Number(cell[1])));
    expect(rows).toHaveLength(8);
    expect(new Set(rows.map(([a,b,c])=>`${a}${b}${c}`)).size).toBe(8);
    for(const [a,b,c,sum,carry] of rows)expect(carry*2+sum).toBe(a+b+c);
  });
});
