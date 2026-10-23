import {test,expect} from '@playwright/test';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const root='.local/historical-batches/technology01-hardware-batch02/';
const read=(p:string)=>JSON.parse(readFileSync(root+p,'utf8'));
type Question={id:string;topic:string;year:number;number:number;correctAnswer:string;previewCollection:string;image:{src:string;sha256:string;width:number;height:number}};
const bank=read('preview/app/src/content/pilot-bank.json') as Question[];
const additions=bank.filter(q=>q.previewCollection==='batch02');
const answers=read('preview/app/src/content/explanations.json') as Array<{questionId:string;summary:string;steps:string[];imageDescription:string;optionText:Record<string,string>}>;
const concepts=read('preview/app/src/content/concepts.json') as Array<{id:string;sectionUrl:string;title:string}>;
const prefix='itpecTextbook:privateHardwareBatch02:';

test('exact scope, private transport, published references and source privacy',async({request})=>{
 expect(additions).toHaveLength(40);expect(bank).toHaveLength(76);expect(new Set(bank.map(q=>q.id)).size).toBe(76);
 const home=await request.get('/');expect(home.status()).toBe(200);expect(await home.text()).toContain('40 Batch 2 private additions plus 36 published Release 1 references');
 expect(home.headers()['x-robots-tag']).toContain('noindex');expect(home.headers()['content-security-policy']).toContain("connect-src 'self'");
 for(const q of bank){const image=await request.get(q.image.src);expect(image.status()).toBe(200);expect(createHash('sha256').update(await image.body()).digest('hex')).toBe(q.image.sha256);}
 for(const path of ['/data/questions.json','/questions.json','/reviews.json','/manifest.json','/decisions.json','/candidate-recommendation.json','/Technology-01.pdf','/.local/historical/technology-01/questions.json','/__pilot/images/not-selected.webp'])expect((await request.get(path)).status()).toBe(404);
 const all=JSON.parse(readFileSync('.local/historical/technology-01/questions.json','utf8'));
 const excluded=all.find((q:{id:string})=>!bank.some(b=>b.id===q.id));
 expect((await request.get(`/__pilot/images/${excluded.images[0].sha256}.webp`)).status()).toBe(404);
 expect((await request.post('/')).status()).toBe(405);
 expect((await request.get('/',{headers:{Host:'localhost:4328'}})).status()).toBe(403);
 expect((await request.get('/',{headers:{Origin:'https://example.com'}})).status()).toBe(403);
});

for(const q of additions)test(`original, accessible choices and preserved grading: ${q.id}`,async({page})=>{
 await page.goto(`/practice/${q.topic}/?question=${q.id}`);
 await expect(page.locator('.question-meta h2')).toContainText(`FE · Morning · Subject A · ${q.year}`);
 await expect(page.locator('.question-meta h2')).toContainText(`Q${q.number}`);
 await expect(page.locator('[data-preview-collection]')).toHaveText('Batch 2 · Private addition · Unapproved');
 const image=page.locator('.exam-image-figure img');await expect(image).toHaveAttribute('src',q.image.src);
 await image.evaluate(async(el:HTMLImageElement)=>el.decode());expect(await image.evaluate((el:HTMLImageElement)=>[el.naturalWidth,el.naturalHeight])).toEqual([q.image.width,q.image.height]);
 const e=answers.find(e=>e.questionId===q.id)!;
 await page.getByText('Read the question as text',{exact:true}).click();await expect(page.locator('.question-transcript p').first()).toHaveText(e.imageDescription);
 for(const option of ['a','b','c','d'])await expect(page.getByRole('radio',{name:`Option ${option.toUpperCase()}: ${e.optionText[option]}`,exact:true})).toBeVisible();
 await page.getByRole('radio',{name:`Option ${q.correctAnswer.toUpperCase()}: ${e.optionText[q.correctAnswer]}`,exact:true}).check();
 await page.getByRole('button',{name:'Check answer',exact:true}).click();await expect(page.getByRole('heading',{name:'✓ That’s correct.'})).toBeVisible();
 await expect(page.locator('.answer-summary')).toHaveText(e.summary);await expect(page.locator('.answer-feedback ol li')).toHaveText(e.steps);
 const progress=await page.evaluate(key=>JSON.parse(localStorage.getItem(key)!),prefix+'guest:v1');
 expect(progress.attempts.at(-1).questionId).toBe(q.id);expect(progress.attempts.at(-1).correct).toBe(true);
 expect(await page.content()).not.toMatch(/preparationHistory|beforeReviewSha256|Printed key:|editorial-review-pending/);
});

for(const topic of [...new Set(additions.map(q=>q.topic))])test(`source highlight and exact reading return: ${topic}`,async({page})=>{
 const c=concepts.find(c=>c.id===topic)!;await page.goto(c.sectionUrl);await page.evaluate(()=>document.fonts.ready);
 const link=page.locator(`.reader-prose [data-concept="${topic}"]`);await expect(link).toHaveCount(1);
 const added=additions.filter(q=>q.topic===topic).length,released=bank.filter(q=>q.topic===topic&&q.previewCollection==='published36').length;
 await expect(link).toContainText(`${added} private + ${released} published`);
 await link.scrollIntoViewIfNeeded();await page.waitForTimeout(300);
 const position=await link.evaluate(el=>{const b=el.closest('[data-reading-block]')!;return {id:b.id,offset:b.getBoundingClientRect().top};});
 await link.click();await expect(page.locator('.question-navigation button')).toHaveCount(added+released);
 await page.getByRole('link',{name:'← Return to textbook',exact:true}).click();
 await expect.poll(()=>page.locator(`[id="${position.id}"]`).evaluate((el,offset)=>Math.abs(el.getBoundingClientRect().top-offset),position.offset)).toBeLessThan(4);
});

