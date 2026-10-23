import {test,expect} from '@playwright/test';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const manifest=JSON.parse(readFileSync('.local/historical/approval-candidates/technology-01/manifest.json','utf8'));

test('exact read-only scope, concept groups and original private image bindings',async({page,request})=>{
 await page.goto('/');await expect(page.getByRole('heading',{level:1})).toHaveText('Final 36-question owner review');
 await expect(page.locator('article')).toHaveCount(36);await expect(page.locator('section[id^="concept-"]')).toHaveCount(7);
 await expect(page.locator('form,button,input,script')).toHaveCount(0);
 for(const entry of manifest.candidates){
  const article=page.locator(`[data-question="${entry.id}"]`);
  await expect(article.locator('.eligibility')).toContainText('unapproved');await expect(article).toContainText('Morning · Subject A');
  await expect(article.locator('.transcription')).toHaveText(entry.review.extraction.imageDescription);
  await expect(article.locator('.worked-steps li')).toHaveText(entry.review.explanation.steps);
  await expect(article.locator('.answer-summary')).toHaveText(entry.review.explanation.summary);
  const image=article.locator('img');await expect(image).toHaveAttribute('alt',entry.review.extraction.imageDescription);
  const response=await request.get(`/images/${entry.id}.webp`);
  expect(createHash('sha256').update(await response.body()).digest('hex')).toBe(entry.record.images[0].sha256);
 }
});

test('no raw sources, other records, mutation or external origins',async({request,page})=>{
 for(const path of ['/manifest.json','/reviews.json','/questions.json','/Technology-01.pdf','/FE%20Vol%201.pdf','/before/reviews.json','/images/HIST-TECH01-2012A-Q030.webp','/approve'])expect((await request.get(path)).status()).toBe(404);
 expect((await request.post('/')).status()).toBe(405);
 expect((await request.get('/',{headers:{Host:'localhost:4326'}})).status()).toBe(403);
 expect((await request.get('/',{headers:{Origin:'https://example.com'}})).status()).toBe(403);
 const response=await request.get('/');expect(response.headers()['x-robots-tag']).toContain('noindex');expect(response.headers()['cache-control']).toBe('no-store');
 await page.addInitScript(()=>{localStorage.setItem('itpecTextbook:guest:v1','owner-review-guest-sentinel');localStorage.setItem('itpecTextbook:account:real:v1','owner-review-account-sentinel');});
 const external:string[]=[];page.on('request',r=>{if(!r.url().startsWith('http://127.0.0.1:4326/'))external.push(r.url());});
 await page.goto('/');expect(await page.evaluate(()=>[localStorage.getItem('itpecTextbook:guest:v1'),localStorage.getItem('itpecTextbook:account:real:v1')])).toEqual(['owner-review-guest-sentinel','owner-review-account-sentinel']);expect(external).toEqual([]);
});

for(const width of [375,1280])test(`keyboard navigation, corrections and readable review at ${width}px`,async({page},info)=>{
 await page.setViewportSize({width,height:900});await page.goto('/');
 await page.keyboard.press('Tab');await expect(page.getByRole('link',{name:'Skip to all 36 questions'})).toBeFocused();await page.keyboard.press('Enter');
 expect(new URL(page.url()).hash).toBe('#question-index');
 for(const id of ['HIST-TECH01-2019A-Q012','HIST-TECH01-2019S-Q023']){
  await page.locator('#question-index').getByRole('link',{name:new RegExp(id)}).click();
  expect(new URL(page.url()).hash).toBe(`#${id}`);
  const article=page.locator(`[data-question="${id}"]`);await expect(article.locator('.integrity')).toContainText('native publication review');
  await article.locator('img').evaluate(async(el:HTMLImageElement)=>{await el.decode();});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await page.screenshot({path:info.outputPath(`${id}-${width}.png`)});
  await article.getByRole('link',{name:'All 36 questions',exact:true}).click();
 }
});
