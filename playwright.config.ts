import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: false,
  workers: 1,
  timeout: 30_000,
  reporter: 'list',
  use: { baseURL: 'http://127.0.0.1:4322', viewport: { width: 1280, height: 800 }, headless: true, screenshot: 'only-on-failure', trace: 'retain-on-failure' },
  webServer: { command: 'node node_modules/astro/bin/astro.mjs preview --host 127.0.0.1 --port 4322', env: { ASTRO_TELEMETRY_DISABLED: '1' }, url: 'http://127.0.0.1:4322/', reuseExistingServer: false, timeout: 30_000 },
});
