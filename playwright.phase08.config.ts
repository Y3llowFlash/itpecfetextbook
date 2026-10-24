import {defineConfig} from '@playwright/test';
export default defineConfig({
  testDir:'./tests/phase08',workers:1,timeout:60_000,reporter:'list',
  use:{baseURL:'http://127.0.0.1:4352',headless:true,trace:'retain-on-failure',screenshot:'only-on-failure'},
  webServer:[
    {command:'node scripts/private-student-preview-server.mjs --phase08',url:'http://127.0.0.1:4352/',timeout:120_000,reuseExistingServer:false},
    {command:'node scripts/question-review-server.mjs --approval-candidates --phase08',url:'http://127.0.0.1:4354/',timeout:120_000,reuseExistingServer:false}
  ]
});
