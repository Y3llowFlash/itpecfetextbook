import {test,expect} from '@playwright/test';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const root='.local/historical-batches/technology01-hardware-batch03/';
const read=(p:string)=>JSON.parse(readFileSync(root+p,'utf8'));
type Q={id:string;topic:string;year:number;number:number;correctAnswer:string;previewCollection:string;image:{src:string;sha256:string;width:number;height:number}};
const bank=read('preview/app/src/content/pilot-bank.json') as Q[];
const additions=bank.filter(q=>q.previewCollection==='batch03');
const answers=read('preview/app/src/content/explanations.json') as Array<{questionId:string;summary:string;steps:string[];imageDescription:string;optionText:Record<string,string>}>;
const concepts=read('preview/app/src/content/concepts.json') as Array<{id:string;sectionUrl:string;title:string}>;
const prefix='itpecTextbook:privateHardwareBatch03:';

test('exact index, all original image hashes and loopback privacy',async({request})=>{
 expect(additions).toHaveLength(40);expect(bank).toHaveLength(139);
 const home=await request.get('/');expect(home.status()).toBe(200);expect(await home.text()).toContain('40 new private questions plus 99 unchanged published references');
 expect(home.headers()['x-robots-tag']).toContain('noindex');expect(home.headers()['content-security-policy']).toContain("connect-src 'self'");
 for(const q of bank){const image=await request.get(q.image.src);expect(image.status()).toBe(200);expect(createHash('sha256').update(await image.body()).digest('hex')).toBe(q.image.sha256);}
 for(const name of ['/data/questions.json','/reviews.json','/manifest.json','/decisions.json','/candidate-recommendation.json','/Technology-01.pdf','/src/content/owner-review.json','/.local/historical/technology-01/questions.json'])expect((await request.get(name)).status()).toBe(404);
 const all=JSON.parse(readFileSync('.local/historical/technology-01/questions.json','utf8'));
 const excluded=all.find((q:{id:string})=>!bank.some(b=>b.id===q.id));expect((await request.get(`/__pilot/images/${excluded.images[0].sha256}.webp`)).status()).toBe(404);
 expect((await request.post('/')).status()).toBe(405);expect((await request.get('/',{headers:{Host:'localhost:4333'}})).status()).toBe(403);expect((await request.get('/',{headers:{Origin:'https://example.com'}})).status()).toBe(403);
});

for(const q of additions)test(`original description, options and grading: ${q.id}`,async({page})=>{
 await page.goto(`/practice/${q.topic}/?question=${q.id}`);
 await expect(page.locator('.question-meta h2')).toContainText(`FE · Morning · Subject A · ${q.year}`);
 await expect(page.locator('.question-meta h2')).toContainText(`Q${q.number}`);
 await expect(page.locator('[data-preview-collection]')).toHaveText('Batch 3 · Private addition · Unapproved');
 const image=page.locator('.exam-image-figure img');await expect(image).toHaveAttribute('src',q.image.src);await image.evaluate(async(el:HTMLImageElement)=>el.decode());expect(await image.evaluate((el:HTMLImageElement)=>[el.naturalWidth,el.naturalHeight])).toEqual([q.image.width,q.image.height]);
 const e=answers.find(e=>e.questionId===q.id)!;
 await page.getByText('Read the question as text',{exact:true}).click();await expect(page.locator('.question-transcript p').first()).toHaveText(e.imageDescription);
 for(const option of ['a','b','c','d'])await expect(page.getByRole('radio',{name:`Option ${option.toUpperCase()}: ${e.optionText[option]}`,exact:true})).toBeVisible();
 await expect(page.locator('.answer-feedback')).toHaveCount(0);
 await page.getByRole('radio',{name:`Option ${q.correctAnswer.toUpperCase()}: ${e.optionText[q.correctAnswer]}`,exact:true}).check();await page.getByRole('button',{name:'Check answer',exact:true}).click();
 await expect(page.getByRole('heading',{name:'✓ That’s correct.'})).toBeVisible();await expect(page.locator('.answer-summary')).toHaveText(e.summary);await expect(page.locator('.answer-feedback ol li')).toHaveText(e.steps);
 const progress=await page.evaluate(key=>JSON.parse(localStorage.getItem(key)!),prefix+'guest:v1');expect(progress.attempts.at(-1).questionId).toBe(q.id);expect(progress.attempts.at(-1).correct).toBe(true);
 expect(await page.content()).not.toMatch(/preparationHistory|beforeReviewSha256|Printed key:|editorial-review-pending/);
});

for(const topic of [...new Set(additions.map(q=>q.topic))])test(`source highlight, counts and reading return: ${topic}`,async({page})=>{
 const c=concepts.find(c=>c.id===topic)!;await page.goto(c.sectionUrl);await page.evaluate(()=>document.fonts.ready);
 const link=page.locator(`.reader-prose [data-concept="${topic}"]`);await expect(link).toHaveCount(1);
 const added=additions.filter(q=>q.topic===topic).length,released=bank.filter(q=>q.previewCollection==='published'&&c.id===topic&&read('preview/app/src/content/concepts.json').find((x:{id:string})=>x.id===topic).questionIds.includes(q.id)).length;
 await expect(link).toContainText(`${released} published + ${added} new private`);
 await link.scrollIntoViewIfNeeded();await page.waitForTimeout(300);const pos=await link.evaluate(el=>{const b=el.closest('[data-reading-block]')!;return {id:b.id,offset:b.getBoundingClientRect().top};});
 await link.click();await expect(page.locator('.question-navigation button')).toHaveCount(added+released);
 await page.getByRole('link',{name:'← Return to textbook',exact:true}).click();await expect.poll(()=>page.locator(`[id="${pos.id}"]`).evaluate((el,offset)=>Math.abs(el.getBoundingClientRect().top-offset),pos.offset)).toBeLessThan(4);
});

