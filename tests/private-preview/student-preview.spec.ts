import {test,expect} from '@playwright/test';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const read=(p:string)=>JSON.parse(readFileSync(`.local/private-student-preview/${p}`,'utf8'));
const bank=read('app/src/content/pilot-bank.json') as Array<{id:string;topic:string;number:number;year:number;correctAnswer:string;image:{src:string;sha256:string;width:number;height:number}}>;
const answers=read('app/src/content/explanations.json') as Array<{questionId:string;summary:string;steps:string[]}>;
const walkthrough=read('walkthrough.json') as Array<{conceptId:string;questionId:string;readingUrl:string;practiceUrl:string}>;
const prefix='itpecTextbook:privatePilot36:';
const guestKey=prefix+'guest:v1';

test('exact scope and truthful metadata; no public/historical extras',async({request})=>{
 expect(bank).toHaveLength(36);expect(new Set(bank.map(q=>q.id)).size).toBe(36);
 const home=await request.get('/');expect(await home.text()).toContain('36 historical questions');
 expect(await home.text()).toContain('FE · Morning · Subject A');expect(await home.text()).not.toContain('not established');
 expect(home.headers()['x-robots-tag']).toContain('noindex');
 for(const path of ['/data/questions.json','/questions.json','/reviews.json','/manifest.json','/review-findings.json','/accessibility-repairs.json','/accessibility-review/findings-before.json','/Technology-01.pdf','/FE%20Vol%201.pdf','/.local/historical/technology-01/questions.json','/__pilot/images/not-selected.webp','/practice/floating-point/'])expect((await request.get(path)).status()).toBe(404);
 const originalCatalog=JSON.parse(readFileSync('.local/historical/technology-01/questions.json','utf8')) as Array<{id:string;images:Array<{sha256:string}>}>;
 const excluded=originalCatalog.find(q=>!bank.some(selected=>selected.id===q.id))!;
 expect((await request.get(`/__pilot/images/${excluded.images[0].sha256}.webp`)).status()).toBe(404);
 expect((await request.post('/')).status()).toBe(405);
 expect((await request.get('/',{headers:{Host:'localhost:4325'}})).status()).toBe(403);
 expect((await request.get('/',{headers:{Origin:'https://example.com'}})).status()).toBe(403);
});

for(const q of bank)test(`original image, verified answer and worked explanation: ${q.id}`,async({page,request})=>{
 await page.goto(`/practice/${q.topic}/?question=${q.id}`);
 await expect(page.locator('.question-meta h2')).toContainText(`FE · Morning · Subject A · ${q.year}`);
 await expect(page.locator('.question-meta h2')).toContainText(`Q${q.number}`);
 await expect(page.locator('.question-meta h2')).not.toContainText('Paper/subject not established');
 await expect(page.locator('.source-note').filter({hasText:'ID:'})).toContainText(q.id);
 await expect(page.locator('[aria-label="Private editorial review"]')).toHaveCount(0);
 expect(await page.content()).not.toMatch(/previewNotices|Editorial review pending|Diagram accessibility review pending/);
 const image=page.locator('.exam-image-figure img');await expect(image).toHaveAttribute('src',q.image.src);
 await image.evaluate(async(el:HTMLImageElement)=>{await el.decode();});
 expect(await image.evaluate((el:HTMLImageElement)=>[el.naturalWidth,el.naturalHeight])).toEqual([q.image.width,q.image.height]);
 const original=await request.get(q.image.src);expect(createHash('sha256').update(await original.body()).digest('hex')).toBe(q.image.sha256);
 await page.getByRole('radio',{name:new RegExp(`^Option ${q.correctAnswer.toUpperCase()}:`)}).check();
 await page.getByRole('button',{name:'Check answer',exact:true}).click();
 await expect(page.getByRole('heading',{name:'✓ That’s correct.'})).toBeVisible();
 const e=answers.find(e=>e.questionId===q.id)!;await expect(page.locator('.answer-summary')).toHaveText(e.summary);
 await expect(page.locator('.answer-feedback ol li')).toHaveText(e.steps);
 const saved=await page.evaluate(key=>JSON.parse(localStorage.getItem(key)!),guestKey);
 expect(saved.attempts.at(-1).questionId).toBe(q.id);expect(saved.attempts.at(-1).correct).toBe(true);
});

