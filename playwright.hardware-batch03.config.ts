import {defineConfig} from '@playwright/test';
export default defineConfig({
 testDir:'./tests/hardware-batch03',workers:1,fullyParallel:false,timeout:30000,reporter:'list',
 outputDir:'.local/releases/historical-40-batch03/student-browser-results',
 use:{baseURL:'http://127.0.0.1:4333',viewport:{width:1280,height:900},headless:true,screenshot:'only-on-failure',trace:'retain-on-failure'},
 webServer:{command:'node scripts/private-student-preview-server.mjs --batch03',env:{PILOT_PORT:'4333'},url:'http://127.0.0.1:4333/',reuseExistingServer:false,timeout:45000},
});
