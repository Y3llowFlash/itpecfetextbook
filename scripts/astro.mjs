import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
// Keep CLI state/telemetry out of the user's global profile and disable outbound telemetry.
const cli = fileURLToPath(new URL('../node_modules/astro/bin/astro.mjs', import.meta.url));
const result = spawnSync(process.execPath, [cli, ...process.argv.slice(2)], {
  stdio: 'inherit', env: { ...process.env, ASTRO_TELEMETRY_DISABLED: '1' },
});
if (result.error) throw result.error;
process.exit(result.status ?? 1);
