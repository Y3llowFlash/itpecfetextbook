/** Read-only local delivery of an explicitly selected, integrity-checked preview. */
import {createServer} from 'node:http';
import {readFile,realpath} from 'node:fs/promises';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {existsSync} from 'node:fs';
const root=fileURLToPath(new URL('../',import.meta.url));
const batch02=process.argv.includes('--batch02');
const batch03=process.argv.includes('--batch03');
const batch05=process.argv.includes('--batch05');
const batch04=process.argv.includes('--batch04');
if(process.argv.slice(2).some(arg=>!['--batch02','--batch03','--batch04','--batch05'].includes(arg))||[batch02,batch03,batch04,batch05].filter(Boolean).length>1)throw Error('Unknown or ambiguous preview selection');
const previewRoot=batch05?'.local/historical-batches/technology01-hardware-batch05/preview':batch04?'.local/historical-batches/technology01-hardware-batch04/preview':batch03?'.local/historical-batches/technology01-hardware-batch03/preview':batch02?'.local/historical-batches/technology01-hardware-batch02/preview':'.local/private-student-preview';
const archivedBatch3=batch03&&existsSync(path.join(root,'.local/releases/historical-40-batch03/state.json'));
const archivedBatch4=batch04&&existsSync(path.join(root,'.local/releases/historical-40-batch04/state.json'));
const checked=spawnSync('python',archivedBatch4?['scripts/release_4.py','archive-preview']:archivedBatch3?['scripts/release_3.py','archive-preview']:[batch05?'scripts/hardware_batch05.py':batch04?'scripts/hardware_batch04.py':batch03?'scripts/hardware_batch03.py':batch02?'scripts/hardware_batch02.py':'scripts/private_student_preview.py','check'],{cwd:root,stdio:archivedBatch3||archivedBatch4?'pipe':'inherit'});
if(checked.status!==0)throw Error('Private preview integrity failed; run npm run questions:pilot:prepare');
const manifest=JSON.parse(await readFile(path.join(root,previewRoot,'manifest.json'),'utf8'));
const port=Number(process.env.PILOT_PORT||(batch05?4340:batch04?4336:batch03?4332:batch02?4327:4324));
if(!Number.isInteger(port)||port<1024||port>65535)throw Error('Invalid private preview port');
const allowedRoots=[path.resolve(root,previewRoot,'app/dist')+path.sep,path.resolve(root,'.local/historical/technology-01/images')+path.sep];
const mime={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json; charset=utf-8','.webp':'image/webp','.png':'image/png','.svg':'image/svg+xml','.woff2':'font/woff2','.txt':'text/plain; charset=utf-8'};
const headers={'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','X-Robots-Tag':'noindex, nofollow, noarchive','Referrer-Policy':'no-referrer',
 'Content-Security-Policy':"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"};
export const server=createServer(async(req,res)=>{
 try{
  if(!['GET','HEAD'].includes(req.method)){res.writeHead(405,headers);res.end();return;}
  const origin=`http://127.0.0.1:${port}`;
  if(req.headers.host!==`127.0.0.1:${port}`||(req.headers.origin&&req.headers.origin!==origin)){res.writeHead(403,headers);res.end();return;}
  let name=decodeURIComponent(new URL(req.url,origin).pathname);
  if(name.includes('..')||name.includes('\\')||name.includes('\0'))throw Error('Invalid path');
  if(name.endsWith('/'))name+='index.html';
  const asset=manifest.assets[name];if(!asset)throw Error('Not an allowlisted preview asset');
  const file=await realpath(asset.path);if(!allowedRoots.some(root=>file.startsWith(root)))throw Error('Outside private delivery roots');
  const bytes=await readFile(file);
  const {createHash}=await import('node:crypto');
  if(createHash('sha256').update(bytes).digest('hex')!==asset.sha256)throw Error('Asset changed since source validation');
  res.writeHead(200,{...headers,'Content-Type':mime[path.extname(file)]||'application/octet-stream'});res.end(req.method==='HEAD'?undefined:bytes);
 }catch{res.writeHead(404,headers);res.end('Not found');}
});
server.listen(port,'127.0.0.1',()=>console.log(`Private student preview: http://127.0.0.1:${port}/ — local progress only; no approval or publication.`));
