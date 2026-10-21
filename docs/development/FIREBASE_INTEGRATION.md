# Firebase security and optional accounts

Implementation and production configuration audit: **2026-10-21**.

## Security issue and remediation

The original local **and deployed** Firestore rules allowed unauthenticated reads, writes and deletes across every document until November 20, 2026. They provided no student isolation. The original deployed ruleset was `6ee044fc-e4b4-48ca-8b20-c70aa4a195e0`.

Replaced this with default-deny rules. Only a Firebase user whose current token has `firebase.sign_in_provider == 'google.com'` and whose UID matches the path may access `users/{uid}/progress/{recordId}`. Anonymous tokens are denied even for their own UID. Public collections, parent profiles and deeper nested documents are denied. Writes validate record shape, allowed fields, sizes, identity, version clock and server timestamp. Attempts cannot be updated; mutable state cannot be overwritten by older clocks. Boolean removals are stored as records rather than deleted by the application.

**Rules were deployed**, exclusively using `--only firestore:rules --project itpec-textbook`, after the first seven emulator security tests passed. The deployed ruleset is `25aa1b04-92f0-4642-a789-dba6de6938a4`. A subsequent read-only API audit confirmed the live source exactly matches the tested `firestore.rules`. No production student records were read, created, modified or deleted during testing.

## Verified Firebase configuration

| Setting | Verified value |
|---|---|
| Project | `itpec-textbook` |
| Web app | `1:959099491967:web:79ee8a1d34410e83e2d14a`, ITPEC Textbook |
| Database | `(default)`, Firestore Native / Standard |
| Location | `asia-southeast1` (Singapore) |
| Billing | `billingEnabled: false`; no billing changes |
| Providers | Google enabled; Anonymous remains enabled in console but is never used by the application and is denied by progress rules |
| Authorized domains | `localhost`, `127.0.0.1`, `itpec-textbook.firebaseapp.com`, `itpec-textbook.web.app`, `itpectextbook.com` |
| Auth domain | `itpec-textbook.firebaseapp.com` |
| Public website | Not deployed |

The existing web app was verified rather than duplicated. Added only the requested development loopback address and future domain to Auth's allowed domains, preserving existing entries. Updated Astro's canonical site to `https://itpectextbook.com`.

The supplied web configuration is public Firebase client configuration. Astro environment names follow `PUBLIC_FIREBASE_*`; `.env.example` contains only public configuration. The production project and bucket remain pinned to this textbook project. Emulation explicitly selects `demo-itpec-textbook` and is restricted to loopback hosts. No Admin/service-account credentials enter frontend code. Owner inspection scripts use the existing Firebase CLI login in memory, print sanitized configuration, and never export credentials. The CLI is pinned locally for reproducible tooling.

## Account experience

All published reading and question practice remain free and accessible without registration. Guests use the existing local repository with no Auth initialization, Anonymous sign-in, Firestore listeners, cloud reads or cloud writes. The prior Analytics integration remains browser-only, and learning records are not custom Analytics events.

The account panel and optional activity reminder provide Google sign-in without a forced modal. Firebase's Google popup uses account selection. Cancellation, popup blocking, unauthorized domains and network errors leave guest learning available. Account identity, synchronization state, retry and sign-out controls appear in the progress page; the header also indicates sync state. Auth persistence restores only an account explicitly chosen on this browser.

## Progress and conflict behavior

The existing `GuestProgressStore`, React subscriptions and `ProgressSyncAdapter` contract were extended. Reading and practice components continue to use the same progress API.

| Record | Identity and merge behavior |
|---|---|
| Attempt | `attempt:{attemptId}`; immutable, stable IDs, union of histories. Transaction checks an existing record before creating it. Replays cannot duplicate uploads or alter an existing cloud attempt. |
| Bookmark | `bookmark:{questionId}`; true/false value with logical clock and device ID. Removals remain as tombstones. |
| Completion | `completion:{sectionId}`; same tombstone/conflict policy as bookmarks. |
| Reading | `reading:latest`; validated same-origin section and anchor. Raw scroll updates remain local; the latest position is checkpointed during a foreground sync. |

Each account has its own durable local records, pending IDs and server cursor under `itpecTextbook:account:{uid}:v1`. Guest migration merges this cache and remote history instead of overwriting cloud data. It first claims the guest source for the intended UID in an atomic localStorage write, then merges and clears the source after account persistence succeeds. Interrupted transfers stay recoverable by that UID and are hidden from a new guest or different account. A failed claim leaves guest data untouched and avoids importing it into the account. Storage warnings report unavailable persistence.

