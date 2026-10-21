import { test, expect } from '@playwright/test';
import { hardwareLessons, lessonPath, pageLabel } from '../../src/lib/lessons';

for (const lesson of hardwareLessons.slice(0, 5)) {
  test(`${lesson.title}: printed references, substantive sections and 320px layout`, async ({ page }, testInfo) => {
    await page.setViewportSize({ width: 320, height: 900 });
    await page.goto(lessonPath(lesson));
    await expect(page.getByRole('heading', { name: lesson.title, exact: true, level: 1 })).toBeVisible();
    await expect(page.locator('[data-source-ref="lesson"]')).toHaveText(`Original textbook · ${pageLabel(lesson.pages)}`);
    await expect(page.locator('[data-source-ref="lesson"]')).toHaveAttribute('title', /First Edition, April 2015/);
    for (const heading of lesson.headings) {
      await expect(page.locator(`#${heading.id} + .source-badge`)).toHaveText(`Original textbook · ${pageLabel(heading.pages)}`);
    }
    expect(await page.locator('.reader-prose').innerText()).not.toContain('Coming later');
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    for (const table of await page.locator('.reader-prose table').all()) {
      const box = await table.boundingBox(); expect(box!.width).toBeLessThanOrEqual(288);
    }
    await page.screenshot({ path: testInfo.outputPath(`${lesson.slug}-320.png`), fullPage: true });
    await page.locator('.mobile-navigation summary').click();
    const nav = page.locator('.mobile-navigation nav');
    await expect(nav.locator('[aria-current="page"]')).toHaveAttribute('href', lessonPath(lesson));
    for (const item of hardwareLessons.slice(0,5)) await expect(nav.locator(`a[href="${lessonPath(item)}"]`)).toBeVisible();
    if (lesson.slug === 'cpu-and-main-memory') {
      await page.setViewportSize({ width: 1280, height: 1000 });
      await page.screenshot({ path: testInfo.outputPath('cpu-desktop.png'), fullPage: true });
      await page.locator('#logic-truth-table').screenshot({ path: testInfo.outputPath('logic-table.png') });
    }
  });
}

test('new concept practice returns to its source block and records guest completion/bookmarks', async ({ page }) => {
  await page.goto('/chapters/hardware/data-representation/');
  const highlight = page.locator('#concept-radix-conversion');
  await expect(highlight).toContainText('3 questions');
  await highlight.scrollIntoViewIfNeeded();
  const before = await page.locator('#radix-weights').evaluate((element) => element.getBoundingClientRect().top);
  await highlight.click();
  await expect(page).toHaveURL(/\/practice\/radix-conversion\//);
  await page.getByRole('radio', { name: 'Option A: 83.25' }).check();
  await page.getByRole('button', { name: 'Check answer' }).click();
  await expect(page.getByText('Let’s work through it.')).toBeVisible();
  await expect(page.getByRole('link', { name: 'Review this idea in the textbook →' })).toHaveAttribute('href', '/chapters/hardware/data-representation/#radix-conversion');
  await page.getByRole('button', { name: 'Try this question again' }).click();
  await page.getByRole('radio', { name: 'Option C: 291.25' }).check();
  await page.getByRole('button', { name: 'Check answer' }).click();
  await expect(page.getByText('✓ That’s correct.')).toBeVisible();
  await expect(page.getByText(/integer part is 256/)).toBeVisible();
  await page.getByRole('button', { name: '◇ Bookmark' }).click();
  await page.getByRole('button', { name: 'Question 3, unanswered' }).click();
  await expect(page.getByRole('heading', { name: '2026 Spring · Subject A · Q2' })).toBeVisible();
  await page.getByRole('button', { name: '← Previous' }).click();
  await expect(page.getByRole('heading', { name: '2025 Spring · Subject A · Q2' })).toBeVisible();
  await page.getByRole('link', { name: '← Return to textbook' }).click();
  await expect(page).toHaveURL(/data-representation\//);
  await expect(highlight).toBeFocused();
  const after = await page.locator('#radix-weights').evaluate((element) => element.getBoundingClientRect().top);
  expect(Math.abs(before - after)).toBeLessThan(3);
  await page.getByRole('button', { name: 'Mark as completed' }).click();
  await page.goto('/progress/');
  await expect(page.getByText('1 of 5 main sections completed')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Remove bookmark 2024S-A-Q001' })).toBeVisible();
  await expect(page.getByRole('link', { name: '2024S-A-Q001 →' })).toHaveCount(2);
  for (const link of await page.getByRole('link', { name: '2024S-A-Q001 →' }).all()) await expect(link).toHaveAttribute('href', '/practice/radix-conversion/?question=2024S-A-Q001');
  await expect(page.getByRole('link', { name: 'Continue reading →' })).toHaveAttribute('href', /data-representation/);
});

test('browser Back restores a new lesson and a direct practice visit returns to its own source', async ({ page }) => {
  await page.goto('/practice/disk-access/');
  await expect(page.getByRole('link', { name: '← Return to textbook' })).toHaveAttribute('href', '/chapters/hardware/auxiliary-storage/');
  await page.goto('/chapters/hardware/auxiliary-storage/');
  const highlight = page.locator('#concept-disk-access');
  await highlight.scrollIntoViewIfNeeded();
  const before = await page.locator('#disk-access-model').evaluate((element) => element.getBoundingClientRect().top);
  await highlight.click(); await page.goBack();
  await expect(highlight).toBeFocused();
  const after = await page.locator('#disk-access-model').evaluate((element) => element.getBoundingClientRect().top);
  expect(Math.abs(before - after)).toBeLessThan(3);
});

test('all new lesson routes remain readable without JavaScript', async ({ browser }) => {
  const context = await browser.newContext({ javaScriptEnabled: false });
  const page = await context.newPage();
  for (const lesson of hardwareLessons.slice(0,5)) {
    await page.goto(`http://127.0.0.1:4322${lessonPath(lesson)}`);
    await expect(page.locator(`[data-source-ref="${lesson.headings[0].id}"]`)).toBeVisible();
    expect((await page.locator('.reader-prose').innerText()).split(/\s+/).length).toBeGreaterThan(500);
  }
  await context.close();
});
