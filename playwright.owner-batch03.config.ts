import {defineConfig} from '@playwright/test';
process.env.OWNER_REVIEW_BATCH='3';
export default defineConfig({
 testDir:'./tests/owner-review',workers:1,fullyParallel:false,timeout:45000,reporter:'list',
 outputDir:'.local/historical-batches/technology01-hardware-batch03/final-approval/browser-results',
 use:{baseURL:'http://127.0.0.1:4335',viewport:{width:1280,height:900},headless:true,screenshot:'only-on-failure',trace:'retain-on-failure'},
 webServer:{command:'node scripts/question-review-server.mjs --approval-candidates --batch3',env:{QUESTION_REVIEW_PORT:'4335'},url:'http://127.0.0.1:4335/',reuseExistingServer:false,timeout:45000},
});
