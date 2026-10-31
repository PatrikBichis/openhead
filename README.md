# OpenHead

**A phone or tablet as a robot's head: face, eyes, cameras, pose, and a protocol to drive it.**

OpenHead turns an iPhone or iPad into a self-contained robot head. The device renders an expressive face, streams its sensors (IMU, status, and later world pose, detected faces and GPS) and exposes a small command API over Wi-Fi. Anything that can open a WebSocket can drive it: a ROS 2 node on a Jetson, a Python script, or an LLM agent through the bundled MCP server.

The protocol is the product. The iOS app is the first client; the desktop simulator is the second.

---

## Why

Robot heads usually need a screen, a camera, an IMU, a localization stack and a Wi-Fi radio. A phone already has all of them, calibrated, in one battery-backed package. OpenHead makes that package addressable from the rest of the robot without the robot having to know anything about iOS.

- **Body-agnostic.** The head knows nothing about necks, servos or wheels. It reports its own pose; the robot owns the kinematics.
- **Data-driven face.** Looks and expressions are theme packs (JSON + assets), not code. Add a cartoon look or a Halloween look by adding a folder.
- **One API, two surfaces.** Streams and commands over WebSocket for controllers; the same commands as MCP tools for agents.
- **Runs without the robot.** A desktop simulator speaks the same protocol, so controllers and agents can be developed before a single servo moves.
- **Built to be validated by an agent.** Screenshots, structured logs and scripted scenarios are part of the protocol, not an afterthought.

---

## Architecture

```mermaid
flowchart LR
    subgraph Device["Head device (iPhone / iPad)"]
        Face["Face engine<br/>web-based · themes · expressions"]
        Display["Display<br/>image · web · overlay"]
        Sensors["Sensors<br/>IMU · status · (pose · faces · GPS)"]
        Cam["Cameras<br/>(v0.2)"]
        Link["Link<br/>WebSocket server · mDNS · pairing"]
        Face --- Link
        Display --- Link
        Sensors --- Link
        Cam --- Link
    end

    subgraph Host["Host (Jetson, PC, …)"]
        Py["openhead<br/>Python client library"]
        MCP["openhead mcp<br/>MCP server"]
        ROS["Robot controller<br/>(e.g. ROS 2 bridge, lives in the robot repo)"]
        Py --> MCP
        Py --> ROS
    end

    Agent["LLM agent<br/>Claude · local model · …"]

    Link <-- "WebSocket · JSON" --> Py
    Agent <-- "MCP (stdio)" --> MCP
```

The device is the server. Hosts discover it over mDNS (`_openhead._tcp`), pair once, and connect. The robot's own code is deliberately outside this repo; it depends on the `openhead` Python package and nothing else.

---

## What the head does

| Capability | Direction | Transport | Version |
| --- | --- | --- | --- |
| Face: theme, emotion, gaze, blink, mouth envelope | host → head | commands + envelope stream (20–30 Hz) | 0.1 |
| Display: image, web page, face, overlay | host → head | command; image by URL or base64 | 0.1 |
| Status: battery, thermal, mode, theme, emotion, link | head → host | subscription, 1 Hz | 0.1 |
| IMU: quaternion, gyro, accel in device frame | head → host | subscription, ≤ 100 Hz | 0.1 |
| Log stream and diagnostics | head → host | subscription + commands (dev mode) | 0.1 |
| Screenshot of what is on screen | host → head | command (dev mode) | 0.1 |
| Pose: position + orientation in world frame (ARKit) | head → host | subscription, ≤ 60 Hz | 0.2 |
| Faces: detected faces with bearing and size | head → host | subscription, ≤ 15 Hz | 0.2 |
| Cameras: still / clip from front or back | host → head | command, result over HTTP | 0.2 |
| GPS, barometer, magnetometer | head → host | subscription, low rate | 0.2 |

Minimum iOS/iPadOS 17. Universal app, full screen on iPad.

---

## Protocol in one picture

Every message is JSON with `type`, `ts`, `seq`. Commands carry an `id` and are answered with `ack` or `error`. Streams are opened with `subscribe` and carry a requested rate, which the device may clamp. Schemas live in [`protocol/schema/`](protocol/schema/) and the protocol follows semver from `0.1.0`.

```mermaid
sequenceDiagram
    autonumber
    participant H as Host (controller or agent)
    participant D as Head device

    H->>D: discover via mDNS (_openhead._tcp)
    H->>D: hello {client, protocol_version}
    D-->>H: pair_required {code_hint}
    Note over D: 6-digit code shown on screen for 60 s
    H->>D: pair {code}
    D-->>H: welcome {token, device, capabilities, themes}

    H->>D: subscribe {topic: "imu", rate_hz: 100}
    H->>D: subscribe {topic: "status", rate_hz: 1}
    loop while subscribed
        D-->>H: imu {q, gyro, accel, frame}
        D-->>H: status {...}
    end

    H->>D: face.set_emotion {name: "curious", intensity: 0.7}
    D-->>H: ack {id}
    loop while speaking (no ack)
        H->>D: face.envelope {level: 0.42}
    end
    H->>D: display.show {type: "image", source, overlay: "face-corner"}
    D-->>H: ack {id}
```

