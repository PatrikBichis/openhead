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
- `display.show` plays video (`content: video`, http(s) URL, `loop`, `muted`) and accepts SVG data URIs; view `video` in `status`.
- `display.subtitle`: subtitles on top of any view, `replace` / `append` (streamed text) / `clear`, `position`, `duration_ms`, and `mouth` to move the mouth with the text; `subtitle` in `status`.
- Capabilities `display.video` and `display.subtitle` in `welcome`.

### Changed

- `expressions.json`: shared emotion presets sit at the top level next to `extra`, as in the plan (was nested under `expressions`).
- `status`: `battery_level` and `rtt_ms` are omitted when unknown instead of sent as `null`, so generated Swift models (which omit nil) stay valid.
- `imu.accel` sign convention spelled out: specific force, +9.81 on +y at rest upright (ROS convention); the example now follows it.
- Topics `imu`, `status`, `log`: a subscription with `fields` gets only those fields, so topic messages no longer require every payload field; `$defs/payload` (used by `system.status` and `system.logs`) still does.
- Shared emotion names extended from 10 to 28: `confused`, `shocked`, `excited`, `bored`, `skeptical`, `worried`, `disgusted`, `embarrassed`, `proud`, `determined`, `relieved`, `annoyed`, `suspicious`, `laughing`, `disappointed`, `focused`, `nervous`, `smug` (`expressions.schema.json`, `face.set_emotion`).

### Notes

- Swift models are generated from the bundle with quicktype into `apps/ios/OpenHead/Protocol/`; `error` is `ProtocolError` and `ack` is `ACK` in Swift.
- `display.show` names its view parameter `content` (not `type`) so it does not clash with the envelope's `type`.
- `protocol_version` is carried in `hello` and `welcome` only, not in every message.
