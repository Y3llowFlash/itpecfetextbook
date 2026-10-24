import {defineConfig} from '@playwright/test';
process.env.OWNER_REVIEW_BATCH='6';
export default defineConfig({
 testDir:'./tests/owner-review',workers:1,fullyParallel:false,timeout:45000,reporter:'list',
 outputDir:'.local/historical-batches/technology01-hardware-batch06/final-approval/browser-results',
 use:{baseURL:'http://127.0.0.1:4347',viewport:{width:1280,height:900},headless:true,screenshot:'only-on-failure',trace:'retain-on-failure'},
 webServer:{command:'node scripts/question-review-server.mjs --approval-candidates --batch6',env:{QUESTION_REVIEW_PORT:'4347'},url:'http://127.0.0.1:4347/',reuseExistingServer:false,timeout:45000},
});
