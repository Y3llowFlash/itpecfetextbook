// @vitest-environment node
import { readFileSync } from 'node:fs';
import { afterAll, beforeAll, beforeEach, describe, expect, it } from 'vitest';
import { initializeTestEnvironment, type RulesTestEnvironment } from '@firebase/rules-unit-testing';
import { initializeApp, deleteApp, type FirebaseApp } from 'firebase/app';
import { connectAuthEmulator, getAuth, GoogleAuthProvider, signInWithCredential } from 'firebase/auth';
import { connectFirestoreEmulator, getFirestore } from 'firebase/firestore';
import { FirestoreProgressAdapter } from '../../src/lib/firestore-sync';
import { GuestProgressStore } from '../../src/lib/progress';
import type { ProgressRecord } from '../../src/lib/models';

let env: RulesTestEnvironment;
const apps: FirebaseApp[] = [];
beforeAll(async () => {
  if (process.env.FIRESTORE_EMULATOR_HOST !== '127.0.0.1:18080' || process.env.FIREBASE_AUTH_EMULATOR_HOST !== '127.0.0.1:19099') throw new Error('Local emulators are required');
  env = await initializeTestEnvironment({ projectId: 'demo-itpec-textbook', firestore: { rules: readFileSync('firestore.rules', 'utf8') } });
});
beforeEach(async () => { await env.clearFirestore(); });
afterAll(async () => { await Promise.all(apps.map((app) => deleteApp(app))); await env?.cleanup(); });
async function device(subject: string) {
  const app = initializeApp({ projectId: 'demo-itpec-textbook', apiKey: 'fake-emulator-key', authDomain: 'localhost' }, `test-${apps.length}`);
  apps.push(app);
  const auth = getAuth(app);
  connectAuthEmulator(auth, 'http://127.0.0.1:19099', { disableWarnings: true });
  const encode = (value: unknown) => Buffer.from(JSON.stringify(value)).toString('base64url');
  const token = `${encode({ alg: 'none', typ: 'JWT' })}.${encode({ sub: subject, iss: 'https://accounts.google.com', aud: 'demo-itpec-textbook', email: `${subject}@example.test`, email_verified: true })}.`;
  const result = await signInWithCredential(auth, GoogleAuthProvider.credential(token));
  const db = getFirestore(app); connectFirestoreEmulator(db, '127.0.0.1', 18080);
  const map = new Map<string, string>();
  const store = new GuestProgressStore(() => ({ getItem: (key) => map.get(key) ?? null, setItem: (key, value) => { map.set(key, value); } }));
  store.switchAccount(result.user.uid);
  return { store, uid: result.user.uid, auth, adapter: new FirestoreProgressAdapter(db, () => auth.currentUser?.uid || null) };
}
async function sync(d: Awaited<ReturnType<typeof device>>) {
  const pulled = await d.adapter.pull(d.uid, d.store.getSnapshot().progress.sync?.cursor);
  d.store.mergeCloud(pulled.records, [], pulled.cursor);
  const local = d.store.getSnapshot().progress.sync!;
  const pushed = await d.adapter.push(d.uid, local.pending.map((key) => local.records[key]));
  d.store.mergeCloud(pushed.records, pushed.records);
}
describe('real Auth and Firestore emulator integration', () => {
  it('accepts a simulated Google credential and merges two devices without duplicating history', async () => {
    const a = await device('two-devices'), b = await device('two-devices');
    expect(a.uid).toBe(b.uid);
    expect((await a.auth.currentUser!.getIdTokenResult()).signInProvider).toBe('google.com');
    a.store.recordAttempt({ id: 'try-a', questionId: 'q1', conceptId: 'cache-memory', selected: 'a', correct: false, at: '2026-10-21T10:00:00Z', revision: '1' });
    b.store.recordAttempt({ id: 'try-b', questionId: 'q2', conceptId: 'cache-memory', selected: 'b', correct: true, at: '2026-10-21T11:00:00Z', revision: '1' });
    a.store.toggleBookmark('q1'); b.store.setCompleted('section1', true);
    await Promise.all([sync(a), sync(b)]); await sync(a); await sync(b);
    for (const d of [a, b]) {
      expect(d.store.getSnapshot().progress.attempts.map((r) => r.id)).toEqual(['try-a', 'try-b']);
      expect(d.store.getSnapshot().progress.bookmarks).toEqual(['q1']);
      expect(d.store.getSnapshot().progress.completedSections).toEqual(['section1']);
    }
    const original = a.store.getSnapshot().progress.sync!.records['attempt:try-a'];
    await a.adapter.push(a.uid, [original]); await a.adapter.push(a.uid, [original]);
    expect((await a.adapter.pull(a.uid)).records.filter((r) => r.kind === 'attempt')).toHaveLength(2);
    b.store.toggleBookmark('q1'); b.store.setCompleted('section1', false); await sync(b); await sync(a);
    expect(a.store.getSnapshot().progress.bookmarks).toEqual([]);
    expect(a.store.getSnapshot().progress.completedSections).toEqual([]);
  });
  it('uses pagination and an incremental server timestamp cursor', async () => {
    const d = await device('pagination');
    const records: ProgressRecord[] = Array.from({ length: 205 }, (_, i) => ({ kind: 'bookmark', key: `q${i}`, value: true, clock: i, device: 'test-device' }));
    await d.adapter.push(d.uid, records);
    const first = await d.adapter.pull(d.uid);
    expect(first.records).toHaveLength(205); expect(first.cursor).toBeDefined();
    expect((await d.adapter.pull(d.uid, first.cursor)).records).toEqual([]);
    await d.adapter.push(d.uid, [{ kind: 'completion', key: 'new-section', value: true, clock: 999, device: 'test-device' }]);
    const next = await d.adapter.pull(d.uid, first.cursor);
    expect(next.records.some((r) => r.key === 'new-section')).toBe(true);
    expect(next.records.length).toBeLessThan(205);
  });
  it('refuses to run an old account request after the active UID changes', async () => {
    const a = await device('account-a'), b = await device('account-b');
    await expect(a.adapter.pull(b.uid)).rejects.toThrow('Account changed');
    await expect(a.adapter.push(b.uid, [{ kind: 'bookmark', key: 'q1', value: true, clock: 1, device: 'a' }])).rejects.toThrow('Account changed');
  });
  it('synchronizes a new lesson reading checkpoint, completion and a non-cache bookmark', async () => {
    const a = await device('chapter-reading'), b = await device('chapter-reading');
    const position = { sectionId: 'fe-v1-ch01-s02', path: '/chapters/hardware/data-representation/', blockId: 'radix-weights', offset: 71, scrollY: 1200, focusId: 'concept-radix-conversion', updatedAt: new Date().toISOString() };
    a.store.saveReading(position); a.store.checkpointReading(); a.store.setCompleted('fe-v1-ch01-s02', true); a.store.toggleBookmark('2024S-A-Q001');
    await sync(a); await sync(b);
    expect(b.store.getSnapshot().progress.reading).toEqual(position);
    expect(b.store.getSnapshot().progress.completedSections).toEqual(['fe-v1-ch01-s02']);
    expect(b.store.getSnapshot().progress.bookmarks).toEqual(['2024S-A-Q001']);
  });
});
