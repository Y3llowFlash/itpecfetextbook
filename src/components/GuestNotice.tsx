import { guestStore, learningStats } from '../lib/progress';
import { useProgress } from '../lib/use-progress';
import { GoogleSignInButton, useAccount } from './AccountControls';

export function StorageNotice() {
  const { persistence } = useProgress();
  if (persistence === 'saved') return null;
  return <p className="storage-warning" role="status">{persistence === 'corrupt'
    ? 'Saved progress could not be read. Your existing data has been kept; new activity will last for this visit.'
    : 'Browser storage is unavailable. You can keep learning, but new progress may not survive closing this page.'}</p>;
}

export default function GuestNotice() {
  const { progress } = useProgress();
  const account = useAccount();
  const stats = learningStats(progress);
  if (account.user || progress.dismissedAccountPrompt || (stats.attempts < 3 && !stats.completedSections)) return null;
  return <aside className="guest-notice" aria-label="Optional account backup">
    <button type="button" className="dismiss-button" aria-label="Dismiss account reminder" onClick={() => guestStore.dismissAccountPrompt()}>×</button>
    <strong>Account backup</strong>
    <p>Sign in with Google to sync progress across devices.</p>
    <GoogleSignInButton />
    {account.error && <p role="alert">{account.error}</p>}
    <a href="/progress/#about-progress">About your progress →</a>
  </aside>;
}
