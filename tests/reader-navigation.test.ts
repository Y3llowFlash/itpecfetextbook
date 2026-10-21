// @vitest-environment node
import {readFileSync} from 'node:fs';
import {createRequire} from 'node:module';
import {describe,it,expect} from 'vitest';
import release from '../src/content/hardware-source-release.json';
import {contents,mainContents,completionId} from '../src/lib/toc';
import {studyContext} from '../src/lib/study-context';
import {publishedQuestions} from '../src/lib/catalog';
import {presentSourceHTML} from '../src/lib/reader-presentation';
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
 it('changes only heading presentation and generated reference badges, preserving all source words and image paths',()=>{
  for(const lesson of release.lessons.slice(0,5))for(const chapterStart of [true,false]){
   const source=readFileSync(`src/content/source-hardware/${lesson.slug}.html`,'utf8');
   const before=new JSDOM(source),after=new JSDOM(presentSourceHTML(source,chapterStart));
   const blocks=(doc:Document)=>[...doc.querySelectorAll('[data-source-block]')].filter(el=>['heading','paragraph','list-item'].includes(el.getAttribute('data-source-kind')!)).map(el=>({id:el.id,text:el.textContent}));
   expect(blocks(after.window.document)).toEqual(blocks(before.window.document));
   expect([...after.window.document.images].map(img=>img.src)).toEqual([...before.window.document.images].map(img=>img.src));
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
 it('derives only contextual published questions and mapped videos, with no default cache recommendation',async()=>{
  const bank=await publishedQuestions();
  const cache=studyContext(contents.find(n=>n.number==='3-5-1')!,[...bank,{...bank.find(q=>q.id==='2024A-A-Q009')!,id:'unpublished',is_published:false} as never]);
  expect(cache.questionIds).toEqual(['2024A-A-Q009','2025S-A-Q010','2026S-A-Q010']);expect(cache.videos[0].url).toBe('https://t.me/itpecmm/101');
  const basic=studyContext(mainContents[0],bank);expect(basic.links).toEqual([]);expect(basic.videos).toEqual([]);
  const disk=studyContext(contents.find(n=>n.number==='4-1-3')!,bank);expect(disk.questionIds).toHaveLength(3);expect(disk.links.map(l=>l.id)).toEqual(['disk-access','defragmentation']);
  expect(new Set(mainContents.flatMap(node=>studyContext(node,bank).questionIds)).size).toBe(23);
 });
});
