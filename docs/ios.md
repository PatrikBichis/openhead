# iOS: Apple setup, TestFlight and device

The iOS app is built and signed only by `ios-testflight.yml` in GitHub Actions, started manually; no Mac is needed and no tests run there. Baseline device is iPhone 12 (iOS 17).

## Apple setup (done once)

| Item | Value |
| --- | --- |
| Team ID | `GJX3M68CH3` (individual account) |
| Bundle ID | `se.bichis.openhead` |
| App name in App Store Connect | OpenHead Robot Face (app id `6829240049`) |
| TestFlight | internal group "Internal", access to all builds; team admins added as testers |
| Distribution certificate | Apple Distribution, created by `tools/apple_setup.py`, expires 2027-10-31 |
| Provisioning profile | "OpenHead App Store" (`IOS_APP_STORE`), expires 2027-10-31 |

Steps:

1. Account Holder accepts the latest Program License Agreement (developer.apple.com); the API returns `PLA_NOT_ACCEPTED` otherwise.
2. App Store Connect → Users and Access → Integrations → Team Keys: create a key with role **Admin** (App Manager can read but not create certificates or profiles). Save the `.p8` under `apps/ios/keys/` (git-ignored) or outside the repo, and fill `ASC_KEY_ID`, `ASC_ISSUER_ID`, `ASC_PRIVATE_KEY_PATH` in `.env`.
3. Set `IOS_BUNDLE_ID` in `.env`, then:

   ```bash
   uv run --project python python tools/apple_setup.py --github
   ```

   It finds or creates the bundle ID, an Apple Distribution certificate (private key generated locally) and the App Store profile; writes them to `~/.appstoreconnect/openhead/`; fills `.env` (paths, generated passwords); and sets the GitHub secrets and variables. It is idempotent: re-run it when the profile or certificate nears expiry.
4. Create the app record in App Store Connect (My Apps → + → New App: iOS, name "OpenHead Robot Face", bundle ID `se.bichis.openhead`, SKU `openhead`). The public API cannot create app records.
5. Run `tools/apple_setup.py` again: it records `ASC_APP_ID`, creates the internal TestFlight group "Internal" (access to all builds) and adds the team's Account Holder and Admins as testers. On each test device install TestFlight, sign in with that Apple ID and turn on automatic updates for OpenHead.

GitHub secrets: `APPLE_DIST_CERT_P12_B64`, `APPLE_DIST_CERT_PASSWORD`, `APPLE_PROVISIONING_PROFILE_B64`, `ASC_KEY_ID`, `ASC_ISSUER_ID`, `ASC_PRIVATE_KEY`, `KEYCHAIN_PASSWORD`. Variables: `APPLE_TEAM_ID`, `IOS_BUNDLE_ID`, `IOS_SCHEME`.

## Building and uploading

```bash
gh workflow run ios-testflight.yml -f upload=false   # unsigned compile check (Swift changes)
gh workflow run ios-testflight.yml                   # signed archive, uploaded to TestFlight
gh run watch
uv run --project python python tools/testflight_status.py --wait <build>   # Apple's processing
```

The workflow runs on `macos-26` with the newest Xcode 26 (Apple requires the iOS 26 SDK for uploads since April 2026). It builds `face/dist`, copies it to `OpenHead/Resources/face`, runs XcodeGen, archives with manual signing (temporary keychain), and uploads with `xcodebuild -exportArchive` using the App Store Connect API key (`ExportOptions.plist`, destination `upload`). It does not wait for processing. The build number is the workflow run number; the version comes from `protocol/VERSION`.

The project is generated from `apps/ios/project.yml`; `OpenHead.xcodeproj` and `OpenHead/Info.plist` are not committed. On a Mac: build the face, copy `face/dist` to `apps/ios/OpenHead/Resources/face`, `xcodegen generate`, open the project.

## The app

| Module | What it does |
| --- | --- |
| `Link/` | WebSocket server (Network.framework) on the configured port, advertised as `_openhead._tcp`; pairing and Keychain tokens; every message decoded with the generated models (`Protocol/`) before it runs; commands run in arrival order; `imu`, `status`, `log` subscriptions; screenshot URLs on port + 1 |
| `Face/` | `face/dist` in a WKWebView served on `openhead-face://`, driven through `window.openhead` (face, `show`, `clear`, `subtitle`); a video that ends reports back so `status` shows the face |
| `Display/` | what fills the screen; images (incl. SVG, GIF), video, the corner face and subtitles are drawn by the face's web layer (`face/src/screen.ts`), web pages natively below it (the web view turns transparent). ATS allows plain http media on the LAN in web views only |
| `Sensors/` | CoreMotion device motion (≤ 100 Hz) in the protocol's frame and sign conventions, mount offset |
| `Logging/` | OSLog per subsystem plus a 2000-line ring buffer for `system.logs` and the `log` topic |
| `Settings/` | name, port, dev mode, theme when offline, IMU mounting, paired clients (revoke) |

