import {defineConfig} from '@playwright/test';
process.env.OWNER_REVIEW_BATCH='7';
export default defineConfig({
 testDir:'./tests/owner-review',workers:1,fullyParallel:false,timeout:45000,reporter:'list',
 outputDir:'.local/historical-batches/technology01-hardware-batch07/final-approval/browser-results',
 use:{baseURL:'http://127.0.0.1:4351',viewport:{width:1280,height:900},headless:true,screenshot:'only-on-failure',trace:'retain-on-failure'},
 webServer:{command:'node scripts/question-review-server.mjs --approval-candidates --batch7',env:{QUESTION_REVIEW_PORT:'4351'},url:'http://127.0.0.1:4351/',reuseExistingServer:false,timeout:45000},
});
