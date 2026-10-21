// Read-only Pages audit. Existing Wrangler credentials stay in memory.
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { homedir } from 'node:os';
import path from 'node:path';
const projectName = 'itpecfetextbook';
const paths = [
  path.join(homedir(), '.wrangler/config/default.toml'),
  path.join(homedir(), '.config/.wrangler/config/default.toml'),
  path.join(process.env.APPDATA || '', 'xdg.config/.wrangler/config/default.toml'),
];
let token = process.env.CLOUDFLARE_API_TOKEN;
if (!token) for (const file of paths) {
  try { token = (await readFile(file, 'utf8')).match(/oauth_token\s*=\s*"([^"]+)"/)?.[1]; } catch { /* Try the next supported Wrangler location. */ }
  if (token) break;
}
if (!token) throw new Error('No existing Cloudflare login is available');
async function get(endpoint) {
  const response = await fetch(`https://api.cloudflare.com/client/v4${endpoint}`, { headers: { Authorization: `Bearer ${token}` }, signal: AbortSignal.timeout(20000) });
  if (!response.ok) throw new Error(`Cloudflare read failed (${response.status}): ${endpoint}`);
  const body = await response.json();
  if (!body.success) throw new Error('Cloudflare project inspection was not authorized');
  return body.result;
}
const accounts = process.env.CLOUDFLARE_ACCOUNT_ID ? [{ id: process.env.CLOUDFLARE_ACCOUNT_ID }] : await get('/accounts?per_page=50');
let report;
for (const account of accounts) {
  let project;
  try { project = await get(`/accounts/${account.id}/pages/projects/${projectName}`); } catch (error) { if (String(error).includes('(404)')) continue; throw error; }
  const deployments = await get(`/accounts/${account.id}/pages/projects/${projectName}/deployments?per_page=5`);
  const source = project.source?.config;
  report = {
    checkedAt: new Date().toISOString(), name: project.name, subdomain: project.subdomain,
    productionBranch: project.production_branch, sourceType: project.source?.type || 'direct-upload',
    source: source ? { owner: source.owner, repo: source.repo_name, productionBranch: source.production_branch, deploymentsEnabled: source.deployments_enabled } : null,
    build: project.build_config ? { command: project.build_config.build_command, output: project.build_config.destination_dir, root: project.build_config.root_dir } : null,
    productionVariableNames: Object.keys(project.deployment_configs?.production?.env_vars || {}),
    nodeVersion: project.deployment_configs?.production?.env_vars?.NODE_VERSION?.value || null,
    productionEmulatorEnabled: project.deployment_configs?.production?.env_vars?.PUBLIC_FIREBASE_USE_EMULATORS?.value === 'true',
    deployments: deployments.map((deployment) => ({ id: deployment.id, environment: deployment.environment, url: deployment.url, createdOn: deployment.created_on, stage: deployment.latest_stage?.name, status: deployment.latest_stage?.status, branch: deployment.deployment_trigger?.metadata?.branch, commit: deployment.deployment_trigger?.metadata?.commit_hash })),
  };
  break;
}
if (!report) throw new Error('The expected itpecfetextbook Pages project was not found');
await mkdir('.local', { recursive: true });
await writeFile('.local/pages-audit.json', JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report, null, 2));