**Settings:** long-press anywhere on the face for 1.5 s. Name and port changes apply after restarting the app.

**Pairing:** when an unknown client says hello, a 6-digit code is shown for 60 s; five wrong codes lock pairing for five minutes. Paired clients are listed (and can be revoked) in settings.

**Status strip** (top right, only when there is something to show): link problem, number of connected clients, dev mode, thermal warning.

## App Store media

`tools/media.py` renders the shipped face engine in headless Chromium at Apple's exact sizes (build `face/dist` first):

```bash
cd python
uv run --with imageio-ffmpeg python ../tools/media.py            # stills, creative and preview
```

| Output | What |
| --- | --- |
| `apps/ios/appstore/screenshots/iphone-6.9/` | 8 screenshots (6 faces, 2 camera HUDs), 2868 × 1320 (6.9" iPhone, landscape) |
| `apps/ios/appstore/screenshots/ipad-13/` | 8 screenshots, 2752 × 2064 (13" iPad, landscape) |
| `apps/ios/appstore/creative/header.png` | product page header, 3840 × 1646 (21:9) |
| `apps/ios/appstore/creative/search-results.png` | search results art, 1920 × 1280 (3:2) |
| `apps/ios/appstore/previews/iphone-6.9-landscape.mp4` | app preview, 1920 × 886, 30 fps, H.264 + stereo AAC, 28 s, with speech |
| `docs/media/` | README GIF, mp4, theme pictures and emotion sheets |

Upload them with `tools/appstore_media.py` (below). The 6.9" set is scaled down for smaller iPhones and the 13" set for smaller iPads. Speech uses a Windows SAPI voice; elsewhere the preview has a silent track. The settings pictures in `docs/media/settings_*.jpg` are real device screenshots.

## Store texts

The texts shown in TestFlight and on the App Store page live in `apps/ios/appstore/metadata/`: one folder per App Store language (`en-US/` is the primary, `sv/` Swedish (App Store Connect calls it `sv`, not `sv-SE`): name, description, subtitle, promotional text, keywords, URLs; a language missing in App Store Connect is created) and `testflight/` for the TestFlight description and "What to Test". Apple locks the page texts and app info while a version is in review; run the tool again once a version can be edited. Edit them there, then:

```bash
uv run --project python python tools/appstore_metadata.py --dry-run   # what would change
uv run --project python python tools/appstore_metadata.py             # push; --build N for What to Test
```

It updates the version being prepared and the app info (nothing is submitted for review): version number from `protocol/VERSION` with its newest valid build, release type (manual), copyright, categories, age rating (`age_rating.json`) and review notes (`review_notes.txt`). Builds must be exported with `testFlightInternalTestingOnly` false (`ExportOptions.plist`) to be selectable.

Screenshots, the header and search-results art and the app preview are uploaded with `uv run --project python python tools/appstore_media.py [screenshots] [creative] [previews]`; it replaces what is there. Header and search art are creative assets (2026): an image in the app's asset library (`appAssetLibraryImages`, category `CREATIVE_ASSETS`) placed on the version's localization (`appAssetLibraryPlacements`, `PRODUCT_PAGE_HEADER_ASSET` and `APP_STORE_SEARCH_RESULTS_ASSET`). They go live with the released version. The privacy policy, support and marketing URLs point to the project site, GitHub Pages from `docs/` on `main` (`index.html`, `privacy.html`, `support.html`, in English; Swedish under `docs/sv/`): https://patrikbichis.github.io/openhead/. Left for the web UI before the first submission: the App Privacy answers (not in the API; the app collects no data), App Review contact, price and availability, and content rights.

## Running on a robot

- Mount the phone in landscape (left or right); the app does not rotate to portrait on iPhone.
- The app must be in the foreground: iOS suspends the server in the background. Use Guided Access (Settings → Accessibility → Guided Access) to keep it there; the screen never dims while the app runs.
- The phone and the robot's computer must be on the same Wi-Fi network (no Wi-Fi Direct). Allow "Local Network" when iOS asks on first launch, or the head cannot be reached.
- Watch the thermal warning in the status strip: `serious` or `critical` means the phone is throttling.
- Turn dev mode on (settings) for screenshots, logs and diagnostics from the host; leave it off on a robot in use.
