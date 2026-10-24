import {test,expect} from '@playwright/test';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import receipt from '../../docs/development/evidence/historical-release-3.json' with {type:'json'};
import sixth from '../../docs/development/evidence/historical-release-6.json' with {type:'json'};
import fifth from '../../docs/development/evidence/historical-release-5.json' with {type:'json'};
import fourth from '../../docs/development/evidence/historical-release-4.json' with {type:'json'};
import second from '../../docs/development/evidence/historical-release-40.json' with {type:'json'};
import first from '../../docs/development/evidence/historical-release-36.json' with {type:'json'};
import concepts from '../../src/content/concepts.json' with {type:'json'};
import answers from '../../src/content/explanations.json' with {type:'json'};
const bytes=readFileSync('public/data/questions.json'),bank=JSON.parse(bytes.toString());

test('actual deployed catalog, all 656 original images, authorized historical scope and private exclusions',async({page})=>{
  test.setTimeout(180_000);
  await page.goto('/');
  const result=await page.evaluate(async()=>{
    const sha=async(bytes:ArrayBuffer)=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))).map(b=>b.toString(16).padStart(2,'0')).join('');
    const response=await fetch('/data/questions.json',{cache:'no-store'}),bytes=await response.arrayBuffer(),questions=JSON.parse(new TextDecoder().decode(bytes));
    const images:Record<string,string>={};let cursor=0;
    await Promise.all(Array.from({length:8},async()=>{while(cursor<questions.length){const q=questions[cursor++],r=await fetch(q.image.src);if(!r.ok)throw Error('Missing image '+q.id);images[q.id]=await sha(await r.arrayBuffer());}}));
    const privatePaths=['/.local/releases/historical-40/state.json','/.local/historical/technology-01/reviews.json','/data-sources/historical-pdfs/Technology-01.pdf','/approval-candidates/technology-01-batch02/manifest.json'];
    const privateStatus=await Promise.all(privatePaths.map(async p=>(await fetch(p)).status));
    return {questions,catalogSha256:await sha(bytes),images,privateStatus};
  });
  expect(result.catalogSha256).toBe(createHash('sha256').update(bytes).digest('hex'));
  expect(result.questions).toEqual(bank);expect(result.questions).toHaveLength(656);
  expect(result.questions.filter((q:any)=>q.format==='historical').map((q:any)=>q.id).sort()).toEqual([...first.records,...second.records,...receipt.records,...fourth.records,...fifth.records,...sixth.records].map(r=>r.id).sort());
  for(const q of bank)expect(result.images[q.id],q.id).toBe(q.image.sha256);
  expect(result.privateStatus).toEqual([404,404,404,404]);
});

for(const cid of Object.keys(receipt.conceptCounts))test(`${cid}: exact highlight, all new answers/transcriptions, mobile, keyboard and guest progress`,async({page},info)=>{
  test.setTimeout(90_000);
  const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
  const c=concepts.find(c=>c.id===cid)!,entries=receipt.records.filter(r=>r.conceptId===cid);
  await page.goto(c.sectionUrl);const highlight=page.locator(`#concept-${cid}`);await expect(highlight).toHaveCount(1);await highlight.scrollIntoViewIfNeeded();await highlight.focus();await page.keyboard.press('Enter');
  await expect(page).toHaveURL(new RegExp(`/practice/${cid}/`));
  for(const entry of entries){
    const q=bank.find((q:any)=>q.id===entry.id),a=answers.find(e=>e.questionId===entry.id)!;
    await page.setViewportSize({width:entry.id.endsWith('Q011')?320:375,height:900});
    await page.goto(`/practice/${cid}/?question=${entry.id}`);
    await expect(page.locator('.question-meta h2')).toHaveText(`${q.year} ${q.season==='S'?'Spring':'Autumn'} · Morning · Q${q.number}`);
    await expect(page.locator('.exam-image-figure img')).toHaveAttribute('src',q.image.src);
    await expect(page.locator('.answer-summary')).toHaveCount(0);
    await page.getByText('Read the question as text',{exact:true}).click();await expect(page.locator('.question-transcript p').first()).toHaveText(a.imageDescription);
    for(const option of q.options)await expect(page.getByRole('radio',{name:`Option ${option.toUpperCase()}: ${a.optionText[option as 'a'|'b'|'c'|'d']}`,exact:true})).toHaveCount(1);
    await page.getByRole('button',{name:`Enlarge original question ${q.id}`}).click();await expect(page.getByRole('dialog').locator('img')).toHaveAttribute('alt',a.imageDescription);await page.keyboard.press('Escape');
    await page.getByRole('radio',{name:new RegExp(`^Option ${q.correctAnswer.toUpperCase()}:`)}).focus();await page.keyboard.press('Space');
    await page.getByRole('button',{name:'Check answer'}).focus();await page.keyboard.press('Enter');
    await expect(page.getByText('✓ That’s correct.')).toBeVisible();await expect(page.locator('.answer-summary')).toHaveText(a.summary);await expect(page.locator('.answer-feedback ol li')).toHaveText(a.steps);
    expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
    expect(await page.locator('body').innerText()).not.toMatch(/source-validated|owner-adjudicated|technicalEligibility|approvalContextFingerprint/);
  }
  await page.getByRole('button',{name:'◇ Bookmark'}).click();await page.reload();await expect(page.getByRole('button',{name:'◆ Bookmarked'})).toBeVisible();await expect(page.getByText('✓ That’s correct.')).toBeVisible();
  await page.getByRole('link',{name:'← Return to textbook'}).click();await expect(highlight).toBeFocused();
  await page.screenshot({path:info.outputPath(`${cid}-mobile.png`)});expect(errors).toEqual([]);
});
