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
| `Face/` | `face/dist` in a WKWebView served on `openhead-face://`, driven through `window.openhead` |
| `Display/` | image (URL or data URI) and web page views; face in a corner with `overlay: face-corner` |
| `Sensors/` | CoreMotion device motion (≤ 100 Hz) in the protocol's frame and sign conventions, mount offset |
| `Logging/` | OSLog per subsystem plus a 2000-line ring buffer for `system.logs` and the `log` topic |
| `Settings/` | name, port, dev mode, theme when offline, IMU mounting, paired clients (revoke) |

**Settings:** long-press anywhere on the face for 1.5 s. Name and port changes apply after restarting the app.

**Pairing:** when an unknown client says hello, a 6-digit code is shown for 60 s; five wrong codes lock pairing for five minutes. Paired clients are listed (and can be revoked) in settings.

**Status strip** (top right, only when there is something to show): link problem, number of connected clients, dev mode, thermal warning.

## Running on a robot

- Mount the phone in landscape (left or right); the app does not rotate to portrait on iPhone.
- The app must be in the foreground: iOS suspends the server in the background. Use Guided Access (Settings → Accessibility → Guided Access) to keep it there; the screen never dims while the app runs.
- The phone and the robot's computer must be on the same Wi-Fi network (no Wi-Fi Direct). Allow "Local Network" when iOS asks on first launch, or the head cannot be reached.
- Watch the thermal warning in the status strip: `serious` or `critical` means the phone is throttling.
- Turn dev mode on (settings) for screenshots, logs and diagnostics from the host; leave it off on a robot in use.
