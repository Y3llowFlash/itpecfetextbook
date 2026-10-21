import { test, expect, type BrowserContext, type Page } from '@playwright/test';

test.beforeAll(() => {
  if (process.env.FIREBASE_AUTH_EMULATOR_HOST !== '127.0.0.1:19099' || process.env.FIRESTORE_EMULATOR_HOST !== '127.0.0.1:18080') throw new Error('Account browser tests require local emulators');
});
async function googleSignIn(page: Page, email: string, name: string) {
  const popupPromise = page.waitForEvent('popup');
  await page.locator('#account').getByRole('button', { name: 'Continue with Google' }).click();
  const popup = await popupPromise;
  await popup.waitForURL(/127\.0\.0\.1:19099/);
  await popup.locator('#add-account-button').click();
  await popup.locator('#email-input').fill(email);
  await popup.locator('#display-name-input').fill(name);
  await popup.locator('#sign-in').click();
  await expect(page.getByRole('heading', { name: `Learning with ${name}` })).toBeVisible();
  await expect(page.locator('#account').getByRole('status')).toHaveText('Progress backed up', { timeout: 20000 });
}
async function emulatorTraffic(context: BrowserContext) {
  const blocked: string[] = [];
  await context.route('**/*', (route) => {
    const request = route.request(), hostname = new URL(request.url()).hostname;
    if (hostname === 'apis.google.com' && request.resourceType() === 'script') return route.continue();
    if (hostname !== '127.0.0.1') { blocked.push(request.url()); return route.abort(); }
    return route.continue();
  });
  return blocked;
}

