import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { setupReader, READER_PATH, conceptReturnPosition } from '../src/lib/reading';
import { guestStore } from '../src/lib/progress';

let teardown: (() => void) | undefined;
beforeEach(() => {
  localStorage.clear(); sessionStorage.clear(); guestStore.refresh();
  history.replaceState(null, '', READER_PATH);
  document.body.innerHTML = '<article data-reader data-section-id="fe-v1-ch01-memory-cache"><div id="cache-definition" data-reading-block><a id="concept-cache-memory" data-concept="cache-memory" href="/practice/cache-memory/">Cache memory</a></div></article>';
  vi.spyOn(document.getElementById('cache-definition')!, 'getBoundingClientRect').mockReturnValue({ top: 120 } as DOMRect);
  Object.defineProperty(window, 'scrollY', { value: 900, configurable: true });
  Object.defineProperty(document, 'fonts', { value: { ready: Promise.resolve() }, configurable: true });
  vi.spyOn(window, 'scrollTo').mockImplementation(() => {});
  vi.spyOn(performance, 'getEntriesByType').mockReturnValue([]);
});
afterEach(() => { teardown?.(); teardown = undefined; document.body.innerHTML = ''; vi.useRealTimers(); });

describe('reading-to-practice return', () => {
  it('returns a shared source concept to its actual section while rejecting unrelated checkpoints',()=>{
    const source={sectionId:'fe-v1-ch01-s03',path:'/chapters/hardware/cpu-and-main-memory/',blockId:'fev1-201504-ch1-r1-pdf-075-b005-l00-paragraph',offset:70,scrollY:900,focusId:'concept-cache-memory',updatedAt:'2026-10-21T07:00:00Z'};
    expect(conceptReturnPosition(source,'cache-memory','fe-v1-ch01-memory-cache')).toEqual(source);
    expect(conceptReturnPosition(source,'radix-conversion','fe-v1-ch01-s02')).toBeNull();
    expect(conceptReturnPosition({...source,path:'https://example.invalid/'},'cache-memory','fe-v1-ch01-memory-cache')).toBeNull();
  });
  it('captures the exact block/offset and focused concept before navigation, preserving it at pagehide', () => {
    teardown = setupReader();
    const link = document.getElementById('concept-cache-memory')!;
    link.addEventListener('click', (event) => event.preventDefault());
    link.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
    const saved = guestStore.getSnapshot().progress.reading;
    expect(saved).toMatchObject({ blockId: 'cache-definition', offset: 120, scrollY: 900, focusId: 'concept-cache-memory' });
    window.dispatchEvent(new Event('pagehide'));
    expect(guestStore.getSnapshot().progress.reading).toEqual(saved);
  });
  it('restores a stable block offset after layout changes and focuses the clicked highlight', async () => {
    guestStore.saveReading({ sectionId: 'fe-v1-ch01-memory-cache', path: READER_PATH, blockId: 'cache-definition', offset: 70, scrollY: 400, focusId: 'concept-cache-memory', updatedAt: '2026-10-21T07:00:00Z' });
    history.replaceState(null, '', `${READER_PATH}?resume=1#concept-cache-memory`);
    vi.spyOn(window, 'requestAnimationFrame').mockImplementation((callback) => { callback(0); return 0; });
    teardown = setupReader();
    await Promise.resolve(); await Promise.resolve();
    expect(window.scrollTo).toHaveBeenCalledWith({ top: 950, behavior: 'instant' });
    expect(document.activeElement?.id).toBe('concept-cache-memory');
    expect(location.search).toBe('');
  });
  it('uses the saved scroll fallback when an older content block no longer exists', async () => {
    guestStore.saveReading({ sectionId: 'fe-v1-ch01-memory-cache', path: READER_PATH, blockId: 'removed-block', offset: 70, scrollY: 400, updatedAt: '2026-10-21T07:00:00Z' });
    history.replaceState(null, '', `${READER_PATH}?resume=1`);
    vi.spyOn(window, 'requestAnimationFrame').mockImplementation((callback) => { callback(0); return 0; });
    teardown = setupReader(); await Promise.resolve(); await Promise.resolve();
    expect(window.scrollTo).toHaveBeenCalledWith({ top: 400, behavior: 'instant' });
  });
});
