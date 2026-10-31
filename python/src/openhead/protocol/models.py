# Generated from protocol/schema by tools/protocol.py. Do not edit.

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel, constr


class OpenHeadProtocol(RootModel[Any]):
    root: Any = Field(..., title="OpenHeadProtocol")
    """
    All OpenHead protocol 0.1.0 schemas in one document. Generated from protocol/schema by tools/protocol.py; do not edit.
    """


class CommonName(RootModel[str]):
    root: str = Field(..., pattern="^[a-z][a-z0-9_-]{0,31}$", title="CommonName")
    """
    Lower-case identifier used for themes and emotions.
    """


class CommonUnit(RootModel[float]):
    root: float = Field(..., ge=0.0, le=1.0, title="CommonUnit")


class Envelope(BaseModel):
    """
    Fields carried by every OpenHead message.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    type: str = Field(..., pattern="^[a-z][a-z_]*(\\.[a-z][a-z_]*)?$")
    """
    Message type, e.g. `hello`, `face.set_emotion`, `imu`.
    """
    ts: int = Field(..., ge=0)
    """
    Sender clock in milliseconds since the Unix epoch.
    """
    seq: int = Field(..., ge=0)
    """
    Per-connection, per-direction counter, starting at 0.
    """


class Error(Envelope):
    """
    Failed command (with `id`) or failed handshake (without).
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    type: Literal["error"] = Field(..., pattern="^[a-z][a-z_]*(\\.[a-z][a-z_]*)?$")
    """
    Message type, e.g. `hello`, `face.set_emotion`, `imu`.
    """
    id: str | None = Field(None, max_length=64, min_length=1)
    code: Literal[
        "unauthorized",
        "unsupported",
        "busy",
        "invalid_params",
        "dev_mode_required",
        "rate_limited",
    ]
    message: str = Field(..., max_length=1024)
    details: dict[str, Any] | None = None


class ExpressionsParams(BaseModel):
    """
    Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    open_l: float | None = Field(None, ge=0.0, le=1.0, title="CommonUnit")
    open_r: float | None = Field(None, ge=0.0, le=1.0, title="CommonUnit")
    tilt_l: float | None = Field(None, ge=-1.0, le=1.0, title="CommonSignedUnit")
    tilt_r: float | None = Field(None, ge=-1.0, le=1.0, title="CommonSignedUnit")
    pupil: float | None = Field(None, ge=0.0, le=1.0, title="CommonUnit")
    gaze_x: float | None = Field(None, ge=-1.0, le=1.0, title="CommonSignedUnit")
    gaze_y: float | None = Field(None, ge=-1.0, le=1.0, title="CommonSignedUnit")
    squint: float | None = Field(None, ge=0.0, le=1.0, title="CommonUnit")
    open: float | None = Field(None, ge=0.0, le=1.0, title="CommonUnit")
    """
    Mouth opening.
    """
    width: float | None = Field(None, ge=0.0, le=1.0, title="CommonUnit")
    """
    Mouth width.
    """
    curve: float | None = Field(None, ge=-1.0, le=1.0, title="CommonSignedUnit")
    """
    Smile (+) or frown (-).
    """
    asym: float | None = Field(None, ge=-1.0, le=1.0, title="CommonSignedUnit")
    teeth: float | None = Field(None, ge=0.0, le=1.0, title="CommonUnit")
    head_tilt: float | None = Field(None, ge=-1.0, le=1.0, title="CommonSignedUnit")
    breath_rate: float | None = Field(None, ge=0.0, le=1.0, title="CommonUnit")
    blink_rate: float | None = Field(None, ge=0.0, le=1.0, title="CommonUnit")
    jitter: float | None = Field(None, ge=0.0, le=1.0, title="CommonUnit")


class FaceEnvelope(Envelope):
    """
    Mouth envelope from the host's speech audio, sent as a stream at 20-30 Hz while speaking. Not a command: no `id` and no reply. The face decays to closed if no update arrives for 200 ms.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    type: Literal["face.envelope"] = Field(
        ..., pattern="^[a-z][a-z_]*(\\.[a-z][a-z_]*)?$"
    )
    """
    Message type, e.g. `hello`, `face.set_emotion`, `imu`.
    """
    level: float = Field(..., ge=0.0, le=1.0, title="CommonUnit")


