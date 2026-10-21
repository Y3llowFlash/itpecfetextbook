import { defineConfig } from 'vitest/config';
export default defineConfig({ test: { include: ['tests/**/*.test.{ts,tsx}'], exclude: ['tests/rules/**'], environment: 'jsdom', restoreMocks: true } });
