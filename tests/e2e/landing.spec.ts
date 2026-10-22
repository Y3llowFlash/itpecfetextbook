import {test,expect} from '@playwright/test';
import {landingBooks,FE_ENTRY} from '../../src/lib/landing-books';
for(const width of [320,375,414,768,1024,1440,1536])test(`level bookshelf: original covers and responsive layout at ${width}px`,async({page},info)=>{
 await page.setViewportSize({width,height:1024});await page.goto('/');await page.evaluate(()=>document.fonts.ready);
 await expect(page.getByRole('heading',{level:1})).toHaveText('Exam Preparation Books');
 await expect(page.locator('[data-level]')).toHaveCount(3);await expect(page.locator('astro-island,script[src]')).toHaveCount(0);
 for(const book of landingBooks){
  const region=page.locator(`[data-level="${book.level}"]`),image=region.locator('img');
  await image.evaluate(async(img:HTMLImageElement)=>{img.loading='eager';await img.decode()});
  await expect(image).toHaveAttribute('alt',`${book.title} — original cover`);
  expect(await image.evaluate((img:HTMLImageElement)=>Math.abs(img.clientWidth/img.clientHeight-img.naturalWidth/img.naturalHeight))).toBeLessThan(.005);
  expect((await image.boundingBox())!.width).toBeGreaterThan(width>=1024?210:230);
  await expect(region.locator('.availability')).toHaveText(book.status);
  if(!book.available){await expect(region.locator('button')).toBeDisabled();await expect(region.locator('a')).toHaveCount(0);}
 }
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 if(width>=1024){const top=await page.locator('.book-stage').evaluateAll(elements=>elements.map(el=>el.getBoundingClientRect().top));expect(Math.max(...top)-Math.min(...top)).toBeLessThan(2);}
 await page.screenshot({path:info.outputPath(`landing-${width}.png`),fullPage:true});
});
test('FE book and button navigate, browser Back returns, and guest progress survives home navigation',async({page})=>{
 await page.goto('/');await page.locator('.book-link').click();await expect(page).toHaveURL(new RegExp(FE_ENTRY+'$'));
 await expect(page.getByRole('heading',{level:1})).toHaveText('Hardware');await page.goBack();
 await page.getByRole('link',{name:'Open Textbook',exact:true}).click();await expect(page).toHaveURL(new RegExp(FE_ENTRY+'$'));
 await page.goto('/practice/cache-memory/');await page.getByRole('radio',{name:'Option B: 360 ns'}).check();await page.getByRole('button',{name:'Check answer'}).click();await page.getByRole('button',{name:'◇ Bookmark'}).click();
 await page.locator('.wordmark').click();await expect(page).toHaveURL('/');await page.getByRole('link',{name:'Open Textbook',exact:true}).click();
 await page.goto('/progress/');await expect(page.getByRole('button',{name:'Remove bookmark 2024A-A-Q009'})).toBeVisible();
 await page.goto('/chapters/hardware/data-representation/#fev1-201504-ch1-r1-pdf-037-b002-l00-text-0');await expect(page.locator('[data-spatial-crop="spatial-p32-01"]')).toBeVisible();
});
test('keyboard focus reaches the FE link and action while skipping disabled levels',async({page})=>{
 await page.goto('/');await page.keyboard.press('Tab');await expect(page.locator('.landing-skip')).toBeFocused();
 await page.keyboard.press('Tab');await expect(page.locator('.landing-wordmark')).toBeFocused();await page.keyboard.press('Tab');await expect(page.locator('.book-link')).toBeFocused();
 expect(await page.locator('.book-link').evaluate(el=>getComputedStyle(el).outlineStyle)).toBe('solid');
 await page.keyboard.press('Tab');await expect(page.locator('.book-action[href]')).toBeFocused();await page.keyboard.press('Enter');await expect(page).toHaveURL(new RegExp(FE_ENTRY+'$'));
});
test('returning home preserves the saved reading checkpoint and browser Back restores its offset',async({page})=>{
 await page.goto('/chapters/hardware/cpu-and-main-memory/');
 await expect(page.locator('astro-island').first()).not.toHaveAttribute('ssr','');
 const block=page.locator('#concept-cache-memory').locator('xpath=ancestor::*[@data-reading-block][1]');
 await block.evaluate(el=>scrollTo(0,scrollY+el.getBoundingClientRect().top-90));
 await expect.poll(()=>page.evaluate(()=>JSON.parse(localStorage.getItem('itpecTextbook:guest:v1')||'{}').reading)).toBeTruthy();
 const before=await page.evaluate(()=>JSON.parse(localStorage.getItem('itpecTextbook:guest:v1')!).reading);
 // Navigate home without first scrolling the reader to its non-sticky masthead.
 // Header-link navigation is covered above; scrolling itself updates the checkpoint.
 await page.goto('/');await expect(page).toHaveURL('/');
 expect(await page.evaluate(()=>JSON.parse(localStorage.getItem('itpecTextbook:guest:v1')!).reading)).toMatchObject({blockId:before.blockId,path:before.path,offset:before.offset});
 await page.goBack();await expect.poll(()=>page.locator(`#${before.blockId}`).evaluate((el,offset)=>Math.abs(el.getBoundingClientRect().top-offset),before.offset)).toBeLessThan(3);
});
test('static guest access and reduced motion retain usable books',async({browser})=>{
 const context=await browser.newContext({javaScriptEnabled:false,reducedMotion:'reduce'}),page=await context.newPage();
 await page.goto('http://127.0.0.1:4322/');await expect(page.locator('.level-fe img')).toBeVisible();
 expect(await page.locator('.book-object').first().evaluate(el=>getComputedStyle(el).transitionDuration)).toBe('0s');
 await page.locator('.book-action[href]').click();await expect(page.getByRole('heading',{level:1})).toHaveText('Hardware');await context.close();
});
