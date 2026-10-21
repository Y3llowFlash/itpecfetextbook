import { execFileSync, spawnSync } from 'node:child_process';
import path from 'node:path';

function javaProcesses() {
  if (process.platform !== 'win32') return [];
  const output = execFileSync('powershell.exe', ['-NoProfile', '-NonInteractive', '-Command',
    "@(Get-CimInstance Win32_Process -Filter \"Name='java.exe'\" | Select-Object ProcessId,CommandLine) | ConvertTo-Json -Compress"], { encoding: 'utf8' }).trim();
  const parsed = output ? JSON.parse(output) : [];
  return Array.isArray(parsed) ? parsed : [parsed];
}
export function runEmulatorTests(command) {
  const before = new Set(javaProcesses().map((p) => p.ProcessId));
  const result = spawnSync(process.execPath, [
    'node_modules/firebase-tools/lib/bin/firebase.js', 'emulators:exec', '--only', 'auth,firestore',
    '--project', 'demo-itpec-textbook', command,
  ], { stdio: 'inherit', env: { ...process.env, DEBUG: '' } });
  // Some Windows CLI/Java combinations leave a child after SIGINT. Clean up only
  // newly started demo emulators whose rules path belongs to this workspace.
  const rulesPath = path.resolve('firestore.rules').replace(/\\/g, '/').toLowerCase();
  for (const p of javaProcesses()) {
    const commandLine = String(p.CommandLine).replace(/\\+/g, '/').toLowerCase();
    if (!before.has(p.ProcessId) && commandLine.includes('cloud-firestore-emulator')
      && commandLine.includes('--project_id demo-itpec-textbook') && commandLine.includes(rulesPath)) {
      try { process.kill(p.ProcessId); } catch { /* Process already exited. */ }
    }
  }
  if (result.error) throw result.error;
  return result.status ?? 1;
}