Mutable conflicts compare a monotonic local clock, seeded from wall time and advanced beyond observed clocks; device ID resolves ties. Latest changes normally win, while exactly concurrent edits converge deterministically. Device clock skew may affect which independent offline edit wins; this is a merge policy, not an authoritative timeline. An immutable cloud attempt wins a collision on the same attempt ID. Incorrect attempts remain in history after a successful retry.

Meaningful changes debounce for 2.5 seconds. Foreground refresh runs at most once per minute when idle, plus sign-in, reconnect, foreground return and explicit retry. An incremental `(updatedAt, document ID)` cursor prevents repeated full history downloads; 200-record query pages cover large histories. Transactions process up to 100 pending records at a time, preserving newer cloud state and acknowledging only records whose versions still match. New local edits made during an upload remain pending.

There are no Firestore snapshot listeners, no persistent shared Firestore disk cache, and no server writes on individual scroll events. The first account/device synchronization downloads that account's history once; a fully synced explicit sign-out clears the local cache, so a later sign-in downloads it again. An idle foreground poll still incurs Firestore's minimum query cost; Spark quota limits still apply.

Offline and failed operations retain the UID-specific outbox. Backoff increases from five seconds to five minutes; permission/auth failures stop automatic retry until a new trigger. Browser storage denial or quota exhaustion falls back to the existing in-memory session with a visible warning: persistence cannot be guaranteed when the browser refuses writes. Corrupt files are preserved for recovery rather than overwritten.

Sign-out stops the sync controller and invalidates in-flight results before clearing the active view and session reading pointer. Storage events clear other tabs immediately. Synced account caches are cleared; an unsynced outbox stays isolated for the same UID. Account switching never imports the previous account into the next one. These application boundaries do not encrypt browser storage against someone with direct access to the browser profile or developer tools.

## Verification

Commands are documented in the README. Tests use the separate `demo-itpec-textbook` project and loopback Auth/Firestore emulators; no real Google users or production learning data are created. Google popup browser tests permit the SDK's required static JavaScript from `apis.google.com`, while production Auth/Firestore API requests are blocked. Optional emulator CDN fonts/styles are blocked.

- TypeScript and Astro diagnostics: pass, no errors/warnings/hints.
- Unit/component tests: 42 passing, including migration, interrupted transfer, account isolation, offline/retry, duplicate attempts, concurrent edits and stale responses.
- Rules and real SDK emulator tests: 10 passing (7 security rules tests and 3 Auth/Firestore integration tests). Covers unauthenticated/Anonymous/cross-user denials, valid owner access, malformed writes, immutable attempts, two devices, removals, pagination, incremental cursors and UID guards.
- Existing production browser tests: 11 passing, including original reading/practice flows, browser Back, storage failure, static HTML, keyboard/zoom, zero guest external requests and 320–1280px viewports.
- Account browser tests: 2 scenarios cover Google popup, migration, cross-device union, offline replay, account switching, mobile layout and cross-tab sign-out/outbox recovery.
- Production build: validates all 420 published questions and approved images, original static lesson, private progress metadata, and absence of old project credentials/dependencies.

The optional Auth/Firestore code is loaded only when accounts are used. Its Firebase vendor chunk currently triggers Vite's advisory 500 kB chunk warning; static reading and guest mode do not load that optional chunk. Browser verification uses Chromium, not a physical Safari/Firefox device. Live Google consent and a deployed production domain were not exercised, because production account creation and website deployment were outside the authorized test scope.

## Deployment and remaining setup

No website Hosting configuration/deployment, billing attachment, paid plan upgrade, Functions, Cloud Run, App Hosting, VM or Storage bucket was created. The old practice repository was not modified. The existing bucket name in client configuration is metadata only; this integration performs no Storage operations.

No additional Firebase console setup is required for the verified local Google provider and authorized domains. Future public launch still needs the separately authorized hosting/DNS/HTTPS work and a real-browser Google consent smoke test on that deployed domain. The website has deliberately not been published.

## Official references

- [Google sign-in for web](https://firebase.google.com/docs/auth/web/google-signin)
- [Security rules emulator testing](https://firebase.google.com/docs/rules/unit-tests)
- [Connect the Auth emulator](https://firebase.google.com/docs/emulator-suite/connect_auth)
- [Firestore transactions](https://firebase.google.com/docs/firestore/manage-data/transactions)
- [Update Auth project configuration with a field mask](https://docs.cloud.google.com/identity-platform/docs/reference/rest/v2/projects/updateConfig)
