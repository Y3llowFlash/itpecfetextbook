import { describe, expect, it } from 'vitest';
import { GuestProgressStore, learningStats, parseProgress, STORAGE_KEY } from '../src/lib/progress';
import { returnUrl } from '../src/lib/reading';
import {CPU_PATH,CACHE_HEADING} from '../src/lib/reading-routes';
import type { Attempt } from '../src/lib/models';

const attempt = (id: string, correct = false): Attempt => ({ id, questionId: '2024A-A-Q009', conceptId: 'cache-memory', selected: correct ? 'b' : 'a', correct, at: '2026-10-21T06:00:00Z', revision: '1' });
const memory = () => { const map = new Map<string, string>(); return { getItem: (key: string) => map.get(key) ?? null, setItem: (key: string, value: string) => { map.set(key, value); } }; };

describe('guest learning progress', () => {
  it('persists a submitted answer across store instances without double-counting its event', () => {
    const storage = memory(), store = new GuestProgressStore(() => storage);
    store.recordAttempt(attempt('attempt-1')); store.recordAttempt(attempt('attempt-1'));
    const reloaded = new GuestProgressStore(() => storage).getSnapshot().progress;
    expect(reloaded.attempts).toHaveLength(1);
    expect(reloaded.practice['cache-memory'].answers['2024A-A-Q009'].selected).toBe('a');
  });
  it('distinguishes historical attempts from the latest correctness per question', () => {
    const store = new GuestProgressStore(memory);
    store.recordAttempt(attempt('attempt-1')); store.recordAttempt(attempt('attempt-2', true));
    expect(learningStats(store.getSnapshot().progress)).toMatchObject({ attempts: 2, questions: 1, correct: 1, incorrect: 0, correctAttempts: 1 });
  });
  it('saves completion, bookmark removal and the current practice question', () => {
    const storage = memory(), store = new GuestProgressStore(() => storage);
    store.setCompleted('fe-v1-ch01-memory-cache', true); store.setCompleted('fe-v1-ch01-memory-cache', true);
    store.toggleBookmark('2024A-A-Q009'); store.toggleBookmark('2024A-A-Q009');
    store.setCurrentQuestion('cache-memory', '2025S-A-Q010');
    const p = new GuestProgressStore(() => storage).getSnapshot().progress;
    expect(p.completedSections).toHaveLength(1); expect(p.bookmarks).toEqual([]); expect(p.practice['cache-memory'].questionId).toBe('2025S-A-Q010');
  });
  it('keeps answering possible when storage access or writes are denied', () => {
    const blocked = new GuestProgressStore(() => { throw new Error('SecurityError'); });
    blocked.recordAttempt(attempt('attempt-1'));
    expect(blocked.getSnapshot().persistence).toBe('unavailable'); expect(blocked.getSnapshot().progress.attempts).toHaveLength(1);
    const quota = new GuestProgressStore(() => ({ getItem: () => null, setItem: () => { throw new Error('QuotaExceededError'); } }));
    quota.recordAttempt(attempt('attempt-2'));
    expect(quota.getSnapshot().persistence).toBe('unavailable'); expect(quota.getSnapshot().progress.attempts).toHaveLength(1);
  });
  it('preserves corrupt or future-version data instead of silently overwriting it', () => {
    const storage = memory(); storage.setItem(STORAGE_KEY, '{"version":99}');
    const store = new GuestProgressStore(() => storage); store.recordAttempt(attempt('attempt-1'));
    expect(store.getSnapshot().persistence).toBe('corrupt'); expect(storage.getItem(STORAGE_KEY)).toBe('{"version":99}');
    expect(() => parseProgress('{"version":99}')).toThrow();
  });
  it('limits reading return to a known same-origin section and retains stable anchors/offsets', () => {
    const store = new GuestProgressStore(memory);
    const position = { sectionId: 'fe-v1-ch01-memory-cache', path: '/chapters/hardware/memory-and-cache/', blockId: 'cache-definition', offset: 124, scrollY: 822, focusId: 'concept-cache-memory', updatedAt: '2026-10-21T06:00:00Z' };
    store.saveReading(position);
    expect(returnUrl(store.getSnapshot().progress.reading)).toBe(`${CPU_PATH}?resume=1#concept-cache-memory`);
    store.saveReading({ ...position, path: 'https://malicious.invalid/' });
    expect(store.getSnapshot().progress.reading).toEqual(position);
    expect(returnUrl({ ...position, path: '//malicious.invalid' })).toBe(`${CPU_PATH}#${CACHE_HEADING}`);
  });
  it('retrying retains history but clears the answer so it can be submitted again', () => {
    const store = new GuestProgressStore(memory); store.recordAttempt(attempt('attempt-1'));
    store.retryQuestion('cache-memory', '2024A-A-Q009');
    expect(store.getSnapshot().progress.practice['cache-memory'].answers['2024A-A-Q009']).toBeUndefined();
    expect(store.getSnapshot().progress.attempts).toHaveLength(1);
  });
});
