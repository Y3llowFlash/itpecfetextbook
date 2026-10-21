export interface Question {
  id: string;
  examId: string;
  number: number;
  year: number | null;
  season: string;
  subject: 'A' | 'B';
  paper: string;
  format: string;
  sourceKind: 'past_paper' | 'sample';
  examLabel: string;
  correctAnswer: string;
  options: string[];
  is_published: true;
  chapter: string;
  section: string;
  topic: string;
  mapping: Record<string, unknown>;
  image: { src: string; width: number; height: number; sha256: string };
  source: { dataset: string; questionPdf: string; pageStart: number; pageEnd: number; originalImagePath: string; documentPath: string };
}

export interface Explanation {
  questionId: string;
  revision: string;
  answer: string;
  summary: string;
  steps: string[];
  takeaway: string;
  optionText: Record<string, string>;
  imageDescription: string;
  reviewedAgainst: string[];
}

export interface VideoLesson {
  id: string;
  title: string;
  platform: 'youtube' | 'telegram' | 'external';
  url: string;
  youtubeId?: string;
  conceptIds: string[];
  questionIds: string[];
  source: string;
}

export interface Concept {
  id: string;
  title: string;
  sectionId: string;
  sectionUrl: string;
  summary: string;
  questionIds: string[];
  mappingEvidence: { questionId: string; reason: string; reviewedAgainst: string[] }[];
  videos: VideoLesson[];
}

export interface ReadingPosition {
  sectionId: string;
  path: string;
  blockId: string;
  offset: number;
  scrollY: number;
  focusId?: string;
  updatedAt: string;
}

export interface Attempt {
  id: string;
  questionId: string;
  conceptId: string;
  selected: string;
  correct: boolean;
  at: string;
  revision: string;
}

export interface GuestProgress {
  version: 1;
  guestId: string;
  attempts: Attempt[];
  bookmarks: string[];
  completedSections: string[];
  reading: ReadingPosition | null;
  practice: Record<string, { questionId: string; answers: Record<string, { selected: string; attemptId: string }> }>;
  dismissedAccountPrompt: boolean;
  sync?: SyncMetadata;
  /** Interrupted transfers remain recoverable only by their intended account. */
  migrationOwner?: string;
}

export type ProgressRecord = {
  kind: 'attempt'; key: string; value: Attempt; clock: number; device: string;
} | {
  kind: 'bookmark' | 'completion'; key: string; value: boolean; clock: number; device: string;
} | {
  kind: 'reading'; key: 'latest'; value: ReadingPosition; clock: number; device: string;
};
export interface SyncCursor { seconds: number; nanoseconds: number; id?: string }
export interface SyncMetadata {
  device: string;
  clock: number;
  records: Record<string, ProgressRecord>;
  pending: string[];
  cursor?: SyncCursor;
}

/** Incremental, idempotent progress transport; implementations must check the active UID. */
export interface ProgressSyncAdapter {
  pull(userId: string, cursor?: SyncCursor): Promise<{ records: ProgressRecord[]; cursor?: SyncCursor }>;
  push(userId: string, records: ProgressRecord[]): Promise<{ records: ProgressRecord[] }>;
}
