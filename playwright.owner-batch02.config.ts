import {defineConfig} from '@playwright/test';
process.env.OWNER_REVIEW_BATCH='2';
export default defineConfig({
 testDir:'./tests/owner-review',workers:1,fullyParallel:false,timeout:30000,reporter:'list',
 outputDir:'.local/historical/approval-candidates/technology-01-batch02/browser-results',
 use:{baseURL:'http://127.0.0.1:4331',viewport:{width:1280,height:900},headless:true,screenshot:'only-on-failure',trace:'retain-on-failure'},
 webServer:{command:'node scripts/question-review-server.mjs --approval-candidates --batch2',env:{QUESTION_REVIEW_PORT:'4331'},url:'http://127.0.0.1:4331/',reuseExistingServer:false,timeout:45000},
});
