import {test,expect} from '@playwright/test';
import {contents,mainContents,contentsUrl} from '../../src/lib/toc';
import {CPU_PATH,CACHE_HEADING} from '../../src/lib/reading-routes';
const cache=contents.find(n=>n.number==='3-5-1')!;
const gates=contents.find(n=>n.number==='3-4-1')!;

test('chapter opens directly into unchanged source with one title and the complete original contents',async({page})=>{
 for(const path of ['/chapters/hardware/']){
  await page.goto(path);
  await expect(page.getByRole('heading',{level:1})).toHaveText('Hardware');
  await expect(page.locator('.source-book [data-source-kind="heading"]').first()).toHaveText('1 Basic Configuration of Computers');
  await expect(page.locator('.source-page > .source-badge').first()).toHaveText('p. 13');
  await expect(page.locator('.source-book')).not.toContainText('Original textbook');
  await expect(page.getByRole('link',{name:/Start Chapter|Read from the beginning|Memory hierarchy & cache/})).toHaveCount(0);
  const nav=page.locator('.sidebar nav');
  expect(await nav.locator('[data-toc-link]').count()).toBe(52);
  for(const node of contents){
   const link=nav.locator(`[data-toc-link="${node.id}"]`);
   await expect(link).toHaveAttribute('href',contentsUrl(node));
   await expect(link).toContainText(node.number);await expect(link).toContainText(node.title);await expect(link).toContainText(`p. ${node.page}`);
  }
  await expect(page.locator('.context-questions')).toHaveCount(1);
  await expect(page.locator('.context-questions a')).toHaveAttribute('href','/practice/five-major-units/');
  await expect(page.locator('.companion-content h2')).toHaveText('1 Basic Configuration of Computers');
 }
});

test('source subsection links, scrolling, keyboard focus and browser history share one contextual selection',async({page})=>{
 await page.goto(`${CPU_PATH}#${CACHE_HEADING}`);
 const nav=page.locator('.sidebar nav');
 await expect(nav.locator('[aria-current="location"]')).toHaveAttribute('data-toc-link',cache.id);
  await expect(page.locator('.context-questions .context-count')).toHaveText('15');
  await expect(page.locator('.companion-practice[href="/practice/cache-memory/"]')).toContainText('10');
  await expect(page.locator('.companion-practice[href="/practice/memory-interleaving/"]')).toContainText('3');
 await expect(page.locator('.companion-practice[href="/practice/memory-hierarchy/"]')).toContainText('1');
  await expect(page.locator('.companion-practice[href="/practice/cache-write-policies/"]')).toContainText('1');
 await expect(page.getByRole('link',{name:'HDD, RAM, register & cache ↗'})).toHaveAttribute('href','https://t.me/itpecmm/101');
 // Use the original heading to simulate reading back through the section.
 await page.locator(`#${gates.id}`).evaluate(el=>scrollTo(0,scrollY+el.getBoundingClientRect().top-145));
 await expect(nav.locator('[aria-current="location"]')).toHaveAttribute('data-toc-link',gates.id);
 await expect(page.locator('.companion-content h2')).toContainText(gates.title);
 // The scrollspy must not create history entries or overwrite the fragment.
 await expect(page).toHaveURL(new RegExp(`#${CACHE_HEADING}$`));
 const group=nav.locator(`details[data-toc-group="${contents.find(n=>n.number==='3-5')!.id}"]`);
 if(!await group.evaluate(el=>(el as HTMLDetailsElement).open))await group.locator(':scope > summary > .toc-chevron').click();
 await nav.locator(`[data-toc-link="${cache.id}"]`).focus();await page.keyboard.press('Enter');
 await expect(page.locator(`#${cache.id}`)).toBeFocused();
 await expect(page.locator('.companion-content h2')).toContainText('High Speed Memory Access');
 await nav.locator(`[data-toc-link="${gates.id}"]`).click();
 await expect(page).toHaveURL(new RegExp(`#${gates.id}$`));
 await page.goBack();await expect(page).toHaveURL(new RegExp(`#${cache.id}$`));
 await expect(nav.locator('[aria-current="location"]')).toHaveAttribute('data-toc-link',cache.id);
 await page.goForward();await expect(nav.locator('[aria-current="location"]')).toHaveAttribute('data-toc-link',gates.id);
});

