# Developer loop

The head is built to be validated by an agent, not only by a person holding the phone. Every change is checked at the cheapest level that can prove it; the same scenario file runs at all three levels.

| Level | Where | Time | Proves | Status |
| --- | --- | --- | --- | --- |
| 1 | PC (Windows, WSL or CI Linux) | seconds | protocol, models, face rendering, simulator behaviour | protocol + face: available; simulator: step 4 |
| 2 | Device on the desk | minutes | WKWebView, sensors, ARKit, performance, thermals | step 8 |
| 3 | GitHub Actions | ~15 min | iOS build, XCUITest screenshots, TestFlight delivery | step 7 |

## Level 1: PC

```bash
uv run --project python python tools/protocol.py check             # schemas, examples, themes
uv run --project python python tools/protocol.py generate --check  # generated Python/Swift/docs up to date
cd python && uv run pytest -q                                      # contract tests (and, from step 4, protocol tests against the simulator)
cd face && npm run build && npm test                               # golden images per theme × emotion, engine API
cd face && npm run gallery                                         # test-results/gallery.png to review by eye
```

Golden images live in `face/tests/golden/` and are compared with a tolerance (`maxDiffPixelRatio 0.01`), so the same files pass on Windows and on CI Linux. After an intentional visual change: review the gallery, `npm run test:update`, commit the new goldens.

From step 4: `openhead sim --headless` serves the same protocol as the app; `openhead run scenarios/x.yaml` runs a scenario against it and `python.yml` does the same in CI.

## Level 2: device on the desk (step 8)

An iPhone 12 (baseline) or the iPhone 18 Pro stands charged with the latest TestFlight build, app in the foreground, dev mode on, paired with the agent's machine. TestFlight automatic updates bring CI builds to it without hands. The agent runs `openhead run scenarios/x.yaml --device head-01.local` or uses the MCP tools: `take_screenshot` to see, `tail_logs` to understand, `get_diagnostics` when something is wrong. This is the only way to verify ARKit, cameras, performance and thermals without a Mac.

## Level 3: CI (step 7)

`ios-check.yml` runs XCUITest on the simulator and uploads screenshots; `ios-testflight.yml` waits for App Store Connect to report Ready to Test and writes version, build number and time to the job summary. Read them with `gh run view` / `gh run download`.

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

The runner reports pass/fail per step, saves screenshots and log excerpts, and against the simulator compares screenshots with goldens. The same file runs in `python.yml`, at level 2 and through the MCP tool `run_scenario`.

## What the agent does on each change

- Always: level 1.
- iOS shell changed: push and wait for `ios-check.yml`.
- Sensors or performance changed: run the scenario on the device and attach screenshot and log excerpt to the PR.
