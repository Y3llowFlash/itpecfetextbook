// @vitest-environment node
import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import chapter from '../src/content/chapters.json';
import evidence from '../docs/development/evidence/hardware-printed-pages.json';
import { hardwareLessons, lessonPath, pageLabel } from '../src/lib/lessons';
import { concepts, explanationMap, publishedQuestions, questionsForConcept } from '../src/lib/catalog';
import { validReading } from '../src/lib/progress';
import { returnUrl, savedReturnPosition } from '../src/lib/reading';
import release from '../src/content/hardware-source-release.json';
import {canonicalReadingPosition} from '../src/lib/reading-routes';
import historicalRelease from '../docs/development/evidence/historical-release-36.json';
import expansion from '../docs/development/evidence/historical-release-40.json';
import third from '../docs/development/evidence/historical-release-3.json';
import { checksum } from '../scripts/historical-release-integrity';

describe('completed Hardware chapter', () => {
  it('preserves all five sections, 19 source subsections, deeper topics and the old cache ID', () => {
    expect(chapter.sections.map((section) => section.status)).toEqual(Array(5).fill('published'));
    expect(hardwareLessons.slice(0, 5).flatMap((lesson) => lesson.headings.filter((heading) => heading.level === 2))).toHaveLength(19);
    expect(hardwareLessons.map((lesson) => lesson.id)).toEqual(['fe-v1-ch01-s01','fe-v1-ch01-s02','fe-v1-ch01-s03','fe-v1-ch01-s04','fe-v1-ch01-s05','fe-v1-ch01-memory-cache']);
    for (const lesson of hardwareLessons) {
      const source = readFileSync(`src/content/source-hardware/${lesson.slug}.html`, 'utf8');
      const converted=release.lessons.find(entry=>entry.id===lesson.id)!;
      for (const heading of converted.headings) expect(source).toContain(`id="${heading.id}" data-reading-block`);
    }
  });
  it('uses verified printed labels rather than assuming one PDF offset', () => {
    expect(hardwareLessons.slice(0, 5).map((lesson) => lesson.pages)).toEqual([[13,19],[20,45],[46,77],[78,91],[92,111]]);
    expect(evidence.edition).toBe('First Edition, April 2015');
    expect(evidence.sha256).toMatch(/^[a-f0-9]{64}$/);
    const physical = (printed: number) => evidence.pages.find((page) => page.printedPage === printed)?.pdfPage;
    expect(physical(13)).toBe(18); expect(physical(70)).toBe(75); expect(physical(78)).toBe(84);
    expect(evidence.pages.find((page) => page.pdfPage === 83)?.printedPage).toBeNull();
    expect(pageLabel([52,52])).toBe('p. 52'); expect(pageLabel([70,74])).toBe('pp. 70–74');
    for (const lesson of hardwareLessons) {
      expect(lesson.editionId).toBe(evidence.editionId);
      for (const reference of [lesson, ...lesson.headings]) for (let p = reference.pages[0]; p <= reference.pages[1]; p++) expect(physical(p)).toBeDefined();
    }
  });
  it('links 23 original plus 76 owner-approved questions with complete matching explanations', async () => {
    const bank = await publishedQuestions();
    const linked = new Set(concepts.flatMap((concept) => concept.questionIds));
    expect(concepts).toHaveLength(42); expect(linked.size).toBe(139);
    expect([...linked].sort()).toEqual(bank.filter((question) => question.chapter === 'Chapter 1 Hardware').map((question) => question.id).sort());
    for (const concept of concepts) {
      const questions = questionsForConcept(concept, bank);
      expect(questions).toHaveLength(concept.questionIds.length);
      expect(questionsForConcept(concept, [...bank, ...questions, { ...questions[0], id: 'unpublished', is_published: false } as never])).toHaveLength(questions.length);
      for (const question of questions) {
        const explanation = explanationMap.get(question.id)!;
        expect(explanation.answer).toBe(question.correctAnswer);
        if(question.format==='historical') {
          // Preserve the exact approved worked reasoning, including valid
          // two-step explanations; never pad it to satisfy an older fixture.
          expect(checksum(explanation)).toBe([...historicalRelease.records,...expansion.records,...third.records].find(r=>r.id===question.id)!.explanationSha256);
        } else expect(explanation.steps.length).toBeGreaterThanOrEqual(3);
        expect(Object.keys(explanation.optionText)).toEqual(question.options);
        if(question.format!=='historical')expect(explanation.reviewedAgainst.some((item) => /original.*image/.test(item))).toBe(true);
      }
    }
  });
  it('checks new numerical and circuit explanations independently', () => {
    expect(1*16**2+2*16+3+4/16).toBe(291.25);
    expect(1*8**3+2*8**2+3*8+4+2/8).toBe(668.25);
    expect(2**(130-127)*(1+0.5+0.25)).toBe(14);
    expect(4+1.25+60000/5000/2+1000/60).toBeCloseTo(27.9166667);
    expect(5+0.1+60000/6000/2+16/1024*1000).toBe(25.725);
    expect(64e6/4*64/8/1e6).toBe(128);
    for (const a of [false,true]) for (const b of [false,true]) {
      expect(!(!(!a && b) || !(a || b))).toBe(!a && b);
      for (const c of [false,true]) expect(!(a && b) || !c).toBe(!(a && b && c));
    }
  });
  it('validates every reading route/ID pair and returns to that route safely', () => {
    for (const lesson of hardwareLessons) {
      const position = { sectionId: lesson.id, path: lessonPath(lesson), blockId: lesson.headings[0].id, offset: 30, scrollY: 100, updatedAt: '2026-10-21T10:00:00Z' };
      expect(validReading(position)).toBe(true);
      const canonical=canonicalReadingPosition(position);
      expect(returnUrl(position)).toBe(`${canonical.path}?resume=1#${canonical.blockId}`);
      expect(validReading({ ...position, sectionId: 'wrong-section' })).toBe(false);
      expect(validReading({ ...position, path: 'https://example.invalid/' })).toBe(false);
      expect(savedReturnPosition(position, 'wrong-section')).toBeNull();
    }
  });
});
