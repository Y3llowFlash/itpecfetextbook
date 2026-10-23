import {test,expect} from '@playwright/test';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const batch2=process.env.OWNER_REVIEW_BATCH==='2';
const batch3=process.env.OWNER_REVIEW_BATCH==='3';
const batch5=process.env.OWNER_REVIEW_BATCH==='5';
const batch4=process.env.OWNER_REVIEW_BATCH==='4';
const manifest=JSON.parse(readFileSync(batch5?'.local/historical-batches/technology01-hardware-batch05/final-approval/manifest.json':batch4?'.local/historical-batches/technology01-hardware-batch04/final-approval/manifest.json':batch3?'.local/historical-batches/technology01-hardware-batch03/final-approval/manifest.json':`.local/historical/approval-candidates/technology-01${batch2?'-batch02':''}/manifest.json`,'utf8'));
const count=batch2||batch3||batch4||batch5?40:36,groups=batch5?16:batch4?20:batch3?28:batch2?21:7,port=batch5?4343:batch4?4339:batch3?4335:batch2?4331:4326;
const highlights=batch5?1:batch4?2:batch3?14:15;

test('Batch 5 exact source highlight and candidate-set binding',async({page})=>{
 test.skip(!batch5,'Batch 5 only');
 await page.goto('/');await expect(page.locator('.highlight-review')).toHaveCount(1);
 await expect(page.locator('body')).toContainText(manifest.candidateSetFingerprint);
 const row=manifest.highlightIntegration[0];expect(row.conceptId).toBe('flip-flops');
 expect(row.editorialReview.questionIds).toHaveLength(3);
 await page.locator('#highlight-index').getByRole('link',{name:'flip-flops',exact:true}).click();
 const card=page.locator('#highlight-flip-flops');await expect(card).toContainText('Printed p.62 / physical PDF p.67');
 await expect(card).toContainText('Owner editorial approval absent');
 await expect(card).toContainText(row.editorialReview.teachingJustification);
});

test('exact read-only scope, concept groups and original private image bindings',async({page,request})=>{
 await page.goto('/');await expect(page.getByRole('heading',{level:1})).toHaveText(`Final ${count}-question owner review`);
 await expect(page.locator('article')).toHaveCount(count);await expect(page.locator('section[id^="concept-"]')).toHaveCount(groups);
 await expect(page.locator('form,button,input,script')).toHaveCount(0);
 if(batch2||batch3||batch4||batch5){
  await expect(page.locator('[data-checklist]')).toHaveCount(40);
  await expect(page.locator('.blockers')).toHaveCount(40);
  await expect(page.getByText(`${highlights} of ${highlights} new source highlights are source validated`,{exact:false})).toBeVisible();
 }
 for(const entry of manifest.candidates){
  const article=page.locator(`[data-question="${entry.id}"]`);
  await expect(article.locator('.eligibility')).toContainText('unapproved');await expect(article).toContainText('Morning · Subject A');
  await expect(article.locator('.transcription')).toHaveText(entry.review.extraction.imageDescription);
  await expect(article.locator('.worked-steps li')).toHaveText(entry.review.explanation.steps);
  await expect(article.locator('.answer-summary')).toHaveText(entry.review.explanation.summary);
  if(batch2||batch3||batch4||batch5){
   await expect(article.locator('.blockers')).toContainText('final-owner-publication-approval-absent');
   await expect(article.locator('.highlight-preview')).toContainText(entry.textbookSupport.paragraphText.replace(/\s+·\s+\d+\s+questions?\b/,''));
   await expect(article).toContainText(entry.approvalContextFingerprint);
  }
  const image=article.locator('img');await expect(image).toHaveAttribute('alt',entry.review.extraction.imageDescription);
  const response=await request.get(`/images/${entry.id}.webp`);
  expect(createHash('sha256').update(await response.body()).digest('hex')).toBe(entry.record.images[0].sha256);
 }
});

test('no raw sources, other records, mutation or external origins',async({request,page})=>{
 for(const path of ['/manifest.json','/reviews.json','/questions.json','/Technology-01.pdf','/FE%20Vol%201.pdf','/before/reviews.json','/images/HIST-TECH01-2012A-Q030.webp','/approve','/concept-plan.json','/highlight-integration-report.json'])expect((await request.get(path)).status()).toBe(404);
 if(batch2||batch3||batch4||batch5)expect((await request.get('/images/HIST-TECH01-2019A-Q012.webp')).status()).toBe(404);
 expect((await request.post('/')).status()).toBe(405);
 expect((await request.get('/',{headers:{Host:`localhost:${port}`}})).status()).toBe(403);
 expect((await request.get('/',{headers:{Origin:'https://example.com'}})).status()).toBe(403);
 const response=await request.get('/');expect(response.headers()['x-robots-tag']).toContain('noindex');expect(response.headers()['cache-control']).toBe('no-store');
 await page.addInitScript(()=>{localStorage.setItem('itpecTextbook:guest:v1','owner-review-guest-sentinel');localStorage.setItem('itpecTextbook:account:real:v1','owner-review-account-sentinel');});
 const external:string[]=[];page.on('request',r=>{if(!r.url().startsWith(`http://127.0.0.1:${port}/`))external.push(r.url());});
 await page.goto('/');expect(await page.evaluate(()=>[localStorage.getItem('itpecTextbook:guest:v1'),localStorage.getItem('itpecTextbook:account:real:v1')])).toEqual(['owner-review-guest-sentinel','owner-review-account-sentinel']);expect(external).toEqual([]);
});

