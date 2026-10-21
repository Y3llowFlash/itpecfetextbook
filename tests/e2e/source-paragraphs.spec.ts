import {test,expect} from '@playwright/test';
const reader='/chapters/hardware/cpu-and-main-memory/';
const uart='fev1-201504-ch1-r1-pdf-083-b307-l00-text-0';

for(const width of [375,1024,1440])test(`PDF word objects render as five readable paragraphs at ${width}px`,async({page},info)=>{
 await page.setViewportSize({width,height:900});await page.goto(reader);
 await page.evaluate(()=>document.fonts.ready);
 const insertion=page.locator('[data-pdf-page="83"]');
 await expect(insertion.locator('p[data-source-paragraph]')).toHaveCount(5);
 await expect(insertion.locator('p[data-source-kind="paragraph"]')).toHaveCount(0);
 await expect(insertion.locator('[data-source-kind="paragraph"]')).toHaveCount(235);
 const paragraph=insertion.locator('[data-source-paragraph="pdf-083-prose-004"]');
 await paragraph.scrollIntoViewIfNeeded();
 await expect(paragraph).toContainText('d) UART (Universal Asynchronous Receiver-Transmitter): UART is a widely used asynchronous serial communication protocol.');
 const words=paragraph.locator('[data-source-block]');
 const first=await words.nth(0).boundingBox(),second=await words.nth(1).boundingBox();
 expect(Math.abs(first!.y-second!.y)).toBeLessThan(2);
 // A full source paragraph wraps naturally rather than becoming 57 rows.
 const bounds=await paragraph.boundingBox();
 expect(bounds!.height).toBeLessThan(width===375?700:450);
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 await page.screenshot({path:info.outputPath(`uart-${width}.png`)});
 // Historical word-level checkpoints retain their exact vertical offset.
 const anchor=page.locator(`#${uart}`);
 await anchor.evaluate(el=>scrollTo(0,scrollY+el.getBoundingClientRect().top-125));
 await page.waitForTimeout(350);
 await page.goto('/progress/');await page.getByRole('link',{name:'Continue reading →'}).click();
 await expect.poll(()=>anchor.evaluate(el=>Math.abs(el.getBoundingClientRect().top-125))).toBeLessThan(3);
});
