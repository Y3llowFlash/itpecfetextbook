import type { GuestProgress, ProgressRecord, ReadingPosition, SyncMetadata } from './models';
import { lessonForPath } from './lessons';

export const recordId = (record: ProgressRecord) => `${record.kind}:${record.key}`;
export const compareRecords = (a: ProgressRecord, b: ProgressRecord) => a.clock - b.clock || (a.device < b.device ? -1 : a.device > b.device ? 1 : 0);
const id = (v: unknown): v is string => typeof v === 'string' && /^[a-zA-Z0-9:_-]{1,160}$/.test(v);
export function validCloudRecord(value: unknown): value is ProgressRecord {
  const r = value as ProgressRecord;
  if (!r || !id(r.key) || !id(r.device) || !Number.isSafeInteger(r.clock) || r.clock < 0) return false;
  if (r.kind === 'bookmark' || r.kind === 'completion') return typeof r.value === 'boolean';
  if (r.kind === 'attempt') {
    const a = r.value;
    return !!a && a.id === r.key && id(a.id) && id(a.questionId) && id(a.conceptId)
      && /^[a-z]$/.test(a.selected) && typeof a.correct === 'boolean' && typeof a.at === 'string'
      && a.at.length <= 40 && Number.isFinite(Date.parse(a.at)) && typeof a.revision === 'string' && a.revision.length <= 160;
  }
  if (r.kind === 'reading') {
    const p = r.value;
    return r.key === 'latest' && !!p && id(p.sectionId) && id(p.blockId)
      && lessonForPath(p.path)?.id === p.sectionId && Number.isFinite(p.offset) && Math.abs(p.offset) < 100000
      && Number.isFinite(p.scrollY) && p.scrollY >= 0 && typeof p.updatedAt === 'string'
      && p.updatedAt.length <= 40 && (!p.focusId || id(p.focusId));
  }
  return false;
}

export function seedSync(p: GuestProgress): SyncMetadata {
  if (p.sync) return p.sync;
  const records: Record<string, ProgressRecord> = {};
  const put = (r: ProgressRecord) => { records[recordId(r)] = r; };
  for (const a of p.attempts) put({ kind: 'attempt', key: a.id, value: a, clock: Math.max(0, Date.parse(a.at) || 0), device: p.guestId });
  // Legacy lists have no modification dates. Existing cloud changes take priority.
  for (const key of p.bookmarks) put({ kind: 'bookmark', key, value: true, clock: 0, device: p.guestId });
  for (const key of p.completedSections) put({ kind: 'completion', key, value: true, clock: 0, device: p.guestId });
  return { device: p.guestId, clock: 0, records, pending: Object.keys(records) };
}

export function trackChanges(before: GuestProgress, after: GuestProgress): GuestProgress {
  const original = seedSync(before);
  const sync: SyncMetadata = { ...original, records: { ...original.records }, pending: [...original.pending] };
  const put = (record: ProgressRecord) => {
    const key = recordId(record); sync.records[key] = record;
    if (!sync.pending.includes(key)) sync.pending.push(key);
  };
  const stamp = () => ({ clock: sync.clock = Math.max(Date.now(), sync.clock + 1), device: sync.device });
  const known = new Set(before.attempts.map((a) => a.id));
  for (const attempt of after.attempts) if (!known.has(attempt.id)) put({ kind: 'attempt', key: attempt.id, value: attempt, ...stamp() });
  for (const [kind, oldList, newList] of [
    ['bookmark', before.bookmarks, after.bookmarks], ['completion', before.completedSections, after.completedSections],
  ] as const) {
    const oldSet = new Set(oldList), newSet = new Set(newList);
    for (const key of new Set([...oldSet, ...newSet])) if (oldSet.has(key) !== newSet.has(key)) put({ kind, key, value: newSet.has(key), ...stamp() });
  }
  return { ...after, sync };
}

export function checkpointReading(p: GuestProgress): GuestProgress {
  const sync = seedSync(p), previous = sync.records['reading:latest'];
  if (!p.reading || JSON.stringify(previous?.value) === JSON.stringify(p.reading)) return p;
  const clock = Math.max(Date.now(), sync.clock + 1);
  // Strip optional undefined fields before serializing to Firestore.
  const value = JSON.parse(JSON.stringify(p.reading)) as ReadingPosition;
  const record: ProgressRecord = { kind: 'reading', key: 'latest', value, clock, device: sync.device };
  return { ...p, sync: { ...sync, clock, records: { ...sync.records, 'reading:latest': record }, pending: [...new Set([...sync.pending, 'reading:latest'])] } };
}

/** Attempts form a union. Boolean removals remain as tombstones; ties use device ID. */
export function mergeRecords(p: GuestProgress, incoming: ProgressRecord[], acknowledged: ProgressRecord[] = []): GuestProgress {
  const original = seedSync(p), records = { ...original.records };
  let clock = original.clock;
  for (const r of incoming) {
    if (!validCloudRecord(r)) throw new Error('Invalid cloud progress');
    const key = recordId(r), existing = records[key];
    clock = Math.max(clock, r.clock);
    // The cloud's immutable attempt wins a collision, without duplicating its ID.
    if (!existing || (r.kind === 'attempt' && acknowledged.some((a) => recordId(a) === key)) || compareRecords(r, existing) > 0) records[key] = r;
  }
  const pending = original.pending.filter((key) => !acknowledged.some((r) => recordId(r) === key && compareRecords(r, records[key]) >= 0));
  const attempts = Object.values(records).filter((r): r is Extract<ProgressRecord, { kind: 'attempt' }> => r.kind === 'attempt')
    .map((r) => r.value).sort((a, b) => a.at.localeCompare(b.at) || a.id.localeCompare(b.id));
  const list = (kind: 'bookmark' | 'completion') => Object.values(records).filter((r) => r.kind === kind && r.value === true).map((r) => r.key).sort();
  const practice = { ...p.practice };
  const existingAttempts = new Set(p.attempts.map((a) => a.id));
  for (const a of attempts) {
    if (existingAttempts.has(a.id)) continue;
    const session = practice[a.conceptId];
    const previous = attempts.find((attempt) => attempt.id === session?.answers[a.questionId]?.attemptId);
    if (previous && (previous.at > a.at || (previous.at === a.at && previous.id > a.id))) continue;
    practice[a.conceptId] = { questionId: session?.questionId || a.questionId, answers: { ...session?.answers, [a.questionId]: { selected: a.selected, attemptId: a.id } } };
  }
  const reading = records['reading:latest'];
  return { ...p, attempts, bookmarks: list('bookmark'), completedSections: list('completion'), practice,
    reading: reading?.kind === 'reading' && (!p.reading || reading.value.updatedAt > p.reading.updatedAt) ? reading.value : p.reading,
    sync: { ...original, clock, records, pending } };
}

export function migrateProgress(account: GuestProgress, guest: GuestProgress): GuestProgress {
  const guestSync = seedSync(guest);
  const records = Object.values(guestSync.records);
  const merged = mergeRecords(account, records);
  const sync = merged.sync!;
  // Migration is durable locally before any network request; deterministic IDs permit retry.
  return { ...merged, reading: !merged.reading || (guest.reading && guest.reading.updatedAt > merged.reading.updatedAt) ? guest.reading : merged.reading,
    sync: { ...sync, pending: [...new Set([...sync.pending, ...records.filter((r) => compareRecords(sync.records[recordId(r)], r) === 0).map(recordId)])] } };
}
