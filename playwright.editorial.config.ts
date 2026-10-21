import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir:'./tests/editorial',workers:1,fullyParallel:false,timeout:180000,
  outputDir:'.local/editorial-test-results',reporter:'list',
  use:{baseURL:'http://127.0.0.1:4341',headless:true,screenshot:'only-on-failure',trace:'retain-on-failure'},
  webServer:{command:'node scripts/editorial-server.mjs --port 4341',url:'http://127.0.0.1:4341/',reuseExistingServer:false,timeout:30000},
});
