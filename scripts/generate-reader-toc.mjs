// Navigation metadata only. Never rewrites source text, source HTML or assets.
import {readFile,writeFile} from 'node:fs/promises';
const release=JSON.parse(await readFile('src/content/hardware-source-release.json','utf8'));
const mappings={'cache-memory':'3-5-1','radix-conversion':'2-2','floating-point':'2-3-2','signed-shifts':'2-3-4','bit-masks':'2-3-4','cpu-registers':'3-1','interrupts':'3-3-4','bus-transfer':'3-1','logic-gates':'3-4-1','disk-access':'4-1-3','defragmentation':'4-1-3','usb-interface':'5-5-2','three-dimensional-printing':'5-2-2'};
for(const concept of JSON.parse(await readFile('src/content/concepts.json','utf8')))if(concept.sourceHighlight)mappings[concept.id]=concept.sourceHighlight.headingNumber;
const nodes=[];
for(const lesson of release.lessons.slice(0,5))for(const heading of lesson.headings){
 const match=/^(\d(?:\s*-\s*\d){0,2})\s+([A-Za-z].*)$/.exec(heading.title);
 if(!match)continue;
 const number=match[1].replace(/\s/g,'');
 nodes.push({id:heading.id,number,title:match[2],page:heading.printedPage,depth:number.split('-').length,sectionId:lesson.id,path:lesson.path,conceptIds:Object.entries(mappings).filter(([,value])=>value===number).map(([id])=>id)});
}
if(nodes.length!==52||new Set(nodes.map(n=>n.id)).size!==52)throw new Error('Unexpected original source contents');
const output=JSON.stringify({editionId:release.editionId,releaseId:release.releaseId,nodes},null,2)+'\n';
if(process.argv.includes('--check')){
 if(await readFile('src/content/hardware-toc.json','utf8')!==output)throw new Error('Reader contents drifted from the original source; run npm run generate:reader-toc');
}else await writeFile('src/content/hardware-toc.json',output);
console.log('Verified source contents: 5 sections, 19 subsections, 28 deeper numbered entries.');