class FaceListThemeInfo(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )
    name: str = Field(..., pattern="^[a-z][a-z0-9_-]{0,31}$", title="CommonName")
    """
    Lower-case identifier used for themes and emotions.
    """
    version: str = Field(
        ..., pattern="^[0-9]+\\.[0-9]+\\.[0-9]+$", title="CommonVersion"
    )
    """
    Semantic version, MAJOR.MINOR.PATCH.
    """
    title: str | None = None
    expressions: list[CommonName]
    """
    Shared emotion names the theme defines.
    """
    extras: list[CommonName]
    """
    Theme-specific expressions, e.g. `cackle`.
    """


class Hello(Envelope):
    """
    First message on a new connection. Without a valid token the device answers `pair_required`; with one it answers `welcome`. The major version must match the device's.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    type: Literal["hello"] = Field(..., pattern="^[a-z][a-z_]*(\\.[a-z][a-z_]*)?$")
    """
    Message type, e.g. `hello`, `face.set_emotion`, `imu`.
    """
    client: str = Field(..., max_length=64, min_length=1)
    """
    Human-readable client name, shown on the pairing screen and in the client list.
    """
    protocol_version: str = Field(
        ..., pattern="^[0-9]+\\.[0-9]+\\.[0-9]+$", title="CommonVersion"
    )
    """
    Semantic version, MAJOR.MINOR.PATCH.
    """
    token: str | None = Field(None, max_length=256, min_length=16)
    """
    Token from an earlier `welcome`.
    """


class QItem(RootModel[float]):
    root: float = Field(..., ge=-1.0, le=1.0)


class LogPayload(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )
    time_ms: int = Field(..., ge=0)
    """
    When the line was logged.
    """
    level: Literal["debug", "info", "notice", "warning", "error", "fault"] = Field(
        ..., title="CommonLogLevel"
    )
    subsystem: str = Field(..., pattern="^[a-z][a-z0-9_.]*$")
    """
    e.g. `link`, `face`, `display`, `sensors`.
    """
    message: str = Field(..., max_length=4096)
    seq_ref: int | None = Field(None, ge=0)
    """
    `seq` of the received message this line is about.
    """


class ModeGetResult(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )
    mode: Literal["idle", "sensing", "capture"] = Field(..., title="CommonMode")
    """
    Camera ownership mode. Only `idle` is supported in 0.1.
    """


class Pair(Envelope):
    """
    Pairing attempt with the code shown on the device. Answered with `welcome`, or `error` with `unauthorized` (wrong code) or `rate_limited` (locked for five minutes after five failures).
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    type: Literal["pair"] = Field(..., pattern="^[a-z][a-z_]*(\\.[a-z][a-z_]*)?$")
    """
    Message type, e.g. `hello`, `face.set_emotion`, `imu`.
    """
    code: str = Field(..., pattern="^[0-9]{4,8}$")
    """
    Devices show six digits; the simulator accepts `0000` in dev mode.
    """


