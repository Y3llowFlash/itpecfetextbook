import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { validateHistoricalRelease, checksum } from '../scripts/historical-release-integrity';
const read = (p: string) => JSON.parse(readFileSync(p,'utf8'));
const expansion=read('docs/development/evidence/historical-release-40.json');
const third=read('docs/development/evidence/historical-release-3.json'),fourth=read('docs/development/evidence/historical-release-4.json');
const latestBank=read('public/data/questions.json'),latestAnswers=read('src/content/explanations.json'),latestConcepts=read('src/content/concepts.json');
const fourthIds=new Set(fourth.records.map((r:any)=>r.id)),fourthConcepts=new Set(fourth.newHighlights.map((r:any)=>r.id));
const fullBank=latestBank.filter((q:any)=>!fourthIds.has(q.id)),fullAnswers=latestAnswers.filter((e:any)=>!fourthIds.has(e.questionId));
const fullConcepts=latestConcepts.filter((c:any)=>!fourthConcepts.has(c.id)).map((c:any)=>({...c,questionIds:c.questionIds.filter((id:string)=>!fourthIds.has(id)),mappingEvidence:c.mappingEvidence.filter((e:any)=>!fourthIds.has(e.questionId))}));
const thirdIds=new Set(third.records.map((r:any)=>r.id)),thirdConcepts=new Set(third.newHighlights.map((r:any)=>r.id));
const expandedBank=fullBank.filter((q:any)=>!thirdIds.has(q.id)),expandedAnswers=fullAnswers.filter((e:any)=>!thirdIds.has(e.questionId));
const previousConcepts=fullConcepts.filter((c:any)=>!thirdConcepts.has(c.id)).map((c:any)=>({...c,questionIds:c.questionIds.filter((id:string)=>!thirdIds.has(id)),mappingEvidence:c.mappingEvidence.filter((e:any)=>!thirdIds.has(e.questionId))}));
// Retain the first release's exact assertions on its unchanged original subset.
const newIds=new Set(expansion.records.map((r:any)=>r.id));
const bank = expandedBank.filter((q:any)=>!newIds.has(q.id)), answers = expandedAnswers.filter((e:any)=>!newIds.has(e.questionId)), concepts = previousConcepts, receipt = read('docs/development/evidence/historical-release-36.json');
describe('exact owner-authorized historical release', () => {
  it('validates 36 approved payloads and preserves 420 authoritative Practice records', () => {
    expect(() => validateHistoricalRelease(bank, answers, concepts, receipt)).not.toThrow();
    expect(receipt.records).toHaveLength(36);
  });
  it('rejects content, accessibility, grading, approval, mapping and metadata changes', () => {
    const id = receipt.records[0].id;
    for (const field of ['correctAnswer','subject','paper','image','review']) {
      const changed = structuredClone(bank);changed.find((q: any) => q.id === id)[field] = 'changed';
      expect(() => validateHistoricalRelease(changed, answers, concepts, receipt)).toThrow();
    }
    for (const field of ['summary','steps','takeaway','imageDescription','optionText']) {
      const changed = structuredClone(answers);changed.find((e: any) => e.questionId === id)[field] = 'changed';
      expect(() => validateHistoricalRelease(bank, changed, concepts, receipt)).toThrow();
    }
    const changed = structuredClone(concepts);changed.find((c: any) => c.id === receipt.records[0].conceptId).questionIds = [];
    expect(() => validateHistoricalRelease(bank, answers, changed, receipt)).toThrow();
  });
  it('rejects extra historical records and changes to original Practice answers', () => {
    expect(() => validateHistoricalRelease([...bank, {...bank[0],id:'HIST-UNAPPROVED',format:'historical'}],answers,concepts,receipt)).toThrow();
    const changed = structuredClone(bank);changed.find((q: any) => q.format !== 'historical').correctAnswer = 'invalid';
    expect(() => validateHistoricalRelease(changed,answers,concepts,receipt)).toThrow();
  });
  it('matches the cross-language canonical receipt encoding', () => {
    expect(checksum({b:2,a:['✓',1]})).toBe('fed87e4f3d71c8bd5e6d54f05f6d9a3319a71c55e21edf7159ef3321cd6ef780');
  });
});

