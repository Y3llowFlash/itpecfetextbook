import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir: './tests/accounts', fullyParallel: false, workers: 1, timeout: 45_000,
  reporter: 'list', outputDir: 'test-results/accounts',
  use: { baseURL: 'http://127.0.0.1:4323', headless: true, screenshot: 'only-on-failure', trace: 'retain-on-failure' },
  webServer: {
    command: 'node node_modules/astro/bin/astro.mjs preview --outDir .local/account-dist --host 127.0.0.1 --port 4323',
    env: { ASTRO_TELEMETRY_DISABLED: '1', PUBLIC_FIREBASE_USE_EMULATORS: 'true' },
    url: 'http://127.0.0.1:4323/', reuseExistingServer: false, timeout: 30_000,
  },
});
