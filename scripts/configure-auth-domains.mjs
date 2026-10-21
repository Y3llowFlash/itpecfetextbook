import { ownerFetch, project } from './firebase-owner-api.mjs';
const endpoint = `https://identitytoolkit.googleapis.com/admin/v2/projects/${project}/config`;
const before = await ownerFetch(endpoint);
const authorizedDomains = [...new Set([...before.authorizedDomains, 'localhost', '127.0.0.1', 'itpectextbook.com', 'itpecfetextbook.pages.dev'])];
if (JSON.stringify(authorizedDomains) !== JSON.stringify(before.authorizedDomains)) {
  await ownerFetch(`${endpoint}?updateMask=authorizedDomains`, { method: 'PATCH', body: JSON.stringify({ authorizedDomains }) });
}
const after = await ownerFetch(endpoint);
console.log(JSON.stringify({ project, authorizedDomains: after.authorizedDomains }, null, 2));
