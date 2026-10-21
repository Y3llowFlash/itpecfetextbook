// @vitest-environment node
import {readFileSync} from 'node:fs';
import {createRequire} from 'node:module';
import {createHash} from 'node:crypto';
import {describe,it,expect} from 'vitest';
import crops from '../src/content/hardware-spatial-crops.json';
import release from '../src/content/hardware-source-release.json';
import {contents} from '../src/lib/toc';
import {presentSourceHTML} from '../src/lib/reader-presentation';
const {JSDOM}=createRequire(import.meta.url)('jsdom') as {JSDOM:new(html:string)=>{window:{document:Document;close():void}}};
const hash=(text:string)=>createHash('sha256').update(text.replace(/\s+/g,' ').trim()).digest('hex');
describe('crop-first source fidelity',()=>{
 it('inventories all 100 source pages and keeps contents and exam highlights as native text',()=>{
  expect(crops.pageReview.map(p=>p.pdfPage)).toEqual(Array.from({length:100},(_,i)=>18+i));
  const covered=crops.regions.flatMap(r=>r.sourceBlockIds);
  expect(new Set(covered).size).toBe(covered.length);
  expect(contents.every(n=>!covered.includes(n.id))).toBe(true);
  expect(release.annotations.every(n=>!covered.includes(n.blockId))).toBe(true);
  for(const r of crops.regions){
   expect(r.bbox[2]).toBeGreaterThan(r.bbox[0]);expect(r.bbox[3]).toBeGreaterThan(r.bbox[1]);
   expect((r.bbox[2]-r.bbox[0])*(r.bbox[3]-r.bbox[1])).toBeLessThan(595.32*841.92*.65);
   expect(r.asset.dpi).toBe(300);
   for(const c of r.coverage)expect(c.croppedGlyphs+c.nativeGlyphs).toBe(c.sourceGlyphs);
  }
 });
 it('replaces the entire BCD example with one image while retaining every old fragment checkpoint',()=>{
  const dom=new JSDOM(presentSourceHTML(readFileSync('src/content/source-hardware/data-representation.html','utf8'))),doc=dom.window.document;
  try{
   const r=crops.regions.find(r=>r.id==='spatial-p32-01')!,figure=doc.querySelector('[data-spatial-crop="spatial-p32-01"]')!;
   expect(r.pdfPage).toBe(37);expect(r.printedPage).toBe(32);
   expect(r.bbox).toEqual([88.74,67.92,506.52,180.78]); // complete pink frame plus 3 PDF points of breathing room
   expect(figure.querySelectorAll('img')).toHaveLength(1);
   expect(figure.querySelectorAll('[data-source-block]')).toHaveLength(r.sourceBlockIds.length);
   for(const id of r.sourceBlockIds){const anchor=doc.getElementById(id)!;expect(anchor.textContent).toBe('');expect(anchor.children).toHaveLength(0);expect(anchor.closest('figure')).toBe(figure);}
   expect(figure.querySelector('img')!.alt).toMatch(/2741/);
   expect(figure.textContent).toBe('p. 32 · Enlarge');
   const page=figure.closest('[data-pdf-page]')!;
   expect(page.querySelector('li[data-source-kind="list-item"]')?.textContent).toMatch(/zoned decimal/i);
  }finally{dom.window.close();}
 });
 it('restores surrounding prose from old image fragments exactly once, in joined selectable paragraphs',()=>{
  let recovered=0;
  for(const lesson of release.lessons.slice(0,5)){
   const dom=new JSDOM(presentSourceHTML(readFileSync(`src/content/source-hardware/${lesson.slug}.html`,'utf8'))),doc=dom.window.document;
   try{
    for(const region of crops.regions.filter(r=>r.path===lesson.path))for(const record of region.recoveries){
     const nodes=doc.querySelectorAll(`[data-source-recovery="${record.id}"]`);expect(nodes).toHaveLength(1);
     expect(hash(nodes[0].textContent!)).toBe(record.textSha256);expect(nodes[0].closest('figure')).toBe(null);recovered++;
    }
    if(lesson.slug==='cpu-and-main-memory'){
     expect(doc.querySelector('[data-source-restored-prose="spatial-p66-01"]')?.textContent?.trim()).toMatch(/^By expanding the logical expression F .* logical laws, we can determine different logical circuits\.$/);
     for(const ids of crops.mergeNativeParagraphs)expect(new Set(ids.map(id=>doc.getElementById(id)!.closest('p'))).size).toBe(1);
    }
   }finally{dom.window.close();}
  }
  expect(recovered).toBe(14);
 });
});
