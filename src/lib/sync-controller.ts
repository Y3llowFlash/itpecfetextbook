import type { GuestProgressStore } from './progress';
import type { ProgressSyncAdapter } from './models';

export type SyncStatus = 'guest' | 'loading' | 'syncing' | 'saved' | 'pending' | 'offline' | 'error';

/** Coordinates a durable outbox. Stale account responses never reach the active store. */
export class SyncController {
  private generation = 0;
  private uid: string | null = null;
  private running = false;
  private retry = 0;
  private timer?: ReturnType<typeof setTimeout>;
  private unsubscribe?: () => void;
  private queued = false;
  private visible = true;
  constructor(private store: GuestProgressStore, private adapter: ProgressSyncAdapter,
    private status: (status: SyncStatus) => void, private online = () => typeof navigator === 'undefined' || navigator.onLine) {}
  start(uid: string, migrateGuest: boolean) {
    this.stop();
    this.uid = uid;
    this.store.switchAccount(uid, migrateGuest);
    this.unsubscribe = this.store.subscribe(() => {
      if (!this.store.getSnapshot().progress.sync?.pending.length) return;
      if (this.running) { this.queued = true; return; }
      this.status(this.online() ? 'pending' : 'offline');
      this.schedule(2500);
    });
    this.status('loading');
    void this.flush();
  }
  stop() {
    this.generation++; this.uid = null; this.running = false; this.queued = false;
    clearTimeout(this.timer); this.unsubscribe?.(); this.unsubscribe = undefined;
  }
  private schedule(delay: number) {
    clearTimeout(this.timer);
    if (!this.visible) return;
    this.timer = setTimeout(() => { void this.flush(); }, delay);
  }
  async flush() {
    const uid = this.uid, generation = this.generation;
    if (!uid || this.store.getUserId() !== uid) return;
    if (this.running) { this.queued = true; return; }
    clearTimeout(this.timer);
    if (!this.online()) { this.status('offline'); this.schedule(30_000); return; }
    this.running = true; this.queued = false;
    const current = () => this.generation === generation && this.uid === uid && this.store.getUserId() === uid;
    this.status('syncing');
    try {
      const sync = this.store.getSnapshot().progress.sync;
      const remote = await this.adapter.pull(uid, sync?.cursor);
      if (!current()) return;
      this.store.mergeCloud(remote.records, [], remote.cursor);
      // Reading stays local while scrolling. Checkpoint only on a meaningful sync.
      this.store.checkpointReading();
      const local = this.store.getSnapshot().progress.sync!;
      const pending = local.pending.map((key) => local.records[key]);
      if (pending.length) {
        const result = await this.adapter.push(uid, pending);
        if (!current()) return;
        this.store.mergeCloud(result.records, result.records);
      }
      this.retry = 0;
      const remains = !!this.store.getSnapshot().progress.sync?.pending.length;
      this.status(remains ? 'pending' : 'saved');
      // Pull on a one-minute cadence while visible; no live listeners.
      this.schedule(remains ? 2500 : 60_000);
    } catch (error) {
      if (!current()) return;
      const code = (error as { code?: string }).code || '';
      this.status(!this.online() ? 'offline' : 'error');
      // Permission failures need a refreshed account/configuration, not a busy loop.
      this.queued = false;
      if (!code.includes('permission-denied') && !code.includes('unauthenticated')) this.schedule(Math.min(300_000, 5000 * 2 ** this.retry++));
    } finally {
      if (current()) {
        this.running = false;
        if (this.queued && this.store.getSnapshot().progress.sync?.pending.length) this.schedule(2500);
      }
    }
  }
  setVisible(visible: boolean) {
    this.visible = visible;
    if (!visible) clearTimeout(this.timer);
    else if (this.uid) void this.flush();
  }
}
