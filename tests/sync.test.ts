import { afterEach, describe, expect, it, vi } from 'vitest';
import type { Attempt, ProgressRecord, ProgressSyncAdapter } from '../src/lib/models';
import { GuestProgressStore, STORAGE_KEY } from '../src/lib/progress';
import { mergeRecords, recordId } from '../src/lib/sync-data';
import { SyncController } from '../src/lib/sync-controller';

const attempt = (id: string): Attempt => ({ id, questionId: '2024A-A-Q009', conceptId: 'cache-memory', selected: 'a', correct: false, at: new Date().toISOString(), revision: '1' });
const memory = () => {
  const map = new Map<string, string>();
  return { getItem: (key: string) => map.get(key) ?? null, setItem: (key: string, value: string) => { map.set(key, value); } };
};
const settle = async () => { for (let i = 0; i < 12; i++) await Promise.resolve(); };
afterEach(() => { vi.useRealTimers(); });

describe('account progress isolation and merging', () => {
  it('transfers guest history once, unions account attempts, and preserves bookmarks and completion', () => {
    const storage = memory(), store = new GuestProgressStore(() => storage);
    store.switchAccount('alice'); store.recordAttempt(attempt('cloud-history'));
    store.switchAccount(null); store.recordAttempt(attempt('guest-history'));
    store.toggleBookmark('2024A-A-Q009'); store.setCompleted('fe-v1-ch01-memory-cache', true);
    store.switchAccount('alice', true);
    expect(store.getSnapshot().progress.attempts.map((a) => a.id).sort()).toEqual(['cloud-history', 'guest-history']);
    expect(store.getSnapshot().progress.bookmarks).toEqual(['2024A-A-Q009']);
    expect(store.getSnapshot().progress.completedSections).toEqual(['fe-v1-ch01-memory-cache']);
    store.switchAccount(null);
    expect(store.getSnapshot().progress.attempts).toEqual([]);
    store.switchAccount('bob', true);
    expect(store.getSnapshot().progress.attempts).toEqual([]);
    store.switchAccount('alice');
    expect(store.getSnapshot().progress.attempts).toHaveLength(2);
  });
  it('keeps offline outbox and incremental cursor across reloads for the same UID only', () => {
    const storage = memory(), first = new GuestProgressStore(() => storage);
    first.switchAccount('alice'); first.recordAttempt(attempt('offline-try'));
    first.mergeCloud([], [], { seconds: 10, nanoseconds: 2 });
    const reload = new GuestProgressStore(() => storage); reload.switchAccount('alice');
    expect(reload.getSnapshot().progress.sync?.pending).toContain('attempt:offline-try');
    expect(reload.getSnapshot().progress.sync?.cursor).toEqual({ seconds: 10, nanoseconds: 2 });
    reload.switchAccount('bob');
    expect(reload.getSnapshot().progress.attempts).toHaveLength(0);
    expect(reload.getSnapshot().progress.sync?.cursor).toBeUndefined();
  });
  it('resolves concurrent boolean changes deterministically and retains removals as tombstones', () => {
    const store = new GuestProgressStore(memory); store.switchAccount('alice');
    const add: ProgressRecord = { kind: 'bookmark', key: 'q1', value: true, clock: 10, device: 'a' };
    const remove: ProgressRecord = { ...add, value: false, device: 'b' };
    const first = mergeRecords(store.getSnapshot().progress, [add, remove]);
    const second = mergeRecords(store.getSnapshot().progress, [remove, add]);
    expect(first.bookmarks).toEqual([]); expect(second.bookmarks).toEqual([]);
    expect(first.sync?.records['bookmark:q1']).toEqual(remove);
    expect(mergeRecords(first, [add]).bookmarks).toEqual([]);
  });
  it('does not acknowledge a newer local edit while an older upload is in flight', () => {
    const store = new GuestProgressStore(memory); store.switchAccount('alice');
    store.toggleBookmark('q1');
    const sent = store.getSnapshot().progress.sync!.records['bookmark:q1'];
    store.toggleBookmark('q1');
    store.mergeCloud([sent], [sent]);
    expect(store.getSnapshot().progress.bookmarks).toEqual([]);
    expect(store.getSnapshot().progress.sync!.pending).toContain('bookmark:q1');
  });
  it('merges different tabs without requeueing an acknowledged history on scroll', () => {
    const storage = memory(), first = new GuestProgressStore(() => storage), second = new GuestProgressStore(() => storage);
    first.switchAccount('alice'); first.recordAttempt(attempt('a1'));
    const record = first.getSnapshot().progress.sync!.records['attempt:a1'];
    first.mergeCloud([record], [record]);
    second.switchAccount('alice'); second.toggleBookmark('q1');
    first.setCompleted('section1', true);
    expect(first.getSnapshot().progress.bookmarks).toEqual(['q1']);
    expect(first.getSnapshot().progress.sync!.pending).not.toContain('attempt:a1');
    expect(first.getSnapshot().progress.sync!.pending).toContain('bookmark:q1');
  });
  it('preserves the original guest file when account persistence is unavailable', () => {
    const storage = memory(), store = new GuestProgressStore(() => storage);
    store.recordAttempt(attempt('guest1'));
    const raw = storage.getItem(STORAGE_KEY);
    const original = storage.setItem;
    storage.setItem = (key, value) => { if (key.includes(':account:')) throw new Error('Quota'); original(key, value); };
    store.switchAccount('alice', true);
    expect(store.getSnapshot().persistence).toBe('unavailable');
    expect(JSON.parse(storage.getItem(STORAGE_KEY)!)).toMatchObject({ attempts: JSON.parse(raw!).attempts, migrationOwner: 'alice' });
    store.switchAccount(null);
    expect(store.getSnapshot().progress.attempts).toEqual([]);
    store.switchAccount('bob', true);
    expect(store.getSnapshot().progress.attempts).toEqual([]);
    store.switchAccount(null); store.switchAccount('alice', true);
    expect(store.getSnapshot().progress.attempts).toHaveLength(1);
  });
  it('does not upload unclaimed guest history when browser storage permission changes', () => {
    const storage = memory(); let denied = false;
    const store = new GuestProgressStore(() => { if (denied) throw new Error('Storage denied'); return storage; });
    store.recordAttempt(attempt('private-guest'));
    const source = storage.getItem(STORAGE_KEY);
    denied = true; store.switchAccount('alice', true);
    expect(store.getSnapshot().progress.attempts).toEqual([]);
    expect(store.getSnapshot().persistence).toBe('unavailable');
    expect(storage.getItem(STORAGE_KEY)).toBe(source);
    denied = false; store.switchAccount(null);
    expect(store.getSnapshot().progress.attempts).toHaveLength(1);
  });
});

