import { useProgress } from '../lib/use-progress';
import { learningStats } from '../lib/progress';
import GuestNotice from './GuestNotice';
import type { PracticeLink } from './SectionActions';

export default function StudyCompanion({ questionCount = 3, links = [{ id: 'cache-memory', title: 'Cache memory', count: questionCount }] }: { questionCount?: number; links?: PracticeLink[] }) {
  const { progress } = useProgress();
  const stats = learningStats(progress);
  return <div className="companion-content">
    <p className="companion-label">YOUR STUDY COMPANION</p>
    <h2>A little practice.<br />A clearer idea.</h2>
    <p>Read at your pace. Follow a yellow highlight when you’re ready to try the idea.</p>
    {links.length ? links.map((link) => <a key={link.id} className="companion-practice" href={`/practice/${link.id}/`}><span>{link.title}</span><strong>{link.count} {link.count === 1 ? 'question' : 'questions'} <span aria-hidden="true">↗</span></strong></a>) : <p className="quiet-note">Build the foundation here. Reviewed exam practice begins with data representation.</p>}
    <div className="companion-rule"></div>
    <h3>Your progress</h3>
    <dl className="companion-stats">
      <div><dt>Questions tried</dt><dd>{stats.questions}</dd></div>
      <div><dt>Correct on latest try</dt><dd>{stats.correct}</dd></div>
      <div><dt>Bookmarks</dt><dd>{stats.bookmarks}</dd></div>
    </dl>
    <a className="text-link" href="/progress/">View your progress →</a>
    <div className="companion-tip"><strong>A useful habit</strong><p>Write down what each value represents, check its units, then choose the operation that answers the question.</p></div>
    <GuestNotice />
    <p className="quiet-note">Free to learn. No account needed.</p>
  </div>;
}
