// Read-only project audit using the owner's existing Firebase CLI login.
// Tokens never leave memory and are never printed or written to this repository.
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { ownerFetch as get, project } from './firebase-owner-api.mjs';
const release = await get(`https://firebaserules.googleapis.com/v1/projects/${project}/releases/cloud.firestore`);
const ruleset = await get(`https://firebaserules.googleapis.com/v1/${release.rulesetName}`);
const auth = await get(`https://identitytoolkit.googleapis.com/admin/v2/projects/${project}/config`);
const google = await get(`https://identitytoolkit.googleapis.com/v2/projects/${project}/defaultSupportedIdpConfigs/google.com`);
const app = await get(`https://firebase.googleapis.com/v1beta1/projects/${project}/webApps/1:959099491967:web:79ee8a1d34410e83e2d14a/config`);
const billing = await get(`https://cloudbilling.googleapis.com/v1/projects/${project}/billingInfo`);
const localRules = await readFile('firestore.rules', 'utf8');
const report = {
  checkedAt: new Date().toISOString(), project, release: release.name, ruleset: release.rulesetName,
  localRulesMatch: ruleset.source.files.some((file) => file.name === 'firestore.rules'
    && file.content.replace(/\r\n/g, '\n') === localRules.replace(/\r\n/g, '\n')),
  rules: ruleset.source.files, authorizedDomains: auth.authorizedDomains,
  anonymousEnabled: auth.signIn?.anonymous?.enabled, googleEnabled: google.enabled,
  app: { projectId: app.projectId, appId: app.appId, authDomain: app.authDomain, storageBucket: app.storageBucket },
  billing: { billingEnabled: billing.billingEnabled },
};
await mkdir('.local', { recursive: true });
await writeFile('.local/firebase-audit.json', JSON.stringify(report, null, 2));
console.log(JSON.stringify(report, null, 2));
