// Loopback-only static reader for reproduced material in the ignored editorial workspace.
import http from 'node:http';
import { readFile, realpath, stat } from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

export const editorialRoot=path.resolve('.local/editorial/chapter-1');
const mime={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json; charset=utf-8','.png':'image/png','.webp':'image/webp'};
export async function editorialFile(root,requestPath) {
  const clean=decodeURIComponent(requestPath.split('?')[0]);
  if(clean.includes('\\')||clean.includes('\0')||clean.split('/').includes('..'))throw new Error('Forbidden');
  const target=path.resolve(root,'.'+(clean==='/'?'/index.html':clean));
  const relative=path.relative(root,target);
  if(relative.startsWith('..')||path.isAbsolute(relative))throw new Error('Forbidden');
  const resolved=await realpath(target);
  const actual=path.relative(await realpath(root),resolved);
  if(actual.startsWith('..')||path.isAbsolute(actual))throw new Error('Forbidden');
  if(!(await stat(resolved)).isFile()||!mime[path.extname(resolved)])throw new Error('Not found');
  return resolved;
}
export function createEditorialServer(root=editorialRoot) {
  return http.createServer(async(req,res)=>{
    res.setHeader('X-Robots-Tag','noindex, nofollow, noarchive');
    res.setHeader('Cache-Control','no-store');
    res.setHeader('X-Content-Type-Options','nosniff');
    res.setHeader('Content-Security-Policy',"default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self'; frame-src 'self'; frame-ancestors 'self'; connect-src 'none'; base-uri 'none'; form-action 'none'");
    if(!['GET','HEAD'].includes(req.method)){res.writeHead(405);res.end();return;}
    try {
      const file=await editorialFile(root,req.url||'/');
      const data=await readFile(file);
      res.setHeader('Content-Type',mime[path.extname(file)]);
      res.writeHead(200);res.end(req.method==='HEAD'?undefined:data);
    } catch(error) {res.writeHead(error.message==='Forbidden'?403:404);res.end('Local editorial file not available');}
  });
}
if(process.argv[1]&&pathToFileURL(path.resolve(process.argv[1])).href===import.meta.url){
  const port=Number(process.argv[process.argv.indexOf('--port')+1]||4340);
  const selected=process.argv.includes('--port')?port:4340;
  if(!Number.isInteger(selected)||selected<1024||selected>65535)throw new Error('Choose a loopback port between 1024 and 65535');
  await stat(path.join(editorialRoot,'index.html')).catch(()=>{throw new Error('Create the local edition first: python scripts/editorial_convert.py convert');});
  const server=createEditorialServer();
  server.listen(selected,'127.0.0.1',()=>console.log(`Local source edition: http://127.0.0.1:${selected}/ (not a Cloudflare/public build)`));
  for(const signal of ['SIGINT','SIGTERM'])process.on(signal,()=>server.close(()=>process.exit(0)));
}
