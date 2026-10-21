import { useEffect, useSyncExternalStore } from 'react';
import { accountStore } from '../lib/account';

export function useAccount() {
  useEffect(() => { accountStore.start(); }, []);
  return useSyncExternalStore(accountStore.subscribe, accountStore.getSnapshot, accountStore.getServerSnapshot);
}
export function GoogleSignInButton() {
  const account = useAccount();
  return <button type="button" className="button button-secondary" disabled={account.busy} onClick={() => void accountStore.signIn()}>{account.busy ? 'Connecting…' : 'Continue with Google'}</button>;
}
const statusText = {
  guest: 'Progress saved on this device', loading: 'Loading your account…', syncing: 'Synchronizing progress…',
  saved: 'Progress backed up', pending: 'Changes waiting to sync', offline: 'Offline — progress saved on this device',
  error: 'Sync unavailable — progress kept on this device',
};
export default function AccountControls({ compact = false }: { compact?: boolean }) {
  const account = useAccount();
  if (compact) return <a className="guest-pill" href="/progress/#account" title={statusText[account.status]} aria-label={account.user ? `Your account and progress: ${statusText[account.status]}` : 'Your progress and optional account'}>
    <span aria-hidden="true">{account.user ? account.status === 'saved' ? '✓' : '◷' : '◌'}</span><span>{account.user ? statusText[account.status] : 'Learning as a guest'}</span><span className="guest-short">{account.user ? 'Account & sync' : 'Your progress'}</span></a>;
  return <section id="account" className="account-panel progress-section" data-sync-state={account.status} aria-label="Optional account backup">
    <h2>{account.user ? `Learning with ${account.user.name}` : 'Account backup'}</h2>
    <p>{account.user ? 'Your attempts, bookmarks and completed sections are backed up to your free Google account. You can continue on another device.' : 'Create a free account to save your learning history and continue across devices. Reading and practice are always available as a guest.'}</p>
    <p className="sync-status" role="status">{statusText[account.status]}</p>
    {account.user ? <div className="button-row">
      <button type="button" className="button button-secondary" disabled={account.busy || account.status === 'syncing'} onClick={() => void accountStore.syncNow()}>Sync now</button>
      <button type="button" className="text-button" disabled={account.busy} onClick={() => void accountStore.signOut()}>Sign out</button>
    </div> : <GoogleSignInButton />}
    {account.user && ['offline', 'pending', 'error'].includes(account.status) && <p className="quiet-note">Unsynced changes stay in this account’s local cache. Sign back into the same account to finish backing them up.</p>}
    {account.error && <p className="storage-warning" role="alert">{account.error}</p>}
    <p className="quiet-note">Guest progress stays on this browser. Signing in merges it with your account history. Signing out returns to a separate guest session.</p>
  </section>;
}