for(const width of [375,768,1024])test(`collapsible contents and contextual tools leave reading space at ${width}px`,async({page},info)=>{
 await page.setViewportSize({width,height:900});await page.goto('/chapters/hardware/');
 const tools=page.locator('[data-study-tools]');await expect(tools).not.toHaveAttribute('open','');
 await expect(page.locator('.companion-content')).not.toBeVisible();
 await expect(page.locator('.source-book').getByText('1 Basic Configuration of Computers',{exact:true})).toBeVisible();
 await tools.locator('summary').focus();await page.keyboard.press('Enter');
 await expect(page.locator('.companion-content h2')).toBeVisible();
 await tools.locator('summary').click();
 const navigation=width<960?page.locator('.mobile-navigation'):page.locator('.sidebar');
 if(width<960)await navigation.locator(':scope > details > summary').click();
 await navigation.locator(`[data-toc-link="${mainContents[2].id}"]`).click();
 await expect(page).toHaveURL(new RegExp(`${CPU_PATH}#${mainContents[2].id}$`));
 if(width<960){
  await expect(page.locator('[data-mobile-contents]')).not.toHaveAttribute('open','');
  await page.locator('.mobile-navigation > details > summary').click();
 }
 const nav=width<960?page.locator('.mobile-navigation nav'):page.locator('.sidebar nav');
 await nav.locator(`details[data-toc-group="${contents.find(n=>n.number==='3-5')!.id}"] > summary > .toc-chevron`).click();
 await nav.locator(`[data-toc-link="${cache.id}"]`).click();
 await expect(page.locator(`#${cache.id}`)).toBeFocused();
 await expect(page.locator('[data-study-context]')).toHaveAttribute('data-study-context',cache.id);
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 await page.screenshot({path:info.outputPath(`reading-${width}.png`)});
});

test('old cache URLs and saved checkpoints preserve source offsets and completion on the canonical route',async({page})=>{
 await page.goto('/chapters/hardware/memory-and-cache/');await expect(page).toHaveURL(new RegExp(`${CPU_PATH}#${CACHE_HEADING}$`));
 await page.getByRole('button',{name:'Mark 3-5-1 complete',exact:true}).click();
 const block=page.locator('#concept-cache-memory').locator('xpath=ancestor::*[@data-reading-block][1]');
 const blockId=await block.getAttribute('id');
 await page.goto('/progress/');
 // Install a historical record away from the reader's pagehide checkpoint.
 await page.evaluate(({blockId})=>{
  const key='itpecTextbook:guest:v1',saved=JSON.parse(localStorage.getItem(key)!);
  saved.reading={sectionId:'fe-v1-ch01-memory-cache',path:'/chapters/hardware/memory-and-cache/',blockId,offset:77,scrollY:900,updatedAt:new Date().toISOString()};localStorage.setItem(key,JSON.stringify(saved));
 },{blockId});await page.reload();
 await expect(page.getByText('0 of 5 main sections completed')).toBeVisible();
 await expect(page.getByRole('link',{name:'3-5-1 High Speed Memory Access',exact:true})).toHaveAttribute('href',contentsUrl(cache));
 await expect(page.getByRole('link',{name:'Continue reading →'})).toHaveAttribute('href',new RegExp(`cpu-and-main-memory/.*#${blockId}$`));
 await page.getByRole('link',{name:'Continue reading →'}).click();
 await expect.poll(()=>block.evaluate(el=>Math.abs(el.getBoundingClientRect().top-77))).toBeLessThan(3);
});