test('comparison filters recover from empty collection and retain reference contents',async({page})=>{
 const q=additions.find(q=>q.topic==='cpu-registers')!;
 await page.goto(`/practice/${q.topic}/?question=${q.id}`);
 await page.getByRole('combobox',{name:'Preview collection'}).selectOption('published36');
 await expect(page.locator('[data-preview-collection]')).toHaveText('Release 1 · Published reference');
 const original=bank.find(q=>q.topic==='cpu-registers'&&q.previewCollection==='published36')!,e=answers.find(e=>e.questionId===original.id)!;
 await expect(page.locator('.source-note').filter({hasText:'ID:'})).toContainText(original.id);
 await page.getByRole('radio',{name:`Option ${original.correctAnswer.toUpperCase()}: ${e.optionText[original.correctAnswer]}`,exact:true}).check();
 await page.getByRole('button',{name:'Check answer',exact:true}).click();await expect(page.locator('.answer-summary')).toHaveText(e.summary);
 await page.goto('/practice/device-drivers/');
 await page.getByRole('combobox',{name:'Preview collection'}).selectOption('published36');
 await expect(page.getByRole('heading',{name:'Practice is not available yet'})).toBeVisible();
 await page.getByRole('combobox',{name:'Preview collection'}).selectOption('batch02');
 await expect(page.locator('.question-navigation button')).toHaveCount(2);
});

test('literal exponent alternatives and neutral diagram descriptions',async({page})=>{
 await page.goto('/practice/signed-integers/?question=HIST-TECH01-2008S-Q003');
 await expect(page.getByRole('radio',{name:'Option A: −2^n through 2^(n−1)',exact:true})).toBeVisible();
 await expect(page.getByRole('radio',{name:'Option C: −2^(n−1) through 2^(n−1) − 1',exact:true})).toBeVisible();
 for(const id of ['HIST-TECH01-2011S-Q013','HIST-TECH01-2017S-Q013']){
  const q=bank.find(q=>q.id===id)!;await page.goto(`/practice/${q.topic}/?question=${id}`);await page.getByText('Read the question as text',{exact:true}).click();
  const text=await page.locator('.question-transcript').innerText();
  expect(text).not.toMatch(/A\(control\)|B\(operation\)|A=Control|device driver is software that controls/i);
 }
});

test('mobile keyboard, original diagram enlargement, navigation and progress isolation',async({page},info)=>{
 const external:string[]=[];page.on('request',r=>{if(!r.url().startsWith('http://127.0.0.1:4328/')&&!r.url().startsWith('data:'))external.push(r.url());});
 await page.addInitScript(()=>{
  localStorage.setItem('itpecTextbook:guest:v1','guest-sentinel');localStorage.setItem('itpecTextbook:privatePilot36:guest:v1','old-pilot-sentinel');
  localStorage.setItem('itpecTextbook:account:real-user:v1','account-sentinel');sessionStorage.setItem('itpecTextbook:return:v1','reading-sentinel');
 });
 await page.setViewportSize({width:320,height:900});
 for(const id of ['HIST-TECH01-2011S-Q013','HIST-TECH01-2018A-Q012','HIST-TECH01-2008A-Q004']){
  const q=bank.find(q=>q.id===id)!;await page.goto(`/practice/${q.topic}/?question=${id}`);
  await page.getByRole('button',{name:`Enlarge original question ${id}`}).focus();await page.keyboard.press('Enter');await expect(page.getByRole('dialog')).toBeVisible();
  const image=page.locator('.image-dialog img');await image.evaluate(async(el:HTMLImageElement)=>el.decode());expect(await image.evaluate((el:HTMLImageElement)=>el.naturalWidth)).toBe(q.image.width);
  await page.screenshot({path:info.outputPath(`${id}-mobile-original.png`)});await page.keyboard.press('Escape');
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 }
 const q=additions.find(q=>q.topic==='cache-memory')!;await page.goto(`/practice/${q.topic}/?question=${q.id}`);
 const wrong=['a','b','c','d'].find(c=>c!==q.correctAnswer)!;await page.getByRole('radio',{name:new RegExp(`^Option ${wrong.toUpperCase()}:`)}).focus();await page.keyboard.press('Space');
 await page.getByRole('button',{name:'Check answer',exact:true}).focus();await page.keyboard.press('Enter');await expect(page.getByRole('heading',{name:'Let’s work through it.'})).toBeVisible();
 await page.getByRole('button',{name:'Next →',exact:true}).click();await expect(page.locator('.source-note').filter({hasText:'ID:'})).not.toContainText(q.id);
 await page.goto('/progress/');await expect(page.getByRole('button',{name:'Continue with Google'})).toHaveCount(0);
 expect(external).toEqual([]);
 expect(await page.evaluate(()=>[localStorage.getItem('itpecTextbook:guest:v1'),localStorage.getItem('itpecTextbook:privatePilot36:guest:v1'),localStorage.getItem('itpecTextbook:account:real-user:v1'),sessionStorage.getItem('itpecTextbook:return:v1')])).toEqual(['guest-sentinel','old-pilot-sentinel','account-sentinel','reading-sentinel']);
 await page.goto('/');await page.getByRole('button',{name:'Reset preview progress'}).click();
 await expect.poll(()=>page.evaluate(key=>localStorage.getItem(key),prefix+'guest:v1')).toBeNull();
 expect(await page.evaluate(()=>localStorage.getItem('itpecTextbook:guest:v1'))).toBe('guest-sentinel');
});
