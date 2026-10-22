import { readFile, readdir } from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
import release from '../src/content/hardware-source-release.json';
import approval from '../docs/development/editorial/chapter1-publication.json';
import evidence from '../docs/development/evidence/hardware-printed-pages.json';
import { digest, webpDimensions } from './question-importer';
import proseRepairs from '../src/content/hardware-prose-repairs.json';
import crops from '../src/content/hardware-spatial-crops.json';

const normalize=(text:string)=>text.replace(/\s+/g,' ').trim();
const { JSDOM }=createRequire(import.meta.url)('jsdom') as {JSDOM:new(html:string)=>{window:{document:Document;close():void}}};
export const sourceAssets=new Map([...release.assets,...crops.regions.map(r=>r.asset)].map(asset=>[asset.path,asset]));
const croppedBlocks=new Map(crops.regions.flatMap(region=>region.coverage.map(block=>[block.id,{region,block}] as const)));

export async function validateSourceRelease(builtRoot?:string){
  if(approval.status!=='owner-approved'||release.publicationStatus!=='owner-approved'||approval.sourceSha256!==release.sourceSha256||release.sourceSha256!==evidence.sha256||approval.releaseId!==release.releaseId)throw new Error('Unapproved source edition');
  if(proseRepairs.sourceSha256!==release.sourceSha256||proseRepairs.releaseId!==release.releaseId)throw new Error('Prose layout metadata belongs to another source edition');
  const config=await readFile('docs/development/editorial/chapter1-spatial-crops.json','utf8');
  if(crops.publicationStatus!=='owner-approved'||crops.sourceSha256!==release.sourceSha256||crops.releaseId!==release.releaseId||digest(config.replace(/\r\n/g,'\n'))!==crops.configSha256||crops.pageReview.length!==100)throw new Error('Unapproved or stale spatial crop manifest');
  const pages=release.lessons.slice(0,5).flatMap(lesson=>lesson.pages);
  if(pages.length!==100||pages.some((page,index)=>page.pdfPage!==index+18||page.printedPage!==evidence.pages.find(p=>p.pdfPage===page.pdfPage)?.printedPage))throw new Error('Source release lost or reordered a page');
  const numbered=new Set<string>();
  // The cache excerpt remains an immutable input for historical compatibility.
  // The root is level selection; five full sections plus the chapter entry remain readers.
  const readers=builtRoot?[...release.lessons.slice(0,5),{...release.lessons[0],path:'/chapters/hardware/'}]:release.lessons;
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
      if(builtRoot&&lesson.pages.some(page=>page.pdfPage===proseRepairs.pdfPage)){
        const inserted=doc.querySelector(`[data-pdf-page="${proseRepairs.pdfPage}"]`)!;
        const paragraphs=[...inserted.querySelectorAll('[data-source-paragraph]')];
        if(paragraphs.length!==proseRepairs.paragraphs.length||inserted.querySelector('p[data-source-kind="paragraph"]'))throw new Error('Fragmented source words were rendered as separate paragraphs');
        for(const group of proseRepairs.paragraphs){
          const paragraph=inserted.querySelector(`[data-source-paragraph="${group.id}"]`)!;
          if(!paragraph||paragraph.tagName!=='P'||paragraph.querySelectorAll('[data-source-block]').length!==group.fragmentCount||digest(normalize(paragraph.textContent||''))!==group.textSha256)throw new Error(`Reviewed source paragraph changed: ${group.id}`);
        }
      }
      for(let index=0;index<expected.length;index++){
        const block=expected[index],element=actual[index];
        if(element.id!==block.id||element.dataset.sourceBlock!==block.sourceId||element.dataset.sourceKind!==block.kind)throw new Error('Source reading order changed');
        const crop=croppedBlocks.get(block.id);
        if(crop&&(crop.block.sourceTextSha256!==block.textSha256||crop.block.sourceGlyphs!==crop.block.croppedGlyphs+crop.block.nativeGlyphs))throw new Error('Invalid crop source coverage');
        if(builtRoot&&crop){
          if(element.dataset.sourceCrop!==crop.region.id||element.textContent!==''||element.children.length||element.closest('[data-spatial-crop]')?.getAttribute('data-spatial-crop')!==crop.region.id)throw new Error(`Duplicated or misplaced crop fragments: ${block.id}`);
        }else if(['paragraph','heading','list-item'].includes(block.kind)){
          const copy=element.cloneNode(true) as HTMLElement;
          copy.querySelectorAll('.concept-count').forEach(n=>n.remove());
          if(digest(normalize(copy.textContent||''))!==block.textSha256)throw new Error(`Source text changed: ${block.id}`);
        }
        for(const id of block.regionIds)if(/^figure-1-\d+$/.test(id))numbered.add(id);
      }
      if(builtRoot){
        const regions=crops.regions.filter(r=>r.path===lesson.path||lesson.pages.some(p=>p.pdfPage===r.pdfPage));
        if(doc.querySelectorAll('[data-spatial-crop]').length!==regions.length)throw new Error('Missing or duplicated spatial crops');
        for(const region of regions){
          const figure=doc.querySelector<HTMLElement>(`[data-spatial-crop="${region.id}"]`),image=figure?.querySelector('img');
          if(!figure||figure.dataset.sourcePdfPage!==String(region.pdfPage)||figure.dataset.sourcePrintedPage!==String(region.printedPage)||figure.querySelectorAll('img').length!==1||image?.getAttribute('src')!=='/'+region.asset.path||image.alt!==region.alt||image.width!==region.asset.width||image.height!==region.asset.height)throw new Error(`Incomplete original source visual: ${region.id}`);
          for(const recovery of region.recoveries){
            const native=doc.querySelector(`[data-source-recovery="${recovery.id}"]`);
            if(!native||native.closest('[data-spatial-crop]')||digest(normalize(native.textContent||''))!==recovery.textSha256)throw new Error(`Lost surrounding source prose: ${recovery.id}`);
          }
        }
        for(const annotation of release.annotations.filter(a=>expected.some(b=>b.id===a.blockId))){
          if(doc.getElementById(annotation.blockId)?.dataset.sourceCrop)throw new Error('Interactive source concept was replaced by an image');
        }
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
  const spatialFiles=await readdir(path.join(builtRoot||'public','textbook/hardware-spatial'));
  if(spatialFiles.length!==crops.regions.length)throw new Error('Unexpected spatial crop files');
  for(const {asset} of crops.regions){
    const bytes=await readFile(path.join(builtRoot||'public',asset.path)),dimensions=webpDimensions(bytes);
    if(digest(bytes)!==asset.sha256||bytes.length!==asset.bytes||dimensions.width!==asset.width||dimensions.height!==asset.height)throw new Error('Changed original spatial crop');
  }
  console.log(`Source release verified: 100 pages, 47 numbered figures, ${crops.regions.length} complete spatial crops, unchanged native text outside reviewed crop coverage.`);
}
