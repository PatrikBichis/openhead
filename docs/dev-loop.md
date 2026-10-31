# Developer loop

The head is built to be validated by an agent, not only by a person holding the phone. **All testing runs locally**; GitHub Actions only builds the iOS app and uploads it to TestFlight, started by hand, to keep Actions minutes to a minimum.

| Level | Where | Time | Proves | Status |
| --- | --- | --- | --- | --- |
| 1 | PC (Windows, WSL) | about a minute | protocol, Python/Swift models, face rendering, simulator, scenarios, CLI | available |
| 2 | Device on the desk | minutes | WKWebView, sensors, ARKit, performance, thermals | step 8 |
| 3 | TestFlight build (GitHub Actions, manual) | ~10 min | the app builds, signs and uploads | step 7 |

## Level 1: PC

```bash
uv run --project python python tools/check.py          # everything (also runs as the pre-push hook)
uv run --project python python tools/check.py --fast   # protocol + Python only
cd face && npm run gallery                             # test-results/gallery.png to review by eye
```

`tools/check.py` runs: protocol validation, generated-file check, ruff, face build with type check, Playwright golden images and API tests, pytest (contract tests, the protocol against the headless simulator, every scenario in `scenarios/` with screenshot goldens, and the CLI end to end), and the Swift contract test when Swift is available.

Install the git hooks once:

```bash
uv run --project python pre-commit install
```

Pre-commit runs the quick checks (schema validation, CHANGELOG rule, generated files, ruff); pre-push runs the full `tools/check.py`.

Golden images live in `face/tests/golden/` and are compared with a tolerance (`maxDiffPixelRatio 0.01`). After an intentional visual change: review the gallery, `npm run test:update`, commit the new goldens.

### Swift on Windows (via WSL)

There is no Swift for the iOS SDK on Windows, but the generated models only use Foundation, so a Linux Swift toolchain in WSL compiles and tests them. Once Swift is installed in WSL (`swiftly`, https://www.swift.org/install/linux/), `tools/check.py` picks it up automatically; without it, the Swift check is reported as skipped and the models are first compiled by the TestFlight build.

## Level 2: device on the desk (step 8)

An iPhone 12 (baseline) or the iPhone 18 Pro stands charged with the latest TestFlight build, app in the foreground, dev mode on, paired with the agent's machine. TestFlight automatic updates bring new builds to it without hands. The agent runs `openhead run scenarios/x.yaml --device head-01.local` or uses the MCP tools: `take_screenshot` to see, `tail_logs` to understand, `get_diagnostics` when something is wrong. This is the only way to verify the iOS shell, ARKit, cameras, performance and thermals without a Mac.

**Keep the app in front.** iOS freezes an app in the background but keeps its port open, so a client then connects and times out "during opening handshake". Using the test phone for anything else (including chatting with the agent over Remote Control) does this; use another device for that, or Guided Access on the phone.

**Known limitation:** screenshots taken while a video plays show black where the video is on iOS (the frame copy for the snapshot comes out black even with CORS); playback itself is fine.

### Latency and smoothness (step 9)

`tools/latency.py` measures a head: command round trip, how far the mouth lags a 25 Hz envelope (a 0.5 Hz sine, read back from screenshots) and whether it follows smoothly, and frame rate and thermal state. Dev mode on.

```bash
uv run --project python python tools/latency.py --out scenario-reports/latency-<device>
```

| Device | Round trip p50 / p95 | Envelope → mouth | Correlation | Frame rate | Date |
| --- | --- | --- | --- | --- | --- |
| Simulator (headless) | 1.3 / 1.7 ms | ~35 ms | 0.99 | 60 fps | 2026-10-31 |
| iPhone 18 Pro, iOS 26, weak Wi-Fi | 4.2 / 27 ms | ~70 ms | 0.99 | 60 fps, nominal | 2026-10-31 |
| iPhone 12 (baseline) | not measured yet | | | | |

The delay includes the mouth's attack smoothing (about 30 ms in the themes) and one frame; correlation near 1 means the mouth follows without jumps. The host sends at 25 Hz on average; on Windows its timer makes single gaps up to ~48 ms.

## Level 3: TestFlight build (step 7)

```bash
gh workflow run ios-testflight.yml      # only when a change is ready to try on the device
gh run watch
```

The job builds the face bundle, generates the Xcode project, archives, signs and uploads. It does not wait for Apple's processing (that would burn macOS minutes); the agent follows the build to Ready to Test locally through the App Store Connect API.

## Scenarios

```yaml
name: halloween-scared
steps:
  - set_theme: halloween
  - set_emotion: { name: scared, intensity: 1.0 }
  - wait_ms: 600
  - screenshot: halloween-scared.png
  - expect_log: { level: info, contains: "theme=halloween" }
  - expect_status: { theme: halloween, emotion: scared }
```

The runner reports pass/fail per step, saves screenshots and log excerpts, and against the simulator compares screenshots with goldens. The same file runs locally against the simulator, at level 2 and through the MCP tool `run_scenario`.

## What the agent does on each change

- Always: level 1 (`tools/check.py`).
- iOS shell changed: when ready, start a TestFlight build and verify on the device.
- Sensors or performance changed: run the scenario on the device and attach screenshot and log excerpt to the PR.
