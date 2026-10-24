import {defineConfig} from '@playwright/test';
export default defineConfig({
 testDir:'./tests/hardware-batch06',workers:1,fullyParallel:false,timeout:30000,reporter:'list',
 outputDir:'.local/historical-batches/technology01-hardware-batch06/browser-results',
 use:{baseURL:'http://127.0.0.1:4345',viewport:{width:1280,height:900},headless:true,screenshot:'only-on-failure',trace:'retain-on-failure'},
 webServer:{command:'node scripts/private-student-preview-server.mjs --batch06',env:{PILOT_PORT:'4345'},url:'http://127.0.0.1:4345/',reuseExistingServer:false,timeout:45000},
});
