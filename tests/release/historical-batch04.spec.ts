import {test,expect} from '@playwright/test';
import {readFileSync} from 'node:fs';
import receipt from '../../docs/development/evidence/historical-release-4.json' with {type:'json'};
import concepts from '../../src/content/concepts.json' with {type:'json'};
import answers from '../../src/content/explanations.json' with {type:'json'};
const bytes=readFileSync('public/data/questions.json'),bank=JSON.parse(bytes.toString());

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
