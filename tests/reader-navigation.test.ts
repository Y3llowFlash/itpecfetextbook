// @vitest-environment node
import {readFileSync} from 'node:fs';
import {createRequire} from 'node:module';
import {describe,it,expect} from 'vitest';
import sixth from '../docs/development/evidence/historical-release-6.json';
import release from '../src/content/hardware-source-release.json';
import {contents,mainContents,completionId} from '../src/lib/toc';
import {studyContext} from '../src/lib/study-context';
import {publishedQuestions} from '../src/lib/catalog';
import {presentSourceHTML} from '../src/lib/reader-presentation';
import proseRepairs from '../src/content/hardware-prose-repairs.json';
import crops from '../src/content/hardware-spatial-crops.json';
import {canonicalReadingPosition,CPU_PATH,CACHE_HEADING} from '../src/lib/reading-routes';
const {JSDOM}=createRequire(import.meta.url)('jsdom') as {JSDOM:new(html:string)=>{window:{document:Document;close():void}}};
describe('original source navigation',()=>{
 it('uses exactly the original 5 / 19 / 28 numbered source headings and printed references',()=>{
  expect([1,2,3].map(depth=>contents.filter(n=>n.depth===depth).length)).toEqual([5,19,28]);
  expect(mainContents.map(n=>n.page)).toEqual([13,20,46,78,92]);
  const headings=release.lessons.slice(0,5).flatMap(s=>s.headings);
  for(const node of contents){
   const original=headings.find(h=>h.id===node.id)!;
   const [_,number,title]=/^(\d(?:\s*-\s*\d){0,2})\s+(.+)$/.exec(original.title)!;
   expect(node.number).toBe(number.replace(/\s/g,''));expect(node.title).toBe(title);expect(node.page).toBe(original.printedPage);
   if(node.depth>1)expect(contents.some(parent=>parent.number===node.number.split('-').slice(0,-1).join('-'))).toBe(true);
  }
 });
 it('preserves all source anchors, native words outside reviewed crops and untouched image paths',()=>{
  const covered=new Set(crops.regions.flatMap(r=>r.sourceBlockIds));
  for(const lesson of release.lessons.slice(0,5))for(const chapterStart of [true,false]){
   const source=readFileSync(`src/content/source-hardware/${lesson.slug}.html`,'utf8');
   const before=new JSDOM(source),after=new JSDOM(presentSourceHTML(source,chapterStart));
   const blocks=(doc:Document)=>[...doc.querySelectorAll('[data-source-block]')].filter(el=>['heading','paragraph','list-item'].includes(el.getAttribute('data-source-kind')!)).map(el=>({id:el.id,text:el.textContent}));
   expect(blocks(after.window.document)).toEqual(blocks(before.window.document).map(b=>covered.has(b.id)?{...b,text:''}:b));
   const untouched=[...before.window.document.images].filter(img=>!covered.has(img.closest('[data-source-block]')!.id)).map(img=>img.src);
   expect([...after.window.document.images].filter(img=>!img.closest('[data-spatial-crop]')).map(img=>img.src)).toEqual(untouched);
   expect(after.window.document.querySelector('.source-badge')?.textContent).toMatch(/^p\./);
   before.window.close();after.window.close();
  }
 });
 it('preserves exact old source checkpoints and legacy completion without completing the whole CPU section',()=>{
  const old={sectionId:'fe-v1-ch01-memory-cache',path:'/chapters/hardware/memory-and-cache/',blockId:release.annotations.find(n=>n.conceptId==='cache-memory')!.blockId,offset:77,scrollY:800,updatedAt:'2026-10-21T00:00:00Z'};
  expect(canonicalReadingPosition(old)).toMatchObject({path:CPU_PATH,sectionId:'fe-v1-ch01-s03',blockId:old.blockId,offset:77});
  expect(canonicalReadingPosition({...old,blockId:'why-a-hierarchy'}).blockId).toBe(CACHE_HEADING);
  expect(completionId(contents.find(n=>n.number==='3-5-1')!)).toBe('fe-v1-ch01-memory-cache');
  expect(completionId(contents.find(n=>n.number==='3')!)).toBe('fe-v1-ch01-s03');
 });
 it('restores the five source paragraphs from fragmented PDF words without losing their reading anchors',()=>{
  const source=readFileSync('src/content/source-hardware/cpu-and-main-memory.html','utf8');
  const before=new JSDOM(source),after=new JSDOM(presentSourceHTML(source));
  const original=before.window.document.querySelector('[data-pdf-page="83"]')!;
  const repaired=after.window.document.querySelector('[data-pdf-page="83"]')!;
  expect(original.querySelectorAll('p[data-source-kind="paragraph"]')).toHaveLength(235);
  expect(repaired.querySelectorAll('p[data-source-kind="paragraph"]')).toHaveLength(0);
  const paragraphs=[...repaired.querySelectorAll('p[data-source-paragraph]')];
  expect(paragraphs).toHaveLength(5);
  expect(paragraphs.map(p=>p.querySelectorAll('[data-source-block]').length)).toEqual([50,56,48,57,24]);
  expect(paragraphs.map(p=>p.textContent)).toEqual(proseRepairs.paragraphs.map(group=>{
   const blocks=[...original.querySelectorAll('[data-source-kind="paragraph"]')];
   return blocks.slice(blocks.findIndex(b=>b.id===group.firstId),blocks.findIndex(b=>b.id===group.lastId)+1).map(b=>b.textContent).join(' ');
  }));
  expect(paragraphs[3].textContent).toMatch(/^d\) UART \(Universal Asynchronous Receiver-Transmitter\): UART is a widely used/);
  const anchors=(doc:Element)=>[...doc.querySelectorAll('[data-reading-block]')].map(el=>({id:el.id,text:el.textContent}));
  expect(anchors(repaired)).toEqual(anchors(original));
  expect(repaired.querySelector('figure')?.outerHTML.replace(/Original textbook · /g,'')).toBe(original.querySelector('figure')?.outerHTML.replace(/Original textbook · /g,''));
  before.window.close();after.window.close();
 });
 it('derives only contextual published questions and mapped videos, with no default cache recommendation',async()=>{
  const bank=await publishedQuestions();
  const cache=studyContext(contents.find(n=>n.number==='3-5-1')!,[...bank,{...bank.find(q=>q.id==='2024A-A-Q009')!,id:'unpublished',is_published:false} as never]);
   expect(cache.questionIds.filter(id=>!sixth.records.some(r=>r.id===id))).toEqual(['2024A-A-Q009','2025S-A-Q010','2026S-A-Q010','HIST-TECH01-2009A-Q028','HIST-TECH01-2011A-Q011','HIST-TECH01-2015A-Q011','HIST-TECH01-2015S-Q011','HIST-TECH01-2018S-Q010','HIST-TECH01-2019A-Q013','HIST-TECH01-2019S-Q011','HIST-TECH01-2022S-Q013','HIST-TECH01-2007S-Q024','HIST-TECH01-2012A-Q017','HIST-TECH01-2014S-Q014','HIST-TECH01-2017S-Q012','HIST-TECH01-2008A-Q026','HIST-TECH01-2013S-Q014','HIST-TECH01-2011S-Q014']);expect(cache.questionIds).toHaveLength(24);expect(cache.questionIds.filter(id=>sixth.records.some(r=>r.id===id))).toHaveLength(6);expect(cache.videos[0].url).toBe('https://t.me/itpecmm/101');
  const basic=studyContext(mainContents[0],bank);expect(basic.links.map(l=>l.id)).toEqual(['five-major-units']);expect(basic.videos).toEqual([]);
   const disk=studyContext(contents.find(n=>n.number==='4-1-3')!,bank);expect(disk.questionIds).toHaveLength(9);expect(disk.links.map(l=>l.id)).toEqual(['disk-access','defragmentation']);
   expect(new Set(mainContents.flatMap(node=>studyContext(node,bank).questionIds)).size).toBe(259);
 });
});
