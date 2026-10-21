import { guestStore } from '../lib/progress';
import { useProgress } from '../lib/use-progress';
import { StorageNotice } from './GuestNotice';

export default function SectionActions({ sectionId, count }: { sectionId: string; count: number }) {
  const { progress } = useProgress();
  const completed = progress.completedSections.includes(sectionId);
  return <div className="section-actions">
    <div><p className="small-label">PUT IT INTO PRACTICE</p><h2>Ready to test the idea?</h2><p>Try {count} real exam questions. You can return to this exact place.</p></div>
    <div className="button-row"><a className="button button-primary" data-concept="cache-memory" id="practice-from-recap" href="/practice/cache-memory/">Practice cache memory <span aria-hidden="true">↗</span></a>
      <button type="button" className="button button-secondary" aria-pressed={completed} onClick={() => guestStore.setCompleted(sectionId, !completed)}>{completed ? '✓ Section completed' : 'Mark as completed'}</button></div>
    <p className="quiet-note" aria-live="polite">{completed ? 'Completed on this device. You can revisit this section anytime.' : 'Your reading and practice progress stay on this device.'}</p>
    <StorageNotice />
  </div>;
}
