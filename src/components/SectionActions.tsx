import { guestStore } from '../lib/progress';
import { useProgress } from '../lib/use-progress';
import { StorageNotice } from './GuestNotice';

export interface PracticeLink { id: string; title: string; count: number }
export default function SectionActions({ sectionId, count, links = [{ id: 'cache-memory', title: 'Cache memory', count }] }: { sectionId: string; count: number; links?: PracticeLink[] }) {
  const { progress } = useProgress();
  const completed = progress.completedSections.includes(sectionId);
  return <div className="section-actions">
    <h2>Section progress</h2>
    <div className="button-row">{links.map((link, i) => <a key={link.id} className="button button-primary" data-concept={link.id} id={i === 0 ? 'practice-from-recap' : `practice-${link.id}`} href={`/practice/${link.id}/`}>Practice {link.title.toLowerCase()} ({link.count}) <span aria-hidden="true">↗</span></a>)}
      <button type="button" className="button button-secondary" aria-pressed={completed} onClick={() => guestStore.setCompleted(sectionId, !completed)}>{completed ? '✓ Section completed' : 'Mark as completed'}</button></div>
    <p className="quiet-note" aria-live="polite">{completed ? 'Completed' : ''}</p>
    <StorageNotice />
  </div>;
}
