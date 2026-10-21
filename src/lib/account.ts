import { guestStore } from './progress';
import type { SyncStatus } from './sync-controller';

export interface AccountSnapshot {
  user: { uid: string; name: string } | null;
  status: SyncStatus;
  busy: boolean;
  error: string | null;
}
const initial: AccountSnapshot = { user: null, status: 'guest', busy: false, error: null };
const ENABLED_KEY = 'itpecTextbook:account-enabled:v1';
let snapshot = initial;
const listeners = new Set<() => void>();
let session: Promise<import('./account-session').AccountSession> | undefined;
let started = false;
const notify = (patch: Partial<AccountSnapshot>) => { snapshot = { ...snapshot, ...patch }; listeners.forEach((l) => l()); };
export function rememberAccount(enabled: boolean) {
  try {
    if (enabled) localStorage.setItem(ENABLED_KEY, 'true');
    else localStorage.removeItem(ENABLED_KEY);
  } catch { /* Accounts still work for this visit if storage is blocked. */ }
}
async function loadSession() {
  session ??= import('./account-session').then(({ createAccountSession }) => createAccountSession(notify)).catch((error) => {
    session = undefined;
    throw error;
  });
  return session;
}
const friendlyError = (error: unknown) => {
  const code = (error as { code?: string }).code;
  if (code === 'auth/popup-closed-by-user' || code === 'auth/cancelled-popup-request') return 'Sign-in was cancelled. You can keep learning as a guest.';
  if (code === 'auth/popup-blocked') return 'Your browser blocked Google sign-in. Allow the sign-in popup and try again.';
  if (code === 'auth/unauthorized-domain') return 'Google sign-in is not configured for this website address yet. Your local progress is safe.';
  if (code === 'auth/network-request-failed') return 'Cannot reach Google sign-in. Check your connection and try again. Your local progress is safe.';
  return 'The account service is unavailable. Your local progress is safe; please try again.';
};

export const accountStore = {
  subscribe: (listener: () => void) => { listeners.add(listener); return () => { listeners.delete(listener); }; },
  getSnapshot: () => snapshot,
  getServerSnapshot: () => initial,
  start() {
    if (started || typeof window === 'undefined') return;
    started = true;
    const restore = () => {
      try {
        if (localStorage.getItem(ENABLED_KEY) === 'true') {
          notify({ busy: true, status: 'loading' });
          void loadSession().catch((error) => notify({ busy: false, error: friendlyError(error), status: 'guest' }));
        }
      } catch { /* Guest mode requires no Firebase initialization. */ }
    };
    restore();
    window.addEventListener('storage', (event) => {
      if (event.key !== ENABLED_KEY) return;
      if (event.newValue === 'true') restore();
      else {
        // Hide account data immediately, even before the Auth SDK processes sign-out.
        guestStore.clearSyncedAccountCache(); guestStore.switchAccount(null);
        notify({ user: null, status: 'guest', busy: false });
        if (session) void session.then((s) => s.signOut()).catch(() => {});
      }
    });
  },
  async signIn() {
    if (snapshot.busy || snapshot.user) return;
    notify({ busy: true, error: null });
    rememberAccount(true);
    try { await (await loadSession()).signIn(); }
    catch (error) {
      if (!snapshot.user) rememberAccount(false);
      notify({ error: friendlyError(error) });
    } finally { notify({ busy: false }); }
  },
  async signOut() {
    notify({ busy: true, error: null });
    try { await (await loadSession()).signOut(); rememberAccount(false); }
    catch (error) { notify({ error: 'Sign-out could not finish. Account progress has been hidden; retry sign-out before sharing this browser.' }); }
    finally { notify({ busy: false }); }
  },
  async syncNow() { try { await (await loadSession()).syncNow(); } catch (error) { notify({ error: friendlyError(error) }); } },
};
