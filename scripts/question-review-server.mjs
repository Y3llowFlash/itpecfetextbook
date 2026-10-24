/** Private, read-only gallery. Approval is a separate explicit CLI operation. */
import { createServer } from 'node:http';
import { readFile, realpath } from 'node:fs/promises';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {existsSync} from 'node:fs';
const candidateMode=process.argv.includes('--approval-candidates');
const batch2=process.argv.includes('--batch2');
const batch3=process.argv.includes('--batch3');
const batch6=process.argv.includes('--batch6');
const batch5=process.argv.includes('--batch5');
const batch4=process.argv.includes('--batch4');
if(process.argv.slice(2).some(arg=>!['--approval-candidates','--batch2','--batch3','--batch4','--batch5','--batch6'].includes(arg)) || ((batch2||batch3||batch4||batch5||batch6)&&!candidateMode) || [batch2,batch3,batch4,batch5,batch6].filter(Boolean).length>1)throw Error('Use --approval-candidates with one optional batch selection');
const archivedBatch3=batch3&&existsSync('.local/releases/historical-40-batch03/state.json');
const archivedBatch4=batch4&&existsSync('.local/releases/historical-40-batch04/state.json');
const archivedBatch5=batch5&&existsSync('.local/releases/historical-40-batch05/state.json');
const candidates=candidateMode?JSON.parse(execFileSync('python',archivedBatch5?['scripts/release_5.py','archive-candidates']:archivedBatch4?['scripts/release_4.py','archive-candidates']:archivedBatch3?['scripts/release_3.py','archive-candidates']:['scripts/approval_candidates.py','check',...(batch6?['--batch','6']:batch5?['--batch','5']:batch4?['--batch','4']:batch3?['--batch','3']:batch2?['--batch','2']:[])],{encoding:'utf8',maxBuffer:2_000_000})):null;
const root = await realpath('.local/historical/technology-01');
const port = Number(process.env.QUESTION_REVIEW_PORT || (batch6?4346:batch5?4342:batch4?4338:batch3?4334:batch2?4330:4319));
if(!Number.isInteger(port)||port<1024||port>65535)throw Error('Invalid owner-review port');
const server = createServer(async (req,res) => {
  try {
    if (req.method !== 'GET' && req.method !== 'HEAD') { res.writeHead(405); res.end(); return; }
    const host = `127.0.0.1:${port}`;
    if (req.headers.host !== host) { res.writeHead(403); res.end(); return; }
    if(req.headers.origin&&req.headers.origin!==`http://${host}`){res.writeHead(403);res.end();return;}
    const pathname = decodeURIComponent(new URL(req.url, `http://${host}`).pathname);
    if(candidateMode){
      const asset=candidates.galleryAssets[pathname];
      if(!asset)throw Error('Not an allowlisted owner-review asset');
      const file=await realpath(asset.path);
      const images=path.join(root,'images')+path.sep;
      if(file!==path.join(candidates.directory,'index.html')&&!file.startsWith(images))throw Error('Owner asset escaped private roots');
      const bytes=await readFile(file);
      if(createHash('sha256').update(bytes).digest('hex')!==asset.sha256)throw Error('Owner-review asset changed');
      res.writeHead(200,{'Content-Type':file.endsWith('.webp')?'image/webp':'text/html; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff','X-Robots-Tag':'noindex, nofollow','Referrer-Policy':'no-referrer','Content-Security-Policy':"default-src 'none'; img-src 'self'; style-src 'unsafe-inline'; connect-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"});
      res.end(req.method==='HEAD'?undefined:bytes);return;
    }
    if (!/^\/(?:index\.html|questions\.json|reviews\.json|manifest\.json|images\/[A-Za-z0-9_-]+\.webp)?$/.test(pathname)) throw new Error('Not a review asset');
    const file = await realpath(path.join(root, pathname === '/' ? 'index.html' : pathname));
    if (!file.startsWith(root + path.sep)) throw new Error('Outside gallery');
    const bytes = await readFile(file);
    res.writeHead(200, { 'Content-Type': file.endsWith('.webp') ? 'image/webp' : file.endsWith('.json') ? 'application/json; charset=utf-8' : 'text/html; charset=utf-8', 'Cache-Control':'no-store', 'X-Content-Type-Options':'nosniff', 'Content-Security-Policy':"default-src 'none'; img-src 'self'; style-src 'unsafe-inline'; frame-ancestors 'none'" });
    res.end(req.method === 'HEAD' ? undefined : bytes);
  } catch { res.writeHead(404); res.end('Not found'); }
});
server.listen(port,'127.0.0.1',()=>console.log(`Private ${candidateMode?`${candidates.candidates}-question owner`:'question'} review: http://127.0.0.1:${port}/ — read-only`));
