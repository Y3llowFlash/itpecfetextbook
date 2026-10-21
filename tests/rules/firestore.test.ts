// @vitest-environment node
import { readFileSync } from 'node:fs';
import { afterAll, beforeAll, beforeEach, describe, it } from 'vitest';
import { initializeTestEnvironment, assertFails, assertSucceeds, type RulesTestEnvironment } from '@firebase/rules-unit-testing';
import { collection, doc, getDoc, getDocs, serverTimestamp, setDoc, deleteDoc } from 'firebase/firestore';
import { hardwareLessons, lessonPath } from '../../src/lib/lessons';
let env: RulesTestEnvironment;
const google = (uid: string) => env.authenticatedContext(uid, { firebase: { sign_in_provider: 'google.com' } }).firestore();
const record = (clock = 1) => ({ kind: 'bookmark', key: 'question-1', value: true, clock, device: 'device-a', updatedAt: serverTimestamp() });
beforeAll(async () => {
  if (!process.env.FIRESTORE_EMULATOR_HOST?.startsWith('127.0.0.1:')) throw new Error('Rules tests require the local emulator');
  env = await initializeTestEnvironment({ projectId: 'demo-itpec-textbook', firestore: { rules: readFileSync('firestore.rules', 'utf8') } });
});
beforeEach(async () => { await env.clearFirestore(); });
afterAll(async () => { await env?.cleanup(); });
describe('student progress security', () => {
  it('allows verified Chapter 1 reading routes, but denies external, unknown and mismatched routes', async () => {
    const ref = doc(google('alice'), 'users/alice/progress/reading:latest');
    let clock = 1;
    const value = { sectionId: 'fe-v1-ch01-s01', path: '/chapters/hardware/basic-configuration/', blockId: 'history-of-computers', offset: 40, scrollY: 500, updatedAt: new Date().toISOString() };
    const reading = (changes = {}) => ({ kind: 'reading', key: 'latest', clock: clock++, device: 'device-a', updatedAt: serverTimestamp(), value: { ...value, ...changes } });
    for (const lesson of hardwareLessons) await assertSucceeds(setDoc(ref, reading({ sectionId: lesson.id, path: lessonPath(lesson) })));
    await assertFails(setDoc(ref, reading({ path: 'https://malicious.invalid/' })));
    await assertFails(setDoc(ref, reading({ path: '/chapters/hardware/not-a-lesson/' })));
    await assertFails(setDoc(ref, reading({ sectionId: 'fe-v1-ch01-s02' })));
  });
  it('denies all unauthenticated reads, queries and writes', async () => {
    const db = env.unauthenticatedContext().firestore();
    await assertFails(getDoc(doc(db, 'users/alice/progress/bookmark:question-1')));
    await assertFails(getDocs(collection(db, 'users/alice/progress')));
    await assertFails(setDoc(doc(db, 'users/alice/progress/bookmark:question-1'), record()));
  });
  it('denies anonymous accounts even for their own UID', async () => {
    const db = env.authenticatedContext('alice', { firebase: { sign_in_provider: 'anonymous' } }).firestore();
    await assertFails(getDoc(doc(db, 'users/alice/progress/bookmark:question-1')));
    await assertFails(setDoc(doc(db, 'users/alice/progress/bookmark:question-1'), record()));
  });
  it('allows the Google owner to create, read, query, update and delete their own record', async () => {
    const db = google('alice'), ref = doc(db, 'users/alice/progress/bookmark:question-1');
    await assertSucceeds(setDoc(ref, record())); await assertSucceeds(getDoc(ref));
    await assertSucceeds(getDocs(collection(db, 'users/alice/progress')));
    await assertSucceeds(setDoc(ref, { ...record(2), value: false }));
    await assertSucceeds(deleteDoc(ref));
  });
  it('denies another account reads, queries, overwrites and deletes', async () => {
    await setDoc(doc(google('alice'), 'users/alice/progress/bookmark:question-1'), record());
    const db = google('bob'), ref = doc(db, 'users/alice/progress/bookmark:question-1');
    await assertFails(getDoc(ref)); await assertFails(getDocs(collection(db, 'users/alice/progress')));
    await assertFails(setDoc(ref, record(2))); await assertFails(deleteDoc(ref));
  });
  it('denies unexpected collections, nested documents and parent profiles', async () => {
    const db = google('alice');
    for (const path of ['users/alice', 'public/example', 'users/alice/progress/example/nested/doc']) {
      await assertFails(setDoc(doc(db, path), record())); await assertFails(getDoc(doc(db, path)));
    }
  });
  it('rejects malformed data, extra fields, client timestamps and stale updates', async () => {
    const ref = doc(google('alice'), 'users/alice/progress/bookmark:question-1');
    await assertFails(setDoc(ref, { ...record(), value: 'yes' }));
    await assertFails(setDoc(ref, { ...record(), privateData: 'unexpected' }));
    await assertFails(setDoc(ref, { ...record(), updatedAt: new Date() }));
    await assertSucceeds(setDoc(ref, record(5))); await assertFails(setDoc(ref, record(4)));
  });
  it('allows valid attempts once and prevents history from being overwritten', async () => {
    const ref = doc(google('alice'), 'users/alice/progress/attempt:try-1');
    const attempt = { kind: 'attempt', key: 'try-1', value: { id: 'try-1', questionId: 'q-1', conceptId: 'cache-memory', selected: 'b', correct: true, at: new Date().toISOString(), revision: '1' }, clock: 1, device: 'device-a', updatedAt: serverTimestamp() };
    await assertSucceeds(setDoc(ref, attempt));
    await assertFails(setDoc(ref, { ...attempt, value: { ...attempt.value, correct: false } }));
  });
});
