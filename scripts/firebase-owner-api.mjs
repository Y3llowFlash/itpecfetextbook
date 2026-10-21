import { createRequire } from 'node:module';
import { readFile } from 'node:fs/promises';
export const project = 'itpec-textbook';
const config = JSON.parse(await readFile(new URL('../.firebaserc', import.meta.url), 'utf8'));
if (config.projects.default !== project) throw new Error('Unexpected Firebase target');
const require = createRequire(import.meta.url);
const cli = createRequire(require.resolve('firebase-tools/package.json'));
const { getGlobalDefaultAccount, getAccessToken } = cli('./lib/auth.js');
const account = getGlobalDefaultAccount();
if (!account?.tokens?.refresh_token) throw new Error('Firebase CLI login is required');
const credentials = await getAccessToken(account.tokens.refresh_token, ['https://www.googleapis.com/auth/cloud-platform', 'https://www.googleapis.com/auth/firebase']);
// Existing CLI credentials remain in memory; only sanitized responses are reported.
export async function ownerFetch(url, options = {}) {
  const response = await fetch(url, { ...options, headers: { Authorization: `Bearer ${credentials.access_token}`, 'Content-Type': 'application/json' } });
  if (!response.ok) throw new Error(`Firebase request failed: ${response.status} ${new URL(url).pathname}`);
  return response.json();
}
