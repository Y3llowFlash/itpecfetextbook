import { readFile, mkdir, writeFile, rename, unlink } from 'node:fs/promises';
import path from 'node:path';
import { randomUUID } from 'node:crypto';

/** Stage validated files, retain recovery copies, and roll back a caught write failure. */
export async function writeQuestionSnapshot(root:string, files:Map<string,Buffer|string>) {
  const output=path.resolve(root),entries:{target:string;before:Buffer|null;after:Buffer;stage:string}[]=[];
  const folder=path.join(output,'.local/question-transactions',randomUUID());
  for(const [relative,value]of files){
    const name=relative.replaceAll('\\','/');
    if(!/^(?:public\/questions\/[A-Za-z0-9_.-]+\.webp|public\/data\/(?:questions|import-manifest)\.json|src\/content\/(?:concepts|explanations)\.json)$/.test(name))throw Error('Not an owned question output');
    const target=path.resolve(output,name);
    if(!target.startsWith(output+path.sep))throw Error('Question output escapes workspace');
    let before:Buffer|null=null;
    try{before=await readFile(target);}catch(error){if((error as NodeJS.ErrnoException).code!=='ENOENT')throw error;}
    const after=Buffer.isBuffer(value)?value:Buffer.from(value);
    if(before?.equals(after))continue;
    entries.push({target,before,after,stage:path.join(folder,`${entries.length}.new`)});
  }
  if(!entries.length)return;
  await mkdir(folder,{recursive:true});
  for(const [i,entry]of entries.entries()){
    await writeFile(entry.stage,entry.after);
    if(entry.before)await writeFile(path.join(folder,`${i}.before`),entry.before);
  }
  await writeFile(path.join(folder,'recovery.json'),JSON.stringify(entries.map((e,i)=>({target:path.relative(output,e.target),backup:e.before?`${i}.before`:null})),null,2));
  const changed:typeof entries=[];
  try{
    for(const entry of entries){await mkdir(path.dirname(entry.target),{recursive:true});await rename(entry.stage,entry.target);changed.push(entry);}
  }catch(error){
    for(const entry of changed.reverse()){
      if(entry.before)await writeFile(entry.target,entry.before);else await unlink(entry.target);
    }
    throw error;
  }
}
