# Protocol

The OpenHead protocol is the product; every client and tool depends on what is here.

| Path | What |
| --- | --- |
| `schema/` | JSON Schema 2020-12, one file per message type: `messages/` (handshake, ack, error), `commands/`, `topics/`, plus `envelope.json`, `command.json`, `common.json` and the theme pack schemas. |
| `examples/` | One or more valid examples per message type; `results/` holds `ack.result` examples per command; `invalid/` holds messages that must fail; `themes/` holds a minimal theme pack. |
| `dist/openhead.schema.json` | All schemas bundled into one document (`$defs` named by title). Generated; use it for code generators in other languages. |
| `docs/` | Generated reference. Start at [docs/README.md](docs/README.md). |
| `VERSION` | Protocol version; also the iOS app's `MARKETING_VERSION`. |
| `CHANGELOG.md` | Updated in the same commit as any schema change (the pre-commit hook enforces it). |

## Conventions

- Every message has `type`, `ts` (ms, sender clock) and `seq`. Commands add `id` and get `ack` or `error` with that `id`.
- Payload fields sit next to the envelope fields (no `params` wrapper).
- Commands that return data describe it in their schema's `$defs/result`; it arrives in `ack.result`.
- Schemas are strict (`unevaluatedProperties: false`); generated models ignore unknown fields so older clients keep working against newer devices within a major version.
- `$ref` forms allowed: `file.json`, `file.json#/$defs/name`, `#/$defs/name`.

## Tooling

```bash
uv run --project python python tools/protocol.py check             # validate everything
uv run --project python python tools/protocol.py generate          # bundle, Python models, docs
uv run --project python python tools/protocol.py generate --check  # what the pre-commit hook runs
```

Python models are written to `python/src/openhead/protocol/`; Swift models (quicktype, Codable + Sendable) to `apps/ios/OpenHead/Protocol/`. `tools/check.py` round-trips every example through both (`python/tests/test_contract.py`, and `tools/swift_contract/` when Swift is installed in WSL). Generating Swift needs Node (`npx`).
