import { getApp, getApps, initializeApp } from 'firebase/app';
import type { Analytics } from 'firebase/analytics';

// Firebase web configuration is public; access control belongs in Firebase rules.
export const useFirebaseEmulators = import.meta.env.PUBLIC_FIREBASE_USE_EMULATORS === 'true';
const firebaseConfig = {
  apiKey: import.meta.env.PUBLIC_FIREBASE_API_KEY || 'AIzaSyBE9JQPLyqAFANLNLQppDWbEuJ9sN-HfME',
  authDomain: import.meta.env.PUBLIC_FIREBASE_AUTH_DOMAIN || 'itpec-textbook.firebaseapp.com',
  projectId: useFirebaseEmulators ? 'demo-itpec-textbook' : 'itpec-textbook',
  storageBucket: 'itpec-textbook.firebasestorage.app',
  messagingSenderId: '959099491967',
  appId: import.meta.env.PUBLIC_FIREBASE_APP_ID || '1:959099491967:web:79ee8a1d34410e83e2d14a',
  measurementId: import.meta.env.PUBLIC_FIREBASE_MEASUREMENT_ID || 'G-E8G96XMX6N',
};

export const app = getApps().some(({ name }) => name === '[DEFAULT]')
  ? getApp()
  : initializeApp(firebaseConfig);

let analyticsPromise: Promise<Analytics | null> | undefined;

/** Analytics runs only in supported production browsers, outside local previews. */
export function getFirebaseAnalytics(): Promise<Analytics | null> {
  if (typeof window === 'undefined' || import.meta.env.DEV || useFirebaseEmulators
    || ['localhost', '127.0.0.1', '[::1]'].includes(window.location.hostname)) {
    return Promise.resolve(null);
  }

  analyticsPromise ??= import('firebase/analytics')
    .then(async ({ getAnalytics, isSupported }) => (await isSupported() ? getAnalytics(app) : null))
    .catch(() => {
      // Analytics must never prevent reading or practising when unavailable.
      console.warn('Firebase Analytics is unavailable in this browser.');
      return null;
    });
  return analyticsPromise;
}