class PairRequired(Envelope):
    """
    Sent by the device when `hello` has no valid token. The device shows a pairing code on screen.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    type: Literal["pair_required"] = Field(
        ..., pattern="^[a-z][a-z_]*(\\.[a-z][a-z_]*)?$"
    )
    """
    Message type, e.g. `hello`, `face.set_emotion`, `imu`.
    """
    code_hint: str = Field(..., max_length=128)
    """
    Where to find the code, e.g. "6-digit code shown on head-01".
    """
    code_length: int = Field(..., ge=4, le=8)
    expires_in_ms: int = Field(..., ge=0, le=600000, title="CommonDurationMs")
    attempts_left: int = Field(..., ge=0)


class StatusPayload(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )
    battery_level: float | None = Field(None, ge=0.0, le=1.0)
    """
    Omitted when unknown (e.g. simulator).
    """
    charging: bool
    thermal_state: Literal["nominal", "fair", "serious", "critical"] = Field(
        ..., title="CommonThermalState"
    )
    view: Literal["face", "image", "web"] = Field(..., title="CommonView")
    """
    What fills the screen.
    """
    overlay: Literal["none", "face-corner"]
    theme: str = Field(..., pattern="^[a-z][a-z0-9_-]{0,31}$", title="CommonName")
    """
    Lower-case identifier used for themes and emotions.
    """
    emotion: str = Field(..., pattern="^[a-z][a-z0-9_-]{0,31}$", title="CommonName")
    """
    Lower-case identifier used for themes and emotions.
    """
    mode: Literal["idle", "sensing", "capture"] = Field(..., title="CommonMode")
    """
    Camera ownership mode. Only `idle` is supported in 0.1.
    """
    dev_mode: bool
    clients: int = Field(..., ge=0)
    """
    Connected, authenticated clients.
    """
    rtt_ms: float | None = Field(None, ge=0.0)
    """
    Round-trip time to the receiving client, from WebSocket ping. Omitted until measured.
    """
    uptime_s: float = Field(..., ge=0.0)


class SubscribeResult(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )
    topic: Literal["imu", "status", "log"] = Field(..., title="CommonTopic")
    """
    Subscribable stream. `pose`, `faces`, `gps` and `env` arrive in 0.2.
    """
    rate_hz: float = Field(..., ge=0.0)
    """
    Actual rate; 0 for event-driven topics.
    """


class DiagnosticsPermissions(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )
    local_network: Literal["granted", "denied", "not_determined", "not_required"] = (
        Field(..., title="SystemDiagnosticsPermission")
    )
    motion: Literal["granted", "denied", "not_determined", "not_required"] = Field(
        ..., title="SystemDiagnosticsPermission"
    )
    camera: Literal["granted", "denied", "not_determined", "not_required"] = Field(
        ..., title="SystemDiagnosticsPermission"
    )


class DiagnosticsArkit(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )
    world_tracking: bool
    face_tracking: bool
    """
    Front-camera face tracking concurrent with world tracking.
    """


class DiagnosticsLastCrash(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )
    time_ms: int = Field(..., ge=0)
    reason: str


class SystemDiagnosticsResult(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )
    uptime_s: float = Field(..., ge=0.0)
    thermal_state: Literal["nominal", "fair", "serious", "critical"] = Field(
        ..., title="CommonThermalState"
    )
    memory_mb: float = Field(..., ge=0.0)
    """
    Memory used by the app.
    """
    frame_rate: float = Field(..., ge=0.0)
    """
    Face render rate over the last second.
    """
    permissions: DiagnosticsPermissions = Field(..., title="DiagnosticsPermissions")
    arkit: DiagnosticsArkit = Field(..., title="DiagnosticsArkit")
    last_crash: DiagnosticsLastCrash | None = Field(None, title="DiagnosticsLastCrash")


class SystemLogsResult(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )
    entries: list[LogPayload]


class SystemScreenshotResult1(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )
    width: int = Field(..., ge=1)
    """
    Pixels.
    """
    height: int = Field(..., ge=1)
    """
    Pixels.
    """
    url: str = Field(..., pattern="^https?://")
    expires_ms: int = Field(..., ge=0, le=600000, title="CommonDurationMs")
    png_base64: str | None = Field(
        None,
        json_schema_extra={
            "contentEncoding": "base64",
            "contentMediaType": "image/png",
        },
    )


class SystemScreenshotResult2(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )
    width: int = Field(..., ge=1)
    """
    Pixels.
    """
    height: int = Field(..., ge=1)
    """
    Pixels.
    """
    url: str | None = Field(None, pattern="^https?://")
    expires_ms: int | None = Field(None, ge=0, le=600000, title="CommonDurationMs")
    png_base64: str = Field(
        ...,
        json_schema_extra={
            "contentEncoding": "base64",
            "contentMediaType": "image/png",
        },
    )


class SystemScreenshotResult(
    RootModel[SystemScreenshotResult1 | SystemScreenshotResult2]
):
    root: SystemScreenshotResult1 | SystemScreenshotResult2 = Field(
        ..., title="SystemScreenshotResult"
    )


class SystemSettingsResult(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )
    settings: dict[str, Any]
    """
    All settings after the command.
    """


class SystemStatusResult(RootModel[StatusPayload]):
    root: StatusPayload = Field(..., title="SystemStatusResult")


class ThemeLayout(BaseModel):
    """
    Placement relative to the screen centre. Defaults are the engine's.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    eye_spacing: float | None = Field(None, ge=0.0, le=1.0, title="CommonUnit")
    eye_size: float | None = Field(None, ge=0.0, le=1.0, title="CommonUnit")
    eye_y: float | None = Field(None, ge=-1.0, le=1.0, title="CommonSignedUnit")
    mouth_width: float | None = Field(None, ge=0.0, le=1.0, title="CommonUnit")
    mouth_y: float | None = Field(None, ge=-1.0, le=1.0, title="CommonSignedUnit")


