import {test,expect} from '@playwright/test';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {CPU_PATH,CACHE_HEADING} from '../../src/lib/reading-routes';
const root='.local/historical-batches/technology01-phase08';
const read=(name:string)=>JSON.parse(readFileSync(root+'/'+name,'utf8'));
const audit=read('audit.json'),manifest=read('final-approval/manifest.json'),state=read('baseline.json');
const owner='http://127.0.0.1:4354',sha=(b:Buffer)=>createHash('sha256').update(b).digest('hex');

test('student counts separate sitewide public records, Hardware references and zero additions',async({page})=>{
 await page.goto('/');
 await expect(page.getByText(/Published sitewide catalog: 687 questions/)).toBeVisible();
 await expect(page.getByText(/290 unchanged Chapter 1 Hardware references and zero new private candidates/)).toBeVisible();
 await expect(page.getByRole('heading',{name:'No new Phase 8 questions available'})).toBeVisible();
 expect(await page.locator('body').innerText()).not.toMatch(/HIST-TECH01-2021S-Q023|HIST-TECH01-2012A-Q030|source-explanation-numeric-conflict/);
 await page.goto('/review/');await expect(page.getByText('No new questions are available in this preview.')).toBeVisible();
 expect(manifest.questionIds).toEqual([]);expect(manifest.publicationReady).toBe(false);
});

test('disposable grading, keyboard enlargement, bookmarks and reload preserve the public guest key',async({page})=>{
 await page.setViewportSize({width:375,height:900});await page.goto('/practice/cache-memory/');
 await page.evaluate(()=>localStorage.setItem('itpecTextbook:guest:v1','public-progress-sentinel'));
 const option=page.getByRole('radio',{name:'Option B: 360 ns'});await option.focus();await page.keyboard.press('Space');
 await page.getByRole('button',{name:'Check answer'}).focus();await page.keyboard.press('Enter');await expect(page.getByText('✓ That’s correct.')).toBeVisible();
 await page.getByRole('button',{name:'◇ Bookmark'}).click();
 await page.getByRole('button',{name:'Enlarge original question 2024A-A-Q009'}).click();await expect(page.getByRole('dialog')).toBeVisible();await page.keyboard.press('Escape');
 await page.reload();await expect(page.getByRole('button',{name:'◆ Bookmarked'})).toBeVisible();await expect(page.getByText('✓ That’s correct.')).toBeVisible();
 expect(await page.evaluate(()=>localStorage.getItem('itpecTextbook:guest:v1'))).toBe('public-progress-sentinel');
 expect(await page.evaluate(()=>Object.keys(localStorage).some(k=>k.startsWith('itpecTextbook:privatePhase08:')))).toBe(true);
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});

test('source/year/unanswered and empty private-collection filtering remain separate',async({page})=>{
 await page.goto('/practice/cache-memory/');await page.getByRole('checkbox',{name:'Unanswered only'}).check();
 await page.getByRole('radio',{name:'Option B: 360 ns'}).check();await page.getByRole('button',{name:'Check answer'}).click();
 await expect(page.getByText('Answer saved · 18 unanswered remain')).toBeVisible();
 await page.getByRole('combobox',{name:'Preview collection'}).selectOption('phase08');
 await expect(page.getByRole('heading',{name:'Practice is not available yet'})).toBeVisible();
 await expect(page.getByText('19 published in this concept \u00b7 0 new private Phase 8 \u00b7 0 match active filters.')).toBeVisible();
 await page.getByRole('combobox',{name:'Preview collection'}).selectOption('published');
 await page.getByRole('combobox',{name:'From year'}).selectOption('2025');await page.getByRole('combobox',{name:'To year'}).selectOption('2025');
 await expect(page.getByRole('heading',{name:'FE · Morning · Subject A · 2025 Spring · Q10',exact:true})).toBeVisible();
 await page.getByRole('combobox',{name:'Question source'}).selectOption('historical-pdf');await expect(page.getByRole('heading',{name:'No questions match these filters'})).toBeVisible();
 await page.reload();await expect(page.getByRole('heading',{name:'No questions match these filters'})).toBeVisible();
});

test('source reading context returns to its actual unchanged Hardware passage',async({page})=>{
 await page.goto(`${CPU_PATH}#${CACHE_HEADING}`);const highlight=page.locator('#concept-cache-memory');
 await highlight.scrollIntoViewIfNeeded();const block=highlight.locator('xpath=ancestor::*[@data-reading-block][1]');const before=await block.evaluate(el=>el.getBoundingClientRect().top);
 await highlight.click();await page.getByRole('link',{name:'← Return to textbook'}).click();await expect(highlight).toBeFocused();
 expect(Math.abs(before-await block.evaluate(el=>el.getBoundingClientRect().top))).toBeLessThan(3);
});