### Command families

| Family | Commands | Version |
| --- | --- | --- |
| `face.*` | `set_theme`, `set_emotion`, `look_at` (screen / head frame), `blink`, `envelope`, `list` | 0.1 |
| `display.*` | `show` (face, image, web), `clear` | 0.1 |
| `system.*` | `status`, `screenshot`, `logs`, `diagnostics`, `settings` | 0.1 |
| `mode.*` | `set` (`idle`, `sensing`, `capture`), `get` | 0.1 (`idle` only), 0.2 |
| `pose.*` | `reset`, `save_map`, `load_map` | 0.2 |
| `camera.*` | `capture`, `stream` | 0.2 |

Error codes: `unauthorized`, `unsupported`, `busy`, `invalid_params`, `dev_mode_required`, `rate_limited`.

---

## Face engine and themes

The face is a standalone web app (TypeScript, Canvas 2D) hosted in a WKWebView on iOS and in a window in the simulator. It exposes a tiny JavaScript API (`setTheme`, `setEmotion`, `setGaze`, `setEnvelope`, `blink`, `tick`) and knows nothing about the network.

```mermaid
flowchart TB
    Host["Host command<br/>set_emotion('happy', 0.8)"] --> Blend["Expression blender<br/>weights · transitions · idle motion"]
    Env["Mouth envelope<br/>from host TTS"] --> Blend
    Gaze["Gaze target<br/>screen · head frame"] --> Blend
    Blend --> Params["Face parameters<br/>eye open · tilt · pupil · gaze · squint<br/>mouth open · width · curve · asym · teeth"]
    Theme["Theme pack<br/>palette · shapes · assets · idle · presets"] --> Render["Renderer"]
    Params --> Render
    Render --> Screen["Screen"]
```

A theme is a folder:

```
face/themes/halloween/
├── theme.json        # palette, eye/mouth shapes (preset | path | image), render style, idle behaviour
├── expressions.json  # parameter preset per emotion name, plus theme-specific extras (e.g. "cackle")
└── assets/           # optional PNG/SVG for eyes, mouth, background
```

Shared emotion names, required in every theme (missing ones fall back to `neutral`):
`neutral` · `happy` · `curious` · `thinking` · `surprised` · `sad` · `angry` · `sleepy` · `scared` · `mischievous`

Built-in themes in v0.1: `cartoon`, `minimal`, `halloween`. Hosts discover themes and their extra expressions with `face.list`.

Voice is **not** part of a theme. A *persona* (theme + resting emotion + TTS voice + speaking style) is defined on the host, which is where the audio lives.

---

## MCP server

`openhead mcp` exposes the head to any MCP-capable agent using the same client library the controllers use. It is a thin adapter: no second implementation of the protocol.

| MCP | Maps to |
| --- | --- |
| Tools `list_themes`, `set_theme`, `set_emotion`, `look_at`, `show_image`, `show_web`, `show_face` | `face.*`, `display.*` |
| Tools `get_status`, `take_screenshot` (returns image), `tail_logs`, `get_diagnostics` | `system.*` (dev mode required for the last three) |
| Tool `wait_for(topic, predicate, timeout_s)` | A subscription that returns on first match (`status`, `log`; `faces` in 0.2) |
| Tool `run_scenario(path)` | Runs a YAML scenario and returns the report with screenshots |
| Resources `openhead://status`, `openhead://themes`, `openhead://logs` | Latest cached value |

High-rate streams (IMU, envelope) are intentionally not exposed over MCP; use the WebSocket API. Transport is stdio in v0.1; Streamable HTTP is planned for v0.2.

```bash
openhead mcp --device auto        # stdio, for Claude Code / Claude Desktop / local agents
```

---

## Developer loop

The head is built to be validated by an agent, not only by a person holding the phone. The same scenario runs at three levels.

```mermaid
flowchart LR
    A["Coding agent"] -->|MCP / CLI| S["Level 1<br/>openhead sim --headless<br/>Playwright golden images"]
    A -->|MCP / CLI| D["Level 2<br/>Device on the desk<br/>TestFlight build · dev mode"]
    A -->|GitHub| CI["Level 3<br/>TestFlight build<br/>(manual, no tests)"]
    S --> R["Screenshots · logs · scenario report"]
    D --> R
    CI --> R
    R --> A
```

- `take_screenshot` returns what is on the screen as an image.
- `tail_logs` streams the app's structured log; every received command is logged with its `seq`.
- `run_scenario` executes a YAML scenario (set theme, set emotion, wait, screenshot, assert on log and status) against the simulator or a real device.
- Screenshot, logs and diagnostics answer only when **dev mode** is enabled in the app's settings.

