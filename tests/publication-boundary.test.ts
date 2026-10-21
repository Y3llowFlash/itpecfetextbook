// @vitest-environment node
import { expect,it } from 'vitest';
import { assertPublicationBoundary, assertApprovedPublicFile } from '../scripts/publication-boundary';
it('rejects reproduced datasets, raw/source assets and disguised local preview HTML',()=>{
  for(const name of ['chapter.json','raw/pdf-018.json','library/figure-1-01.png','cells/table-1.png','compare/pdf-018.html','data/source-book.json','original.pdf'])expect(()=>assertPublicationBoundary(name)).toThrow();
  expect(()=>assertPublicationBoundary('index.html','<body data-local-source-edition="ITPEC_LOCAL_SOURCE_EDITION_V1">')).toThrow();
  expect(()=>assertPublicationBoundary('_astro/accidental.js','const edition={"publicationAuthorization": "not-established"}')).toThrow();
  expect(()=>assertPublicationBoundary('unknown.html','',new Set(['index.html']))).toThrow();
  for(const name of ['book.txt','renamed-source.bin','_astro/source.pdf','questions/unapproved.webp'])expect(()=>assertApprovedPublicFile(name,new Set(['index.html']),new Set(['approved.webp']))).toThrow();
});
it('permits the current public fallback and published question snapshot',()=>{
  for(const name of ['index.html','data/questions.json','data/import-manifest.json','questions/approved.webp','_astro/reader.js'])expect(()=>assertPublicationBoundary(name)).not.toThrow();
  for(const name of ['index.html','robots.txt','sitemap.xml','_headers','_astro/font.woff2','questions/approved.webp'])expect(()=>assertApprovedPublicFile(name,new Set(['index.html']),new Set(['approved.webp']))).not.toThrow();
});