describe('exact Release 2 append-only authorization',()=>{
  const validate=(b=expandedBank,a=expandedAnswers,c=concepts,r=expansion)=>validateHistoricalRelease(b,a,c,receipt,r);
  it('validates all 40 new questions, 15 highlights, and unchanged first 456',()=>{expect(()=>validate()).not.toThrow();expect(expansion.records).toHaveLength(40);expect(expansion.newHighlights).toHaveLength(15);});
  it('rejects every academic, source, accessibility or approval mutation',()=>{
    for(const entry of expansion.records){
      const b=structuredClone(expandedBank);b.find((q:any)=>q.id===entry.id).correctAnswer='invalid';expect(()=>validate(b)).toThrow();
      const a=structuredClone(expandedAnswers);a.find((e:any)=>e.questionId===entry.id).imageDescription='stale';expect(()=>validate(expandedBank,a)).toThrow();
    }
  },15000);
  it('rejects altered highlights, extra questions and changed original concepts',()=>{
    for(const entry of expansion.newHighlights){const c=structuredClone(concepts);c.find((c:any)=>c.id===entry.id).sourceHighlight.fragmentSha256='changed';expect(()=>validate(expandedBank,expandedAnswers,c)).toThrow();}
    const c=structuredClone(concepts);c.find((c:any)=>c.id==='logic-gates').summary='changed';expect(()=>validate(expandedBank,expandedAnswers,c)).toThrow();
    expect(()=>validate([...expandedBank,{...expandedBank[0],id:'HIST-UNAPPROVED'}])).toThrow();
  });
  it('rejects expanded or rebound approval receipts',()=>{for(const field of ['candidateManifestSha256','candidateSetFingerprint','authorizedCount','excludedUnapproved'])expect(()=>validate(expandedBank,expandedAnswers,concepts,{...expansion,[field]:'changed'})).toThrow();});
});

describe('exact Release 3 append-only authorization',()=>{
  const validate=(b=fullBank,a=fullAnswers,c=fullConcepts,r=third)=>validateHistoricalRelease(b,a,c,receipt,expansion,r);
  it('validates all 536 records, unchanged prior releases, 40 additions and 14 highlights',()=>{expect(()=>validate()).not.toThrow();expect(third.records).toHaveLength(40);expect(third.newHighlights).toHaveLength(14);});
  it('rejects every new answer, accessible description, and source highlight mutation',()=>{
    for(const entry of third.records){const b=structuredClone(fullBank);b.find((q:any)=>q.id===entry.id).correctAnswer='invalid';expect(()=>validate(b)).toThrow();const a=structuredClone(fullAnswers);a.find((e:any)=>e.questionId===entry.id).imageDescription='stale';expect(()=>validate(fullBank,a)).toThrow();}
    for(const entry of third.newHighlights){const c=structuredClone(fullConcepts);c.find((c:any)=>c.id===entry.id).sourceHighlight.fragmentSha256='changed';expect(()=>validate(fullBank,fullAnswers,c)).toThrow();}
  },30000);
  it('rejects expanded, rebound or overlapping authorization and previous-record changes',()=>{
    for(const field of ['candidateManifestSha256','candidateSetFingerprint','authorizedCount','excludedUnapproved'])expect(()=>validate(fullBank,fullAnswers,fullConcepts,{...third,[field]:'changed'})).toThrow();
    const b=structuredClone(fullBank);b.find((q:any)=>q.format!=='historical').correctAnswer='changed';expect(()=>validate(b)).toThrow();
    expect(()=>validate([...fullBank,{...fullBank[0],id:'HIST-UNAPPROVED'}])).toThrow();
  });
});

describe('exact Release 4 append-only authorization',()=>{
 const validate=(b=latestBank,a=latestAnswers,c=latestConcepts,r=fourth)=>validateHistoricalRelease(b,a,c,receipt,expansion,third,r);
 it('validates 576 records, 40 exact additions, two new highlights and unchanged 536',()=>{expect(()=>validate()).not.toThrow();expect(fourth.records).toHaveLength(40);expect(fourth.newHighlights.map((r:any)=>r.id).sort()).toEqual(['cache-write-policies','display-memory']);});
 it('rejects every new answer, accessible description, mapping and highlight mutation',()=>{
  for(const entry of fourth.records){
   const b=structuredClone(latestBank);b.find((q:any)=>q.id===entry.id).correctAnswer='invalid';expect(()=>validate(b)).toThrow();
   const a=structuredClone(latestAnswers);a.find((e:any)=>e.questionId===entry.id).imageDescription='changed';expect(()=>validate(latestBank,a)).toThrow();
   const mapped=structuredClone(latestBank);mapped.find((q:any)=>q.id===entry.id).review.mappings[0].conceptId='wrong';expect(()=>validate(mapped)).toThrow();
  }
  for(const entry of fourth.newHighlights){const c=structuredClone(latestConcepts);c.find((c:any)=>c.id===entry.id).sourceHighlight.fragmentSha256='stale';expect(()=>validate(latestBank,latestAnswers,c)).toThrow();}
 },30000);
 it('rejects changed scope, old content and approval receipt bindings',()=>{
  for(const field of ['candidateManifestSha256','candidateSetFingerprint','authorizedCount','excludedUnapproved'])expect(()=>validate(latestBank,latestAnswers,latestConcepts,{...fourth,[field]:'changed'})).toThrow();
  const b=structuredClone(latestBank);b.find((q:any)=>thirdIds.has(q.id)).correctAnswer='changed';expect(()=>validate(b)).toThrow();
  expect(()=>validate([...latestBank,{...latestBank[0],id:'HIST-UNAPPROVED'}])).toThrow();
 });
});
