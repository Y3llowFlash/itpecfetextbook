/** Private, read-only gallery. Approval is a separate explicit CLI operation. */
import { createServer } from 'node:http';
import { readFile, realpath } from 'node:fs/promises';
import path from 'node:path';
const root = await realpath('.local/historical/technology-01');
const port = Number(process.env.QUESTION_REVIEW_PORT || 4319);
const server = createServer(async (req,res) => {
  try {
    if (req.method !== 'GET' && req.method !== 'HEAD') { res.writeHead(405); res.end(); return; }
    const host = `127.0.0.1:${port}`;
    if (req.headers.host !== host) { res.writeHead(403); res.end(); return; }
    const pathname = decodeURIComponent(new URL(req.url, `http://${host}`).pathname);
    if (!/^\/(?:index\.html|questions\.json|reviews\.json|manifest\.json|images\/[A-Za-z0-9_-]+\.webp)?$/.test(pathname)) throw new Error('Not a review asset');
    const file = await realpath(path.join(root, pathname === '/' ? 'index.html' : pathname));
    if (!file.startsWith(root + path.sep)) throw new Error('Outside gallery');
    const bytes = await readFile(file);
    res.writeHead(200, { 'Content-Type': file.endsWith('.webp') ? 'image/webp' : file.endsWith('.json') ? 'application/json; charset=utf-8' : 'text/html; charset=utf-8', 'Cache-Control':'no-store', 'X-Content-Type-Options':'nosniff', 'Content-Security-Policy':"default-src 'none'; img-src 'self'; style-src 'unsafe-inline'; frame-ancestors 'none'" });
    res.end(req.method === 'HEAD' ? undefined : bytes);
  } catch { res.writeHead(404); res.end('Not found'); }
});
server.listen(port,'127.0.0.1',()=>console.log(`Private question review: http://127.0.0.1:${port}/`));
