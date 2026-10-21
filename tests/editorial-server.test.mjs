import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp,writeFile,rm } from 'node:fs/promises';
import path from 'node:path';
import { createEditorialServer,editorialFile } from '../scripts/editorial-server.mjs';

test('local server blocks traversal, raw PDFs and writes; adds a restrictive publication boundary',async()=>{
  const base=path.resolve('.local/editorial');
  const root=await mkdtemp(path.join(base,'server-test-'));
  const server=createEditorialServer(root);
  try{
    await writeFile(path.join(root,'index.html'),'<p>Local test fixture</p>');
    await writeFile(path.join(root,'source.pdf'),'not a served artifact');
    await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
    const url=`http://127.0.0.1:${server.address().port}`;
    const response=await fetch(url);
    assert.equal(response.status,200);assert.match(response.headers.get('content-security-policy'),/connect-src 'none'/);
    assert.equal(response.headers.get('cache-control'),'no-store');assert.match(response.headers.get('x-robots-tag'),/noindex/);
    assert.equal((await fetch(url,{method:'POST'})).status,405);
    assert.equal((await fetch(url+'/source.pdf')).status,404);
    for(const candidate of ['/../.env','/%2e%2e/.env','/%5c..%5c.env','/%00'])await assert.rejects(editorialFile(root,candidate));
  }finally{
    await new Promise(resolve=>server.close(resolve));
    const relative=path.relative(base,path.resolve(root));
    assert.ok(relative.startsWith('server-test-')&&!relative.includes(path.sep));
    await rm(root,{recursive:true,force:true});
  }
});