test('collection/year/source filters, empty recovery and published reference preservation',async({page})=>{
 await page.goto('/practice/logic-gates/');await page.getByRole('combobox',{name:'Preview collection'}).selectOption('published');await expect(page.locator('[data-preview-collection]')).toHaveText('Published reference');
 await page.getByRole('combobox',{name:'Question source'}).selectOption('itpec-practice');await expect(page.locator('.source-note').filter({hasText:'ID:'})).not.toContainText('HIST-');
 await page.getByRole('combobox',{name:'Question source'}).selectOption('historical-pdf');await expect(page.locator('.source-note').filter({hasText:'ID:'})).toContainText('HIST-');
 await page.goto('/practice/arithmetic-circuits/');await page.getByRole('combobox',{name:'Preview collection'}).selectOption('published');await expect(page.getByRole('heading',{name:'Practice is not available yet'})).toBeVisible();
 await page.getByRole('combobox',{name:'Preview collection'}).selectOption('batch03');await expect(page.locator('.question-navigation button')).toHaveCount(3);
 await page.getByRole('combobox',{name:'From year'}).selectOption('2021');await expect(page.locator('.question-navigation button')).toHaveCount(1);
 await expect(page.locator('.practice-filters p[aria-live]')).toContainText('0 published in this concept · 3 new private Batch 3 · 1 match active filters.');
});

test('owner gallery is complete, read-only and navigable',async({page})=>{
 await page.goto('/review/');await expect(page.locator('article')).toHaveCount(40);await expect(page.getByRole('button',{name:/approve|publish/i})).toHaveCount(0);
 for(const q of additions){const article=page.locator(`article[id="${q.id}"]`);await expect(article.locator('img')).toHaveAttribute('src',q.image.src);await expect(article).toContainText('Approval: unapproved');}
});

test('mobile keyboard, source enlargement, bookmark and persistent disposable progress',async({page},info)=>{
 const external:string[]=[];page.on('request',r=>{if(!r.url().startsWith('http://127.0.0.1:4333/')&&!r.url().startsWith('data:'))external.push(r.url());});
 await page.addInitScript(()=>{localStorage.setItem('itpecTextbook:guest:v1','guest-sentinel');localStorage.setItem('itpecTextbook:account:real-user:v1','account-sentinel');sessionStorage.setItem('itpecTextbook:return:v1','reading-sentinel');});
 await page.setViewportSize({width:320,height:900});
 for(const id of ['HIST-TECH01-2021S-Q021','HIST-TECH01-2009A-Q007','HIST-TECH01-2007S-Q005']){
  const q=additions.find(q=>q.id===id)!;await page.goto(`/practice/${q.topic}/?question=${id}`);await page.getByRole('button',{name:`Enlarge original question ${id}`}).focus();await page.keyboard.press('Enter');await expect(page.getByRole('dialog')).toBeVisible();
  await page.screenshot({path:info.outputPath(`${id}-mobile.png`)});await page.keyboard.press('Escape');expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 }
 const q=additions.find(q=>q.topic==='arithmetic-circuits')!;await page.goto(`/practice/${q.topic}/?question=${q.id}`);
 await page.getByRole('button',{name:'◇ Bookmark',exact:true}).click();const wrong=['a','b','c','d'].find(o=>o!==q.correctAnswer)!;
 await page.getByRole('radio',{name:new RegExp(`^Option ${wrong.toUpperCase()}:`)}).focus();await page.keyboard.press('Space');await page.getByRole('button',{name:'Check answer',exact:true}).focus();await page.keyboard.press('Enter');await expect(page.getByRole('heading',{name:'Let’s work through it.'})).toBeVisible();
 await page.reload();await expect(page.getByRole('button',{name:'◆ Bookmarked',exact:true})).toBeVisible();await expect(page.getByRole('heading',{name:'Let’s work through it.'})).toBeVisible();
 await page.getByRole('button',{name:'Next →',exact:true}).click();await expect(page.locator('.source-note').filter({hasText:'ID:'})).not.toContainText(q.id);
 expect(external).toEqual([]);expect(await page.evaluate(()=>[localStorage.getItem('itpecTextbook:guest:v1'),localStorage.getItem('itpecTextbook:account:real-user:v1'),sessionStorage.getItem('itpecTextbook:return:v1')])).toEqual(['guest-sentinel','account-sentinel','reading-sentinel']);
 await page.goto('/');await page.getByRole('button',{name:'Reset preview progress'}).click();await expect.poll(()=>page.evaluate(key=>localStorage.getItem(key),prefix+'guest:v1')).toBeNull();expect(await page.evaluate(()=>localStorage.getItem('itpecTextbook:guest:v1'))).toBe('guest-sentinel');
});
