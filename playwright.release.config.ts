import { defineConfig } from '@playwright/test';
const origin=process.env.RELEASE_ORIGIN || 'http://127.0.0.1:4322';
if(!['http://127.0.0.1:4322','https://itpecfetextbook.pages.dev'].includes(origin))throw Error('Release verification requires the local build or existing production origin');
export default defineConfig({testDir:'./tests/release',workers:1,timeout:45_000,reporter:'list',
  use:{baseURL:origin,viewport:{width:1280,height:900},headless:true,screenshot:'only-on-failure',trace:'retain-on-failure'},
  ...(origin.startsWith('http:')?{webServer:{command:'node node_modules/astro/bin/astro.mjs preview --host 127.0.0.1 --port 4322',url:origin,reuseExistingServer:false,timeout:30_000}}:{})});
