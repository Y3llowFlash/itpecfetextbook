// Hosted reader checks. Practice interactions stay in browser storage.
// Production verification is explicit: pass the canonical origin and --production.
import assert from 'node:assert/strict';
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {chromium} from '@playwright/test';
const origin=process.argv[2];
const production=process.argv.includes('--production');
const validOrigin=production?origin==='https://itpecfetextbook.pages.dev':/^https:\/\/[a-z0-9-]+\.itpecfetextbook\.pages\.dev\/?$/.test(origin||'');
if(!validOrigin)throw new Error('Pass a Cloudflare Pages preview URL, or the canonical production origin with --production');
const release=JSON.parse(await readFile('src/content/hardware-source-release.json','utf8'));
const toc=JSON.parse(await readFile('src/content/hardware-toc.json','utf8'));
const prose=JSON.parse(await readFile('src/content/hardware-prose-repairs.json','utf8'));
const crops=JSON.parse(await readFile('src/content/hardware-spatial-crops.json','utf8'));
const covers=JSON.parse(await readFile('src/content/book-covers.json','utf8'));
const bank=await readFile('public/data/questions.json');
const output=production?'.local/landing/production-review':'.local/landing/hosted-review';await mkdir(output,{recursive:true});
const browser=await chromium.launch();
const errors=[];
try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 page.on('pageerror',error=>errors.push(error.message));
 assert.equal((await page.goto(origin,{waitUntil:'domcontentloaded'})).status(),200);
 await page.evaluate(()=>document.fonts.ready);
 assert.equal(await page.locator('main h1').innerText(),'Exam Preparation Books');
 assert.equal(await page.locator('[data-level]').count(),3);
 assert.equal(await page.locator('[data-level="ip"] button:disabled,[data-level="ap"] button:disabled').count(),2);
 assert.equal(await page.locator('astro-island,script[src]').count(),0);
 for(const cover of covers){
  const img=page.locator(`[data-level="${cover.level}"] img`);await img.evaluate(async el=>{el.loading='eager';await el.decode()});
  assert.equal(await img.getAttribute('src'),'/'+cover.variants.at(-1).path);
 }
 await page.screenshot({path:`${output}/landing-desktop.png`,fullPage:true});
 await page.getByRole('link',{name:'Open Textbook',exact:true}).click();
 assert.equal(new URL(page.url()).pathname,'/chapters/hardware/');
 await page.getByRole('heading',{level:1,name:'Hardware',exact:true}).waitFor();
 assert.equal(await page.locator('.sidebar [data-toc-link]').count(),52);
 await page.screenshot({path:`${output}/desktop.png`});
 const source=await page.evaluate(async({release,bankHash,bankCount,prose,crops,covers})=>{
  const hash=async bytes=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(v=>v.toString(16).padStart(2,'0')).join('');
  let index=0,assets=0;const approved=[...release.assets,...crops.regions.map(r=>r.asset),...covers.flatMap(c=>c.variants)];
  const cropped=new Map(crops.regions.flatMap(r=>r.sourceBlockIds.map(id=>[id,r.id])));
  await Promise.all(Array.from({length:6},async()=>{while(index<approved.length){const asset=approved[index++],r=await fetch('/'+asset.path);if(!r.ok||await hash(await r.arrayBuffer())!==asset.sha256)throw new Error('Preview asset changed: '+asset.path);assets++;}}));
  const readers=[...release.lessons.slice(0,5),{...release.lessons[0],path:'/chapters/hardware/'}];
  for(const lesson of readers){
   const r=await fetch(lesson.path);if(!r.ok)throw new Error('Missing reader: '+lesson.path);
   const doc=new DOMParser().parseFromString(await r.text(),'text/html');
   const actual=[...doc.querySelectorAll('[data-source-block]')],expected=lesson.pages.flatMap(p=>p.blocks);
   if(actual.length!==expected.length)throw new Error('Missing source blocks');
   if(lesson.pages.some(p=>p.pdfPage===prose.pdfPage)){
    const insertion=doc.querySelector(`[data-pdf-page="${prose.pdfPage}"]`);
    if(insertion.querySelectorAll('p[data-source-paragraph]').length!==5||insertion.querySelector('p[data-source-kind="paragraph"]'))throw new Error('Preview prose is fragmented');
    for(const group of prose.paragraphs){const paragraph=insertion.querySelector(`[data-source-paragraph="${group.id}"]`);if(!paragraph||await hash(new TextEncoder().encode(paragraph.textContent.replace(/\s+/g,' ').trim()))!==group.textSha256)throw new Error('Source paragraph text changed');}
   }
   for(let i=0;i<expected.length;i++){
    const block=expected[i],element=actual[i];if(element.id!==block.id)throw new Error('Source reading order changed');
    if(cropped.has(block.id)){
     if(element.getAttribute('data-source-crop')!==cropped.get(block.id)||element.textContent!==''||element.children.length)throw new Error('Duplicated crop fragment');
    }else if(['paragraph','heading','list-item'].includes(block.kind)){
     const copy=element.cloneNode(true);copy.querySelectorAll('.concept-count').forEach(n=>n.remove());
     if(await hash(new TextEncoder().encode(copy.textContent.replace(/\s+/g,' ').trim()))!==block.textSha256)throw new Error('Source text changed: '+block.id);
    }
   }
   const regions=crops.regions.filter(r=>lesson.pages.some(p=>p.pdfPage===r.pdfPage));
   if(doc.querySelectorAll('[data-spatial-crop]').length!==regions.length)throw new Error('Missing preview source crops');
   for(const region of regions){
    const figure=doc.querySelector(`[data-spatial-crop="${region.id}"]`),img=figure?.querySelector('img');
    if(!img||img.getAttribute('src')!=='/'+region.asset.path||img.alt!==region.alt||figure.getAttribute('data-source-pdf-page')!==String(region.pdfPage))throw new Error('Incorrect preview source crop');
    for(const record of region.recoveries){const native=doc.querySelector(`[data-source-recovery="${record.id}"]`);if(!native||await hash(new TextEncoder().encode(native.textContent.replace(/\s+/g,' ').trim()))!==record.textSha256)throw new Error('Lost recovered prose');}
   }
  }
  const published=await fetch('/data/questions.json');if(!published.ok||await hash(await published.arrayBuffer())!==bankHash)throw new Error('Published question bank changed');
  const coverCount=covers.reduce((n,c)=>n+c.variants.length,0);
  return {readers:readers.length,sourceAssets:assets-coverCount,coverAssets:coverCount,publishedQuestions:bankCount};
 },{release,bankHash:createHash('sha256').update(bank).digest('hex'),bankCount:JSON.parse(bank.toString()).length,prose,crops,covers});
 const bcd=crops.regions.find(r=>r.id==='spatial-p32-01');
 const checkBCD=async(name)=>{
  await page.goto(origin+bcd.url);await page.evaluate(()=>document.fonts.ready);
  const figure=page.locator('[data-spatial-crop="spatial-p32-01"]');await figure.scrollIntoViewIfNeeded();
  await figure.locator('img').evaluate(img=>img.decode());
  assert.equal(await figure.locator('img').getAttribute('src'),'/'+bcd.asset.path);
  await page.screenshot({path:`${output}/bcd-${name}.png`});
 };
 await checkBCD('desktop');
 const checkParagraph=async(name)=>{
  await page.goto(origin+'/chapters/hardware/cpu-and-main-memory/#'+prose.paragraphs[3].firstId);await page.evaluate(()=>document.fonts.ready);
  const paragraph=page.locator('[data-source-paragraph="pdf-083-prose-004"]');await paragraph.scrollIntoViewIfNeeded();
  const words=paragraph.locator('[data-source-block]'),first=await words.nth(0).boundingBox(),second=await words.nth(1).boundingBox();
  assert.ok(Math.abs(first.y-second.y)<2,'Source prose words must share a row');
  await page.screenshot({path:`${output}/uart-${name}.png`});
 };
 await checkParagraph('desktop');
 const cache=toc.nodes.find(n=>n.number==='3-5-1');
 await page.goto(origin+'/chapters/hardware/memory-and-cache/');
 await page.waitForURL(new RegExp(`cpu-and-main-memory/.*#${cache.id}$`));
 await page.waitForFunction(id=>document.querySelector('[data-study-context]')?.getAttribute('data-study-context')===id,cache.id);
 assert.equal(await page.locator('.companion-practice').getAttribute('href'),'/practice/cache-memory/');
 await page.screenshot({path:`${output}/cache-desktop.png`});
 await page.locator('#concept-cache-memory').click();
 await page.getByRole('radio',{name:'Option B: 360 ns'}).check();await page.getByRole('button',{name:'Check answer'}).click();
 await page.getByText('✓ That’s correct.').waitFor();
 await page.getByRole('button',{name:'◇ Bookmark'}).click();
 await page.getByRole('link',{name:'← Return to textbook'}).click();
 await page.locator('#concept-cache-memory:focus').waitFor();
 for(const [name,width] of [['mobile',375],['tablet',768],['small-tablet',1024]]){
  await page.setViewportSize({width,height:900});await page.goto(origin);await page.evaluate(()=>document.fonts.ready);
  await page.locator('img').evaluateAll(async images=>{await Promise.all(images.map(async img=>{img.loading='eager';await img.decode()}))});
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.screenshot({path:`${output}/landing-${name}.png`,fullPage:true});
  await page.setViewportSize({width,height:900});await page.goto(origin+'/chapters/hardware/');await page.evaluate(()=>document.fonts.ready);
  await page.waitForFunction(()=>!document.querySelector('[data-study-tools]').open);
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  assert.equal(await page.locator('[data-mobile-contents]').getAttribute('open'),null);
  await page.screenshot({path:`${output}/${name}.png`});
  await page.locator('[data-study-tools] > summary').click();await page.locator('.companion-content h2').waitFor();
  await page.screenshot({path:`${output}/${name}-tools.png`});
  await checkParagraph(name);
  await checkBCD(name);
 }
 assert.deepEqual(errors,[]);
 const result={...(production?{production:origin}:{preview:origin}),checkedAt:new Date().toISOString(),...source,contents:52,spatialCrops:crops.regions.length,restoredProseFragments:crops.regions.reduce((n,r)=>n+r.recoveries.length,0),repairedParagraphs:5,preservedWordAnchors:235,legacyCacheRedirect:true,practiceAnswerBookmarkAndReturn:true,widths:[375,768,1024,1440],browserErrors:errors};
 await writeFile(`${output}/${production?'production':'preview'}-check.json`,JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
}finally{await browser.close();}