class ThemeRender(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )
    stroke: float | None = Field(None, ge=0.0, le=0.1)
    """
    Outline width; 0 for none.
    """
    glow: float | None = Field(None, ge=0.0, le=1.0, title="CommonUnit")
    scanlines: bool | None = None
    pixelate: int | None = Field(None, ge=0, le=64)
    """
    Pixel block size in points; 0 for off.
    """


class ThemeEnvelope(BaseModel):
    """
    How the speech envelope drives mouth `open`: open = gain * level^gamma, smoothed with attack/release.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    gain: float | None = Field(None, ge=0.0, le=4.0)
    gamma: float | None = Field(None, ge=0.1, le=4.0)
    attack_ms: int | None = Field(None, ge=0, le=1000)
    release_ms: int | None = Field(None, ge=0, le=1000)


class ThemeRangeM(RootModel[int]):
    root: int = Field(..., ge=0, le=60000)


class ThemeShape1(BaseModel):
    """
    One of: a built-in preset, an SVG path in normalised coordinates ([-1, 1] box), or an image from `assets/`.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    preset: Literal["round", "almond", "slit", "pixel", "line"]


class ThemeShape2(BaseModel):
    """
    One of: a built-in preset, an SVG path in normalised coordinates ([-1, 1] box), or an image from `assets/`.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    path: str = Field(..., max_length=8192, min_length=1)


class ThemeShape3(BaseModel):
    """
    One of: a built-in preset, an SVG path in normalised coordinates ([-1, 1] box), or an image from `assets/`.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    image: str = Field(..., pattern="^assets/[A-Za-z0-9_./-]+\\.(png|svg)$")
    anchor: list[CommonUnit] | None = Field(None, max_length=2, min_length=2)
    """
    Point in the image placed at the feature centre. Default [0.5, 0.5].
    """
    scale: float | None = Field(None, gt=0.0, le=10.0)


class Capability(RootModel[str]):
    root: str = Field(..., pattern="^[a-z][a-z0-9_.-]*$")


class WelcomeInsets(BaseModel):
    """
    Safe-area insets in points.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    top: float = Field(..., ge=0.0)
    left: float = Field(..., ge=0.0)
    bottom: float = Field(..., ge=0.0)
    right: float = Field(..., ge=0.0)


class WelcomeScreen(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )
    width: float = Field(..., gt=0.0)
    """
    Points.
    """
    height: float = Field(..., gt=0.0)
    """
    Points.
    """
    scale: float = Field(..., gt=0.0)
    safe_area: WelcomeInsets


class Ack(Envelope):
    """
    Successful reply to a command. Commands that return data put it in `result`; its shape is the command schema's `$defs/result`.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    type: Literal["ack"] = Field(..., pattern="^[a-z][a-z_]*(\\.[a-z][a-z_]*)?$")
    """
    Message type, e.g. `hello`, `face.set_emotion`, `imu`.
    """
    id: str = Field(..., max_length=64, min_length=1)
    result: dict[str, Any] | None = None


class Command(Envelope):
    """
    Base for commands. Every command is answered with `ack` or `error` carrying the same `id`.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    id: str = Field(..., max_length=64, min_length=1)
    """
    Client-chosen id, echoed in the reply.
    """


class DisplayClear(Command):
    """
    Remove any image or web page and show the face full screen.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    type: Literal["display.clear"] = Field(
        ..., pattern="^[a-z][a-z_]*(\\.[a-z][a-z_]*)?$"
    )
    """
    Message type, e.g. `hello`, `face.set_emotion`, `imu`.
    """


