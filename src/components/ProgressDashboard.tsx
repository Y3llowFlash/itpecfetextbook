import { learningStats, guestStore } from '../lib/progress';
import { useProgress } from '../lib/use-progress';
import { returnUrl } from '../lib/reading';
import type { Question } from '../lib/models';
import GuestNotice, { StorageNotice } from './GuestNotice';
import AccountControls, { useAccount } from './AccountControls';
import { hardwareLessons, lessonForPath, lessonPath } from '../lib/lessons';
import definitions from '../content/concepts.json';
import {contents,completionId,contentsUrl} from '../lib/toc';
import {canonicalReadingPosition} from '../lib/reading-routes';

export default function ProgressDashboard({ questions }: { questions: Question[] }) {
  const { progress } = useProgress();
  const account = useAccount();
  const stats = learningStats(progress);
  const latest = new Map(progress.attempts.map((a) => [a.questionId, a]));
  const known = new Map(questions.map((q) => [q.id, q]));
  const bookmarks = progress.bookmarks.filter((id) => known.has(id));
  const resumeLesson = progress.reading && lessonForPath(canonicalReadingPosition(progress.reading).path);
  const completedSubsections=contents.filter(node=>node.depth>1&&progress.completedSections.includes(completionId(node)));
  const conceptForQuestion = (id: string) => definitions.find((concept) => concept.questionIds.includes(id))?.id || 'cache-memory';
  const exportProgress = () => {
    const url = URL.createObjectURL(new Blob([JSON.stringify(progress, null, 2)], { type: 'application/json' }));
    const link = document.createElement('a'); link.href = url; link.download = 'itpec-fe-progress.json'; link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  };
  return <div className="progress-dashboard">
    <h1>Progress</h1><p>{account.user?'Synced to your account.':'Saved in this browser.'}</p>
    <StorageNotice />
    <dl className="progress-stat-grid"><div><dt>Questions tried</dt><dd>{stats.questions}</dd></div><div><dt>Correct on latest try</dt><dd>{stats.correct}</dd></div><div><dt>Still practising</dt><dd>{stats.incorrect}</dd></div><div><dt>Total attempts</dt><dd>{stats.attempts}</dd></div></dl>
    <section className="progress-section"><h2>Reading</h2>{resumeLesson&&<p>{resumeLesson.title}</p>}
      <a className="button button-primary" href={returnUrl(progress.reading, '/chapters/hardware/')}>{progress.reading ? 'Continue reading →' : 'Open Chapter 1'}</a></section>
    <section className="progress-section"><h2>Chapter 1 completion</h2><p>{hardwareLessons.slice(0, 5).filter((lesson) => progress.completedSections.includes(lesson.id)).length} of 5 main sections completed</p><ul className="section-progress">{hardwareLessons.slice(0,5).map((lesson) => <li key={lesson.id}><a href={lessonPath(lesson)}>{lesson.title}</a><span>{progress.completedSections.includes(lesson.id) ? 'Completed' : 'In progress'}</span></li>)}</ul>
      {completedSubsections.length>0&&<><h3>Completed subsections</h3><ul className="section-progress">{completedSubsections.map(node=><li key={node.id}><a href={contentsUrl(node)}>{node.number} {node.title}</a><span>Completed</span></li>)}</ul></>}
    </section>
    <section className="progress-section"><h2>Question history</h2>{latest.size ? <ul className="history-list">{[...latest.values()].reverse().map((a) => <li key={a.questionId}><div><a href={`/practice/${a.conceptId}/?question=${a.questionId}`}>{a.questionId} →</a><span>{a.correct ? '✓ Correct on latest attempt' : 'Review this question'}</span></div><span>{new Date(a.at).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })}</span></li>)}</ul> : <div className="empty-state"><p>No answers yet.</p><a href="/practice/">Practice</a></div>}</section>
    <section className="progress-section"><h2>Bookmarked questions <span className="muted">({bookmarks.length})</span></h2>{bookmarks.length ? <ul className="history-list">{bookmarks.map((id) => <li key={id}><a href={`/practice/${conceptForQuestion(id)}/?question=${id}`}>{id} →</a><button type="button" className="text-button" onClick={() => guestStore.toggleBookmark(id)}>Remove<span className="sr-only"> bookmark {id}</span></button></li>)}</ul> : <p>Save a question during practice to find it here.</p>}</section>
    <AccountControls />
    <section className="progress-section" id="about-progress"><h2>Your progress belongs to you</h2><p>Learning is always available without registration. Guest progress stays in this browser. Clearing browser data removes it; private browsing may not retain it.</p><p>Optional Google sign-in backs up submitted attempts, incorrect-answer history, bookmarks, completed sections and periodic reading checkpoints. Offline changes are kept locally for the same account and retried when the connection returns.</p><button className="button button-secondary" type="button" onClick={exportProgress}>Download my progress</button><p className="quiet-note">Keep the downloaded file private: it contains your learning history. Restore from a file is not available in this pilot.</p></section>
    <GuestNotice />
  </div>;
}
