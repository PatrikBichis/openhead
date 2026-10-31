# AGENTS.md

Working rules for coding agents in this repository. `PLAN.md` (Swedish) is the source of truth for scope, decisions and the order of work; do not deviate from its "Beslut och antaganden" without the owner's say-so. Work the steps in "Arbetsordning" in order and check each step's acceptance criterion before starting the next. `README.md` describes the product.

## Target hardware

- Baseline device is **iPhone 12** (A14, iOS 17+). Every feature must work there. Newer devices (e.g. iPhone 18 Pro used for testing) may only be used for verification, never as a requirement: no APIs, sensors (LiDAR) or performance budgets an iPhone 12 lacks.
- `IPHONEOS_DEPLOYMENT_TARGET = 17.0`. Universal app.
- Android/ARCore may come later; keep `protocol/` and `face/` platform-neutral.
- ROS 2 stays out of this repo; a bridge is built separately on the `openhead` Python package if needed.

## Development machine

- Windows 11 with an AMD GPU (no CUDA). WSL (Ubuntu 24.04) is available when a Linux tool is needed.
- No Mac and no local Swift: iOS is built and signed only in GitHub Actions (`macos-15`); generated Swift models are compiled on Linux in `protocol.yml`. Keep macOS jobs path-filtered.
- Python: always via **uv** (`uv sync`, `uv run ...`); the venv lives in `python/.venv`. Never `pip install` into the system Python.
- Node 22+ for the face engine (`npm ci` in `face/`) and for quicktype (`npx`).
- GitHub CLI: `C:\Program Files\GitHub CLI\gh.exe` (may not be on PATH in agent shells).

## Rules from the plan

- Python models (pydantic) and Swift models are generated from `protocol/schema` by `tools/protocol.py generate`; hand-written copies are not allowed. Commit the generated files; CI fails if they are stale.
- A schema change updates `protocol/CHANGELOG.md` in the same commit; `protocol.yml` fails otherwise.
- Themes are validated against `theme.schema.json` / `expressions.schema.json` by `tools/protocol.py check`.
- `face/dist` is never committed; it is built by `face.yml` and by the iOS workflows before `xcodegen`, so the app never ships a stale engine.
- No face logic in Swift: the iOS app hosts `face/dist` in a WKWebView.

## What to do on every change

1. **Level 1 (PC, seconds).** Build the engine and run its tests; run the protocol checks and pytest:
   ```bash
   uv run --project python python tools/protocol.py check
   uv run --project python python tools/protocol.py generate --check
   cd python && uv run pytest -q
   cd face && npm run build && npm test
   ```
   From step 4: run the scenarios against `openhead sim --headless`.
2. **iOS shell changed:** push and wait for `ios-check.yml` (`gh run watch`), read its screenshots artifact.
3. **Sensors or performance changed:** run the scenario against the desk device (level 2) and put the screenshot and log excerpt in the PR description.
4. Before claiming something works, run the command that proves it and read the output (`.claude/skills/verification-before-completion`).

See `docs/dev-loop.md` for the three levels in detail.

## Secrets

- Secrets go in `.env` (git-ignored). Every key must also be listed, empty, in `.env.example` with a comment.
- Never commit certificates, `.p8`, `.p12` or provisioning profiles. Signing files live in `~/.appstoreconnect/openhead/`; `tools/apple_setup.py` manages them and the GitHub secrets (see `docs/ios.md`).

## Commits

- Small, frequent commits with a message that says what and why.

## Agent resources in this repo

- Skills: `.claude/skills/` (installed with `npx skills add ... -a claude-code --copy`, pinned in `skills-lock.json`). Update with `npx skills update`.
- MCP: `.mcp.json` registers DeepWiki (`https://mcp.deepwiki.com/mcp`) for questions about upstream repos, e.g. `modelcontextprotocol/python-sdk`, `yonaskolb/XcodeGen`, `fastlane/fastlane`, `r0x0r/pywebview`, `microsoft/playwright`, `glideapps/quicktype`.
- See `docs/agents.md` for why each skill is here.
