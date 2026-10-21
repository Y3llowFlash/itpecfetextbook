import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';
const source=JSON.parse(readFileSync('.local/editorial/chapter-1/chapter.json','utf8')) as {
  pages:Array<{pdfPage:number;printedPage:number|null;blocks:Array<{id:string;kind:string;sourceText:string}>}>;
  annotations:Array<{conceptId:string;quote:string;count:number;pdfPage:number;blockId:string}>;
};

test('all 100 source pages render every recorded block, original figures and source order',async({page})=>{
  for(const original of source.pages){
    await page.goto(`/reader/pdf-${String(original.pdfPage).padStart(3,'0')}.html`);
    await expect(page.locator('[data-editorial-reader]')).toHaveAttribute('data-pdf-page',String(original.pdfPage));
    const ids=await page.locator('[data-source-block]').evaluateAll(elements=>elements.map(e=>e.id));
    expect(ids).toEqual(original.blocks.filter(b=>b.kind!=='page-furniture').map(b=>b.id));
    expect(await page.locator('.reader-body svg').count()).toBe(0);
    for(const img of await page.locator('.reader-body img').all())await expect(img).toHaveAttribute('src',/^\.\.\/(assets|cells)\/.*\.png$/);
  }
});

for(const physical of [18,27,43,51,67,71,83,84,100,104,110,117]){
  test(`PDF ${physical}: responsive source reading and comparison`,async({page},info)=>{
    const url=`/reader/pdf-${String(physical).padStart(3,'0')}.html`;
    await page.setViewportSize({width:320,height:900});await page.goto(url);
    expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
    for(const image of await page.locator('.visual-scroll img').all()){
      const factor=await image.evaluate((img:HTMLImageElement)=>img.getBoundingClientRect().width/Number(img.getAttribute('width')));
      expect(factor).toBeGreaterThan(.5);
    }
    await expect(page.getByText('LOCAL EDITORIAL PREVIEW',{exact:false})).toBeVisible();
    await page.screenshot({path:info.outputPath(`pdf-${physical}-320.png`),fullPage:true});
    await page.setViewportSize({width:1440,height:1000});await page.goto(`/compare/pdf-${String(physical).padStart(3,'0')}.html`);
    await expect(page.getByRole('img')).toBeVisible();
    expect(await page.getByRole('img').evaluate((img:HTMLImageElement)=>img.naturalWidth)).toBeGreaterThan(1000);
    const frame=page.frameLocator('iframe');await expect(frame.locator('.reader-body')).toBeVisible();
    await page.screenshot({path:info.outputPath(`pdf-${physical}-comparison.png`),fullPage:true});
  });
}

test('source quote annotations add published counts without replacing source words',async({page})=>{
  for(const annotation of source.annotations){
    await page.goto(`/reader/pdf-${String(annotation.pdfPage).padStart(3,'0')}.html`);
    const link=page.locator(`.reader-body [data-concept="${annotation.conceptId}"]`);
    await expect(link).toHaveAttribute('target','_blank');
    await expect(link).toContainText(annotation.quote);
    await expect(link.locator('small')).toHaveAttribute('aria-label',`${annotation.count} published questions`);
    await expect(link).toHaveAttribute('href',`https://itpecfetextbook.pages.dev/practice/${annotation.conceptId}/`);
  }
});

test('source grid retains all prefix rows and superscripts; raw-only tables retain original pixels',async({page})=>{
  await page.goto('/reader/pdf-027.html');
  const table=page.locator('.source-table table');await expect(table).toHaveCount(1);
  await expect(table.locator('tr')).toHaveCount(6);await expect(table).toContainText('Peta');
  expect(await table.locator('sup').count()).toBeGreaterThanOrEqual(10);
  await page.goto('/reader/pdf-042.html');
  const originals=page.locator('.reader-body img');expect(await originals.count()).toBeGreaterThan(0);
  await expect(page.locator('.reader-body')).toContainText('Floating point numbers');
});

test('private preview makes no external requests, offers source resume and remains readable without JS',async({page,browser})=>{
  const external:string[]=[];
  page.on('request',request=>{if(!request.url().startsWith('http://127.0.0.1:4341'))external.push(request.url());});
  await page.goto('/reader/pdf-018.html');
  const block=page.locator('.reader-body p').last();await block.scrollIntoViewIfNeeded();await page.waitForTimeout(350);
  await page.goto('/');await expect(page.locator('[data-editorial-resume]')).toBeVisible();
  const saved=await page.evaluate(()=>JSON.parse(localStorage.getItem('itpecTextbook:editorial:source:v1')!));
  await page.locator('[data-editorial-resume]').click();await expect(page).toHaveURL(/resume=1#/);
  await expect.poll(async()=>Math.abs(await page.locator(`#${saved.blockId}`).evaluate(el=>el.getBoundingClientRect().top)-saved.offset)).toBeLessThan(8);
  expect(external).toEqual([]);
  const context=await browser.newContext({javaScriptEnabled:false});const staticPage=await context.newPage();
  await staticPage.goto('http://127.0.0.1:4341/reader/pdf-018.html');
  await expect(staticPage.locator('.reader-body')).toContainText('ENIAC');
  await expect(staticPage.getByRole('link',{name:'Compare with source page'})).toBeVisible();
  await context.close();
});
