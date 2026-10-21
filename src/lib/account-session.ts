import { browserLocalPersistence, connectAuthEmulator, getAuth, GoogleAuthProvider, onAuthStateChanged, setPersistence, signInWithPopup, signOut as firebaseSignOut } from 'firebase/auth';
import { connectFirestoreEmulator, initializeFirestore, memoryLocalCache } from 'firebase/firestore';
import { app, useFirebaseEmulators } from './firebase';
import { guestStore } from './progress';
import { FirestoreProgressAdapter } from './firestore-sync';
import { SyncController } from './sync-controller';
import { rememberAccount, type AccountSnapshot } from './account';

export interface AccountSession { signIn(): Promise<void>; signOut(): Promise<void>; syncNow(): Promise<void> }

export async function createAccountSession(notify: (patch: Partial<AccountSnapshot>) => void): Promise<AccountSession> {
  if (useFirebaseEmulators && !['localhost', '127.0.0.1', '[::1]'].includes(location.hostname)) throw new Error('Emulators are allowed only on loopback hosts');
  const auth = getAuth(app);
  if (useFirebaseEmulators) connectAuthEmulator(auth, 'http://127.0.0.1:19099', { disableWarnings: true });
  await setPersistence(auth, browserLocalPersistence).catch(() => { /* Firebase retains an in-memory session when persistent storage is denied. */ });
  // Initialize Firestore only after a Google account is actually present.
  let controller: SyncController | undefined;
  let activeUid: string | null = null;
  let signingOut = false;
  const clearView = () => {
    controller?.stop(); activeUid = null;
    guestStore.clearSyncedAccountCache();
    guestStore.switchAccount(null);
    notify({ user: null, status: 'guest', busy: false });
  };
  onAuthStateChanged(auth, (user) => {
    if (signingOut || !user || user.isAnonymous || !user.providerData.some((p) => p.providerId === 'google.com')) {
      if (activeUid || guestStore.getUserId()) clearView();
      notify({ busy: false, status: 'guest', user: null });
      return;
    }
    if (activeUid === user.uid) return;
    const migrateGuest = !activeUid && guestStore.getUserId() === null;
    if (activeUid) { controller?.stop(); guestStore.clearSyncedAccountCache(); guestStore.switchAccount(null); }
    activeUid = user.uid;
    rememberAccount(true);
    if (!controller) {
      const db = initializeFirestore(app, { localCache: memoryLocalCache() });
      if (useFirebaseEmulators) connectFirestoreEmulator(db, '127.0.0.1', 18080);
      const adapter = new FirestoreProgressAdapter(db, () => !signingOut && auth.currentUser?.uid === activeUid ? activeUid : null);
      controller = new SyncController(guestStore, adapter, (status) => notify({ status }));
    }
    controller.start(user.uid, migrateGuest);
    notify({ user: { uid: user.uid, name: user.displayName || 'Google account' }, busy: false, error: null });
  }, () => {
    clearView(); notify({ error: 'Could not restore your account. Guest learning remains available.' });
  });
  window.addEventListener('online', () => { if (!document.hidden) void controller?.flush(); });
  window.addEventListener('offline', () => { if (activeUid) notify({ status: 'offline' }); });
  document.addEventListener('visibilitychange', () => controller?.setVisible(!document.hidden));
  window.addEventListener('pagehide', () => controller?.setVisible(false));
  window.addEventListener('pageshow', () => { if (!document.hidden) controller?.setVisible(true); });
  const provider = new GoogleAuthProvider();
  provider.setCustomParameters({ prompt: 'select_account' });
  return {
    async signIn() { signingOut = false; await signInWithPopup(auth, provider); },
    async signOut() {
      signingOut = true;
      clearView();
      rememberAccount(false);
      await firebaseSignOut(auth);
      signingOut = false;
    },
    async syncNow() { if (activeUid) await controller?.flush(); },
  };
}
