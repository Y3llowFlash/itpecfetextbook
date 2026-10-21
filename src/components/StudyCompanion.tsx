import { useProgress } from '../lib/use-progress';
import { learningStats } from '../lib/progress';
import GuestNotice from './GuestNotice';

export default function StudyCompanion({ questionCount = 3 }: { questionCount?: number }) {
  const { progress } = useProgress();
  const stats = learningStats(progress);
  return <div className="companion-content">
    <p className="companion-label">YOUR STUDY COMPANION</p>
    <h2>A little practice.<br />A clearer idea.</h2>
    <p>Read at your pace. Follow a yellow highlight when you’re ready to try the idea.</p>
    <a className="companion-practice" href="/practice/cache-memory/">
      <span>Cache memory</span><strong>{questionCount} questions <span aria-hidden="true">↗</span></strong>
    </a>
    <div className="companion-rule"></div>
    <h3>Your progress</h3>
    <dl className="companion-stats">
      <div><dt>Questions tried</dt><dd>{stats.questions}</dd></div>
      <div><dt>Correct on latest try</dt><dd>{stats.correct}</dd></div>
      <div><dt>Bookmarks</dt><dd>{stats.bookmarks}</dd></div>
    </dl>
    <a className="text-link" href="/progress/">View your progress →</a>
    <div className="companion-tip"><strong>A useful distinction</strong><p>A cache miss isn’t an error. It just means the requested data must be found at another level.</p></div>
    <GuestNotice />
    <p className="quiet-note">Free to learn. No account needed.</p>
  </div>;
}
