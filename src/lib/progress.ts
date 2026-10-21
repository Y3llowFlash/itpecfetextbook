import type { Attempt, GuestProgress, ReadingPosition } from './models';
import { checkpointReading, mergeRecords, migrateProgress, seedSync, trackChanges, validCloudRecord } from './sync-data';
import { lessonForPath } from './lessons';

export const STORAGE_KEY = 'itpecTextbook:guest:v1';
const validId = (value: unknown): value is string => typeof value === 'string' && /^[a-zA-Z0-9:_-]{1,160}$/.test(value);
export const newId = () => globalThis.crypto?.randomUUID?.() || `local-${Date.now()}-${Math.random().toString(36).slice(2)}`;
export const emptyProgress = (): GuestProgress => ({ version: 1, guestId: '', attempts: [], bookmarks: [], completedSections: [], reading: null, practice: {}, dismissedAccountPrompt: false });

export function validReading(value: unknown): value is ReadingPosition {
  const p = value as ReadingPosition;
  return Boolean(p && validId(p.sectionId) && validId(p.blockId) && lessonForPath(p.path)?.id === p.sectionId &&
    Number.isFinite(p.offset) && Math.abs(p.offset) < 100000 && Number.isFinite(p.scrollY) && p.scrollY >= 0 &&
    typeof p.updatedAt === 'string' && (!p.focusId || validId(p.focusId)));
}

