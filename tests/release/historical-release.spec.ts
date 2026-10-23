import { test,expect } from '@playwright/test';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import receipt from '../../docs/development/evidence/historical-release-36.json' with {type:'json'};
import explanations from '../../src/content/explanations.json' with {type:'json'};
import concepts from '../../src/content/concepts.json' with {type:'json'};
const bank=JSON.parse(readFileSync('public/data/questions.json','utf8'));
const sha=(b:Buffer)=>createHash('sha256').update(b).digest('hex');

test('real served catalog and all 36 image bytes equal the reviewed release; private records are absent',async({request})=>{
  const response=await request.get('/data/questions.json');expect(response.ok()).toBe(true);
  expect(sha(await response.body())).toBe(sha(readFileSync('public/data/questions.json')));
  const served=await response.json();expect(served).toHaveLength(456);
  expect(served.filter((q:any)=>q.format==='historical').map((q:any)=>q.id).sort()).toEqual(receipt.records.map(r=>r.id).sort());
  for(const entry of receipt.records){
    const q=served.find((q:any)=>q.id===entry.id),image=await request.get(q.image.src);
    expect(image.ok(),entry.id).toBe(true);expect(sha(await image.body()),entry.id).toBe(entry.imageSha256);
  }
  for(const path of ['/.local/historical/technology-01/reviews.json','/data-sources/historical-pdfs/Technology-01.pdf','/approval-candidates/manifest.json'])expect((await request.get(path)).status()).toBe(404);
});

for(const cid of Object.keys(receipt.conceptCounts)){
 test(`${cid}: source highlight, authorized grading, bookmark, reload and return to reading`,async({page})=>{
  const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
  const entry=receipt.records.find(r=>r.conceptId===cid)!;
  const q=bank.find((q:any)=>q.id===entry.id),e=explanations.find(e=>e.questionId===entry.id)!,c=concepts.find(c=>c.id===cid)!;
  await page.goto(c.sectionUrl);const highlight=page.locator(`#concept-${cid}`);await highlight.scrollIntoViewIfNeeded();await highlight.click();
  await expect(page).toHaveURL(new RegExp(`/practice/${cid}/`));
  await page.goto(`/practice/${cid}/?question=${entry.id}`);
  await expect(page.locator('.question-meta h2')).toHaveText(`${q.year} ${q.season==='S'?'Spring':'Autumn'} · Morning · Q${q.number}`);
  await expect(page.locator('.exam-image-figure img')).toHaveAttribute('src',q.image.src);
  await page.getByText('Read the question as text',{exact:true}).click();
  await expect(page.locator('.question-transcript p').first()).toHaveText(e.imageDescription);
  const option=page.getByRole('radio',{name:new RegExp(`^Option ${q.correctAnswer.toUpperCase()}:`)});
  await option.focus();await page.keyboard.press('Space');await page.getByRole('button',{name:'Check answer'}).focus();await page.keyboard.press('Enter');
  await expect(page.getByText('✓ That’s correct.')).toBeVisible();await expect(page.locator('.answer-summary')).toHaveText(e.summary);
  await expect(page.locator('.answer-feedback ol li')).toHaveText(e.steps);
  await page.getByRole('button',{name:'◇ Bookmark'}).click();await page.reload();
  await expect(page.getByRole('button',{name:'◆ Bookmarked'})).toBeVisible();await expect(page.getByText('✓ That’s correct.')).toBeVisible();
  await page.getByRole('link',{name:'← Return to textbook'}).click();await expect(highlight).toBeFocused();
  expect(errors).toEqual([]);
 });
}

for(const [id,width] of [['HIST-TECH01-2019A-Q012',375],['HIST-TECH01-2019S-Q023',320]] as const){
 test(`${id}: native accessibility correction and original diagram at ${width}px`,async({page},info)=>{
  const entry=receipt.records.find(r=>r.id===id)!,e=explanations.find(e=>e.questionId===id)!;
  await page.setViewportSize({width,height:900});await page.goto(`/practice/${entry.conceptId}/?question=${id}`);
  await page.getByText('Read the question as text',{exact:true}).click();await expect(page.locator('.question-transcript p').first()).toHaveText(e.imageDescription);
  if(id.endsWith('Q012'))expect(e.imageDescription).toContain('inside the Processor');
  else{expect(e.imageDescription).toContain('crossing without a dot');await expect(page.getByRole('radio').nth(3)).toHaveAttribute('aria-label','Option D: B AND (A OR B)');}
  await page.getByRole('button',{name:`Enlarge original question ${id}`}).click();await expect(page.getByRole('dialog')).toBeVisible();
  await expect(page.getByRole('dialog').locator('img')).toHaveAttribute('alt',e.imageDescription);await page.keyboard.press('Escape');
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  expect(await page.locator('body').innerText()).not.toMatch(/editorial warning|source-validated|owner-adjudicated|unapproved|technicalEligibility/i);
  await page.screenshot({path:info.outputPath(`${id}-${width}.png`),fullPage:true});
 });
}

test('historical source filtering and unanswered navigation preserve submitted feedback',async({page})=>{
 await page.goto('/practice/logic-gates/');await page.getByRole('combobox',{name:'Question source'}).selectOption('historical-pdf');
 await expect(page.locator('.practice-filters')).toContainText('24 of 29 questions match.');
 await page.getByRole('checkbox',{name:'Unanswered only'}).check();
 const first=receipt.records.filter(r=>r.conceptId==='logic-gates').map(r=>bank.find((q:any)=>q.id===r.id)).sort((a,b)=>a.id.localeCompare(b.id))[0];
 await page.getByRole('radio',{name:new RegExp(`^Option ${first.correctAnswer.toUpperCase()}:`)}).check();await page.getByRole('button',{name:'Check answer'}).click();
 await expect(page.getByText('✓ That’s correct.')).toBeVisible();await expect(page.getByText('Answer saved · 23 unanswered remain')).toBeVisible();
 await page.getByRole('button',{name:'Next →'}).click();await expect(page.getByText('✓ That’s correct.')).toHaveCount(0);
});