test('Google popup, guest migration, two devices, offline recovery and account switching', async ({ browser }, testInfo) => {
  const firstContext = await browser.newContext();
  const secondContext = await browser.newContext();
  const first = await firstContext.newPage(), second = await secondContext.newPage();
  const suffix = Date.now();
  const email = `student-${suffix}@example.test`;
  // Google's static popup loader is required even with the Auth emulator.
  const blocked = await Promise.all([emulatorTraffic(firstContext), emulatorTraffic(secondContext)]);
  await first.goto('/practice/cache-memory/');
  await first.getByRole('radio', { name: 'Option A: 315 ns' }).check();
  await first.getByRole('button', { name: 'Check answer' }).click();
  await first.getByRole('button', { name: '◇ Bookmark' }).click();
  await first.goto('/progress/');
  await googleSignIn(first, email, 'Test Student');
  await expect(first.locator('.progress-stat-grid')).toContainText('1');
  await first.screenshot({ path: testInfo.outputPath('signed-in-account.png'), fullPage: true });
  await first.setViewportSize({ width: 375, height: 900 });
  expect(await first.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await first.screenshot({ path: testInfo.outputPath('signed-in-mobile.png'), fullPage: true });
  await first.setViewportSize({ width: 1280, height: 800 });

  await second.goto('/progress/');
  await googleSignIn(second, email, 'Test Student');
  await expect(second.getByRole('link', { name: '2024A-A-Q009 →' })).toHaveCount(2);
  await expect(second.getByRole('button', { name: 'Remove bookmark 2024A-A-Q009' })).toBeVisible();

  await second.goto('/chapters/hardware/memory-and-cache/');
  await second.getByRole('button', { name: 'Mark as completed' }).click();
  await second.goto('/progress/');
  await expect(second.locator('#account').getByRole('status')).toHaveText('Progress backed up', { timeout: 20000 });
  await first.getByRole('button', { name: 'Sync now' }).click();
  await expect(first.getByText('✓ Memory hierarchy & cache is marked complete.')).toBeVisible();

  await second.goto('/practice/cache-memory/');
  await expect(second.getByText('Let’s work through it.')).toBeVisible();
  await secondContext.setOffline(true);
  await second.getByRole('button', { name: '◆ Bookmarked' }).click();
  await second.getByRole('button', { name: 'Next →' }).click();
  await second.getByRole('radio', { name: 'Option C: 0.83' }).check();
  await second.getByRole('button', { name: 'Check answer' }).click();
  await expect(second.getByText('✓ That’s correct.')).toBeVisible();
  await secondContext.setOffline(false);
  await second.goto('/progress/');
  await expect(second.locator('#account').getByRole('status')).toHaveText('Progress backed up', { timeout: 20000 });
  await first.getByRole('button', { name: 'Sync now' }).click();
  await expect(first.getByRole('link', { name: '2025S-A-Q010 →' })).toBeVisible();
  await expect(first.getByRole('button', { name: 'Remove bookmark 2024A-A-Q009' })).toHaveCount(0);

  await first.getByRole('button', { name: 'Sign out', exact: true }).click();
  await expect(first.locator('.history-list')).toHaveCount(0);
  await expect(first.getByRole('link', { name: '2024A-A-Q009 →' })).toHaveCount(0);
  await googleSignIn(first, `other-${suffix}@example.test`, 'Other Student');
  await expect(first.getByRole('link', { name: '2024A-A-Q009 →' })).toHaveCount(0);
  await expect(first.getByRole('link', { name: '2025S-A-Q010 →' })).toHaveCount(0);
  // Optional emulator styling and Google's popup pixel remain blocked.
  expect(blocked.flat().filter((url) => !/unpkg\.com|fonts\.googleapis\.com|fonts\.gstatic\.com|www\.google\.com\/images\/cleardot\.gif/.test(url))).toEqual([]);
  await firstContext.close(); await secondContext.close();
});

test('sign-out clears other tabs immediately and preserves an offline outbox for its owner', async ({ context, page }) => {
  const blocked = await emulatorTraffic(context);
  const email = `tabs-${Date.now()}@example.test`;
  await page.goto('/progress/'); await googleSignIn(page, email, 'Tab Student');
  await page.goto('/practice/cache-memory/');
  await page.getByRole('radio', { name: 'Option B: 360 ns' }).check();
  await page.getByRole('button', { name: 'Check answer' }).click();
  await expect(page.locator('.guest-pill')).toHaveAttribute('title', 'Progress backed up', { timeout: 20000 });
  const other = await context.newPage(); await other.goto('/progress/');
  await expect(other.getByRole('heading', { name: 'Learning with Tab Student' })).toBeVisible();
  await expect(other.locator('#account').getByRole('status')).toHaveText('Progress backed up', { timeout: 20000 });
  await context.setOffline(true);
  await page.getByRole('button', { name: '◇ Bookmark' }).click();
  await expect(page.locator('.guest-pill')).toHaveAttribute('title', 'Offline — progress saved on this device');
  await other.getByRole('button', { name: 'Sign out', exact: true }).click();
  await expect(page.getByText('✓ That’s correct.')).toHaveCount(0);
  await expect(page.getByRole('button', { name: '◆ Bookmarked' })).toHaveCount(0);
  await expect(other.getByRole('heading', { name: 'Learning with Tab Student' })).toHaveCount(0);
  await context.setOffline(false);
  await googleSignIn(other, `tabs-other-${Date.now()}@example.test`, 'Different Student');
  await expect(other.getByRole('link', { name: '2024A-A-Q009 →' })).toHaveCount(0);
  await other.getByRole('button', { name: 'Sign out', exact: true }).click();
  await googleSignIn(other, email, 'Tab Student');
  await expect(other.getByRole('button', { name: 'Remove bookmark 2024A-A-Q009' })).toBeVisible();
  expect(blocked.filter((url) => !/unpkg\.com|fonts\.googleapis\.com|fonts\.gstatic\.com|www\.google\.com\/images\/cleardot\.gif/.test(url))).toEqual([]);
});

test('a new lesson reading checkpoint, bookmark and completion resume on another signed-in device', async ({ browser }) => {
  const a = await browser.newContext(), b = await browser.newContext();
  await emulatorTraffic(a); await emulatorTraffic(b);
  const first = await a.newPage(), second = await b.newPage();
  const email = `chapter1-${Date.now()}@example.test`;
  await first.goto('/chapters/hardware/data-representation/');
  await first.locator('#concept-radix-conversion').click();
  await first.getByRole('radio', { name: 'Option C: 291.25' }).check();
  await first.getByRole('button', { name: 'Check answer' }).click();
  await first.getByRole('button', { name: '◇ Bookmark' }).click();
  await first.goto('/progress/'); await googleSignIn(first, email, 'Chapter Student');
  await second.goto('/progress/'); await googleSignIn(second, email, 'Chapter Student');
  await expect(second.getByRole('button', { name: 'Remove bookmark 2024S-A-Q001' })).toBeVisible();
  await second.getByRole('link', { name: 'Continue reading →' }).click();
  await expect(second).toHaveURL(/data-representation\//);
  await expect(second.locator('#concept-radix-conversion')).toBeFocused();
  await second.getByRole('button', { name: 'Mark as completed' }).click();
  await second.goto('/progress/');
  await expect(second.locator('#account').getByRole('status')).toHaveText('Progress backed up', { timeout: 20000 });
  await first.getByRole('button', { name: 'Sync now' }).click();
  await expect(first.getByText('1 of 5 main sections completed')).toBeVisible();
  await second.goto('/chapters/hardware/auxiliary-storage/');
  await second.evaluate(() => document.fonts.ready);
  const figure = second.locator('#figure-disk-geometry-figure');
  await figure.evaluate((element) => window.scrollTo(0, window.scrollY + element.getBoundingClientRect().top - 75));
  await second.waitForTimeout(350); // Allow the reader's 250ms checkpoint debounce.
  await second.goto('/progress/');
  await expect(second.locator('#account').getByRole('status')).toHaveText('Progress backed up', { timeout: 20000 });
  await first.getByRole('button', { name: 'Sync now' }).click();
  await expect(first.getByRole('link', { name: 'Continue reading →' })).toHaveAttribute('href', /auxiliary-storage\/.*#figure-disk-geometry-figure/);
  await first.getByRole('link', { name: 'Continue reading →' }).click();
  await expect(first).toHaveURL(/#figure-disk-geometry-figure/);
  await expect.poll(() => first.locator('#figure-disk-geometry-figure').evaluate((element) => Math.abs(element.getBoundingClientRect().top - 75))).toBeLessThan(3);
  await a.close(); await b.close();
});
