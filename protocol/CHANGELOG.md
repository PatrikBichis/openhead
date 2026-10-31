# Protocol changelog

All changes to `protocol/schema` are recorded here, in the same commit as the change. The protocol follows [semver](https://semver.org) from 0.1.0; until 0.1.0 is tagged anything may change.

## Unreleased (0.1.0)

### Added

- Envelope (`type`, `ts`, `seq`) and command base (`id`).
- Handshake: `hello`, `pair_required`, `pair`, `welcome`; replies `ack` (optional `result`) and `error` with codes `unauthorized`, `unsupported`, `busy`, `invalid_params`, `dev_mode_required`, `rate_limited`.
- Streams: `subscribe` / `unsubscribe`; topics `imu`, `status`, `log`.
- Commands: `face.set_theme`, `face.set_emotion`, `face.look_at` (screen and head frames), `face.blink`, `face.list`, `display.show`, `display.clear`, `system.status`, `system.screenshot`, `system.logs`, `system.diagnostics`, `system.settings`, `mode.set`, `mode.get`.
- `face.envelope` stream message (no `id`, no reply).
- Theme pack schemas: `theme.schema.json`, `expressions.schema.json`.

### Notes

- `display.show` names its view parameter `content` (not `type`) so it does not clash with the envelope's `type`.
- `protocol_version` is carried in `hello` and `welcome` only, not in every message.
