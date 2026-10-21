import { spawnSync } from 'node:child_process';
import { runEmulatorTests } from './emulator-tests.mjs';
const node = process.execPath;
const run = (args, env = {}) => {
  const result = spawnSync(node, args, { stdio: 'inherit', env: { ...process.env, DEBUG: '', ...env } });
  if (result.status !== 0) process.exit(result.status || 1);
};
// Isolated test output; never replace the real production dist/ with a demo build.
run(['scripts/astro.mjs', 'build', '--outDir', '.local/account-dist'], { PUBLIC_FIREBASE_USE_EMULATORS: 'true' });
process.exit(runEmulatorTests('node node_modules/@playwright/test/cli.js test --config playwright.accounts.config.ts'));