for(const width of [375,1280])test(`keyboard navigation, corrections and readable review at ${width}px`,async({page},info)=>{
 await page.setViewportSize({width,height:900});await page.goto('/');
 await page.keyboard.press('Tab');await expect(page.getByRole('link',{name:`Skip to all ${count} questions`})).toBeFocused();await page.keyboard.press('Enter');
 expect(new URL(page.url()).hash).toBe('#question-index');
 const cases=batch5?manifest.finalVisualReview.filter((r:{pdfPage:number})=>[125,128,190,208,243,288].includes(r.pdfPage)).map((r:{id:string})=>r.id):batch4?manifest.finalVisualReview.filter((r:{pdfPage:number})=>[40,58,97,111,147,195,216,222,265,283,287,289,333].includes(r.pdfPage)).map((r:{id:string})=>r.id):batch3?manifest.finalVisualReview.filter((r:{pdfPage:number})=>[9,108,155,157,238,263,299,306,317,325,330].includes(r.pdfPage)).map((r:{id:string})=>r.id):batch2?manifest.finalVisualReview.map((r:{id:string})=>r.id):['HIST-TECH01-2019A-Q012','HIST-TECH01-2019S-Q023'];
 for(const id of cases){
  await page.locator('#question-index').getByRole('link',{name:new RegExp(id)}).click();
  expect(new URL(page.url()).hash).toBe(`#${id}`);
  const article=page.locator(`[data-question="${id}"]`);
  if(!batch2&&!batch3&&!batch4&&!batch5)await expect(article.locator('.integrity')).toContainText('native publication review');
  else {await article.locator('.blockers summary').focus();await page.keyboard.press('Enter');await expect(article.locator('.blockers ul')).toBeVisible();}
  await article.locator('img').evaluate(async(el:HTMLImageElement)=>{await el.decode();});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await page.screenshot({path:info.outputPath(`${id}-${width}.png`)});
  await article.getByRole('link',{name:`All ${count} questions`,exact:true}).click();
 }
});

test('Batch 4 exact highlights, complex-source index and literal source typos',async({page})=>{
 test.skip(!batch4,'Only the final Batch 4 package has these exact source cases.');
 await page.goto('/');await expect(page.locator('.highlight-review')).toHaveCount(2);await expect(page.locator('#complex-index a')).toHaveCount(13);
 for(const row of manifest.highlightIntegration){
  await page.locator('#highlight-index').getByRole('link',{name:row.conceptId,exact:true}).click();
  const section=page.locator(`[id="highlight-${row.conceptId}"]`);await expect(section).toContainText(row.editorialReview.teachingJustification);await expect(section).toContainText('Owner editorial approval absent');
 }
 const article=page.locator('[data-question="HIST-TECH01-2012A-Q002"]');await article.locator('.literal-source > summary').click();
 await expect(article.locator('.literal-source')).toContainText('bimary');await expect(article.locator('.literal-source')).toContainText('unmatched parenthesis');
 await expect(article.locator('.transcription')).toContainText('binary number');await expect(article.locator('.concept-source-link')).toHaveAttribute('href',/127\.0\.0\.1:4336\/chapters\/hardware\/cpu-and-main-memory\/#concept-arithmetic-circuits/);
});

test('Batch 3 individual highlights and literal-versus-editorial evidence',async({page})=>{
 test.skip(!batch3,'Only the final Batch 3 package adds the explicit fourteen-highlight index.');
 await page.goto('/');await expect(page.locator('.highlight-review')).toHaveCount(14);
 for(const r of manifest.highlightIntegration){
  await page.locator('#highlight-index').getByRole('link',{name:r.conceptId,exact:true}).click();
  const section=page.locator(`[id="highlight-${r.conceptId}"]`);await expect(section).toContainText(r.editorialReview.teachingJustification);await expect(section).toContainText('Owner editorial approval absent');
 }
 const article=page.locator('[data-question="HIST-TECH01-2010S-Q031"]');await article.locator('.literal-source > summary').click();
 await expect(article.locator('.literal-source')).toContainText('Parenthetic');await expect(article.locator('.literal-source')).toContainText('A: Exclusive logical sum; B: Logical product');
});
