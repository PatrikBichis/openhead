# Protocol changelog

All changes to `protocol/schema` are recorded here, in the same commit as the change. The protocol follows [semver](https://semver.org) from 0.1.0; until 0.1.0 is tagged anything may change.

## Unreleased

### Changed

- `gps`: a message is sent only when there is a new fix (new `sensor_time_s`), instead of repeating the latest fix every second while the head stands still.
- `system.settings` `offline_theme` is the head's own theme: it applies as soon as it is set (before, only at the next start), and the face returns to it when the last paired client disconnects. Clients still switch theme with `face.set_theme`. The app's settings call it "Theme".

## 0.3.0 (2026-11-01)

### Added

- Topic `gps` (1 Hz): latitude, longitude, altitude, horizontal and vertical accuracy, speed, course, sensor time. The first subscription asks for location access.
- Topic `env` (10 Hz): air pressure and relative altitude (barometer), raw magnetic field (magnetometer), compass heading with true/magnetic reference and accuracy. The barometer asks for Motion & Fitness access.
- Capabilities `gps` and `env` in `welcome`; `location` and `motion_fitness` in `system.diagnostics` permissions (optional, absent from 0.2 devices).
- HUD templates `{lat}`, `{lon}`, `{alt}`, `{gps_acc}` while `gps` runs and `{pressure}` (hPa) while `env` runs.

### Notes

- Sensors are those of an iPhone 12. The proximity sensor is left out: turning it on blanks the screen when something is near, which would hide the face. The ambient light sensor has no public API.

## 0.2.0 (2026-11-01)

### Added

- Modes `capture` (front camera, several faces with boxes) and `sensing` (ARKit world tracking and one face via the depth camera) in `mode.set`.
- `display.show {content: camera, hud}`: the front camera with a HUD theme over it; view `camera` in `status`.
- Topics `faces` (id, bearing, elevation, size, confidence, box, locked; `source` vision/arkit/sim) and `pose` (position, orientation, tracking state, world frame).
- `face.look_at {frame: face, face_id?}`: the eyes follow a detected face.
- `face.list` lists HUD themes (`huds`); `status` reports how many `faces` are seen.
- Capabilities `camera`, `faces`, `pose` in `welcome`.
- HUD theme schema `hud.schema.json` (tint, scanlines, vignette, boxes, lock, text blocks with templates, boot text, widgets `compass`, `horizon`, `battery`); templates for device values (battery, thermal, heading, pitch, roll, position, mode).
- `display.hud`: the host's own values, text blocks and widgets on the HUD (`values`, `blocks`, `widgets`, `clear`).

## 0.1.0 (2026-10-31)

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
