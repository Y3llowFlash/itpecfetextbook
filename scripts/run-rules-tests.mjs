import { runEmulatorTests } from './emulator-tests.mjs';
process.exit(runEmulatorTests('node node_modules/vitest/vitest.mjs run --config vitest.rules.config.ts'));