class DisplayShow(Command):
    """
    Change what fills the screen. `content` is named so to avoid clashing with the envelope's `type`. Images come as an http(s) URL the device fetches, or as a `data:image/...;base64,` URI under 1 MB. With `overlay: face-corner` the face keeps running in a corner.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    type: Literal["display.show"] = Field(
        ..., pattern="^[a-z][a-z_]*(\\.[a-z][a-z_]*)?$"
    )
    """
    Message type, e.g. `hello`, `face.set_emotion`, `imu`.
    """
    content: Literal["face", "image", "web"] = Field(..., title="CommonView")
    """
    What fills the screen.
    """
    source: str | None = Field(
        None,
        max_length=1400000,
        pattern="^(https?://|data:image/(png|jpeg|gif|webp);base64,)",
    )
    """
    Required for `image` and `web`. `web` accepts http(s) URLs only.
    """
    overlay: Literal["none", "face-corner"] | None = None
    """
    Default `none`.
    """
    duration_ms: int | None = Field(None, ge=0, le=600000, title="CommonDurationMs")
    """
    Return to the face after this time. Omit to hold.
    """


class Expressions(BaseModel):
    """
    A theme's `expressions.json`: a face parameter preset per shared emotion name, plus theme-specific ones under `extra`. Only `neutral` is required and must set every parameter; missing shared names fall back to it. Parameters a preset leaves out keep the neutral value.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    neutral: ExpressionsParams
    happy: ExpressionsParams | None = None
    curious: ExpressionsParams | None = None
    thinking: ExpressionsParams | None = None
    surprised: ExpressionsParams | None = None
    sad: ExpressionsParams | None = None
    angry: ExpressionsParams | None = None
    sleepy: ExpressionsParams | None = None
    scared: ExpressionsParams | None = None
    mischievous: ExpressionsParams | None = None
    extra: (
        dict[constr(pattern=r"^[a-z][a-z0-9_-]{0,31}$"), ExpressionsParams] | None
    ) = None
    """
    Theme-specific expressions, e.g. `cackle`.
    """


class FaceBlink(Command):
    """
    Blink once now, in the theme's blink style.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    type: Literal["face.blink"] = Field(..., pattern="^[a-z][a-z_]*(\\.[a-z][a-z_]*)?$")
    """
    Message type, e.g. `hello`, `face.set_emotion`, `imu`.
    """


class FaceList(Command):
    """
    List installed themes with their expressions.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    type: Literal["face.list"] = Field(..., pattern="^[a-z][a-z_]*(\\.[a-z][a-z_]*)?$")
    """
    Message type, e.g. `hello`, `face.set_emotion`, `imu`.
    """


class FaceListResult(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )
    active: str = Field(..., pattern="^[a-z][a-z0-9_-]{0,31}$", title="CommonName")
    """
    Lower-case identifier used for themes and emotions.
    """
    themes: list[FaceListThemeInfo]


class FaceLookAt(Command):
    """
    Point the gaze. `screen`: `x`, `y` in [-1, 1] with origin at the screen centre, +x right, +y up. `head`: `yaw`, `pitch` in degrees in the head frame, +yaw left, +pitch up. The world frame needs pose and arrives in 0.2.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    type: Literal["face.look_at"] = Field(
        ..., pattern="^[a-z][a-z_]*(\\.[a-z][a-z_]*)?$"
    )
    """
    Message type, e.g. `hello`, `face.set_emotion`, `imu`.
    """
    frame: Literal["screen", "head"]
    x: float | None = Field(None, ge=-1.0, le=1.0, title="CommonSignedUnit")
    y: float | None = Field(None, ge=-1.0, le=1.0, title="CommonSignedUnit")
    yaw: float | None = Field(None, ge=-90.0, le=90.0)
    pitch: float | None = Field(None, ge=-90.0, le=90.0)
    duration_ms: int | None = Field(None, ge=0, le=600000, title="CommonDurationMs")
    """
    Hold the gaze, then return to idle motion. Omit to hold until the next `look_at`.
    """


class FaceSetEmotion(Command):
    """
    Blend towards an emotion. Shared names: neutral, happy, curious, thinking, surprised, sad, angry, sleepy, scared, mischievous; themes may add extras (see `face.list`). Names the theme lacks fall back to `neutral` with a warning in the log.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    type: Literal["face.set_emotion"] = Field(
        ..., pattern="^[a-z][a-z_]*(\\.[a-z][a-z_]*)?$"
    )
    """
    Message type, e.g. `hello`, `face.set_emotion`, `imu`.
    """
    name: str = Field(..., pattern="^[a-z][a-z0-9_-]{0,31}$", title="CommonName")
    """
    Lower-case identifier used for themes and emotions.
    """
    intensity: float | None = Field(None, ge=0.0, le=1.0, title="CommonUnit")
    """
    Weight of the emotion. Default 1.
    """
    duration_ms: int | None = Field(None, ge=0, le=600000, title="CommonDurationMs")
    """
    Return to the resting emotion after this time. Omit to hold.
    """
    blend: Literal["replace", "add"] | None = None
    """
    `replace` fades out other emotions; `add` layers on top. Default `replace`.
    """


