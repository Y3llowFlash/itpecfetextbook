import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { validateHistoricalRelease, checksum } from '../scripts/historical-release-integrity';
const read = (p: string) => JSON.parse(readFileSync(p,'utf8'));
const bank = read('public/data/questions.json'), answers = read('src/content/explanations.json'), concepts = read('src/content/concepts.json'), receipt = read('docs/development/evidence/historical-release-36.json');
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
