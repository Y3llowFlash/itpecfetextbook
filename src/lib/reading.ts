import type { ReadingPosition } from './models';
import { guestStore, validReading } from './progress';
import { accountStore } from './account';
import {canonicalReadingPosition,CPU_PATH,CACHE_HEADING,CACHE_LEGACY_ID} from './reading-routes';

export const READER_PATH = CPU_PATH;
const RETURN_KEY = 'itpecTextbook:return:v1';

export function returnUrl(position: ReadingPosition | null, fallback = `${READER_PATH}#${CACHE_HEADING}`) {
  const source=position&&validReading(position)?canonicalReadingPosition(position):null;
  return source ? `${source.path}?resume=1#${encodeURIComponent(source.focusId || source.blockId)}` : fallback;
}

export function savedReturnPosition(fallback: ReadingPosition | null, sectionId?: string): ReadingPosition | null {
  if(fallback&&validReading(fallback))fallback=canonicalReadingPosition(fallback);
  if(sectionId===CACHE_LEGACY_ID)sectionId='fe-v1-ch01-s03';
  if (sectionId && fallback?.sectionId !== sectionId) fallback = null;
  if (typeof window === 'undefined') return fallback;
  try {
    const raw = sessionStorage.getItem(RETURN_KEY);
    const parsed = raw ? JSON.parse(raw) : null;
    const position=validReading(parsed)?canonicalReadingPosition(parsed):null;
    if (validReading(position) && (!sectionId || position.sectionId === sectionId) && (!fallback || position.updatedAt >= fallback.updatedAt)) return position;
  } catch { /* durable or in-memory pointer remains available */ }
  return fallback;
}

/** One source concept can appear in both the full section and a source excerpt. */
export function conceptReturnPosition(fallback:ReadingPosition|null,conceptId:string,sectionId:string){
  if(fallback&&validReading(fallback))fallback=canonicalReadingPosition(fallback);
  if(sectionId===CACHE_LEGACY_ID)sectionId='fe-v1-ch01-s03';
  const matches=(p:ReadingPosition|null)=>!!p&&validReading(p)&&(p.sectionId===sectionId||p.focusId===`concept-${conceptId}`);
  const saved=savedReturnPosition(null);
  if(matches(saved)&&(!matches(fallback)||saved!.updatedAt>=fallback!.updatedAt))return saved;
  return matches(fallback)?fallback:null;
}

export function setupReader() {
  const reader = document.querySelector<HTMLElement>('[data-reader]');
  if (!reader) return;
  const sectionId = reader.dataset.sectionId!;
  const readerPath = reader.dataset.readerPath||location.pathname;
  let timer: ReturnType<typeof setTimeout>;
  let leavingForPractice = false;
  let cancelled = false;
  let resumeRequested = new URLSearchParams(location.search).get('resume') === '1';
  let restoring = resumeRequested;
  let restoreScheduled = false;
  // Reads only the existing opt-in marker for guests. A remembered account must
  // settle before a native fragment scroll can overwrite its saved checkpoint.
  accountStore.start();
  const accountLoading = () => accountStore.getSnapshot().busy && !accountStore.getSnapshot().user;
  const capture = (focusId?: string) => {
    if (restoring || accountLoading()) return;
    const blocks = [...reader.querySelectorAll<HTMLElement>('[data-reading-block]')];
    const anchor = focusId ? document.getElementById(focusId) : undefined;
    const block = anchor?.closest<HTMLElement>('[data-reading-block]') || [...blocks].reverse().find((b) => b.getBoundingClientRect().top <= 130) || blocks[0];
    if (!block?.id) return;
    const position: ReadingPosition = { sectionId, path: readerPath, blockId: block.id, offset: block.getBoundingClientRect().top,
      scrollY: window.scrollY, focusId, updatedAt: new Date().toISOString() };
    guestStore.saveReading(position);
    return position;
  };
  const onScroll = () => { clearTimeout(timer); timer = setTimeout(() => capture(), 250); };
  window.addEventListener('scroll', onScroll, { passive: true });
  const onHide = () => { clearTimeout(timer); if (!leavingForPractice) capture(); };
  window.addEventListener('pagehide', onHide);
  const linkHandlers = [...reader.querySelectorAll<HTMLAnchorElement>('[data-concept]')].map((link) => {
    const onClick = () => {
      leavingForPractice = true;
      clearTimeout(timer);
      const position = capture(link.id);
      try { if (position) sessionStorage.setItem(RETURN_KEY, JSON.stringify(position)); } catch { /* guest in-memory fallback remains */ }
    };
    link.addEventListener('click', onClick);
    return () => link.removeEventListener('click', onClick);
  });

  async function restore(force = false) {
    if (!force && !resumeRequested) return;
    resumeRequested = true;
    restoring = true;
    if (accountLoading() || restoreScheduled) return;
    const position = savedReturnPosition(guestStore.getSnapshot().progress.reading, sectionId);
    if (!position || position.sectionId !== sectionId) { restoring = false; resumeRequested = false; return; }
    restoreScheduled = true;
    const owner = guestStore.getUserId();
    await document.fonts.ready;
    if (cancelled) return;
    requestAnimationFrame(() => requestAnimationFrame(() => {
      if (cancelled) return;
      if (owner !== guestStore.getUserId()) { restoreScheduled = false; restoring = false; resumeRequested = false; return; }
      const block = document.getElementById(position!.blockId);
      const target = block ? window.scrollY + block.getBoundingClientRect().top - position!.offset : position!.scrollY;
      window.scrollTo({ top: Math.max(0, target), behavior: 'instant' });
      if (position!.focusId) document.getElementById(position!.focusId)?.focus({ preventScroll: true });
      history.replaceState(null, '', `${readerPath}#${encodeURIComponent(position!.focusId || position!.blockId)}`);
      restoreScheduled = false;
      restoring = false;
      resumeRequested = false;
    }));
  }
  const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming | undefined;
  void restore(navigation?.type === 'back_forward');
  const unsubscribeAccount = accountStore.subscribe(() => {
    if (resumeRequested && !accountLoading()) void restore(true);
  });
  const onShow = (event: PageTransitionEvent) => {
    if (event.persisted) {
      leavingForPractice = false;
      void restore(true);
    }
  };
  window.addEventListener('pageshow', onShow);
  return () => {
    cancelled = true;
    clearTimeout(timer);
    window.removeEventListener('scroll', onScroll);
    window.removeEventListener('pagehide', onHide);
    window.removeEventListener('pageshow', onShow);
    unsubscribeAccount();
    linkHandlers.forEach((cleanup) => cleanup());
  };
}