class FaceSetTheme(Command):
    """
    Switch the face to an installed theme. Unknown names give `invalid_params`.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    type: Literal["face.set_theme"] = Field(
        ..., pattern="^[a-z][a-z_]*(\\.[a-z][a-z_]*)?$"
    )
    """
    Message type, e.g. `hello`, `face.set_emotion`, `imu`.
    """
    name: str = Field(..., pattern="^[a-z][a-z0-9_-]{0,31}$", title="CommonName")
    """
    Lower-case identifier used for themes and emotions.
    """
    transition_ms: int | None = Field(None, ge=0, le=600000, title="CommonDurationMs")
    """
    Cross-fade time. Default 300.
    """


class ImuPayload(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )
    q: list[QItem] = Field(..., max_length=4, min_length=4)
    """
    Orientation as unit quaternion [x, y, z, w], relative to a gravity-aligned reference frame.
    """
    gyro: list[float] = Field(..., max_length=3, min_length=3, title="ImuVec3")
    """
    Angular rate in rad/s.
    """
    accel: list[float] = Field(..., max_length=3, min_length=3, title="ImuVec3")
    """
    Specific force (gravity + user acceleration) in m/s^2.
    """
    frame: Literal["device", "mount"]
    sensor_time_s: float = Field(..., ge=0.0)
    """
    Sensor timestamp in seconds since device boot, for precise intervals between samples.
    """


class Log(Envelope, LogPayload):
    """
    One structured log line, sent as it happens. Every received command is logged with its `seq` in `seq_ref`.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    type: Literal["log"] = Field(..., pattern="^[a-z][a-z_]*(\\.[a-z][a-z_]*)?$")
    """
    Message type, e.g. `hello`, `face.set_emotion`, `imu`.
    """


class ModeGet(Command):
    """
    Current camera ownership mode.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    type: Literal["mode.get"] = Field(..., pattern="^[a-z][a-z_]*(\\.[a-z][a-z_]*)?$")
    """
    Message type, e.g. `hello`, `face.set_emotion`, `imu`.
    """


class ModeSet(Command):
    """
    Choose who owns the cameras. In 0.1 only `idle` is accepted; other modes give `unsupported`.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    type: Literal["mode.set"] = Field(..., pattern="^[a-z][a-z_]*(\\.[a-z][a-z_]*)?$")
    """
    Message type, e.g. `hello`, `face.set_emotion`, `imu`.
    """
    mode: Literal["idle", "sensing", "capture"] = Field(..., title="CommonMode")
    """
    Camera ownership mode. Only `idle` is supported in 0.1.
    """


class Status(Envelope, StatusPayload):
    """
    Device status, up to 1 Hz. Also the result of `system.status`.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    type: Literal["status"] = Field(..., pattern="^[a-z][a-z_]*(\\.[a-z][a-z_]*)?$")
    """
    Message type, e.g. `hello`, `face.set_emotion`, `imu`.
    """


class Subscribe(Command):
    """
    Open a stream. The device clamps `rate_hz` to what it supports and returns the actual rate. Subscribing again to the same topic replaces the earlier subscription.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    type: Literal["subscribe"] = Field(..., pattern="^[a-z][a-z_]*(\\.[a-z][a-z_]*)?$")
    """
    Message type, e.g. `hello`, `face.set_emotion`, `imu`.
    """
    topic: Literal["imu", "status", "log"] = Field(..., title="CommonTopic")
    """
    Subscribable stream. `pose`, `faces`, `gps` and `env` arrive in 0.2.
    """
    rate_hz: float | None = Field(None, gt=0.0, le=1000.0)
    """
    Requested rate. Ignored for event-driven topics such as `log`.
    """
    fields: list[str] | None = None
    """
    Only send these payload fields. Omit for all.
    """


class SystemDiagnostics(Command):
    """
    Health snapshot for debugging. Dev mode only.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    type: Literal["system.diagnostics"] = Field(
        ..., pattern="^[a-z][a-z_]*(\\.[a-z][a-z_]*)?$"
    )
    """
    Message type, e.g. `hello`, `face.set_emotion`, `imu`.
    """


class SystemLogs(Command):
    """
    Most recent lines from the device's log ring buffer (2000 lines), oldest first. Dev mode only.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    type: Literal["system.logs"] = Field(
        ..., pattern="^[a-z][a-z_]*(\\.[a-z][a-z_]*)?$"
    )
    """
    Message type, e.g. `hello`, `face.set_emotion`, `imu`.
    """
    n: int | None = Field(None, ge=1, le=2000)
    """
    Default 100.
    """
    level: Literal["debug", "info", "notice", "warning", "error", "fault"] | None = (
        Field(None, title="CommonLogLevel")
    )
    """
    Minimum level. Default `debug`.
    """


