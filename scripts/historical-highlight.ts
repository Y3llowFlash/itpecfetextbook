/** The existing publisher's source-paragraph gate, shared with candidate preparation. */
import {readFile} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {digest} from './question-importer';
import {passageMatch} from '../src/lib/question-highlights';
import {presentSourceHTML} from '../src/lib/reader-presentation';

export function validateNewHighlight(source:string,definition:any,node:any,nodes:any[],existing:any[]) {
 const overlay=definition.sourceHighlight;
 if(!node || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(definition.id) || existing.some(c=>c.id===definition.id) ||
    !definition.title?.trim() || !definition.summary?.trim() || definition.sectionId!==node.sectionId || definition.sectionUrl!==node.path || overlay?.headingNumber!==node.number)
  throw Error('New concept identity, definition or exact heading disagrees');
 const html=presentSourceHTML(source),match=overlay&&passageMatch(html,overlay.passageId);
 if(!match || html.split(`id="${overlay.passageId}"`).length!==2 || digest(match[2])!==overlay.fragmentSha256 || /<(?:a|script|iframe|form)\b/i.test(match[2]) || existing.some(c=>c.sourceHighlight?.passageId===overlay.passageId))
  throw Error('Missing, duplicate, nested or changed highlight paragraph');
 const owners=nodes.filter(n=>n.path===node.path).map(n=>({node:n,offset:html.indexOf(`id="${n.id}"`)})).filter(n=>n.offset>=0&&n.offset<match.index!).sort((a,b)=>b.offset-a.offset);
 if(owners[0]?.node.id!==node.id)throw Error('Highlight crosses a numbered textbook subsection');
 // Unnumbered local labels such as "(2) Pipeline control" belong to this subsection.
 // A numbered heading absent from the authoritative contents must still fail closed.
 const between=html.slice(owners[0].offset,match.index);
 const headings=[...between.matchAll(/<h[1-4]\b[^>]*>([\s\S]*?)<\/h[1-4]>/g)];
 if(headings.some(h=>/^\s*\d+(?:\s*-\s*\d+)*\s+[A-Za-z]/.test(h[1].replace(/<[^>]*>/g,''))))throw Error('Unrecognized numbered heading before highlight');
 return {conceptId:definition.id,passageId:overlay.passageId,fragmentSha256:digest(match[2]),headingNumber:node.number,
  sectionId:node.sectionId,subsectionId:node.id,status:'source-validated-pending-owner-editorial-approval',
  wordingPreserved:true,duplicatesExistingHighlight:false,answerKeyAnnotationAdded:false};
}

if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const plan=JSON.parse(await readFile(process.argv[2],'utf8'));
 const toc=JSON.parse(await readFile('src/content/hardware-toc.json','utf8'));
 // An explicit immutable baseline supports rechecking a completed release;
 // the publisher itself always supplies the actual current concept list.
 if(process.argv.length>4)throw Error('Use a plan and optional archived existing-concept baseline');
 const existing=JSON.parse(await readFile(process.argv[3]||'src/content/concepts.json','utf8'));
 const results=[];
 for(const definition of plan.filter((c:any)=>c.newConcept)){
  try{
   const node=toc.nodes.find((n:any)=>n.number===definition.sourceHighlight?.headingNumber);
   const source=await readFile(`src/content/source-hardware/${node?.path.split('/').filter(Boolean).at(-1)}.html`,'utf8');
   results.push(validateNewHighlight(source,definition,node,toc.nodes,existing));
  }catch(error){results.push({conceptId:definition.id,status:'correction-required',issue:String(error),ownerEditorialApprovalGranted:false});}
 }
 console.log(JSON.stringify(results));
}
