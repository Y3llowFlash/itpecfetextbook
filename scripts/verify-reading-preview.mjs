// Read-only hosted-preview checks. Practice interactions stay in browser storage.
import assert from 'node:assert/strict';
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {chromium} from '@playwright/test';
const origin=process.argv[2];
if(!origin||!/^https:\/\/[a-z0-9-]+\.itpecfetextbook\.pages\.dev\/?$/.test(origin))throw new Error('Pass a Cloudflare Pages preview URL; production is excluded');
const release=JSON.parse(await readFile('src/content/hardware-source-release.json','utf8'));
const toc=JSON.parse(await readFile('src/content/hardware-toc.json','utf8'));
const bank=await readFile('public/data/questions.json');
const output='.local/reading-review';await mkdir(output,{recursive:true});
const browser=await chromium.launch();
const errors=[];
try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 page.on('pageerror',error=>errors.push(error.message));
 assert.equal((await page.goto(origin,{waitUntil:'domcontentloaded'})).status(),200);
 await page.evaluate(()=>document.fonts.ready);
 assert.equal(await page.locator('main h1').innerText(),'Hardware');
 assert.equal(await page.locator('.sidebar [data-toc-link]').count(),52);
 await page.screenshot({path:`${output}/desktop.png`});
 const source=await page.evaluate(async({release,bankHash})=>{
  const hash=async bytes=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(v=>v.toString(16).padStart(2,'0')).join('');
  let index=0,assets=0;
  await Promise.all(Array.from({length:6},async()=>{while(index<release.assets.length){const asset=release.assets[index++],r=await fetch('/'+asset.path);if(!r.ok||await hash(await r.arrayBuffer())!==asset.sha256)throw new Error('Preview asset changed: '+asset.path);assets++;}}));
  const readers=[...release.lessons.slice(0,5),{...release.lessons[0],path:'/'},{...release.lessons[0],path:'/chapters/hardware/'}];
  for(const lesson of readers){
   const r=await fetch(lesson.path);if(!r.ok)throw new Error('Missing reader: '+lesson.path);
   const doc=new DOMParser().parseFromString(await r.text(),'text/html');
   const actual=[...doc.querySelectorAll('[data-source-block]')],expected=lesson.pages.flatMap(p=>p.blocks);
   if(actual.length!==expected.length)throw new Error('Missing source blocks');
   for(let i=0;i<expected.length;i++){
    const block=expected[i],element=actual[i];if(element.id!==block.id)throw new Error('Source reading order changed');
    if(['paragraph','heading','list-item'].includes(block.kind)){
     const copy=element.cloneNode(true);copy.querySelectorAll('.concept-count').forEach(n=>n.remove());
     if(await hash(new TextEncoder().encode(copy.textContent.replace(/\s+/g,' ').trim()))!==block.textSha256)throw new Error('Source text changed: '+block.id);
    }
   }
  }
  const published=await fetch('/data/questions.json');if(!published.ok||await hash(await published.arrayBuffer())!==bankHash)throw new Error('Published question bank changed');
  return {readers:readers.length,sourceAssets:assets,publishedQuestions:420};
 },{release,bankHash:createHash('sha256').update(bank).digest('hex')});
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
  await page.setViewportSize({width,height:900});await page.goto(origin+'/chapters/hardware/');await page.evaluate(()=>document.fonts.ready);
  await page.waitForFunction(()=>!document.querySelector('[data-study-tools]').open);
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  assert.equal(await page.locator('[data-mobile-contents]').getAttribute('open'),null);
  await page.screenshot({path:`${output}/${name}.png`});
  await page.locator('[data-study-tools] > summary').click();await page.locator('.companion-content h2').waitFor();
  await page.screenshot({path:`${output}/${name}-tools.png`});
 }
 assert.deepEqual(errors,[]);
 const result={preview:origin,checkedAt:new Date().toISOString(),...source,contents:52,legacyCacheRedirect:true,practiceAnswerBookmarkAndReturn:true,widths:[375,768,1024,1440],browserErrors:errors};
 await writeFile(`${output}/preview-check.json`,JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
}finally{await browser.close();}
