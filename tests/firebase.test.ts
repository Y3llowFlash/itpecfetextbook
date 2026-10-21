// @vitest-environment node
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const sdk = vi.hoisted(() => ({
  isSupported: vi.fn(),
  getAnalytics: vi.fn(),
}));
vi.mock('firebase/analytics', () => sdk);

beforeEach(() => {
  vi.resetModules();
  sdk.isSupported.mockReset().mockResolvedValue(true);
  sdk.getAnalytics.mockReset().mockReturnValue({ name: 'analytics' });
  vi.stubEnv('DEV', false);
});
afterEach(() => {
  vi.unstubAllGlobals();
  vi.unstubAllEnvs();
});

describe('Firebase browser initialization', () => {
  it('can be imported during static rendering without starting Analytics', async () => {
    const { app, getFirebaseAnalytics } = await import('../src/lib/firebase');
    expect(app.options.projectId).toBe('itpec-textbook');
    await expect(getFirebaseAnalytics()).resolves.toBeNull();
    expect(sdk.isSupported).not.toHaveBeenCalled();
  });

  it.each(['localhost', '127.0.0.1', '[::1]'])('does not send Analytics from %s previews', async (hostname) => {
    vi.stubGlobal('window', { location: { hostname } });
    const { getFirebaseAnalytics } = await import('../src/lib/firebase');
    await expect(getFirebaseAnalytics()).resolves.toBeNull();
    expect(sdk.isSupported).not.toHaveBeenCalled();
  });

  it('skips Analytics during development on other hostnames', async () => {
    vi.stubGlobal('window', { location: { hostname: 'dev.example.com' } });
    vi.stubEnv('DEV', true);
    const { getFirebaseAnalytics } = await import('../src/lib/firebase');
    await expect(getFirebaseAnalytics()).resolves.toBeNull();
    expect(sdk.isSupported).not.toHaveBeenCalled();
  });

  it('initializes Analytics once for concurrent calls in a supported production browser', async () => {
    vi.stubGlobal('window', { location: { hostname: 'textbook.example.com' } });
    const { app, getFirebaseAnalytics } = await import('../src/lib/firebase');
    const [first, second] = await Promise.all([getFirebaseAnalytics(), getFirebaseAnalytics()]);
    expect(first).toBe(second);
    expect(sdk.getAnalytics).toHaveBeenCalledExactlyOnceWith(app);
  });

  it('keeps unsupported browsers usable without Analytics', async () => {
    vi.stubGlobal('window', { location: { hostname: 'textbook.example.com' } });
    sdk.isSupported.mockResolvedValue(false);
    const { getFirebaseAnalytics } = await import('../src/lib/firebase');
    await expect(getFirebaseAnalytics()).resolves.toBeNull();
    expect(sdk.getAnalytics).not.toHaveBeenCalled();
  });

  it('does not reject when browser storage or Analytics initialization fails', async () => {
    vi.stubGlobal('window', { location: { hostname: 'textbook.example.com' } });
    sdk.isSupported.mockRejectedValue(new Error('Browser storage denied'));
    vi.spyOn(console, 'warn').mockImplementation(() => {});
    const { getFirebaseAnalytics } = await import('../src/lib/firebase');
    await expect(getFirebaseAnalytics()).resolves.toBeNull();
    expect(sdk.getAnalytics).not.toHaveBeenCalled();
  });
});
