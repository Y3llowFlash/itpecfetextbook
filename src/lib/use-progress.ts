import { useSyncExternalStore } from 'react';
import { guestStore } from './progress';
export function useProgress() { return useSyncExternalStore(guestStore.subscribe, guestStore.getSnapshot, guestStore.getServerSnapshot); }
