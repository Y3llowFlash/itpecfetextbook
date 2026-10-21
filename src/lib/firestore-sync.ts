import { collection, doc, documentId, getDocsFromServer, limit, orderBy, query, runTransaction, serverTimestamp, startAfter, startAt, Timestamp, type Firestore, type QueryConstraint, type QueryDocumentSnapshot } from 'firebase/firestore';
import type { ProgressRecord, ProgressSyncAdapter, SyncCursor } from './models';
import { compareRecords, recordId, validCloudRecord } from './sync-data';

/** No snapshot listeners or persistent Firestore cache. Durable offline data lives in our UID-scoped store. */
export class FirestoreProgressAdapter implements ProgressSyncAdapter {
  constructor(private db: Firestore, private activeUid: () => string | null) {}
  private check(uid: string) { if (this.activeUid() !== uid) throw new Error('Account changed during synchronization'); }
  async pull(uid: string, cursor?: SyncCursor) {
    this.check(uid);
    const records: ProgressRecord[] = [];
    let nextCursor = cursor, last: QueryDocumentSnapshot | undefined;
    for (;;) {
      this.check(uid);
      const constraints: QueryConstraint[] = [orderBy('updatedAt'), orderBy(documentId()), limit(200)];
      if (last) constraints.push(startAfter(last));
      else if (cursor) constraints.push(cursor.id
        ? startAfter(new Timestamp(cursor.seconds, cursor.nanoseconds), cursor.id)
        : startAt(new Timestamp(cursor.seconds, cursor.nanoseconds)));
      const page = await getDocsFromServer(query(collection(this.db, 'users', uid, 'progress'), ...constraints));
      this.check(uid);
      for (const document of page.docs) {
        const { updatedAt, ...data } = document.data();
        if (!validCloudRecord(data) || recordId(data) !== document.id || !(updatedAt instanceof Timestamp)) throw new Error('Invalid cloud progress record');
        records.push(data);
        nextCursor = { seconds: updatedAt.seconds, nanoseconds: updatedAt.nanoseconds, id: document.id };
      }
      if (page.size < 200) return { records, cursor: nextCursor };
      last = page.docs.at(-1);
    }
  }
  async push(uid: string, records: ProgressRecord[]) {
    const accepted: ProgressRecord[] = [];
    for (let offset = 0; offset < records.length; offset += 100) {
      this.check(uid);
      const chunk = records.slice(offset, offset + 100);
      const result = await runTransaction(this.db, async (transaction) => {
        this.check(uid);
        const refs = chunk.map((r) => doc(this.db, 'users', uid, 'progress', recordId(r)));
        const snapshots = await Promise.all(refs.map((ref) => transaction.get(ref)));
        this.check(uid);
        return chunk.map((record, i) => {
          const raw = snapshots[i].data();
          if (raw) {
            const { updatedAt: _, ...remote } = raw;
            if (!validCloudRecord(remote)) throw new Error('Invalid cloud progress record');
            // Immutable attempts and newer state win without rewriting existing data.
            if (record.kind === 'attempt' || compareRecords(remote, record) >= 0) return remote;
          }
          transaction.set(refs[i], { ...record, updatedAt: serverTimestamp() });
          return record;
        });
      });
      this.check(uid);
      accepted.push(...result);
    }
    return { records: accepted };
  }
}
