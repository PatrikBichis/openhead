# AGENTS.md

Working rules for coding agents in this repository. `PLAN.md` (Swedish) is the source of truth for scope and decisions; do not deviate from its "Beslut och antaganden" without the owner's say-so. `README.md` describes the product.

## Target hardware

- Baseline device is **iPhone 12** (A14, iOS 17+). Every feature must work there. Newer devices (e.g. iPhone 17/18 Pro used for testing) may only be used for verification, never as a requirement: no APIs, sensors (LiDAR) or performance budgets that an iPhone 12 lacks.
- `IPHONEOS_DEPLOYMENT_TARGET = 17.0`. Universal app.
- Android/ARCore may come later; keep the protocol and face engine platform-neutral (nothing iOS-specific in `protocol/` or `face/`).

## Development machine

- Windows 11 with an AMD GPU (no CUDA). WSL (Ubuntu 24.04) is available when a Linux tool is needed.
- No Mac: iOS is built and signed only in GitHub Actions (`macos-15` runners). Keep macOS jobs path-filtered.
- Python: always via **uv** (`uv sync`, `uv run ...`); the venv lives in `python/.venv`. Never `pip install` into the system Python.
- Node 22+ for the face engine; `npm ci` in `face/`.
- GitHub CLI: `C:\Program Files\GitHub CLI\gh.exe` (may not be on PATH in agent shells).

## Secrets

- Secrets go in `.env` (git-ignored). Every key must also be listed, empty, in `.env.example` with a comment.
- Never commit certificates, `.p8`, `.p12` or provisioning profiles.

## Commits

- Small, frequent commits with a message that says what and why.
- Generated code (models from schema) is regenerated, never edited by hand.
- A schema change updates `protocol/CHANGELOG.md` in the same commit.

## Verification loop

Before claiming something works, run it (see `.claude/skills/verification-before-completion`):

1. Level 1 (PC): build `face/`, run Playwright and `uv run pytest`, run scenarios against `openhead sim --headless`.
2. Level 2 (device on desk): `openhead run scenarios/x.yaml --device <host>` or MCP tools against a TestFlight build in dev mode.
3. Level 3 (CI): push and read `ios-check.yml` / `ios-testflight.yml` results with `gh run view`.

## Agent resources in this repo

- Skills: `.claude/skills/` (installed with `npx skills add ... -a claude-code --copy`, pinned in `skills-lock.json`). Update with `npx skills update`.
- MCP: `.mcp.json` registers DeepWiki (`https://mcp.deepwiki.com/mcp`) for questions about upstream repos, e.g. `modelcontextprotocol/python-sdk`, `yonaskolb/XcodeGen`, `fastlane/fastlane`, `r0x0r/pywebview`, `microsoft/playwright`.
- See `docs/agents.md` for why each skill is here.
