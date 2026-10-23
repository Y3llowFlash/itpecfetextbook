/** Validate the owner-authorized published payload without private source files. */
import { createHash } from 'node:crypto';

export function canonical(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`;
  if (value && typeof value === 'object') return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${canonical((value as Record<string, unknown>)[key])}`).join(',')}}`;
  return JSON.stringify(value);
}
export const checksum = (value: unknown) => createHash('sha256').update(canonical(value)).digest('hex');

export function validateHistoricalRelease(questions: any[], explanations: any[], concepts: any[], receipt: any, expansion?: any, third?: any) {
  if (third) { validateThird(questions, explanations, concepts, receipt, expansion, third); return; }
  if (expansion) {
    validateExpansion(questions, explanations, concepts, receipt, expansion);
    return;
  }
  if (receipt.schema !== 'itpec-historical-release-v1' || receipt.authorizedCount !== 36 || receipt.records.length !== 36 || receipt.excludedUnapproved !== 297) throw Error('Invalid first historical release authorization scope');
  const ids = new Set<string>(receipt.records.map((r: any) => r.id));
  const historical = questions.filter(q => q.format === 'historical' || q.review?.sources.some((s: any) => s.kind === 'historical-pdf'));
  if (ids.size !== 36 || historical.length !== 36 || historical.some(q => !ids.has(q.id)) || questions.length !== receipt.total || receipt.total !== 456) throw Error('Unauthorized historical publication');
  const practice = Object.fromEntries(questions.filter(q => !ids.has(q.id)).map(q => [q.id, q]));
  if (Object.keys(practice).length !== 420 || checksum(practice) !== receipt.practiceRecordsSha256) throw Error('Original authoritative Practice catalog changed');
  const counts: Record<string, number> = {};
  for (const approved of receipt.records) {
    const q = questions.find(q => q.id === approved.id), e = explanations.find(e => e.questionId === approved.id);
    if (!q || !e || checksum(q) !== approved.questionSha256 || checksum(e) !== approved.explanationSha256 || checksum(q.review.mappings) !== approved.mappingSha256 || q.review.approvalFingerprint !== approved.approvalFingerprint || q.image.sha256 !== approved.imageSha256) throw Error(`Published approval payload changed: ${approved.id}`);
    if (q.correctAnswer !== e.answer || q.paper !== 'AM' || q.subject !== 'A' || q.review.examType !== 'FE' || q.review.reviewStatus !== 'approved' || q.review.publicationStatus !== 'published') throw Error(`Invalid grading/metadata/approval: ${approved.id}`);
    const links = concepts.filter(c => c.questionIds.includes(approved.id));
    if (links.length !== 1 || links[0].id !== approved.conceptId || q.review.mappings[0].conceptId !== approved.conceptId) throw Error(`Approved concept placement changed: ${approved.id}`);
    counts[approved.conceptId] = (counts[approved.conceptId] || 0) + 1;
  }
  if (checksum(counts) !== checksum(receipt.conceptCounts)) throw Error('Seven-concept authorization distribution changed');
}

/** Append-only Release 2: retain every Release 1 assertion and bind the new scope. */
function validateExpansion(questions:any[], explanations:any[], concepts:any[], previous:any, receipt:any) {
  if(receipt.schema!=='itpec-historical-release-2-v1'||receipt.authorizedCount!==40||receipt.records.length!==40||receipt.excludedUnapproved!==257||receipt.total!==496||receipt.historicalCount!==76||receipt.images!==496||receipt.candidateManifestSha256!=='39bcc7b8ca0488bccfe61e5a66ab5ff7e61fa7e7310ff2b3089cc3449b85cea3'||receipt.candidateSetFingerprint!=='4a887d4730c7c8e4f5a43ff7585bbb0081fa0b4fbb81463e7fb348e1c3853cf0')throw Error('Invalid Release 2 authorization');
  const ids=new Set<string>(receipt.records.map((r:any)=>r.id));
  if(ids.size!==40||previous.records.some((r:any)=>ids.has(r.id))||questions.length!==496||new Set(questions.map(q=>q.id)).size!==496)throw Error('Expanded or overlapping release scope');
  const old=questions.filter(q=>!ids.has(q.id)),oldAnswers=explanations.filter(e=>!ids.has(e.questionId));
  validateHistoricalRelease(old,oldAnswers,concepts,previous);
  if(checksum(Object.fromEntries(old.map(q=>[q.id,q])))!==receipt.previousRecordsSha256||checksum(oldAnswers)!==receipt.previousExplanationsSha256)throw Error('Previously published content changed');
  const counts:Record<string,number>={};
  for(const entry of receipt.records){
    const q=questions.find(q=>q.id===entry.id),e=explanations.find(e=>e.questionId===entry.id);
    if(!q||!e||q.format!=='historical'||checksum(q)!==entry.questionSha256||checksum(e)!==entry.explanationSha256||checksum(q.review.mappings)!==entry.mappingSha256||q.review.approvalFingerprint!==entry.approvalFingerprint||q.image.sha256!==entry.imageSha256)throw Error(`Release 2 approved payload changed: ${entry.id}`);
    if(q.correctAnswer!==e.answer||q.paper!=='AM'||q.subject!=='A'||q.review.examType!=='FE'||q.review.reviewStatus!=='approved'||q.review.publicationStatus!=='published')throw Error('Invalid Release 2 grading or metadata');
    const links=concepts.filter(c=>c.questionIds.includes(q.id));
    if(links.length!==1||links[0].id!==entry.conceptId||q.review.mappings[0].conceptId!==entry.conceptId)throw Error('Release 2 placement changed');
    counts[entry.conceptId]=(counts[entry.conceptId]||0)+1;
  }
  if(Object.keys(counts).length!==21||checksum(counts)!==checksum(receipt.conceptCounts))throw Error('Release 2 concept distribution changed');
  const newIds=new Set<string>(receipt.newHighlights.map((d:any)=>d.id));
  if(receipt.newHighlights.length!==15||newIds.size!==15||concepts.length!==28)throw Error('Wrong new highlight scope');
  for(const entry of receipt.newHighlights){
    const c=concepts.find(c=>c.id===entry.id);
    const definition=c&&Object.fromEntries(['id','title','summary','sectionId','sectionUrl','anchor','sourceHighlight'].filter(k=>k in c).map(k=>[k,c[k]]));
    if(!c||checksum(definition)!==entry.definitionSha256||checksum(c.sourceHighlight)!==checksum(entry.sourceHighlight))throw Error('Owner-reviewed highlight changed');
  }
  const oldConcepts=concepts.filter(c=>!newIds.has(c.id)).map(c=>({...c,questionIds:c.questionIds.filter((id:string)=>!ids.has(id)),mappingEvidence:c.mappingEvidence.filter((e:any)=>!ids.has(e.questionId))}));
  if(checksum(oldConcepts)!==receipt.previousConceptsSha256)throw Error('Previous concepts or placements changed');
}

/** Release 3 recursively verifies the exact unchanged Release 2 subset. */
function validateThird(questions:any[], explanations:any[], concepts:any[], first:any, second:any, receipt:any) {
  if(receipt.schema!=='itpec-historical-release-3-v1'||receipt.authorizedCount!==40||receipt.records.length!==40||receipt.excludedUnapproved!==217||receipt.total!==536||receipt.historicalCount!==116||receipt.images!==536||receipt.candidateManifestSha256!=='3d260fec5224408e642b1a405501097d423011a0e317b73e0224c302887e3721'||receipt.candidateSetFingerprint!=='94f7afb532d4aaeb6eb367fcfe0fc8f03e77699121bd5883a4a82bf18f2ca6f2')throw Error('Invalid Release 3 authorization');
  const ids=new Set<string>(receipt.records.map((r:any)=>r.id)),newConcepts=new Set<string>(receipt.newHighlights.map((r:any)=>r.id));
  if(ids.size!==40||newConcepts.size!==14||receipt.newHighlights.length!==14||questions.length!==536||new Set(questions.map(q=>q.id)).size!==536||concepts.length!==42||[...first.records,...second.records].some((r:any)=>ids.has(r.id)))throw Error('Expanded or overlapping Release 3 scope');
  const old=questions.filter(q=>!ids.has(q.id)),oldAnswers=explanations.filter(e=>!ids.has(e.questionId));
  const oldConcepts=concepts.filter(c=>!newConcepts.has(c.id)).map(c=>({...c,questionIds:c.questionIds.filter((id:string)=>!ids.has(id)),mappingEvidence:c.mappingEvidence.filter((e:any)=>!ids.has(e.questionId))}));
  validateHistoricalRelease(old,oldAnswers,oldConcepts,first,second);
  if(checksum(Object.fromEntries(old.map(q=>[q.id,q])))!==receipt.previousRecordsSha256||checksum(oldAnswers)!==receipt.previousExplanationsSha256||checksum(oldConcepts)!==receipt.previousConceptsSha256)throw Error('Previous release content changed');
  const counts:Record<string,number>={};
  for(const entry of receipt.records){
    const q=questions.find(q=>q.id===entry.id),e=explanations.find(e=>e.questionId===entry.id);
    if(!q||!e||q.format!=='historical'||checksum(q)!==entry.questionSha256||checksum(e)!==entry.explanationSha256||checksum(q.review.mappings)!==entry.mappingSha256||q.review.approvalFingerprint!==entry.approvalFingerprint||q.image.sha256!==entry.imageSha256)throw Error('Release 3 approved payload changed: '+entry.id);
    if(q.correctAnswer!==e.answer||q.paper!=='AM'||q.subject!=='A'||q.review.examType!=='FE'||q.review.reviewStatus!=='approved'||q.review.publicationStatus!=='published')throw Error('Invalid Release 3 grading or metadata');
    const links=concepts.filter(c=>c.questionIds.includes(q.id));
    if(links.length!==1||links[0].id!==entry.conceptId||q.review.mappings[0].conceptId!==entry.conceptId)throw Error('Release 3 placement changed');
    counts[entry.conceptId]=(counts[entry.conceptId]||0)+1;
  }
  if(Object.keys(counts).length!==28||checksum(counts)!==checksum(receipt.conceptCounts))throw Error('Release 3 concept distribution changed');
  for(const entry of receipt.newHighlights){
    const c=concepts.find(c=>c.id===entry.id),definition=c&&Object.fromEntries(['id','title','summary','sectionId','sectionUrl','anchor','sourceHighlight'].filter(k=>k in c).map(k=>[k,c[k]]));
    if(!c||checksum(definition)!==entry.definitionSha256||checksum(c.sourceHighlight)!==checksum(entry.sourceHighlight))throw Error('Release 3 owner-reviewed highlight changed');
  }
}