test('private reference preview never loads production Firebase or external services',async({page})=>{
 const external:string[]=[];page.on('request',r=>{if(!r.url().startsWith('http://127.0.0.1:4352/'))external.push(r.url());});
 await page.goto('/');await page.goto('/practice/cache-memory/');await page.getByRole('radio',{name:'Option A: 315 ns'}).check();await page.getByRole('button',{name:'Check answer'}).click();
 await expect(page.getByText('Let’s work through it.')).toBeVisible();expect(external).toEqual([]);
});

test('owner gallery accounts for all 66 and groups the original 29 by actual chapters',async({page})=>{
 await page.goto(owner+'/');await expect(page.getByRole('heading',{name:'Phase 8 — read-only owner audit'})).toBeVisible();
 await expect(page.locator('article[data-question-id]')).toHaveCount(66);await expect(page.locator('article[data-eligible="false"]')).toHaveCount(66);
 for(const [chapter,title,count] of [[2,'Information Processing System',11],[3,'Software',12],[5,'Network',5],[7,'Data Structure and Algorithm',1]] as const){
  await expect(page.getByRole('heading',{level:2,name:`Chapter ${chapter} — ${title} (${count})`,exact:true})).toHaveCount(1);
 }
 await expect(page.getByRole('heading',{name:'Final approval candidates: 0',exact:true})).toBeVisible();
 expect(await page.getByRole('button').count()).toBe(0);expect(await page.locator('form').count()).toBe(0);
});

test('all 66 delivered owner images equal the immutable original source hashes',async({request})=>{
 for(const row of audit.questions){
  const response=await request.get(owner+`/images/${row.id}.webp`);expect(response.ok(),row.id).toBe(true);
  expect(sha(await response.body()),row.id).toBe(row.sourceBinding.images[0]);
 }
});

test('owner accessible descriptions contain complete source powers, literal typos and table data',async({page})=>{
 await page.goto(owner+'/');
 const power=page.locator('article#HIST-TECH01-2020S-Q019');await power.getByText('Accessible source description and original choices',{exact:true}).click();
 await expect(power.locator('dd')).toHaveText(['2^4','2^10','2^20','2^32']);
 const ecc=page.locator('article#HIST-TECH01-2009A-Q023');await ecc.getByText('Accessible source description and original choices',{exact:true}).click();
 await expect(ecc.locator('dd').last()).toHaveText('Party');expect(await ecc.locator('details').first().innerText()).not.toContain('C explicitly');
 const mix=page.locator('article#HIST-TECH01-2021S-Q012');await mix.getByText('Accessible source description and original choices',{exact:true}).click();await expect(mix.locator('details').first()).toContainText('0.3, 50%');
 const memory=page.locator('article#HIST-TECH01-2008A-Q023');await memory.getByText('Accessible source description and original choices',{exact:true}).click();
 await expect(memory.locator('dd').first()).toHaveText('Highest 3FFFFF; Lowest 0000000 (hex)');
});

test('all seven protected cases are visibly qualified and excluded from grading',async({page})=>{
 await page.goto(owner+'/');
 for(const id of state.protectedIds){const article=page.locator(`article#${id}`);await expect(article).toHaveAttribute('data-eligible','false');await article.getByText('Preserved academic answer and worked explanation',{exact:true}).click();await expect(article).toContainText('Qualified owner-adjudicated; protected');}
 await expect(page.locator('article#HIST-TECH01-2012A-Q030')).toContainText('ordinary single-answer');
});

for(const width of [375,1024])test(`owner navigation and original image enlargement fit ${width}px`,async({page,context},info)=>{
 await page.setViewportSize({width,height:900});await page.goto(owner+'/');
 await page.getByRole('link',{name:'Skip to audit',exact:true}).focus();await page.keyboard.press('Enter');
 const link=page.locator('nav[aria-label="Textbook chapter groups"] a').filter({hasText:'Chapter 2'});await link.focus();await page.keyboard.press('Enter');
 await expect(page).toHaveURL(/#group-\d+$/);expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 const imageLink=page.getByRole('link',{name:'Enlarge original HIST-TECH01-2021S-Q023',exact:true});await imageLink.scrollIntoViewIfNeeded();
 const popupPromise=context.waitForEvent('page');await imageLink.click();const popup=await popupPromise;await popup.waitForLoadState();await expect(popup.locator('img')).toBeVisible();await popup.close();
 await page.screenshot({path:info.outputPath(`owner-${width}.png`)});
});

test('delivery is loopback-only, read-only, no-store, allowlisted and denies raw source data',async({request})=>{
 for(const base of [owner,'http://127.0.0.1:4352']){
  const response=await request.get(base+'/');expect(response.status()).toBe(200);expect(response.headers()['cache-control']).toBe('no-store');expect(response.headers()['x-robots-tag']).toContain('noindex');
  expect((await request.post(base+'/',{data:'approve'})).status()).toBe(405);
  expect((await request.get(base+'/',{headers:{Origin:'https://itpecfetextbook.pages.dev'}})).status()).toBe(403);
  for(const path of ['/reviews.json','/questions.json','/data/questions.json','/Technology-01.pdf','/.local/historical/technology-01/reviews.json'])expect((await request.get(base+path)).status(),path).toBe(404);
 }
});
