// @vitest-environment node
import { expect,it } from 'vitest';
import release from '../src/content/hardware-source-release.json';
import { validateSourceRelease } from '../scripts/source-release';
it('publishes the approved complete source edition with exact text and asset hashes',async()=>{
  await expect(validateSourceRelease()).resolves.toBeUndefined();
  expect(release.lessons.slice(0,5).flatMap(lesson=>lesson.pages).map(page=>page.pdfPage)).toEqual(Array.from({length:100},(_,i)=>i+18));
  expect(release.annotations).toHaveLength(11);
  expect(release.unanchoredConcepts).toEqual(['bit-masks','three-dimensional-printing']);
},30000);
