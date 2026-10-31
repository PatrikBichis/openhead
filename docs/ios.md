# iOS: Apple setup, TestFlight and device

The iOS app is built and signed only by `ios-testflight.yml` in GitHub Actions, started manually; no Mac is needed and no tests run there. Baseline device is iPhone 12 (iOS 17).

## Apple setup (done once)

| Item | Value |
| --- | --- |
| Team ID | `GJX3M68CH3` (individual account) |
| Bundle ID | `se.bichis.openhead` |
| App name in App Store Connect | OpenHead Robot Face |
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
5. TestFlight → Internal Testing: create a group and add the testers; turn on automatic updates on the desk devices.

GitHub secrets: `APPLE_DIST_CERT_P12_B64`, `APPLE_DIST_CERT_PASSWORD`, `APPLE_PROVISIONING_PROFILE_B64`, `ASC_KEY_ID`, `ASC_ISSUER_ID`, `ASC_PRIVATE_KEY`, `KEYCHAIN_PASSWORD`. Variables: `APPLE_TEAM_ID`, `IOS_BUNDLE_ID`, `IOS_SCHEME`.

## Running on a robot

To be written with step 7: foreground requirement, Guided Access, shared Wi-Fi, thermal warnings.