export function parseProgress(raw: string): GuestProgress {
  const p = JSON.parse(raw) as GuestProgress;
  if (!p || p.version !== 1 || !validId(p.guestId) || !Array.isArray(p.attempts) || !Array.isArray(p.bookmarks) ||
    !Array.isArray(p.completedSections) || !p.practice || typeof p.practice !== 'object' || Array.isArray(p.practice)) throw new Error('Invalid guest progress');
  if (!p.bookmarks.every(validId) || !p.completedSections.every(validId) || (p.reading && !validReading(p.reading))) throw new Error('Invalid guest records');
  if (p.migrationOwner && !validId(p.migrationOwner)) throw new Error('Invalid migration owner');
  for (const a of p.attempts) {
    if (!a || !validId(a.id) || !validId(a.questionId) || !validId(a.conceptId) || !/^[a-z]$/.test(a.selected) || typeof a.correct !== 'boolean' || typeof a.at !== 'string') throw new Error('Invalid attempt');
  }
  for (const [key, session] of Object.entries(p.practice)) {
    if (!validId(key) || !session || !validId(session.questionId) || !session.answers || typeof session.answers !== 'object') throw new Error('Invalid practice session');
    for (const [questionId, answer] of Object.entries(session.answers)) {
      if (!validId(questionId) || !answer || !/^[a-z]$/.test(answer.selected) || !validId(answer.attemptId)) throw new Error('Invalid practice answer');
    }
  }
  if (p.sync && (!validId(p.sync.device) || !Number.isSafeInteger(p.sync.clock) || p.sync.clock < 0
    || !p.sync.records || !Array.isArray(p.sync.pending)
    || !Object.entries(p.sync.records).every(([key, record]) => validCloudRecord(record) && key === `${record.kind}:${record.key}`)
    || !p.sync.pending.every((key) => typeof key === 'string' && Object.hasOwn(p.sync!.records, key))
    || (p.sync.cursor && (!Number.isInteger(p.sync.cursor.seconds) || !Number.isInteger(p.sync.cursor.nanoseconds)
      || p.sync.cursor.nanoseconds < 0 || p.sync.cursor.nanoseconds >= 1e9
      || (p.sync.cursor.id !== undefined && !/^[a-zA-Z0-9:_-]{1,180}$/.test(p.sync.cursor.id)))))) throw new Error('Invalid sync metadata');
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
  private storageKey = STORAGE_KEY;
  private userId: string | null = null;
  private snapshot: ProgressSnapshot = { progress: emptyProgress(), persistence: 'saved' };
  private readonly serverSnapshot = this.snapshot;
  constructor(private storageProvider: () => StorageLike = () => window.localStorage) {}
  private load() {
    if (this.initialized) return;
    this.initialized = true;
    const progress = { ...emptyProgress(), guestId: newId() };
    try {
      this.storage = this.storageProvider();
      const raw = this.storage.getItem(this.storageKey);
      const saved = raw ? parseProgress(raw) : progress;
      if (!this.userId && saved.migrationOwner) {
        // An interrupted transfer must never appear in a new guest/account view.
        this.snapshot = { progress, persistence: 'unavailable' }; this.storage = undefined;
      } else this.snapshot = { progress: saved, persistence: 'saved' };
    } catch (error) {
      this.snapshot = { progress, persistence: this.storage ? 'corrupt' : 'unavailable' };
      // Preserve corrupt data for recovery; never overwrite it silently.
      this.storage = undefined;
    }
  }
  getSnapshot = () => { this.load(); return this.snapshot; };
  getServerSnapshot = () => this.serverSnapshot;
  subscribe = (listener: () => void) => { this.listeners.add(listener); return () => this.listeners.delete(listener); };
  private update(mutator: (progress: GuestProgress) => GuestProgress, track = true) {
    this.load();
    // Merge concurrent tab changes before applying a local mutation.
    if (this.userId && this.storage) {
      try {
        const raw = this.storage.getItem(this.storageKey);
        if (raw) {
          const other = parseProgress(raw), own = this.snapshot.progress;
          const otherSync = seedSync(other);
          const merged = mergeRecords(own, Object.values(otherSync.records));
          this.snapshot = { ...this.snapshot, progress: { ...merged, sync: { ...merged.sync!,
            pending: [...new Set([...merged.sync!.pending, ...otherSync.pending])], cursor: own.sync?.cursor } } };
        }
      } catch { /* Never replace usable in-memory progress with damaged data. */ }
    }
    const next = mutator(this.snapshot.progress);
    const progress = track ? trackChanges(this.snapshot.progress, next) : next;
    let persistence = this.snapshot.persistence;
    if (this.storage) {
      try { this.storage.setItem(this.storageKey, JSON.stringify(progress)); persistence = 'saved'; }
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
  getUserId = () => this.userId;
  getStorageKey = () => this.storageKey;
  clearSyncedAccountCache() {
    if (!this.userId || this.getSnapshot().progress.sync?.pending.length) return;
    try {
      const raw = this.storage?.getItem(this.storageKey);
      if (raw && parseProgress(raw).sync?.pending.length) return;
      this.storage?.setItem(this.storageKey, JSON.stringify({ ...emptyProgress(), guestId: newId() }));
    } catch { /* The active view is still cleared; a UID-scoped cache is never shown to a different user. */ }
  }
  /** Switch the active view before loading any other identity's progress. */
  switchAccount(userId: string | null, migrateGuest = false) {
    if (userId !== null && !validId(userId)) throw new Error('Invalid account ID');
    let previousGuest = !this.userId && userId && migrateGuest ? this.getSnapshot().progress : null;
    let transferFailed = false;
    if (previousGuest && userId) {
      // Claim the source in one atomic localStorage write before uploading it.
      // If a later write fails, another account cannot inherit this history.
      let source: StorageLike | undefined;
      try { source = this.storageProvider(); }
      catch { previousGuest = null; transferFailed = true; }
      if (source && previousGuest) {
        try {
          const raw = source.getItem(STORAGE_KEY);
          const stored = raw ? parseProgress(raw) : previousGuest;
          if (stored.migrationOwner && stored.migrationOwner !== userId) previousGuest = null;
          else {
            previousGuest = stored.migrationOwner ? stored : previousGuest;
            source.setItem(STORAGE_KEY, JSON.stringify({ ...previousGuest, migrationOwner: userId }));
          }
        } catch { previousGuest = null; transferFailed = true; }
      }
    }
    this.userId = userId;
    this.storageKey = userId ? `itpecTextbook:account:${userId}:v1` : STORAGE_KEY;
    this.storage = undefined;
    this.initialized = false;
    this.snapshot = { progress: emptyProgress(), persistence: 'saved' };
    this.load();
    if (userId) {
      this.update((p) => previousGuest ? migrateProgress(p, previousGuest) : { ...p, sync: seedSync(p) }, false);
      // Transfer, rather than copy, the guest history. A later account must not inherit it.
      const activeStorage = this.storage as StorageLike | undefined;
      if (previousGuest && this.snapshot.persistence === 'saved' && activeStorage) {
        try { activeStorage.setItem(STORAGE_KEY, JSON.stringify({ ...emptyProgress(), guestId: newId() })); }
        catch { this.snapshot = { ...this.snapshot, persistence: 'unavailable' }; }
      }
      if (transferFailed) this.snapshot = { ...this.snapshot, persistence: 'unavailable' };
    }
    if (typeof window !== 'undefined') {
      try { window.sessionStorage.removeItem('itpecTextbook:return:v1'); } catch { /* no account pointer remains in memory */ }
    }
    this.listeners.forEach((listener) => listener());
  }
  mergeCloud(records: import('./models').ProgressRecord[], acknowledged: import('./models').ProgressRecord[] = [], cursor?: import('./models').SyncCursor) {
    this.update((p) => {
      const merged = mergeRecords(p, records, acknowledged);
      return { ...merged, sync: { ...merged.sync!, cursor: cursor || merged.sync?.cursor } };
    }, false);
  }
  checkpointReading() { this.update(checkpointReading, false); }
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
if (typeof window !== 'undefined') window.addEventListener('storage', (event) => { if (event.key === guestStore.getStorageKey()) guestStore.refresh(); });

export function learningStats(progress: GuestProgress) {
  const latest = new Map<string, Attempt>();
  for (const attempt of progress.attempts) latest.set(attempt.questionId, attempt);
  return { attempts: progress.attempts.length, correctAttempts: progress.attempts.filter((a) => a.correct).length,
    questions: latest.size, correct: [...latest.values()].filter((a) => a.correct).length,
    incorrect: [...latest.values()].filter((a) => !a.correct).length, completedSections: progress.completedSections.length, bookmarks: progress.bookmarks.length };
}
