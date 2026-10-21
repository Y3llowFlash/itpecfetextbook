import { test, expect } from '@playwright/test';
import { hardwareFigures, figurePageLabel } from '../../src/lib/figures';
import { hardwareLessons, lessonPath } from '../../src/lib/lessons';

for(const lesson of hardwareLessons.slice(0,5)) {
  test(`${lesson.slug}: original figures, accessible descriptions and mobile SVG bounds`,async({page},testInfo)=>{
    await page.setViewportSize({width:320,height:900});
    await page.goto(lessonPath(lesson));
    const figures=hardwareFigures.filter(f=>f.lesson===lesson.slug);
    await expect(page.locator('[data-original-figure]')).toHaveCount(figures.length);
    for(const figure of figures) {
      const item=page.locator(`#figure-${figure.id}`);
      await expect(item.getByRole('img',{name:`${figure.title} ${figure.alt}`,exact:true})).toHaveCount(1);
      await expect(item.locator(`[data-figure-source="${figure.id}"]`)).toHaveText(`Original textbook · ${figurePageLabel(figure.sourcePages)}`);
      const problems=await item.locator('svg').evaluate(svg=>{
        const root=svg as SVGSVGElement, view=root.viewBox.baseVal, scale=root.getBoundingClientRect().width/view.width;
        return [...root.querySelectorAll('text')].flatMap(text=>{
          const rect=text.getBBox(),size=parseFloat(getComputedStyle(text).fontSize)*scale;
          const issues=[];
          if(rect.x < -0.5 || rect.y < -0.5 || rect.x+rect.width>view.width+0.5 || rect.y+rect.height>view.height+0.5)issues.push(`${text.textContent}: outside viewBox`);
          if(size<14)issues.push(`${text.textContent}: ${size.toFixed(1)}px text`);
          return issues;
        });
      });
      expect(problems,figure.id).toEqual([]);
      await item.screenshot({path:testInfo.outputPath(`${figure.id}-320.png`)});
    }
    expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
    // Inline figures add no image downloads and cannot request third-party artwork.
    expect(await page.locator('.technical-figure image, .technical-figure img').count()).toBe(0);
    const duplicateIds=await page.evaluate(()=>{
      const ids=[...document.querySelectorAll('[id]')].map(el=>el.id);return ids.filter((id,index)=>ids.indexOf(id)!==index);
    });
    expect(duplicateIds).toEqual([]);
    await page.setViewportSize({width:1280,height:900});
    await page.screenshot({path:testInfo.outputPath(`${lesson.slug}-desktop.png`),fullPage:true});
  });
}

test('new diagrams remain described without JavaScript and retain figure reading checkpoints',async({browser})=>{
  const context=await browser.newContext({javaScriptEnabled:false});
  const page=await context.newPage();
  await page.goto('http://127.0.0.1:4322/chapters/hardware/cpu-and-main-memory/');
  await expect(page.locator('#figure-memory-address-grid')).toHaveAttribute('data-reading-block','');
  await expect(page.locator('#figure-memory-address-grid figcaption')).toContainText('The address is not the byte');
  await expect(page.locator('#figure-memory-address-grid svg desc')).toContainText('Address 2');
  await context.close();
});

test('keyboard navigation through exam highlights still restores a nearby figure context',async({page})=>{
  await page.goto('/chapters/hardware/auxiliary-storage/');
  const figure=page.locator('#figure-disk-geometry-figure');
  await figure.scrollIntoViewIfNeeded();
  await page.waitForTimeout(350);
  await page.goto('/progress/');
  await page.getByRole('link',{name:'Continue reading →'}).click();
  await expect(page).toHaveURL(/auxiliary-storage\/.*#figure-disk-geometry-figure/);
  const top=await figure.evaluate(el=>el.getBoundingClientRect().top);
  expect(top).toBeGreaterThan(-100);expect(top).toBeLessThan(450);
  const highlight=page.locator('#concept-disk-access');
  await highlight.focus();await page.keyboard.press('Enter');
  await expect(page).toHaveURL(/practice\/disk-access/);
  await page.getByRole('link',{name:'← Return to textbook'}).click();
  await expect(highlight).toBeFocused();
});
