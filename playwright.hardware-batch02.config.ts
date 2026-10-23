import {defineConfig} from '@playwright/test';
export default defineConfig({
 testDir:'./tests/hardware-batch02',workers:1,fullyParallel:false,timeout:30000,reporter:'list',
 outputDir:'.local/historical-batches/technology01-hardware-batch02/browser-results',
 use:{baseURL:'http://127.0.0.1:4328',viewport:{width:1280,height:900},headless:true,screenshot:'only-on-failure',trace:'retain-on-failure'},
 webServer:{command:'node scripts/private-student-preview-server.mjs --batch02',env:{PILOT_PORT:'4328'},url:'http://127.0.0.1:4328/',reuseExistingServer:false,timeout:45000},
});
