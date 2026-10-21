import {test,expect} from '@playwright/test';
import crops from '../../src/content/hardware-spatial-crops.json' with {type:'json'};

for(const width of [375,1440])test(`all original spatial crops load, keep aspect and stay within reader bounds at ${width}px`,async({page},info)=>{
 test.setTimeout(90000);await page.setViewportSize({width,height:1000});
 for(const path of new Set(crops.regions.map(r=>r.path))){
  await page.goto(path);await page.evaluate(()=>document.fonts.ready);
  const regions=crops.regions.filter(r=>r.path===path);
  await expect(page.locator('[data-spatial-crop]')).toHaveCount(regions.length);
  // Decode every asset, including lazily loaded regions below the viewport.
  const result=await page.locator('[data-spatial-crop]').evaluateAll(async figures=>Promise.all(figures.map(async figure=>{
   const img=figure.querySelector('img')!;img.loading='eager';await img.decode();
   const scroll=figure.querySelector<HTMLElement>('.source-crop-scroll')!,rect=img.getBoundingClientRect();
   return {id:figure.getAttribute('data-spatial-crop'),loaded:img.naturalWidth>0,aspect:Math.abs(rect.width/rect.height-img.naturalWidth/img.naturalHeight),readable:rect.width>=Math.min(560,parseFloat((figure as HTMLElement).style.getPropertyValue('--crop-width')))-1,contained:scroll.getBoundingClientRect().right<=innerWidth,alt:img.alt,scrollLabel:scroll.getAttribute('aria-label'),tabIndex:scroll.tabIndex};
  })));
  expect(result.every(r=>r.loaded&&r.aspect<.02&&r.readable&&r.contained&&r.alt.length>15&&r.scrollLabel&&r.tabIndex===0)).toBe(true);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  const example=page.locator('[data-spatial-crop]').first();await example.scrollIntoViewIfNeeded();
  await page.screenshot({path:info.outputPath(`${path.split('/').at(-2)}-${width}.png`)});
 }
});

test('BCD complete example supports keyboard panning, enlargement and old reading checkpoints',async({page,context},info)=>{
 const bcd=crops.regions.find(r=>r.id==='spatial-p32-01')!;
 await page.setViewportSize({width:375,height:900});await page.goto(bcd.url);
 const figure=page.locator('[data-spatial-crop="spatial-p32-01"]'),scroll=figure.locator('.source-crop-scroll');
 await expect(figure).toHaveAttribute('data-source-pdf-page','37');await expect(figure).toHaveAttribute('data-source-printed-page','32');
 await expect(figure.locator('img')).toHaveAttribute('alt',/2741/);
 await scroll.focus();await page.keyboard.press('ArrowRight');
 await expect.poll(()=>scroll.evaluate(el=>el.scrollLeft)).toBeGreaterThan(0);
 await scroll.evaluate(el=>{el.scrollLeft=0});await figure.scrollIntoViewIfNeeded();
 await page.screenshot({path:info.outputPath('bcd-375.png')});
 const enlarged=context.waitForEvent('page');await figure.locator('figcaption a').focus();await page.keyboard.press('Enter');
 const imagePage=await enlarged;await imagePage.waitForLoadState();expect(imagePage.url()).toContain(bcd.asset.path);await imagePage.close();
 // A previously saved text-fragment ID now restores to the complete source box.
 await page.evaluate(({id,path})=>{
  const key='itpecTextbook:guest:v1',saved=JSON.parse(localStorage.getItem(key)!);
  saved.reading={sectionId:'fe-v1-ch01-s02',path,blockId:id,offset:95,scrollY:1000,updatedAt:new Date().toISOString()};localStorage.setItem(key,JSON.stringify(saved));
 },{id:bcd.sourceBlockIds.at(-1)!,path:bcd.path});
 await page.goto('/progress/');await page.getByRole('link',{name:'Continue reading →'}).click();
 await expect.poll(()=>page.locator(`#${bcd.sourceBlockIds.at(-1)}`).evaluate(el=>Math.abs(el.getBoundingClientRect().top-95))).toBeLessThan(3);
 await page.setViewportSize({width:1440,height:1000});await figure.scrollIntoViewIfNeeded();await page.screenshot({path:info.outputPath('bcd-1440.png')});
});