describe('sync lifecycle and failure handling', () => {
  it('retries a failed upload, keeps local data, and never duplicates an attempt', async () => {
    vi.useFakeTimers();
    const store = new GuestProgressStore(memory); store.recordAttempt(attempt('try1'));
    const cloud = new Map<string, ProgressRecord>();
    let fail = true;
    const adapter: ProgressSyncAdapter = {
      pull: vi.fn(async () => ({ records: [...cloud.values()] })),
      push: vi.fn(async (_, records) => {
        if (fail) { fail = false; throw new Error('Network'); }
        for (const r of records) cloud.set(recordId(r), r);
        return { records };
      }),
    };
    const status = vi.fn(), controller = new SyncController(store, adapter, status);
    controller.start('alice', true); await settle();
    expect(status).toHaveBeenLastCalledWith('error');
    expect(store.getSnapshot().progress.attempts).toHaveLength(1);
    expect(store.getSnapshot().progress.sync!.pending).toHaveLength(1);
    await vi.advanceTimersByTimeAsync(5000); await settle();
    expect(status).toHaveBeenLastCalledWith('saved');
    expect(cloud.size).toBe(1); expect(store.getSnapshot().progress.sync!.pending).toEqual([]);
    await controller.flush();
    expect(adapter.push).toHaveBeenCalledTimes(2);
    expect(cloud.size).toBe(1); controller.stop();
  });
  it('does not call Firestore while offline and resumes when online', async () => {
    vi.useFakeTimers();
    const store = new GuestProgressStore(memory); store.recordAttempt(attempt('offline'));
    let online = false;
    const adapter: ProgressSyncAdapter = { pull: vi.fn(async () => ({ records: [] })), push: vi.fn(async (_, records) => ({ records })) };
    const status = vi.fn(), controller = new SyncController(store, adapter, status, () => online);
    controller.start('alice', true); await settle();
    expect(adapter.pull).not.toHaveBeenCalled(); expect(status).toHaveBeenLastCalledWith('offline');
    online = true; await controller.flush();
    expect(adapter.push).toHaveBeenCalledOnce(); expect(status).toHaveBeenLastCalledWith('saved');
    controller.stop();
  });
  it('discards a response for the previous account after switching identities', async () => {
    vi.useFakeTimers();
    const store = new GuestProgressStore(memory);
    let finish!: (result: { records: ProgressRecord[] }) => void;
    const adapter: ProgressSyncAdapter = { pull: () => new Promise((resolve) => { finish = resolve; }), push: vi.fn(async (_, records) => ({ records })) };
    const controller = new SyncController(store, adapter, vi.fn());
    controller.start('alice', false); await settle();
    controller.stop(); store.switchAccount('bob');
    finish({ records: [{ kind: 'attempt', key: 'alice-try', value: attempt('alice-try'), clock: 1, device: 'a' }] });
    await settle();
    expect(store.getSnapshot().progress.attempts).toEqual([]);
    expect(adapter.push).not.toHaveBeenCalled(); controller.stop();
  });
  it('coalesces rapid meaningful changes and pauses polling while hidden', async () => {
    vi.useFakeTimers();
    const store = new GuestProgressStore(memory);
    const adapter: ProgressSyncAdapter = { pull: vi.fn(async () => ({ records: [] })), push: vi.fn(async (_, records) => ({ records })) };
    const controller = new SyncController(store, adapter, vi.fn());
    controller.start('alice', false); await settle();
    store.toggleBookmark('q1'); store.setCompleted('s1', true); store.recordAttempt(attempt('try1'));
    await vi.advanceTimersByTimeAsync(2500);
    expect(adapter.push).toHaveBeenCalledOnce();
    controller.setVisible(false);
    const pulls = vi.mocked(adapter.pull).mock.calls.length;
    await vi.advanceTimersByTimeAsync(180000);
    expect(adapter.pull).toHaveBeenCalledTimes(pulls); controller.stop();
  });
});