for(const [id,fragments] of [
 ['HIST-TECH01-2019A-Q012',['Main memory is outside the box labeled Processor','right-pointing arrow leads from Main memory','right-pointing arrow leads from a to the Instruction decoder']],
 ['HIST-TECH01-2019S-Q023',['upper AND gate and a lower OR gate','crossing without a dot is not a junction','upper input of a final OR gate','There are no inversion bubbles']],
] as const)test(`corrected source-diagram transcription: ${id}`,async({page},info)=>{
 const q=bank.find(q=>q.id===id)!;
 const original=JSON.parse(readFileSync('.local/historical/technology-01/reviews.json','utf8'))[id];
 await page.goto(`/practice/${q.topic}/?question=${id}`);
 await page.getByText('Read the question as text',{exact:true}).click();
 const transcript=page.locator('.question-transcript');
 for(const fragment of fragments)await expect(transcript).toContainText(fragment);
 if(id==='HIST-TECH01-2019S-Q023')await expect(page.getByRole('radio',{name:'Option D: B AND (A OR B)',exact:true})).toBeVisible();
 expect(q.correctAnswer).toBe(original.verification.independentAnswer);
 const e=answers.find(e=>e.questionId===id)!;
 expect(e.summary).toBe(original.explanation.summary);expect(e.steps).toEqual(original.explanation.steps);
 await page.getByRole('button',{name:`Enlarge original question ${id}`}).click();
 const zoom=page.getByRole('dialog').getByRole('img');
 for(const fragment of fragments)await expect(zoom).toHaveAttribute('alt',new RegExp(fragment.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')));
 await page.keyboard.press('Escape');
 await page.setViewportSize({width:375,height:900});
 await page.screenshot({path:info.outputPath(`${id}-accessible-mobile.png`),fullPage:true});
});

for(const entry of walkthrough)test(`reading, existing highlight, practice and exact return: ${entry.conceptId}`,async({page},info)=>{
 await page.goto('/chapters/hardware/');await page.goto(entry.readingUrl);await page.evaluate(()=>document.fonts.ready);
 const link=page.locator(`.reader-prose [data-concept="${entry.conceptId}"]`);await expect(link).toHaveCount(1);
 const count=bank.filter(q=>q.topic===entry.conceptId).length;await expect(link).toContainText(`${count} ${count===1?'question':'questions'}`);
 await link.scrollIntoViewIfNeeded();await page.waitForTimeout(300);
 const position=await link.evaluate(el=>{const b=el.closest('[data-reading-block]')!;return {id:b.id,offset:b.getBoundingClientRect().top};});
 await page.screenshot({path:info.outputPath(`${entry.conceptId}-reading.png`)});
 await link.click();await expect(page.locator('.question-navigation button')).toHaveCount(count);
 await expect(page.locator('.source-note').filter({hasText:'ID:'})).toContainText(entry.questionId);
 await page.screenshot({path:info.outputPath(`${entry.conceptId}-practice.png`),fullPage:true});
 await page.getByRole('link',{name:'← Return to textbook',exact:true}).click();
 await expect.poll(()=>page.locator(`[id="${position.id}"]`).evaluate((el,offset)=>Math.abs(el.getBoundingClientRect().top-offset),position.offset)).toBeLessThan(4);
});

test('wrong answer, retry, all year/source/unanswered filters and exact counts',async({page})=>{
 const q=bank.find(q=>q.topic==='logic-gates')!;
 await page.goto(`/practice/logic-gates/?question=${q.id}`);
 const wrong=['a','b','c','d'].find(c=>c!==q.correctAnswer)!;
 await page.getByRole('radio',{name:new RegExp(`^Option ${wrong.toUpperCase()}:`)}).check();await page.getByRole('button',{name:'Check answer',exact:true}).click();
 await expect(page.getByRole('heading',{name:'Let’s work through it.'})).toBeVisible();
 await page.getByRole('button',{name:'Try this question again'}).click();
 await page.getByRole('radio',{name:new RegExp(`^Option ${q.correctAnswer.toUpperCase()}:`)}).check();await page.getByRole('button',{name:'Check answer',exact:true}).click();
 await expect(page.getByRole('heading',{name:'✓ That’s correct.'})).toBeVisible();
 await page.getByRole('checkbox',{name:'Unanswered only'}).check();
 const second=bank.filter(q=>q.topic==='logic-gates')[1];
 await expect(page.locator('.source-note').filter({hasText:'ID:'})).toContainText(second.id);
 await page.getByRole('radio',{name:new RegExp(`^Option ${second.correctAnswer.toUpperCase()}:`)}).check();await page.getByRole('button',{name:'Check answer',exact:true}).click();
 await expect(page.getByText('Answer saved · 22 unanswered remain')).toBeVisible();
 await page.getByRole('button',{name:'Next →',exact:true}).click();
 await expect(page.locator('.question-navigation button')).toHaveCount(22);
 await page.getByRole('checkbox',{name:'Unanswered only'}).uncheck();
 const year=2018,count=bank.filter(q=>q.topic==='logic-gates'&&q.year===year).length;
 await page.getByRole('combobox',{name:'From year'}).selectOption(String(year));await page.getByRole('combobox',{name:'To year'}).selectOption(String(year));
 await expect(page.getByText(`${count} of 24 questions match.`)).toBeVisible();
 await page.getByRole('combobox',{name:'Question source'}).selectOption('itpec-practice');
 await expect(page.getByRole('heading',{name:'No questions match these filters'})).toBeVisible();
 await page.reload();await expect(page.getByRole('heading',{name:'No questions match these filters'})).toBeVisible();
 await page.getByRole('combobox',{name:'Question source'}).selectOption('historical-pdf');await expect(page.getByText(`${count} of 24 questions match.`)).toBeVisible();
});

test('mobile keyboard, image enlargement, navigation, progress/account isolation and reset',async({page},info)=>{
 const external:string[]=[];page.on('request',r=>{if(!r.url().startsWith('http://127.0.0.1:4325/')&&!r.url().startsWith('data:'))external.push(r.url());});
 await page.addInitScript(()=>{
  localStorage.setItem('itpecTextbook:guest:v1','genuine-guest-sentinel');localStorage.setItem('itpecTextbook:account:real-user:v1','genuine-account-sentinel');
  localStorage.setItem('itpecTextbook:authOptIn:v1','real-user');sessionStorage.setItem('itpecTextbook:return:v1','genuine-return-sentinel');
 });
 await page.setViewportSize({width:375,height:900});const q=bank.find(q=>q.topic==='logic-gates')!;
 await page.goto(`/practice/${q.topic}/?question=${q.id}`);
 await page.getByRole('button',{name:`Enlarge original question ${q.id}`}).focus();await page.keyboard.press('Enter');
 await expect(page.getByRole('dialog')).toBeVisible();await page.keyboard.press('Escape');await expect(page.getByRole('dialog')).not.toBeVisible();
 const radio=page.getByRole('radio',{name:new RegExp(`^Option ${q.correctAnswer.toUpperCase()}:`)});await radio.focus();await page.keyboard.press('Space');
 await page.getByRole('button',{name:'Check answer',exact:true}).focus();await page.keyboard.press('Enter');
 await expect(page.getByRole('heading',{name:'✓ That’s correct.'})).toBeVisible();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 await page.screenshot({path:info.outputPath('boolean-mobile.png'),fullPage:true});
 await page.goto('/progress/');await expect(page.getByRole('button',{name:'Continue with Google'})).toHaveCount(0);
 await expect(page.getByRole('heading',{name:'Private preview progress'})).toBeVisible();
 const genuine=await page.evaluate(()=>[localStorage.getItem('itpecTextbook:guest:v1'),localStorage.getItem('itpecTextbook:account:real-user:v1'),sessionStorage.getItem('itpecTextbook:return:v1')]);
 expect(genuine).toEqual(['genuine-guest-sentinel','genuine-account-sentinel','genuine-return-sentinel']);expect(external).toEqual([]);
 await page.goto('/');await page.getByRole('button',{name:'Reset preview progress'}).click();
 await expect.poll(()=>page.evaluate(key=>localStorage.getItem(key),guestKey)).toBeNull();
 expect(await page.evaluate(()=>localStorage.getItem('itpecTextbook:guest:v1'))).toBe('genuine-guest-sentinel');
});

test('all six radix originals remain readable through mobile enlargement',async({page},info)=>{
 await page.setViewportSize({width:320,height:900});
 for(const q of bank.filter(q=>q.topic==='radix-conversion')){
  await page.goto(`/practice/${q.topic}/?question=${q.id}`);
  await page.getByRole('button',{name:`Enlarge original question ${q.id}`}).click();
  await expect(page.getByRole('dialog')).toBeVisible();
  const image=page.locator('.image-dialog img');await image.evaluate(async(el:HTMLImageElement)=>{await el.decode();});
  expect(await image.evaluate((el:HTMLImageElement)=>el.naturalWidth)).toBe(q.image.width);
  await page.screenshot({path:info.outputPath(`${q.id}-radix-320.png`)});
  await page.keyboard.press('Escape');expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 }
});
