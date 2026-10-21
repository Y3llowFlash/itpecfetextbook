import type { Attempt, GuestProgress, ReadingPosition } from './models';

export const STORAGE_KEY = 'itpecTextbook:guest:v1';
const validId = (value: unknown): value is string => typeof value === 'string' && /^[a-zA-Z0-9:_-]{1,160}$/.test(value);
export const newId = () => globalThis.crypto?.randomUUID?.() || `local-${Date.now()}-${Math.random().toString(36).slice(2)}`;
export const emptyProgress = (): GuestProgress => ({ version: 1, guestId: '', attempts: [], bookmarks: [], completedSections: [], reading: null, practice: {}, dismissedAccountPrompt: false });

export function validReading(value: unknown): value is ReadingPosition {
  const p = value as ReadingPosition;
  return Boolean(p && validId(p.sectionId) && validId(p.blockId) && p.path === '/chapters/hardware/memory-and-cache/' &&
    Number.isFinite(p.offset) && Math.abs(p.offset) < 100000 && Number.isFinite(p.scrollY) && p.scrollY >= 0 &&
    typeof p.updatedAt === 'string' && (!p.focusId || validId(p.focusId)));
}

export function parseProgress(raw: string): GuestProgress {
  const p = JSON.parse(raw) as GuestProgress;
  if (!p || p.version !== 1 || !validId(p.guestId) || !Array.isArray(p.attempts) || !Array.isArray(p.bookmarks) ||
    !Array.isArray(p.completedSections) || !p.practice || typeof p.practice !== 'object' || Array.isArray(p.practice)) throw new Error('Invalid guest progress');
  if (!p.bookmarks.every(validId) || !p.completedSections.every(validId) || (p.reading && !validReading(p.reading))) throw new Error('Invalid guest records');
  for (const a of p.attempts) {
    if (!a || !validId(a.id) || !validId(a.questionId) || !validId(a.conceptId) || !/^[a-z]$/.test(a.selected) || typeof a.correct !== 'boolean' || typeof a.at !== 'string') throw new Error('Invalid attempt');
  }
  for (const [key, session] of Object.entries(p.practice)) {
    if (!validId(key) || !session || !validId(session.questionId) || !session.answers || typeof session.answers !== 'object') throw new Error('Invalid practice session');
    for (const [questionId, answer] of Object.entries(session.answers)) {
      if (!validId(questionId) || !answer || !/^[a-z]$/.test(answer.selected) || !validId(answer.attemptId)) throw new Error('Invalid practice answer');
    }
  }
  return { ...p, bookmarks: [...new Set(p.bookmarks)], completedSections: [...new Set(p.completedSections)] };
}

export type Persistence = 'saved' | 'unavailable' | 'corrupt';
export interface ProgressSnapshot { progress: GuestProgress; persistence: Persistence }
type StorageLike = Pick<Storage, 'getItem' | 'setItem'>;

/** Browser-local repository. It has no auth, network requests or cloud side effects. */
export class GuestProgressStore {
  private listeners = new Set<() => void>();
  private initialized = false;
  private storage: StorageLike | undefined;
  private snapshot: ProgressSnapshot = { progress: emptyProgress(), persistence: 'saved' };
  private readonly serverSnapshot = this.snapshot;
  constructor(private storageProvider: () => StorageLike = () => window.localStorage) {}
  private load() {
    if (this.initialized) return;
    this.initialized = true;
    const progress = { ...emptyProgress(), guestId: newId() };
    try {
      this.storage = this.storageProvider();
      const raw = this.storage.getItem(STORAGE_KEY);
      this.snapshot = { progress: raw ? parseProgress(raw) : progress, persistence: 'saved' };
    } catch (error) {
      this.snapshot = { progress, persistence: this.storage ? 'corrupt' : 'unavailable' };
      // Preserve corrupt data for recovery; never overwrite it silently.
      this.storage = undefined;
    }
  }
  getSnapshot = () => { this.load(); return this.snapshot; };
  getServerSnapshot = () => this.serverSnapshot;
  subscribe = (listener: () => void) => { this.listeners.add(listener); return () => this.listeners.delete(listener); };
  private update(mutator: (progress: GuestProgress) => GuestProgress) {
    this.load();
    const progress = mutator(this.snapshot.progress);
    let persistence = this.snapshot.persistence;
    if (this.storage) {
      try { this.storage.setItem(STORAGE_KEY, JSON.stringify(progress)); persistence = 'saved'; }
      catch { persistence = 'unavailable'; }
    }
    this.snapshot = { progress, persistence };
    this.listeners.forEach((listener) => listener());
  }
  refresh = () => {
    this.initialized = false;
    this.load();
    this.listeners.forEach((listener) => listener());
  };
  saveReading(position: ReadingPosition) {
    if (!validReading(position)) return;
    this.update((p) => ({ ...p, reading: position }));
  }
  setCompleted(sectionId: string, completed: boolean) {
    if (!validId(sectionId)) return;
    this.update((p) => ({ ...p, completedSections: completed ? [...new Set([...p.completedSections, sectionId])] : p.completedSections.filter((id) => id !== sectionId) }));
  }
  toggleBookmark(questionId: string) {
    if (!validId(questionId)) return;
    this.update((p) => ({ ...p, bookmarks: p.bookmarks.includes(questionId) ? p.bookmarks.filter((id) => id !== questionId) : [...p.bookmarks, questionId] }));
  }
  recordAttempt(attempt: Attempt) {
    this.update((p) => {
      if (p.attempts.some((a) => a.id === attempt.id)) return p;
      const previous = p.practice[attempt.conceptId];
      return { ...p, attempts: [...p.attempts, attempt], practice: { ...p.practice, [attempt.conceptId]: {
        questionId: attempt.questionId, answers: { ...previous?.answers, [attempt.questionId]: { selected: attempt.selected, attemptId: attempt.id } },
      } } };
    });
  }
  setCurrentQuestion(conceptId: string, questionId: string) {
    this.update((p) => ({ ...p, practice: { ...p.practice, [conceptId]: { questionId, answers: p.practice[conceptId]?.answers || {} } } }));
  }
  retryQuestion(conceptId: string, questionId: string) {
    this.update((p) => {
      const answers = { ...p.practice[conceptId]?.answers };
      delete answers[questionId];
      return { ...p, practice: { ...p.practice, [conceptId]: { questionId, answers } } };
    });
  }
  dismissAccountPrompt() { this.update((p) => ({ ...p, dismissedAccountPrompt: true })); }
}

export const guestStore = new GuestProgressStore();
if (typeof window !== 'undefined') window.addEventListener('storage', (event) => { if (event.key === STORAGE_KEY) guestStore.refresh(); });

export function learningStats(progress: GuestProgress) {
  const latest = new Map<string, Attempt>();
  for (const attempt of progress.attempts) latest.set(attempt.questionId, attempt);
  return { attempts: progress.attempts.length, correctAttempts: progress.attempts.filter((a) => a.correct).length,
    questions: latest.size, correct: [...latest.values()].filter((a) => a.correct).length,
    incorrect: [...latest.values()].filter((a) => !a.correct).length, completedSections: progress.completedSections.length, bookmarks: progress.bookmarks.length };
}
