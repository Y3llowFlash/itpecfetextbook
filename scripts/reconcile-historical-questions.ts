import { readFile, writeFile } from 'node:fs/promises';
import { digest } from './question-importer';
import { matchOccurrence } from '../src/lib/question-policy';
import type { Question } from '../src/lib/models';
const folder='.local/historical/technology-01';
const records=JSON.parse(await readFile(`${folder}/questions.json`,'utf8'));
let reviews:Record<string,any>={};try{reviews=JSON.parse(await readFile(`${folder}/reviews.json`,'utf8'));}catch(error){if((error as NodeJS.ErrnoException).code!=='ENOENT')throw error;}
const bytes=await readFile('public/data/questions.json');
const bank=JSON.parse(bytes.toString('utf8')) as Question[];
const candidates=bank.filter(q=>q.is_published===true).map(q=>({id:q.id,examType:`FE-${q.paper}`,year:q.year,season:q.season,number:q.number,imageSha256:q.image.sha256,answer:q.correctAnswer}));
const decisions=records.map((r:any)=>{
  const metadata=reviews[r.id]?.contentSha256===r.contentSha256?reviews[r.id]?.metadata:undefined;
  const match=matchOccurrence({id:r.id,examType:metadata?.status==='verified'?`${metadata.examType}-${metadata.paper}`:null,year:r.year,season:r.season,number:r.number,contentSha256:r.contentSha256,imageSha256:r.images[0]?.sha256,answer:r.printedAnswer},candidates);
  return {id:r.id,...match,...(match.status==='matched'?{historicalPrintedAnswer:r.printedAnswer,sourceReferences:r.sourceReferences,explanationPolicy:match.conflict?'withhold contradictory explanation; owner review required':'preserve existing published explanation'}:{})};
});
const report={sourceSha256:records[0]?.sourceReferences[0]?.sha256,catalogSha256:digest(bytes),matched:decisions.filter((d:any)=>d.status==='matched').length,ambiguous:decisions.filter((d:any)=>d.status==='needs-review').length,distinct:decisions.filter((d:any)=>d.status==='distinct').length,answerConflicts:decisions.filter((d:any)=>d.conflict===true).length,decisions};
if(!process.argv.includes('--dry-run')){
  const file=`${folder}/duplicate-report.json`,output=JSON.stringify(report,null,2)+'\n';
  let previous='';try{previous=await readFile(file,'utf8');}catch(error){if((error as NodeJS.ErrnoException).code!=='ENOENT')throw error;}
  if(previous!==output)await writeFile(file,output);
}
console.log(JSON.stringify({...report,decisions:undefined,dryRun:process.argv.includes('--dry-run')},null,2));
