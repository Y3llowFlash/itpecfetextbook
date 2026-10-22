/** Only the approved reader bundle may be public; raw editorial artifacts stay local. */
export function assertApprovedPublicFile(filename:string,htmlRoutes:Set<string>,questionImages:Set<string>,approvedSourceAssets:Set<string>=new Set(),approvedCoverAssets:Set<string>=new Set()){
  const name=filename.replaceAll('\\','/');
  const rootFiles=new Set(['favicon.svg','robots.txt','sitemap.xml','_headers','data/questions.json','data/import-manifest.json']);
  const question=name.startsWith('questions/')&&questionImages.has(name.slice('questions/'.length));
  if(!htmlRoutes.has(name)&&!rootFiles.has(name)&&!question&&!approvedSourceAssets.has(name)&&!approvedCoverAssets.has(name)&&!/^_astro\/[^/]+\.(?:js|css|woff2)$/.test(name))throw new Error(`Unapproved public file: ${name}`);
}

export function assertPublicationBoundary(filename: string, content?: string, htmlRoutes?: Set<string>) {
  const name=filename.replaceAll('\\','/');
  if (/\.(?:pdf|py|mjs)$|(?:^|\/)(?:raw|library|cells|compare)(?:\/|$)|chapter\.json$|(?:page|figure)-manifest\.json$|validation-(?:report|summary)\.json$|outline\.json$|annotations\.json$|editorial\.(?:css|js)$/.test(name)) throw new Error(`Local source-edition artifact in public output: ${name}`);
  if(name.endsWith('.json')&&!['data/questions.json','data/import-manifest.json'].includes(name)) throw new Error(`Unapproved public dataset: ${name}`);
  if(name.endsWith('.html')&&htmlRoutes&&!htmlRoutes.has(name))throw new Error(`Unapproved source/HTML route: ${name}`);
  if(content&&/ITPEC_LOCAL_SOURCE_EDITION_V1|editorial-publication-status|"publicationAuthorization"\s*:\s*"not-established"/.test(content))throw new Error(`Reproduced editorial source material in public output: ${name}`);
}
