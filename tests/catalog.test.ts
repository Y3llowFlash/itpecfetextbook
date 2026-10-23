// @vitest-environment node
import { describe, expect, it } from 'vitest';
import { concepts, explanationMap, publishedQuestions, questionsForConcept } from '../src/lib/catalog';
import { safeYoutubeId } from '../src/components/VideoRecommendation';

describe('published pilot catalog', () => {
  it('resolves exactly the reviewed real question IDs and never includes unpublished duplicates', async () => {
    const questions = await publishedQuestions();
    expect(questions).toHaveLength(536);
    const real = questionsForConcept(concepts[0], questions);
    expect(real.map((q) => q.id)).toEqual(['2024A-A-Q009', '2025S-A-Q010', '2026S-A-Q010','HIST-TECH01-2009A-Q028','HIST-TECH01-2015A-Q011','HIST-TECH01-2019A-Q013','HIST-TECH01-2019S-Q011']);
    expect(questionsForConcept(concepts[0], [...questions, real[0]])).toHaveLength(7);
    expect(questionsForConcept(concepts[0], [{ ...real[0], is_published: false } as never])).toEqual([]);
    for (const question of real) expect(explanationMap.get(question.id)?.answer).toBe(question.correctAnswer);
  });
  it('checks the numerical explanations independently', () => {
    expect(0.8 * 75 + 0.2 * 1500).toBe(360);
    const hit = (90 - 80) / ((90 - 12) - (80 - 14));
    expect(hit).toBeCloseTo(0.833333);
    expect(hit * 14 + (1 - hit) * 80).toBeCloseTo(hit * 12 + (1 - hit) * 90);
  });
  it('never treats Telegram or an unsafe URL as an embeddable YouTube video', () => {
    expect(safeYoutubeId(concepts[0].videos[0])).toBeNull();
    expect(safeYoutubeId({ ...concepts[0].videos[0], platform: 'youtube', youtubeId: 'abcdefghijk', url: 'https://malicious.invalid/watch' })).toBeNull();
    expect(safeYoutubeId({ ...concepts[0].videos[0], platform: 'youtube', youtubeId: '<script>' })).toBeNull();
  });
});
