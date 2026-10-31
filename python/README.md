# openhead (Python)

Client library, desktop simulator, scenario runner and CLI for the OpenHead protocol. See the repository [README](../README.md).

```bash
cd python
uv sync                                   # .venv with the [sim] extra and dev tools
uv run playwright install chromium        # once, for the simulator
(cd ../face && npm ci && npm run build)   # the simulator renders face/dist
uv run pytest -q
```

## Simulator

```bash
uv run openhead sim                       # window, idle motion, pairing code 0000 (dev mode)
uv run openhead sim --headless            # no window, no idle motion (tests, agents)
```

Speaks the same protocol as the iOS app on port 8765 (screenshots on 8766), advertises `_openhead._tcp` over mDNS, validates every incoming message against the JSON Schema and renders `face/dist` in Chromium through Playwright. Paired clients are kept in `~/.openhead/sim-device-tokens.json`. Synthetic IMU (a head slowly looking around) and status.

## CLI

```bash
uv run openhead pair 0000 --device localhost
uv run openhead emotion curious --device localhost
uv run openhead screenshot -o face.png --device localhost
uv run openhead run ../scenarios/smoke.yaml --device localhost --compare
uv run openhead --help
```

`--device` defaults to `$OPENHEAD_DEVICE`, else mDNS discovery. Tokens live in `~/.openhead/tokens.json` (`$OPENHEAD_TOKENS`).

## Library

```python
from openhead.client import Head

head = await Head.connect("head-01.local")
if not head.paired:
    await head.pair("123456")              # code shown on the device
await head.face.set_theme("halloween")
await head.face.set_emotion("curious", 0.7)
png = await head.system.screenshot()       # dev mode
async for sample in head.subscribe("imu", 100):
    print(sample.q)
```

The client reconnects with backoff and re-subscribes; `head.face.envelope(level)` streams the mouth envelope without acks.

## Scenarios

YAML files in `scenarios/` (steps: `set_theme`, `set_emotion`, `look_at`, `blink`, `show_image`, `show_web`, `show_face`, `clear_display`, `envelope`, `wait_ms`, `screenshot`, `expect_log`, `expect_status`). `openhead run` writes `report.json`, `log.txt` and screenshots to `scenario-reports/`; with `--compare` screenshots are checked against `scenarios/golden/<name>/` (1 % tolerance). `tests/test_scenarios.py` runs every scenario against the headless simulator.

## Generated code

`src/openhead/protocol/models.py`, `registry.py` and `schema.json` are generated from `protocol/schema` by `tools/protocol.py`; do not edit them by hand.
