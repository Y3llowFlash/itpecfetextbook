import { readFile, readdir } from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
import release from '../src/content/hardware-source-release.json';
import approval from '../docs/development/editorial/chapter1-publication.json';
import evidence from '../docs/development/evidence/hardware-printed-pages.json';
import { digest } from './question-importer';

const normalize=(text:string)=>text.replace(/\s+/g,' ').trim();
const { JSDOM }=createRequire(import.meta.url)('jsdom') as {JSDOM:new(html:string)=>{window:{document:Document;close():void}}};
export const sourceAssets=new Map(release.assets.map(asset=>[asset.path,asset]));

export async function validateSourceRelease(builtRoot?:string){
  if(approval.status!=='owner-approved'||release.publicationStatus!=='owner-approved'||approval.sourceSha256!==release.sourceSha256||release.sourceSha256!==evidence.sha256||approval.releaseId!==release.releaseId)throw new Error('Unapproved source edition');
  const pages=release.lessons.slice(0,5).flatMap(lesson=>lesson.pages);
  if(pages.length!==100||pages.some((page,index)=>page.pdfPage!==index+18||page.printedPage!==evidence.pages.find(p=>p.pdfPage===page.pdfPage)?.printedPage))throw new Error('Source release lost or reordered a page');
  const numbered=new Set<string>();
  // The cache excerpt remains an immutable input for historical compatibility.
  // Public readers contain five full sections plus the two chapter entry aliases.
  const readers=builtRoot?[...release.lessons.slice(0,5),{...release.lessons[0],path:'/'},{...release.lessons[0],path:'/chapters/hardware/'}]:release.lessons;
  for(const lesson of readers){
    const file=builtRoot?path.join(builtRoot,lesson.path,'index.html'):path.join('src/content/source-hardware',lesson.slug+'.html');
    const html=await readFile(file,'utf8');
    if(!builtRoot&&digest(html.replace(/\r\n/g,'\n'))!==lesson.htmlSha256)throw new Error(`Changed source HTML: ${lesson.slug}`);
    const dom=new JSDOM(html),doc=dom.window.document;
    try{
      const ids=[...doc.querySelectorAll('[id]')].map(node=>node.id);
      if(new Set(ids).size!==ids.length)throw new Error(`Duplicate source anchors: ${lesson.slug}`);
      const actual=[...doc.querySelectorAll<HTMLElement>('[data-source-block]')];
      const expected=lesson.pages.flatMap(page=>page.blocks);
      if(actual.length!==expected.length)throw new Error(`Missing source blocks: ${lesson.slug}`);
      for(let index=0;index<expected.length;index++){
        const block=expected[index],element=actual[index];
        if(element.id!==block.id||element.dataset.sourceBlock!==block.sourceId||element.dataset.sourceKind!==block.kind)throw new Error('Source reading order changed');
        if(['paragraph','heading','list-item'].includes(block.kind)){
          const copy=element.cloneNode(true) as HTMLElement;
          copy.querySelectorAll('.concept-count').forEach(n=>n.remove());
          if(digest(normalize(copy.textContent||''))!==block.textSha256)throw new Error(`Source text changed: ${block.id}`);
        }
        for(const id of block.regionIds)if(/^figure-1-\d+$/.test(id))numbered.add(id);
      }
      if(doc.querySelector('.source-book svg,.review-tag,[data-local-source-edition]')||/ITPEC_LOCAL_SOURCE_EDITION_V1|editorial-publication-status/.test(html))throw new Error('Editorial workspace or substitute figure leaked into public reader');
      const root=builtRoot?doc.querySelector('.source-book'):doc;
      for(const image of root!.querySelectorAll('img')){
        const src=image.getAttribute('src')||'';
        if(!sourceAssets.has(src.slice(1))||!image.getAttribute('alt'))throw new Error('Unapproved or undescribed source visual');
      }
    }finally{dom.window.close();}
  }
  if(numbered.size!==47)throw new Error('A numbered source figure is missing from the release');
  const folder=path.join(builtRoot||'public','textbook/hardware');
  const files=await readdir(folder);
  if(files.length!==release.assets.length)throw new Error('Unexpected source figure files');
  for(const asset of release.assets){
    const content=await readFile(path.join(builtRoot||'public',asset.path));
    if(digest(content)!==asset.sha256||content.length!==asset.bytes)throw new Error(`Source asset hash mismatch: ${asset.path}`);
  }
  console.log(`Source release verified: 100 pages in source order, 47 numbered figures, ${sourceAssets.size} approved lossless assets, unchanged native source text.`);
}
