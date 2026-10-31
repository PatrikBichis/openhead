# OpenHead protocol reference

Protocol version 0.1.0. Generated from `protocol/schema` by `tools/protocol.py`; do not edit. Examples are in `protocol/examples`.

| Type | Schema | Description |
| --- | --- | --- |
| `ack` | [Ack](messages/ack.md) | Successful reply to a command. |
| `display.clear` | [DisplayClear](commands/display.clear.md) | Remove any image or web page and show the face full screen. |
| `display.show` | [DisplayShow](commands/display.show.md) | Change what fills the screen. |
| `display.subtitle` | [DisplaySubtitle](commands/display.subtitle.md) | Text on top of whatever is shown (face, image, video, web page): for a robot without a speaker, or to show an AI answer as it streams in. |
| `error` | [Error](messages/error.md) | Failed command (with `id`) or failed handshake (without). |
| `face.blink` | [FaceBlink](commands/face.blink.md) | Blink once now, in the theme's blink style. |
| `face.envelope` | [FaceEnvelope](commands/face.envelope.md) | Mouth envelope from the host's speech audio, sent as a stream at 20-30 Hz while speaking. |
| `face.list` | [FaceList](commands/face.list.md) | List installed themes with their expressions. |
| `face.look_at` | [FaceLookAt](commands/face.look_at.md) | Point the gaze. |
| `face.set_emotion` | [FaceSetEmotion](commands/face.set_emotion.md) | Blend towards an emotion, independently of speech (the mouth envelope is added on top). |
| `face.set_theme` | [FaceSetTheme](commands/face.set_theme.md) | Switch the face to an installed theme. |
| `hello` | [Hello](messages/hello.md) | First message on a new connection. |
| `imu` | [Imu](topics/imu.md) | Inertial sample, up to 100 Hz. |
| `log` | [Log](topics/log.md) | One structured log line, sent as it happens. |
| `mode.get` | [ModeGet](commands/mode.get.md) | Current camera ownership mode. |
| `mode.set` | [ModeSet](commands/mode.set.md) | Choose who owns the cameras. |
| `pair` | [Pair](messages/pair.md) | Pairing attempt with the code shown on the device. |
| `pair_required` | [PairRequired](messages/pair_required.md) | Sent by the device when `hello` has no valid token. |
| `status` | [Status](topics/status.md) | Device status, up to 1 Hz. |
| `subscribe` | [Subscribe](commands/subscribe.md) | Open a stream. |
| `system.diagnostics` | [SystemDiagnostics](commands/system.diagnostics.md) | Health snapshot for debugging. |
| `system.logs` | [SystemLogs](commands/system.logs.md) | Most recent lines from the device's log ring buffer (2000 lines), oldest first. |
| `system.screenshot` | [SystemScreenshot](commands/system.screenshot.md) | PNG of what is on screen. |
| `system.settings` | [SystemSettings](commands/system.settings.md) | Read all settings, or set one. |
| `system.status` | [SystemStatus](commands/system.status.md) | Current status, same content as the `status` topic. |
| `unsubscribe` | [Unsubscribe](commands/unsubscribe.md) | Close a stream. |
| `welcome` | [Welcome](messages/welcome.md) | Session accepted. |

Shared: [Envelope](envelope.md), [Command](command.md), [Common](common.md). Theme packs: [Theme](theme.schema.md), [Expressions](expressions.schema.md).