class SystemScreenshot(Command):
    """
    PNG of what is on screen. Dev mode only. With `delivery: url` the image is served by the device's HTTP server (WebSocket port + 1) for 60 s and must be fetched with the token in an `Authorization: Bearer` header.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    type: Literal["system.screenshot"] = Field(
        ..., pattern="^[a-z][a-z_]*(\\.[a-z][a-z_]*)?$"
    )
    """
    Message type, e.g. `hello`, `face.set_emotion`, `imu`.
    """
    scale: float | None = Field(None, gt=0.0, le=1.0)
    """
    Fraction of native resolution. Default 1.
    """
    delivery: Literal["url", "inline"] | None = None
    """
    Default `url`.
    """


class SystemSettings(Command):
    """
    Read all settings, or set one. `set` needs dev mode. Known keys in 0.1: `name`, `port`, `mount_offset` ([x, y, z, w] quaternion), `offline_theme`.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    type: Literal["system.settings"] = Field(
        ..., pattern="^[a-z][a-z_]*(\\.[a-z][a-z_]*)?$"
    )
    """
    Message type, e.g. `hello`, `face.set_emotion`, `imu`.
    """
    action: Literal["get", "set"]
    key: str | None = Field(None, pattern="^[a-z][a-z0-9_]*$")
    value: Any | None = None
    """
    Any JSON value valid for the key.
    """


class SystemStatus(Command):
    """
    Current status, same content as the `status` topic.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    type: Literal["system.status"] = Field(
        ..., pattern="^[a-z][a-z_]*(\\.[a-z][a-z_]*)?$"
    )
    """
    Message type, e.g. `hello`, `face.set_emotion`, `imu`.
    """


class ThemePalette(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )
    bg: str = Field(
        ..., pattern="^#([0-9a-fA-F]{6}|[0-9a-fA-F]{8})$", title="ThemeColor"
    )
    """
    #RRGGBB or #RRGGBBAA.
    """
    sclera: str = Field(
        ..., pattern="^#([0-9a-fA-F]{6}|[0-9a-fA-F]{8})$", title="ThemeColor"
    )
    """
    #RRGGBB or #RRGGBBAA.
    """
    iris: str = Field(
        ..., pattern="^#([0-9a-fA-F]{6}|[0-9a-fA-F]{8})$", title="ThemeColor"
    )
    """
    #RRGGBB or #RRGGBBAA.
    """
    pupil: str = Field(
        ..., pattern="^#([0-9a-fA-F]{6}|[0-9a-fA-F]{8})$", title="ThemeColor"
    )
    """
    #RRGGBB or #RRGGBBAA.
    """
    lid: str = Field(
        ..., pattern="^#([0-9a-fA-F]{6}|[0-9a-fA-F]{8})$", title="ThemeColor"
    )
    """
    #RRGGBB or #RRGGBBAA.
    """
    mouth: str = Field(
        ..., pattern="^#([0-9a-fA-F]{6}|[0-9a-fA-F]{8})$", title="ThemeColor"
    )
    """
    #RRGGBB or #RRGGBBAA.
    """
    teeth: str = Field(
        ..., pattern="^#([0-9a-fA-F]{6}|[0-9a-fA-F]{8})$", title="ThemeColor"
    )
    """
    #RRGGBB or #RRGGBBAA.
    """
    accent: str = Field(
        ..., pattern="^#([0-9a-fA-F]{6}|[0-9a-fA-F]{8})$", title="ThemeColor"
    )
    """
    #RRGGBB or #RRGGBBAA.
    """


class ThemeShapes(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )
    eye: ThemeShape1 | ThemeShape2 | ThemeShape3 = Field(..., title="ThemeShape")
    """
    One of: a built-in preset, an SVG path in normalised coordinates ([-1, 1] box), or an image from `assets/`.
    """
    mouth: ThemeShape1 | ThemeShape2 | ThemeShape3 = Field(..., title="ThemeShape")
    """
    One of: a built-in preset, an SVG path in normalised coordinates ([-1, 1] box), or an image from `assets/`.
    """


class ThemeIdle(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )
    blink_interval_ms: list[ThemeRangeM] = Field(
        ..., max_length=2, min_length=2, title="ThemeRangeMs"
    )
    """
    [min, max] in milliseconds; a value is drawn uniformly each time.
    """
    blink_duration_ms: int = Field(..., ge=30, le=2000)
    saccade_interval_ms: list[ThemeRangeM] | None = Field(
        None, max_length=2, min_length=2, title="ThemeRangeMs"
    )
    """
    [min, max] in milliseconds; a value is drawn uniformly each time.
    """
    saccade_amplitude: float | None = Field(None, ge=0.0, le=1.0, title="CommonUnit")
    breath_period_ms: int | None = Field(None, ge=500, le=20000)
    breath_amplitude: float | None = Field(None, ge=0.0, le=1.0, title="CommonUnit")


class Theme(BaseModel):
    """
    A theme's `theme.json`: look and idle behaviour of the face. Expressions live in `expressions.json` next to it; images in `assets/`. Lengths are fractions of the screen's shortest side.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    name: str = Field(..., pattern="^[a-z][a-z0-9_-]{0,31}$", title="CommonName")
    """
    Must equal the folder name.
    """
    version: str = Field(
        ..., pattern="^[0-9]+\\.[0-9]+\\.[0-9]+$", title="CommonVersion"
    )
    """
    Semantic version, MAJOR.MINOR.PATCH.
    """
    title: str | None = Field(None, max_length=64)
    description: str | None = Field(None, max_length=512)
    palette: ThemePalette = Field(..., title="ThemePalette")
    shapes: ThemeShapes = Field(..., title="ThemeShapes")
    layout: ThemeLayout | None = Field(None, title="ThemeLayout")
    """
    Placement relative to the screen centre. Defaults are the engine's.
    """
    render: ThemeRender | None = Field(None, title="ThemeRender")
    idle: ThemeIdle = Field(..., title="ThemeIdle")
    envelope: ThemeEnvelope | None = Field(None, title="ThemeEnvelope")
    """
    How the speech envelope drives mouth `open`: open = gain * level^gamma, smoothed with attack/release.
    """
    resting_emotion: str | None = Field(
        None, pattern="^[a-z][a-z0-9_-]{0,31}$", title="CommonName"
    )
    """
    Emotion shown when nothing else is set. Default `neutral`.
    """


