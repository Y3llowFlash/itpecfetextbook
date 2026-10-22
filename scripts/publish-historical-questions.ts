/** Explicit owner-approved promotion, separate from extraction and Practice sync. */
import { execFileSync } from 'node:child_process';
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { digest, webpDimensions } from './question-importer';
import { matchOccurrence } from '../src/lib/question-policy';
import type { Question, Concept, Explanation } from '../src/lib/models';
import { passageMatch } from '../src/lib/question-highlights';
import { presentSourceHTML } from '../src/lib/reader-presentation';
import { writeQuestionSnapshot } from './question-snapshot';

const dryRun = process.argv.includes('--dry-run');
if (process.argv.slice(2).some(a=>a!=='--dry-run')) throw Error('Only --dry-run is supported');
const approved = JSON.parse(execFileSync('python',['scripts/historical_questions.py','export'],{encoding:'utf8',maxBuffer:20_000_000})) as {record:Record<string,any>;review:Record<string,any>}[];
const read = async (file:string)=>JSON.parse(await readFile(file,'utf8'));
const questions:Question[]=await read('public/data/questions.json');
const concepts:Concept[]=await read('src/content/concepts.json');
const explanations:Explanation[]=await read('src/content/explanations.json');
const toc=await read('src/content/hardware-toc.json');
const additions:string[]=[],updates:string[]=[],conflicts:{id:string;reason:string}[]=[],assets=new Map<string,Buffer>();
for (const {record:r,review:v} of approved) {
  // Multiple-page extraction is retained locally. Promotion requires one reviewed complete composite.
  if (r.images.length!==1) {conflicts.push({id:r.id,reason:'Multi-page record needs a reviewed composite image before promotion'});continue;}
  const candidate={id:r.id,examType:`${v.metadata.examType}-${v.metadata.paper}`,year:r.year,season:r.season,number:r.number,contentSha256:r.contentSha256,imageSha256:r.images[0].sha256,answer:r.printedAnswer};
  const match=matchOccurrence(candidate,questions.map(q=>({id:q.id,examType:`FE-${q.paper}`,year:q.year,season:q.season,number:q.number,imageSha256:q.image.sha256,answer:q.correctAnswer})));
  if(match.status==='needs-review'){conflicts.push({id:r.id,reason:`Ambiguous duplicate: ${match.candidateIds.join(', ')}`});continue;}
  const refs=r.sourceReferences.map((s:any)=>({...s,printedAnswer:r.printedAnswer}));
  if(match.status==='matched') {
    const q=questions.find(q=>q.id===match.canonicalId)!;
    // Published Practice fields and explanations are authoritative and remain unchanged.
    const fresh=refs.filter((ref:any)=>!q.review?.sources.some(s=>s.kind==='historical-pdf'&&s.sourceId===ref.sourceId&&s.sha256===ref.sha256&&s.pages.join(',')===ref.pages.join(',')));
    if(!fresh.length)continue;
    q.review={...(q.review||{examType:'FE',answerVerification:'verified',mappingStatus:'verified',extractionQuality:'complete',reviewStatus:'approved',publicationStatus:'published',mappings:[]}),sources:[...(q.review?.sources||[{kind:'itpec-practice',filename:q.source.questionPdf,pages:[q.source.pageStart,q.source.pageEnd]}]),...fresh],approvalFingerprint:v.approval.fingerprint};
    if(match.conflict)q.review.discrepancies=[...(q.review.discrepancies||[]),{authoritativeAnswer:q.correctAnswer,printedAnswer:r.printedAnswer,sourceId:'technology-01'}];
    updates.push(q.id);continue;
  }
  const old=questions.find(q=>q.id===r.id);
  if(old){conflicts.push({id:r.id,reason:'Canonical historical ID already exists with differing content'});continue;}
  let concept=concepts.find(c=>c.id===v.mapping.conceptId);
  const node=toc.nodes.find((n:any)=>n.number===v.mapping.headingNumber);
  if (!node || v.mapping.sectionId!==node.sectionId || v.mapping.subsectionId!==node.id || !/^[a-z0-9-]+$/.test(v.mapping.conceptId)) {conflicts.push({id:r.id,reason:'An exact textbook heading mapping must be reviewed first'});continue;}
  if(!concept){
    const highlight=v.mapping.sourceHighlight;
    const source=presentSourceHTML(await readFile(`src/content/source-hardware/${node.path.split('/').filter(Boolean).at(-1)}.html`,'utf8'));
    const passage=highlight&&passageMatch(source,highlight.passageId);
    const headingOffset=source.indexOf(`id="${node.id}"`),passageOffset=passage?source.indexOf(passage[0]):-1;
    const between=source.slice(headingOffset,passageOffset);
    if(!passage || digest(passage[2])!==highlight.fragmentSha256 || /<a\b/.test(passage[2]) || passageOffset<headingOffset || /<h[1-4]\b/.test(between.slice(between.indexOf('>')+1)) || !v.mapping.title || !v.mapping.summary){conflicts.push({id:r.id,reason:'New concept requires an unchanged, owner-reviewed paragraph immediately within its precise source heading; provide title and summary'});continue;}
    concept={id:v.mapping.conceptId,title:v.mapping.title,summary:v.mapping.summary,sectionId:node.sectionId,sectionUrl:node.path,anchor:highlight.passageId,questionIds:[],mappingEvidence:[],videos:[],sourceHighlight:{headingNumber:node.number,passageId:highlight.passageId,fragmentSha256:highlight.fragmentSha256}};
    concepts.push(concept);
  }else if(node.sectionId!==concept.sectionId || (!node.conceptIds.includes(concept.id)&&concept.sourceHighlight?.headingNumber!==node.number)){conflicts.push({id:r.id,reason:'Concept and precise source heading disagree'});continue;}
  const file=path.resolve('.local/historical/technology-01',r.images[0].path);
  if(!file.startsWith(path.resolve('.local/historical/technology-01/images')+path.sep))throw Error('Unsafe local crop path');
  const bytes=await readFile(file),sha=digest(bytes),filename=`${r.id}.${sha.slice(0,12)}.webp`;
  if(sha!==r.images[0].sha256)throw Error('Reviewed crop changed');
  const q:Question={id:r.id,examId:`${r.year}${r.season}_${v.metadata.examType}_${v.metadata.paper}`,number:r.number,year:r.year,season:r.season,subject:v.metadata.subject,paper:v.metadata.paper,format:'historical',sourceKind:'past_paper',examLabel:'',correctAnswer:v.verification.independentAnswer,options:['a','b','c','d'],is_published:true,chapter:'Chapter 1 Hardware',section:node.title,topic:concept.title,mapping:{headingNumber:node.number,subsectionId:node.id},image:{src:`/questions/${filename}`,...webpDimensions(bytes),sha256:sha},source:{dataset:'Technology-01.pdf',questionPdf:'Technology-01.pdf',pageStart:r.regions[0].pdfPage,pageEnd:r.regions.at(-1).pdfPage,originalImagePath:'',documentPath:`questions/${r.id}`},review:{examType:v.metadata.examType,sources:refs,answerVerification:'verified',mappingStatus:'verified',extractionQuality:'complete',reviewStatus:'approved',publicationStatus:'published',mappings:[v.mapping],approvalFingerprint:v.approval.fingerprint}};
  questions.push(q);assets.set(filename,bytes);additions.push(q.id);
  concept.questionIds.push(q.id);concept.mappingEvidence.push({questionId:q.id,reason:v.mapping.reason,reviewedAgainst:['original question image',v.mapping.evidence]});
  explanations.push({questionId:q.id,revision:v.approval.fingerprint.slice(0,12),answer:q.correctAnswer,summary:v.explanation.summary,steps:v.explanation.steps,takeaway:v.explanation.takeaway,optionText:v.extraction.optionText,imageDescription:v.extraction.imageDescription,reviewedAgainst:v.verification.evidence.map((e:any)=>JSON.stringify(e))});
}
console.log(JSON.stringify({dryRun,approvedInputs:approved.length,additions,updates,conflicts},null,2));
if(conflicts.length)process.exitCode=2;
else if(!dryRun&&(additions.length||updates.length)){
  questions.sort((a,b)=>a.id.localeCompare(b.id));
  const manifest=await read('public/data/import-manifest.json');
  if(additions.length)manifest.sources.push({path:'owner-approved/Technology-01.pdf',sha256:approved[0].record.sourceReferences[0].sha256,records:additions.length,published:additions.length});
  Object.assign(manifest,{total:questions.length,questionIds:questions.map(q=>q.id),images:questions.map(q=>q.image.src),datasetHash:digest(JSON.stringify(questions))});
  const writes=new Map<string,Buffer|string>([...assets].map(([name,bytes])=>[`public/questions/${name}`,bytes]));
  for(const [file,value]of [['public/data/questions.json',questions],['public/data/import-manifest.json',manifest],['src/content/concepts.json',concepts],['src/content/explanations.json',explanations]] as const)writes.set(file,JSON.stringify(value,null,2)+'\n');
  await writeQuestionSnapshot(process.cwd(),writes);
  execFileSync(process.execPath,['scripts/generate-reader-toc.mjs'],{stdio:'inherit'});
}
