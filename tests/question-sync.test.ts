// @vitest-environment node
import { afterEach, it, expect } from 'vitest';
import { mkdtemp, mkdir, writeFile, readFile, readdir, rm } from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import fs from 'node:fs';
import { planSync, syncQuestions } from '../scripts/question-sync';
import type { Question } from '../src/lib/models';
import { writeQuestionSnapshot } from '../scripts/question-snapshot';
const bank=JSON.parse(fs.readFileSync('public/data/questions.json','utf8')) as Question[];
const roots:string[]=[];
it('validates every snapshot destination before changing a previously published file',async()=>{
  const root=await mkdtemp(path.join(os.tmpdir(),'itpec-sync-'));roots.push(root);
  await mkdir(path.join(root,'public/data'),{recursive:true});await writeFile(path.join(root,'public/data/questions.json'),'original');
  await expect(writeQuestionSnapshot(root,new Map([['public/data/questions.json','changed'],['../outside.json','forbidden']]))).rejects.toThrow('owned question output');
  expect(await readFile(path.join(root,'public/data/questions.json'),'utf8')).toBe('original');
  expect(await readdir(root)).toEqual(['public']);
});
afterEach(async()=>{for(const root of roots.splice(0)){if(!root.startsWith(path.resolve(os.tmpdir())+path.sep))throw Error('Unsafe cleanup');await rm(root,{recursive:true,force:true});}});
it('retains canonical IDs and published answers, flags changes, and handles safe source updates',()=>{
  const q=bank[0];
  expect(planSync([q],[{...q,correctAnswer:q.correctAnswer==='a'?'b':'a'}]).questions).toEqual([q]);
  expect(planSync([q],[{...q,correctAnswer:'z'}]).conflicts).toHaveLength(1);
  const moved={...q,source:{...q.source,dataset:'moved.json'}};
  expect(planSync([q],[moved]).updates).toEqual([q.id]);
  expect(planSync([q],[moved]).questions[0].correctAnswer).toBe(q.correctAnswer);
  expect(planSync([q],[{...q,id:'other-id'}]).conflicts).toHaveLength(1);
});
it('dry-run writes nothing, excludes unpublished images, adds once and becomes idempotent',async()=>{
  const root=await mkdtemp(path.join(os.tmpdir(),'itpec-sync-'));roots.push(root);
  const source=path.join(root,'source'),output=path.join(root,'output');
  const q=bank[0],imagePath='database/builder/output_images/q.webp';
  const row={question_id:q.id,is_published:true,exam_id:q.examId,question_no:q.number,year:q.year,season:q.season,subject:q.subject,paper:q.paper,format:q.format,correct_answer:q.correctAnswer,source_pdf:q.source.questionPdf,source_page_start:q.source.pageStart,source_page_end:q.source.pageEnd,question_image_path:imagePath};
  await mkdir(path.join(source,'database/firebase_import'),{recursive:true});
  await mkdir(path.dirname(path.join(source,imagePath)),{recursive:true});
  await writeFile(path.join(source,imagePath),await readFile(path.join('public',q.image.src)));
  const input=JSON.stringify([row,{...row,question_id:'2023A-AM-Q002',is_published:false,question_image_path:'absent.webp'}]);
  const file=path.join(source,'database/firebase_import/questions_subjectA_firestore.json');await writeFile(file,input);
  expect((await syncQuestions(source,output,true)).additions).toEqual([q.id]);
  expect(await readdir(root)).toEqual(['source']);
  const first=await syncQuestions(source,output);expect(first.skippedUnpublished).toBe(1);
  const snapshot=await readFile(path.join(output,'public/data/questions.json'),'utf8');
  expect((await syncQuestions(source,output)).additions).toEqual([]);
  expect(await readFile(path.join(output,'public/data/questions.json'),'utf8')).toBe(snapshot);
  expect(await readFile(file,'utf8')).toBe(input);
});
