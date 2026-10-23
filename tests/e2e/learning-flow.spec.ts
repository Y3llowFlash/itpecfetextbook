import { test, expect } from '@playwright/test';

const lesson = '/chapters/hardware/cpu-and-main-memory/#fev1-201504-ch1-r1-pdf-075-b005-l00-text-0';
test('read, practise real questions, save progress, and return to the exact reading position', async ({ page }) => {
  const errors: string[] = []; page.on('pageerror', (error) => errors.push(error.message));
  page.on('console', (message) => { if (message.type() === 'error') errors.push(message.text()); });
  await page.goto(lesson);
  await expect(page.locator('.source-book').getByRole('heading', { name: '3-5-1 High Speed Memory Access', exact:true })).toBeVisible();
  const concept = page.locator('#concept-cache-memory');
  await concept.scrollIntoViewIfNeeded();
  const before = await concept.locator('xpath=ancestor::*[@data-reading-block][1]').evaluate((element) => element.getBoundingClientRect().top);
  await concept.click();
  await expect(page).toHaveURL(/\/practice\/cache-memory\//);
  await expect(page.getByText('10 related published questions. Take them one at a time.')).toBeVisible();
  await page.getByRole('radio', { name: 'Option A: 315 ns' }).check();
  await page.getByRole('button', { name: 'Check answer' }).click();
  await expect(page.getByText('Let’s work through it.')).toBeVisible();
  await expect(page.getByText(/average access time is 0.8/)).toBeVisible();
  await page.getByRole('button', { name: '◇ Bookmark' }).click();
  await page.reload();
  await expect(page.getByRole('button', { name: '◆ Bookmarked' })).toBeVisible();
  await expect(page.getByText('Let’s work through it.')).toBeVisible();
  await page.getByRole('button', { name: 'Next →' }).click();
  await expect(page.getByRole('heading', { name: '2025 Spring · Subject A · Q10' })).toBeVisible();
  await page.getByRole('radio', { name: 'Option C: 0.83' }).check();
  await page.getByRole('button', { name: 'Check answer' }).click();
  await expect(page.getByText('✓ That’s correct.')).toBeVisible();
  await page.getByRole('button', { name: 'Next →' }).click();
  await page.getByRole('radio', { name: 'Option D: On a cache miss, fetch data from main memory.' }).check();
  await page.getByRole('button', { name: 'Check answer' }).click();
  await expect(page.getByText('✓ That’s correct.')).toBeVisible();
  await page.getByRole('link', { name: '← Return to textbook' }).click();
  await expect(page).toHaveURL(/cpu-and-main-memory\//);
  await expect(page.locator('#concept-cache-memory')).toBeFocused();
  const after = await concept.locator('xpath=ancestor::*[@data-reading-block][1]').evaluate((element) => element.getBoundingClientRect().top);
  expect(Math.abs(before - after)).toBeLessThan(3);
  await page.getByRole('button', { name: 'Mark as completed' }).click();
  await expect(page.getByRole('button', { name: '✓ Section completed' })).toHaveAttribute('aria-pressed', 'true');
  await page.goto('/progress/');
  await expect(page.locator('.progress-stat-grid')).toContainText('3');
  await expect(page.locator('.study-companion')).toHaveCount(0);
  await expect(page.getByRole('link', { name: '2024A-A-Q009 →' })).toHaveCount(2);
  expect(errors).toEqual([]);
});

test('browser Back restores the clicked reading block', async ({ page }) => {
  await page.goto(lesson); await page.locator('#concept-cache-memory').scrollIntoViewIfNeeded();
  const before = await page.locator('#concept-cache-memory').locator('xpath=ancestor::*[@data-reading-block][1]').evaluate((element) => element.getBoundingClientRect().top);
  await page.locator('#concept-cache-memory').click();
  await expect(page.getByRole('heading', { name: 'Cache memory', exact: true })).toBeVisible();
  await page.goBack();
  await expect(page.locator('#concept-cache-memory')).toBeFocused();
  const after = await page.locator('#concept-cache-memory').locator('xpath=ancestor::*[@data-reading-block][1]').evaluate((element) => element.getBoundingClientRect().top);
  expect(Math.abs(before - after)).toBeLessThan(3);
});

test('learning remains usable when browser storage is blocked', async ({ page }) => {
  await page.addInitScript(() => { Object.defineProperty(window, 'localStorage', { get() { throw new DOMException('Blocked', 'SecurityError'); } }); });
  await page.goto('/practice/cache-memory/');
  await page.getByRole('radio', { name: 'Option B: 360 ns' }).check();
  await page.getByRole('button', { name: 'Check answer' }).click();
  await expect(page.getByText('✓ That’s correct.')).toBeVisible();
  await expect(page.locator('main').getByRole('status')).toContainText('Browser storage is unavailable');
});

test('reader works as static HTML without JavaScript', async ({ browser }) => {
  const context = await browser.newContext({ javaScriptEnabled: false });
  const page = await context.newPage();
  await page.goto(`http://127.0.0.1:4322${lesson}`);
  await expect(page.locator('.source-book')).toContainText('Cache memory');
  await expect(page.locator('#concept-cache-memory')).toHaveAttribute('href', '/practice/cache-memory/');
  await context.close();
});

test('keyboard selection and image zoom remain accessible', async ({ page }) => {
  await page.goto('/practice/cache-memory/');
  const option = page.getByRole('radio', { name: 'Option B: 360 ns' });
  await option.focus(); await page.keyboard.press('Space');
  await page.getByRole('button', { name: 'Check answer' }).focus(); await page.keyboard.press('Enter');
  await expect(page.getByText('✓ That’s correct.')).toBeVisible();
  await page.getByRole('button', { name: 'Enlarge original question 2024A-A-Q009' }).click();
  await expect(page.getByRole('dialog')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Close ×' })).toBeFocused();
  await page.keyboard.press('Escape'); await expect(page.getByRole('dialog')).not.toBeVisible();
});

test('reading and practice do not request external services', async ({ page }) => {
  const external: string[] = [];
  page.on('request', (request) => { if (!request.url().startsWith('http://127.0.0.1:4322/')) external.push(request.url()); });
  await page.goto(lesson); await page.locator('#concept-cache-memory').click();
  await page.getByRole('radio', { name: 'Option A: 315 ns' }).check(); await page.getByRole('button', { name: 'Check answer' }).click();
  await expect(page.getByText('Let’s work through it.')).toBeVisible();
  expect(external).toEqual([]);
});

for (const width of [320, 375, 414, 768, 1280]) {
  test(`reader and practice fit a ${width}px screen`, async ({ page }, testInfo) => {
    await page.setViewportSize({ width, height: 900 });
    await page.goto(lesson); await page.evaluate(() => document.fonts.ready);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    await page.screenshot({ path: testInfo.outputPath(`reader-${width}.png`) });
    await page.goto('/practice/cache-memory/');
    await page.getByRole('button', { name: 'Question 3, unanswered' }).click();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    const clipped = await page.locator('.button').evaluateAll((buttons) => buttons.filter((button) => {
      const rect = button.getBoundingClientRect(); return rect.width > 0 && (rect.left < 0 || rect.right > innerWidth + 1);
    }).map((button) => button.textContent));
    expect(clipped).toEqual([]);
    await page.screenshot({ path: testInfo.outputPath(`practice-${width}.png`), fullPage: true });
  });
}
