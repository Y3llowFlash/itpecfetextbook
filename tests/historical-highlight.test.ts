import {describe,it,expect} from 'vitest';
import {createHash} from 'node:crypto';
import {validateNewHighlight} from '../scripts/historical-highlight';
const digest=(s:string)=>createHash('sha256').update(s).digest('hex');
const node={id:'numbered-source',number:'3-5-2',sectionId:'s03',path:'/chapters/hardware/cpu-and-main-memory/'};
const next={...node,id:'next-numbered-source',number:'3-6'};
const paragraph='Original source explains overlapping instruction stages without exam answer labels.';
const definition={id:'synthetic-pipeline',title:'Pipeline control',summary:'Overlap instruction stages.',sectionId:node.sectionId,sectionUrl:node.path,sourceHighlight:{headingNumber:node.number,passageId:'source-paragraph',fragmentSha256:digest(paragraph)}};
const source=(middle='')=>`<h4 id="${node.id}">3-5-2 Speeding-up of Processor</h4>${middle}<p id="source-paragraph">${paragraph}</p>`;
describe('shared historical publisher paragraph gate',()=>{
 it('accepts an unchanged paragraph after a legitimate unnumbered child label',()=>{
  const result=validateNewHighlight(source('<h4>(2) Pipeline control</h4>'),definition,node,[node,next],[]);
  expect(result.status).toBe('source-validated-pending-owner-editorial-approval');expect(result.wordingPreserved).toBe(true);
 });
 it('rejects a later numbered subsection even when the fragment hash matches',()=>{
  expect(()=>validateNewHighlight(source(`<h4 id="${next.id}">3-6 Other topic</h4>`),definition,node,[node,next],[])).toThrow(/numbered textbook subsection/);
 });
 it('rejects an unrecognized numbered heading absent from the contents',()=>{
  expect(()=>validateNewHighlight(source('<h4>3-9 Unexpected heading</h4>'),definition,node,[node],[])).toThrow(/Unrecognized numbered/);
 });
 it('rejects stale hashes, duplicate IDs, existing highlights and nested links',()=>{
  for(const html of [source().replace(paragraph,'Changed'),source()+`<p id="source-paragraph">${paragraph}</p>`])expect(()=>validateNewHighlight(html,definition,node,[node],[])).toThrow();
  expect(()=>validateNewHighlight(source(),definition,node,[node],[definition])).toThrow();
  expect(()=>validateNewHighlight(source(),definition,node,[node],[{id:'another',sourceHighlight:{passageId:'source-paragraph'}}])).toThrow();
  const linked=`<a href="/practice/synthetic/">${paragraph}</a>`;
  expect(()=>validateNewHighlight(source().replace(paragraph,linked),{...definition,sourceHighlight:{...definition.sourceHighlight,fragmentSha256:digest(linked)}},node,[node],[])).toThrow(/nested/);
 });
 it('rejects mismatched section, route, heading, unstable IDs and missing titles',()=>{
  for(const patch of [{sectionId:'other'},{sectionUrl:'/other/'},{id:'Invalid ID'},{title:''},{sourceHighlight:{...definition.sourceHighlight,headingNumber:'3-4-1'}}])expect(()=>validateNewHighlight(source(),{...definition,...patch},node,[node],[])).toThrow();
 });
});
