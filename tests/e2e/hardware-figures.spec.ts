import { test, expect } from '@playwright/test';
import release from '../../src/content/hardware-source-release.json' with { type: 'json' };
import crops from '../../src/content/hardware-spatial-crops.json' with { type: 'json' };

for(const lesson of release.lessons.slice(0,5)){
  test(`${lesson.slug}: source visuals, readable scale, labels and mobile bounds`,async({page},info)=>{
    await page.setViewportSize({width:320,height:900});await page.goto(lesson.path);
    expect(await page.locator('.source-book svg').count()).toBe(0);
    const regions=crops.regions.filter(r=>r.path===lesson.path),covered=new Set(regions.flatMap(r=>r.sourceBlockIds));
    expect(await page.locator('.source-book figure').count()).toBe(lesson.pages.flatMap(p=>p.blocks).filter(b=>['figure','formula','table','source-visual'].includes(b.kind)&&!covered.has(b.id)).length+regions.length);
    const images=page.locator('.source-book .source-visual-scroll img');
    for(const index of [...new Set([0,Math.floor(await images.count()/2),(await images.count())-1])]){
      const img=images.nth(index);await img.scrollIntoViewIfNeeded();
      await expect.poll(()=>img.evaluate((el:HTMLImageElement)=>el.naturalWidth)).toBeGreaterThan(0);
      await expect(img).toHaveAttribute('alt',/\S/);await expect(img).toHaveAttribute('src',/^\/textbook\/hardware\/[a-f0-9]{64}\.webp$/);
      expect(await img.evaluate(el=>el.getBoundingClientRect().width/Number(el.getAttribute('width')))).toBeGreaterThan(.5);
      await page.screenshot({path:info.outputPath(`source-${index}-320.png`)});
    }
    expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
    const duplicates=await page.evaluate(()=>{const ids=[...document.querySelectorAll('[id]')].map(el=>el.id);return ids.filter((id,index)=>ids.indexOf(id)!==index)});
    expect(duplicates).toEqual([]);
    await page.setViewportSize({width:1440,height:1000});await page.goto(lesson.path);
    await page.screenshot({path:info.outputPath(`${lesson.slug}-desktop.png`)});
  });
}

test('original figures remain described and readable without JavaScript',async({browser})=>{
  const context=await browser.newContext({javaScriptEnabled:false});const page=await context.newPage();
  await page.goto('http://127.0.0.1:4322/chapters/hardware/cpu-and-main-memory/');
  const figure=page.locator('[data-pdf-page="56"] figure').first();
  await expect(figure).toHaveAttribute('data-reading-block','');
  await expect(figure.locator('img')).toHaveAttribute('alt',/\S/);
  await expect(figure.locator('figcaption')).toContainText('p. 51');
  await context.close();
});

test('figure checkpoints and keyboard exam navigation restore original source context',async({page})=>{
  const record=release.lessons.find(l=>l.slug==='auxiliary-storage')!.pages.flatMap(p=>p.blocks).find(b=>b.regionIds.includes('figure-1-42'))!;
  await page.goto('/chapters/hardware/auxiliary-storage/');
  const figure=page.locator(`#${record.id}`);await figure.evaluate(el=>scrollTo(0,scrollY+el.getBoundingClientRect().top-75));
  await page.waitForTimeout(350);await page.goto('/progress/');
  await page.getByRole('link',{name:'Continue reading →'}).click();
  await expect.poll(()=>figure.evaluate(el=>Math.abs(el.getBoundingClientRect().top-75))).toBeLessThan(3);
  const highlight=page.locator('#concept-disk-access');await highlight.focus();await page.keyboard.press('Enter');
  await expect(page).toHaveURL(/practice\/disk-access/);await page.getByRole('link',{name:'← Return to textbook'}).click();
  await expect(highlight).toBeFocused();
});

test('cache practice returns to the full CPU source section when opened there',async({page})=>{
  await page.goto('/chapters/hardware/cpu-and-main-memory/');const link=page.locator('#concept-cache-memory');
  await link.scrollIntoViewIfNeeded();const block=link.locator('xpath=ancestor::*[@data-reading-block][1]');
  const offset=await block.evaluate(el=>el.getBoundingClientRect().top);await link.click();
  await page.getByRole('link',{name:'← Return to textbook'}).click();
  await expect(page).toHaveURL(/cpu-and-main-memory/);await expect(link).toBeFocused();
  await expect.poll(()=>block.evaluate((el,expected)=>Math.abs(el.getBoundingClientRect().top-expected),offset)).toBeLessThan(3);
});
