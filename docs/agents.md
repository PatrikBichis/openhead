# Agent skills and tools

Skills are stored in the repo so every clone and every agent gets the same set. They were picked from [skills.sh](https://skills.sh) for the OpenHead stack.

| Skill | Source | Used for |
| --- | --- | --- |
| `mcp-builder` | `anthropics/skills` | `openhead.mcp` (Python MCP SDK / FastMCP) |
| `webapp-testing` | `anthropics/skills` | Playwright checks of the face engine and simulator |
| `swiftui-pro` | `twostraws/swiftui-agent-skill` | iOS shell (SwiftUI, iPad resizability) |
| `swift-concurrency` | `avdlee/swift-concurrency-agent-skill` | `Link` (NWListener), sensors, Swift 6 strict concurrency |
| `github-actions` | `callstackincubator/agent-skills` | iOS simulator build artifacts and `gh run download` (written for React Native; use the patterns, not the RN parts) |
| `uv` | `astral-sh/claude-code-plugins` | Python venv and dependencies |
| `python-testing-patterns` | `wshobson/agents` | pytest, async tests against the simulator |
| `vite` | `antfu/skills` | Face engine build |
| `verification-before-completion` | `obra/superpowers` | Evidence before claiming work is done |

Written for this repo (not from skills.sh, so not in `skills-lock.json`):

| Skill | Used for |
| --- | --- |
| `openhead-conversation` | Talking through the head with the MCP tools: the `say`/`listen` loop, cues such as `[happy]`, `[serious]` and `[laugh]`, and the limits (0.4) |

Not found on skills.sh in a quality worth adding: fastlane/TestFlight, XcodeGen, JSON Schema, ARKit (v0.2). Use DeepWiki for those.

## Managing skills

```bash
npx skills add <owner/repo> --skill <name> -a claude-code --copy -y
npx skills check
npx skills update
```

Review a skill's files before committing it; skills run with the agent's permissions. Set `DISABLE_TELEMETRY=1` to opt out of the CLI's install telemetry.

## DeepWiki

`.mcp.json` registers the DeepWiki MCP server (no auth, public repos only). Tools: `read_wiki_structure`, `read_wiki_contents`, `ask_question`. Useful repos: `modelcontextprotocol/python-sdk`, `yonaskolb/XcodeGen`, `fastlane/fastlane`, `r0x0r/pywebview`, `microsoft/playwright`, `koxudaxi/datamodel-code-generator`, `python-websockets/websockets`.