```yaml
name: halloween-scared
steps:
  - set_theme: halloween
  - set_emotion: { name: scared, intensity: 1.0 }
  - wait_ms: 600
  - screenshot: halloween-scared.png
  - expect_status: { theme: halloween, emotion: scared }
```

See [`docs/dev-loop.md`](docs/dev-loop.md).

---

## Security

- Pairing: the device shows a 6-digit code for 60 s when an unknown client connects. A correct code yields a per-client token (Keychain on the device, `~/.openhead/tokens.json` on the host). Five failed attempts lock pairing for five minutes.
- All commands and subscriptions require a valid token. mDNS advertises name and port only.
- Dev mode gates `system.screenshot`, `system.logs`, `system.diagnostics` and `settings.set`. Off by default; shown as an icon in the status bar.
- Screenshot and photo URLs are served by the device over HTTP with the token in a header and expire after 60 s.
- No TLS in v0.1; the network is assumed private. TLS is planned for v0.2 and advertised through `capabilities`.
- Clients can be revoked in the app's settings. The MCP server is a client like any other.

---

## Repository layout

```
openhead/
├── protocol/
│   ├── schema/             # JSON Schema (2020-12): envelope, commands/, topics/, theme.schema.json
│   ├── VERSION             # 0.1.0 – also drives the app's MARKETING_VERSION
│   ├── CHANGELOG.md
│   └── docs/               # generated reference
├── face/                   # face engine (TypeScript + Canvas, Vite)
│   ├── src/
│   ├── themes/             # cartoon/ minimal/ halloween/
│   └── tests/              # Playwright golden images per theme × emotion
├── apps/ios/               # SwiftUI shell; project.yml for XcodeGen
│   ├── OpenHead/           # App/ Link/ Sensors/ Display/ Face/ Settings/ Logging/
│   ├── OpenHeadTests/
│   └── OpenHeadUITests/    # XCUITest with screenshots
├── python/                 # one package: openhead (extras: [mcp], [sim])
│   └── src/openhead/
│       ├── protocol/       # pydantic models generated from schema
│       ├── client/         # asyncio client
│       ├── sim/            # simulator: server + window running face/dist
│       ├── mcp/            # MCP server
│       └── cli/            # openhead discover|pair|screenshot|logs|emotion|theme|show|run|sim|mcp
├── scenarios/              # YAML scenarios, run against simulator and device
├── examples/
├── docs/                   # ios.md · dev-loop.md · themes.md
├── tools/                  # protocol.py · check.py (all local tests) · apple_setup.py
└── .github/workflows/      # ios-testflight (manual; the only workflow)
```

Python and Swift models are generated from the schemas by `tools/protocol.py` and committed; hand-written copies are not allowed. All testing runs locally (`tools/check.py`, also as the pre-push hook); GitHub Actions only builds the iOS app and uploads it to TestFlight. The face bundle is built in that workflow and copied into the app before each build.

---

## Quick start

**Without hardware**

```bash
pip install -e "python/[sim,mcp]"
openhead sim                                  # simulated head with a face window (pairing code 0000)
openhead pair 0000 --device localhost
openhead emotion curious && openhead screenshot -o face.png
openhead run scenarios/smoke.yaml
openhead mcp --device localhost               # expose it to an agent
```

**With an iPhone or iPad**

1. Install the app from TestFlight (see [`docs/ios.md`](docs/ios.md)) and put the device on the same Wi-Fi as the host.
2. Open the app; it shows a pairing code when the first client connects.
3. `openhead discover` then `openhead pair <code> --device head-01.local`.
4. `openhead run scenarios/smoke.yaml --device head-01.local`.

---

## Device support

| Device | Face | IMU / status | World pose (0.2) | Face tracking (0.2) |
| --- | --- | --- | --- | --- |
| iPhone 12 and later | yes | yes | ARKit, back camera | front camera, concurrent with world tracking (A12+) |
| iPad mini (5th gen+) | yes | yes | ARKit | on-device vision |
| iPad (7th gen+) | yes | yes | ARKit | on-device vision |
| Desktop simulator | yes | synthetic | synthetic | synthetic |

---

## Status

Early development. The protocol is unstable until `0.1.0` is tagged; robot integrations should track `main` until then and pin a tag afterwards.

- [x] 1. Repo skeleton, local schema validation
- [x] 2. Protocol schemas 0.1 with generated models and docs
- [x] 3. Face engine with three themes and golden-image tests
- [ ] 4. Simulator, Python client, CLI, smoke scenario
- [ ] 5. MCP server (stdio)
- [ ] 6. Apple Developer setup and secrets
- [ ] 7. iOS shell: link, pairing, face, status, settings, logs, screenshot → first TestFlight build
- [ ] 8. Device in the loop: smoke scenario green on simulator and device
- [ ] 9. IMU stream and envelope-driven mouth
- [ ] 10. Tag `0.1.0`

---

## License

Apache 2.0 (proposed). See [`LICENSE`](LICENSE).
