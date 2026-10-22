import {readFile,readdir} from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import covers from '../src/content/book-covers.json';
import {digest,webpDimensions} from './question-importer';
export const coverAssets=new Map(covers.flatMap(cover=>cover.variants.map(v=>[v.path,v] as const)));
export async function validateLandingAssets(root='public'){
 if(covers.map(c=>c.level).join(',')!=='fe,ip,ap'||coverAssets.size!==6)throw new Error('Landing must use the three approved main-edition covers');
 for(const cover of covers){
  if(digest(await readFile(cover.sourcePath))!==cover.sourceSha256)throw new Error('Original cover changed');
  for(const asset of cover.variants){
   const bytes=await readFile(path.join(root,asset.path)),size=webpDimensions(bytes);
   if(digest(bytes)!==asset.sha256||bytes.length!==asset.bytes||size.width!==asset.width||size.height!==asset.height||Math.abs(asset.width/asset.height-cover.width/cover.height)>.003)throw new Error('Cover pixels, dimensions or aspect ratio changed');
  }
 }
 if((await readdir(path.join(root,'covers'))).length!==coverAssets.size)throw new Error('Unexpected public cover assets');
}
export async function validateLandingPage(root:string){
 const {JSDOM}=createRequire(import.meta.url)('jsdom') as {JSDOM:new(html:string)=>{window:{document:Document;close():void}}};
 const dom=new JSDOM(await readFile(path.join(root,'index.html'),'utf8')),doc=dom.window.document;
 try{
  if(doc.querySelector('h1')?.textContent!=='Exam Preparation Books'||doc.querySelectorAll('[data-level]').length!==3||doc.querySelector('.source-book,astro-island,script[src]'))throw new Error('Landing page must be static level selection');
  for(const cover of covers){
   const book=doc.querySelector(`[data-level="${cover.level}"]`)!,img=book?.querySelector('img');
   if(!img||img.src!=='/'+cover.variants.at(-1)!.path||!img.alt||img.width!==cover.width||img.height!==cover.height)throw new Error('Incorrect book-cover assignment');
   if(cover.level==='fe'){
    if(book.querySelectorAll('a[href="/chapters/hardware/"]').length!==2)throw new Error('FE must open the existing textbook');
   }else if(book.querySelector('a')||!book.querySelector('button:disabled'))throw new Error('Unavailable levels must not navigate');
  }
  if(doc.querySelector('a[href^="http"]')||doc.querySelector('a[href*="/ip/"],a[href*="/ap/"]'))throw new Error('Unexpected landing navigation');
 }finally{dom.window.close();}
}
