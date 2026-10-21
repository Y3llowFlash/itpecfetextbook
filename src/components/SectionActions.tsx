import { guestStore } from '../lib/progress';
import { useProgress } from '../lib/use-progress';
import { StorageNotice } from './GuestNotice';
import { useAccount } from './AccountControls';

export interface PracticeLink { id: string; title: string; count: number }
export default function SectionActions({ sectionId, count, links = [{ id: 'cache-memory', title: 'Cache memory', count }] }: { sectionId: string; count: number; links?: PracticeLink[] }) {
  const { progress } = useProgress();
  const account = useAccount();
  const completed = progress.completedSections.includes(sectionId);
  return <div className="section-actions">
    <div><p className="small-label">KEEP LEARNING</p><h2>{count ? 'Ready to test the idea?' : 'A foundation for the next section'}</h2><p>{count ? `Try ${count} related published questions. You can return to this exact place.` : 'Review the examples, then mark this section complete when you can explain the main ideas.'}</p></div>
    <div className="button-row">{links.map((link, i) => <a key={link.id} className="button button-primary" data-concept={link.id} id={i === 0 ? 'practice-from-recap' : `practice-${link.id}`} href={`/practice/${link.id}/`}>Practice {link.title.toLowerCase()} ({link.count}) <span aria-hidden="true">↗</span></a>)}
      <button type="button" className="button button-secondary" aria-pressed={completed} onClick={() => guestStore.setCompleted(sectionId, !completed)}>{completed ? '✓ Section completed' : 'Mark as completed'}</button></div>
    <p className="quiet-note" aria-live="polite">{completed ? 'Section completed. You can revisit it anytime.' : account.user ? 'Meaningful progress changes sync to your account.' : 'Your reading and practice progress stay on this device.'}</p>
    <StorageNotice />
  </div>;
}
