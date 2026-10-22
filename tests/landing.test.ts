// @vitest-environment node
import {expect,it} from 'vitest';
import {landingBooks,FE_ENTRY} from '../src/lib/landing-books';
import {validateLandingAssets} from '../scripts/landing-assets';
import {assertApprovedPublicFile} from '../scripts/publication-boundary';
it('uses exactly the original FE Volume 1, IP main edition, and AP Volume 1 covers',async()=>{
 expect(FE_ENTRY).toBe('/chapters/hardware/');expect(landingBooks.map(b=>b.level)).toEqual(['fe','ip','ap']);
 expect(landingBooks.map(b=>b.available)).toEqual([true,false,false]);
 expect(landingBooks.map(b=>b.sourcePath)).toEqual(['design-references/fe-vol-1.png','design-references/ip-main-2017.png','design-references/ap-vol-1.png']);
 await expect(validateLandingAssets()).resolves.toBeUndefined();
});
it('permits only explicitly approved optimized cover files, never reference images or unused volumes',()=>{
 const approved=new Set(landingBooks.flatMap(b=>b.variants.map(v=>v.path)));
 for(const p of approved)expect(()=>assertApprovedPublicFile(p,new Set(),new Set(),new Set(),approved)).not.toThrow();
 for(const p of ['covers/unknown.webp','covers/ap-vol-2.png','design-references/landing-reference.png','design-references/fe-vol-1.png'])expect(()=>assertApprovedPublicFile(p,new Set(),new Set(),new Set(),approved)).toThrow();
});