class Unsubscribe(Command):
    """
    Close a stream. Acknowledged even if the topic was not subscribed.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    type: Literal["unsubscribe"] = Field(
        ..., pattern="^[a-z][a-z_]*(\\.[a-z][a-z_]*)?$"
    )
    """
    Message type, e.g. `hello`, `face.set_emotion`, `imu`.
    """
    topic: Literal["imu", "status", "log"] = Field(..., title="CommonTopic")
    """
    Subscribable stream. `pose`, `faces`, `gps` and `env` arrive in 0.2.
    """


class WelcomeDevice(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )
    name: str = Field(..., max_length=64, min_length=1)
    platform: Literal["ios", "ipados", "android", "sim"]
    model: str
    """
    Hardware identifier, e.g. `iPhone13,2`.
    """
    os_version: str
    app_version: str
    screen: WelcomeScreen


class Imu(Envelope, ImuPayload):
    """
    Inertial sample, up to 100 Hz. Right-handed frame: in `device` frame +x is right, +y is up and +z points out of the screen (portrait). `mount` applies the `mount_offset` setting.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    type: Literal["imu"] = Field(..., pattern="^[a-z][a-z_]*(\\.[a-z][a-z_]*)?$")
    """
    Message type, e.g. `hello`, `face.set_emotion`, `imu`.
    """


class Welcome(Envelope):
    """
    Session accepted. Carries the client's token (new after pairing, unchanged on reconnect), the device description and what it supports.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    type: Literal["welcome"] = Field(..., pattern="^[a-z][a-z_]*(\\.[a-z][a-z_]*)?$")
    """
    Message type, e.g. `hello`, `face.set_emotion`, `imu`.
    """
    token: str = Field(..., max_length=256, min_length=16)
    protocol_version: str = Field(
        ..., pattern="^[0-9]+\\.[0-9]+\\.[0-9]+$", title="CommonVersion"
    )
    """
    Semantic version, MAJOR.MINOR.PATCH.
    """
    device: WelcomeDevice
    capabilities: list[Capability]
    """
    Feature flags. Known in 0.1: `face`, `display.image`, `display.web`, `imu`, `status`, `log`, `screenshot`. Clients ignore unknown values.
    """
    themes: list[CommonName]
    dev_mode: bool
