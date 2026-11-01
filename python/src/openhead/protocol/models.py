# Generated from protocol/schema by tools/protocol.py. Do not edit.

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel, constr


class OpenHeadProtocol(RootModel[Any]):
    root: Any = Field(..., title="OpenHeadProtocol")
    """
    All OpenHead protocol 0.3.0 schemas in one document. Generated from protocol/schema by tools/protocol.py; do not edit.
    """


class CommonName(RootModel[str]):
    root: str = Field(..., pattern="^[a-z][a-z0-9_-]{0,31}$", title="CommonName")
    """
    Lower-case identifier used for themes and emotions.
    """


class EnvFields(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )
    pressure_kpa: float | None = Field(None, ge=0.0)
    """
    Air pressure in kilopascals.
    """
    relative_altitude_m: float | None = None
    """
    Change in altitude in metres since the barometer started (this subscription or an earlier one still running).
    """
    magnetic_field_ut: list[float] | None = Field(None, max_length=3, min_length=3)
    """
    Raw magnetic field in microtesla, device frame; includes the device's own bias.
    """
    heading_deg: float | None = Field(None, ge=0.0, le=360.0)
    """
    Compass heading of the screen's top edge as the head is mounted (landscape), degrees clockwise from north.
    """
    heading_ref: Literal["true", "magnetic"] | None = None
    """
    `true` north needs location access; otherwise magnetic north.
    """
    heading_accuracy_deg: float | None = Field(None, ge=0.0)
    """
    Maximum heading error in degrees.
    """
    sensor_time_s: float | None = Field(None, ge=0.0)
    """
    Seconds since device boot (the clock of `imu`).
    """


class EnvPayload(EnvFields):
    """
    Payload when the subscription names no `fields`: every reading the device has.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    sensor_time_s: float = Field(..., ge=0.0)
    """
    Seconds since device boot (the clock of `imu`).
    """


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


class FaceListHudInfo(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )
    name: str = Field(..., pattern="^[a-z][a-z0-9_-]{0,31}$", title="CommonName")
    """
    Lower-case identifier used for themes and emotions.
    """
    title: str
    version: str | None = Field(
        None, pattern="^[0-9]+\\.[0-9]+\\.[0-9]+$", title="CommonVersion"
    )
    """
    Semantic version, MAJOR.MINOR.PATCH.
    """


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
    expressions: list[str]
    """
    Shared emotion names the theme defines.
    """
    extras: list[str]
    """
    Theme-specific expressions, e.g. `cackle`.
    """


class FacesBox(BaseModel):
    """
    Where the face is in the camera view as shown on screen, normalised 0-1, origin top-left.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    x: float = Field(..., ge=0.0, le=1.0)
    y: float = Field(..., ge=0.0, le=1.0)
    w: float = Field(..., ge=0.0, le=1.0)
    h: float = Field(..., ge=0.0, le=1.0)


class FacesFace(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )
    id: int = Field(..., ge=0)
    """
    Stable while the face stays in view.
    """
    bearing: float = Field(..., ge=-90.0, le=90.0)
    """
    Degrees, + to the head's left.
    """
    elevation: float = Field(..., ge=-90.0, le=90.0)
    """
    Degrees, + up.
    """
    size: float = Field(..., ge=0.0, le=1.0)
    """
    Face width as a share of the camera's field of view: bigger is closer.
    """
    distance_m: float | None = Field(None, ge=0.0)
    """
    Metres, when the depth camera measures it (`sensing`).
    """
    confidence: float = Field(..., ge=0.0, le=1.0)
    box: FacesBox | None = None
    locked: bool | None = None
    """
    The face the HUD and `look_at {frame: face}` follow.
    """


class FacesFields(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )
    faces: list[FacesFace] | None = Field(None, max_length=16)
    source: Literal["vision", "arkit", "sim"] | None = None
    sensor_time_s: float | None = Field(None, ge=0.0)


class FacesPayload(FacesFields):
    """
    Complete payload, as sent when the subscription names no `fields`.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    faces: list[FacesFace] = Field(..., max_length=16)
    source: Literal["vision", "arkit", "sim"]
    sensor_time_s: float = Field(..., ge=0.0)


class GpsFields(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )
    lat: float | None = Field(None, ge=-90.0, le=90.0)
    """
    Latitude in degrees, + north.
    """
    lon: float | None = Field(None, ge=-180.0, le=180.0)
    """
    Longitude in degrees, + east.
    """
    alt_m: float | None = None
    """
    Altitude above mean sea level in metres.
    """
    h_accuracy_m: float | None = Field(None, ge=0.0)
    """
    Radius of horizontal uncertainty in metres (68 %).
    """
    v_accuracy_m: float | None = Field(None, ge=0.0)
    """
    Vertical uncertainty in metres.
    """
    speed_m_s: float | None = Field(None, ge=0.0)
    """
    Ground speed in m/s.
    """
    course_deg: float | None = Field(None, ge=0.0, le=360.0)
    """
    Direction of travel, degrees clockwise from true north.
    """
    sensor_time_s: float | None = Field(None, ge=0.0)
    """
    When the fix was taken, seconds since device boot (the clock of `imu`).
    """


class GpsPayload(GpsFields):
    """
    Complete payload, as sent when the subscription names no `fields`.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    lat: float = Field(..., ge=-90.0, le=90.0)
    """
    Latitude in degrees, + north.
    """
    lon: float = Field(..., ge=-180.0, le=180.0)
    """
    Longitude in degrees, + east.
    """
    h_accuracy_m: float = Field(..., ge=0.0)
    """
    Radius of horizontal uncertainty in metres (68 %).
    """
    sensor_time_s: float = Field(..., ge=0.0)
    """
    When the fix was taken, seconds since device boot (the clock of `imu`).
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


class Scanlines(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )
    opacity: float = Field(..., ge=0.0, le=1.0)
    spacing: float | None = Field(None, ge=2.0, le=12.0)
    """
    Pixels between lines.
    """


class Boxes(BaseModel):
    """
    How every detected face is marked.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    style: Literal["corners", "rect", "bracket", "none"]
    width: float | None = Field(None, ge=0.5, le=8.0)
    """
    Line width in points.
    """
    label: str | None = Field(None, max_length=80)


class Lock(BaseModel):
    """
    How the locked face (the largest, or the one `look_at` follows) is marked.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    style: Literal["crosshair", "rect", "corners", "none"]
    label: str | None = Field(None, max_length=40)
    """
    Shown big near the bottom while locked.
    """
    blink_ms: int | None = Field(None, ge=0, le=5000)


class Boot(BaseModel):
    """
    Lines typed out one by one when the view opens, then kept on screen at the left.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    lines: list[str] = Field(..., max_length=24)
    ms_per_line: int | None = Field(None, ge=20, le=2000)


class HudWidget(BaseModel):
    """
    An instrument drawn from device values.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    type: Literal["compass", "horizon", "battery"]
    """
    `compass`: heading tape; `horizon`: artificial horizon from pitch and roll; `battery`: level and charging.
    """
    at: (
        Literal[
            "top",
            "bottom",
            "center",
            "top-left",
            "top-right",
            "bottom-left",
            "bottom-right",
        ]
        | None
    ) = None
    """
    Default: top for compass, center for horizon, top-right for battery.
    """
    size: float | None = Field(None, ge=0.5, le=3.0)


class LogFields(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )
    time_ms: int | None = Field(None, ge=0)
    """
    When the line was logged.
    """
    level: Literal["debug", "info", "notice", "warning", "error", "fault"] | None = (
        Field(None, title="CommonLogLevel")
    )
    subsystem: str | None = Field(None, pattern="^[a-z][a-z0-9_.]*$")
    """
    e.g. `link`, `face`, `display`, `sensors`.
    """
    message: str | None = Field(None, max_length=4096)
    seq_ref: int | None = Field(None, ge=0)
    """
    `seq` of the received message this line is about.
    """


class LogPayload(LogFields):
    """
    Complete payload, as sent when the subscription names no `fields`.
    """

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


class PoseFields(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )
    position: list[float] | None = Field(None, max_length=3, min_length=3)
    """
    Metres in the world frame.
    """
    q: list[float] | None = Field(None, max_length=4, min_length=4)
    """
    Unit quaternion [x, y, z, w], device frame to world frame.
    """
    tracking_state: Literal["normal", "limited", "not_available"] | None = None
    tracking_reason: (
        Literal[
            "initializing", "excessive_motion", "insufficient_features", "relocalizing"
        ]
        | None
    ) = None
    """
    Why tracking is `limited`.
    """
    frame: Literal["world"] | None = None
    sensor_time_s: float | None = Field(None, ge=0.0)


class PosePayload(PoseFields):
    """
    Complete payload, as sent when the subscription names no `fields`.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    position: list[float] = Field(..., max_length=3, min_length=3)
    """
    Metres in the world frame.
    """
    q: list[float] = Field(..., max_length=4, min_length=4)
    """
    Unit quaternion [x, y, z, w], device frame to world frame.
    """
    tracking_state: Literal["normal", "limited", "not_available"]
    frame: Literal["world"]
    sensor_time_s: float = Field(..., ge=0.0)


class StatusFields(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )
    battery_level: float | None = Field(None, ge=0.0, le=1.0)
    """
    Omitted when unknown (e.g. simulator).
    """
    charging: bool | None = None
    thermal_state: Literal["nominal", "fair", "serious", "critical"] | None = Field(
        None, title="CommonThermalState"
    )
    view: Literal["face", "image", "video", "web", "camera"] | None = Field(
        None, title="CommonView"
    )
    """
    What fills the screen.
    """
    overlay: Literal["none", "face-corner"] | None = None
    subtitle: str | None = Field(None, max_length=4000)
    """
    Subtitle text on screen. Omitted when none.
    """
    theme: str | None = Field(
        None, pattern="^[a-z][a-z0-9_-]{0,31}$", title="CommonName"
    )
    """
    Lower-case identifier used for themes and emotions.
    """
    emotion: str | None = Field(
        None, pattern="^[a-z][a-z0-9_-]{0,31}$", title="CommonName"
    )
    """
    Lower-case identifier used for themes and emotions.
    """
    mode: Literal["idle", "sensing", "capture"] | None = Field(None, title="CommonMode")
    """
    Camera ownership mode. Only `idle` is supported in 0.1.
    """
    faces: int | None = Field(None, ge=0)
    """
    Faces seen now (modes `capture` and `sensing`). Omitted in `idle`.
    """
    dev_mode: bool | None = None
    clients: int | None = Field(None, ge=0)
    """
    Connected, authenticated clients.
    """
    rtt_ms: float | None = Field(None, ge=0.0)
    """
    Round-trip time to the receiving client, from WebSocket ping. Omitted until measured.
    """
    uptime_s: float | None = Field(None, ge=0.0)


class StatusPayload(StatusFields):
    """
    Complete payload, as sent when the subscription names no `fields`.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    charging: bool
    thermal_state: Literal["nominal", "fair", "serious", "critical"] = Field(
        ..., title="CommonThermalState"
    )
    view: Literal["face", "image", "video", "web", "camera"] = Field(
        ..., title="CommonView"
    )
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
    uptime_s: float = Field(..., ge=0.0)


class SubscribeResult(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )
    topic: Literal["imu", "status", "log", "faces", "pose", "gps", "env"] = Field(
        ..., title="CommonTopic"
    )
    """
    Subscribable stream. `faces` needs mode `capture` or `sensing`, `pose` needs `sensing`; `gps` asks for location access and `env` for Motion & Fitness access on first use.
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
    location: Literal["granted", "denied", "not_determined", "not_required"] | None = (
        Field(None, title="SystemDiagnosticsPermission")
    )
    """
    For `gps` and true-north heading; absent from 0.2 devices.
    """
    motion_fitness: (
        Literal["granted", "denied", "not_determined", "not_required"] | None
    ) = Field(None, title="SystemDiagnosticsPermission")
    """
    For the barometer in `env`; absent from 0.2 devices.
    """


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
    anchor: list[float] | None = Field(None, max_length=2, min_length=2)
    """
    Point in the image placed at the feature centre. Default [0.5, 0.5].
    """
    scale: float | None = Field(None, gt=0.0, le=10.0)


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
    Change what fills the screen. `content` is named so to avoid clashing with the envelope's `type`. Images (PNG, JPEG, GIF including animated, WebP, SVG) come as an http(s) URL the device fetches, or as a `data:image/...;base64,` URI under 1 MB. Video comes as an http(s) URL (H.264 or HEVC in MP4/MOV; the simulator plays H.264, VP9 and AV1); without `loop` the face returns when it ends. `camera` shows the front camera with a HUD theme (`hud`) drawn over it: boxes around faces, the locked target, text; it switches to mode `capture` if needed. With `overlay: face-corner` the face keeps running in a corner.
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
    content: Literal["face", "image", "video", "web", "camera"] = Field(
        ..., title="CommonView"
    )
    """
    What fills the screen.
    """
    source: str | None = Field(
        None,
        max_length=1400000,
        pattern="^(https?://|data:image/(png|jpeg|gif|webp|svg\\+xml);base64,)",
    )
    """
    Required for `image`, `video` and `web`. `video` and `web` accept http(s) URLs only.
    """
    overlay: Literal["none", "face-corner"] | None = None
    """
    Default `none`.
    """
    hud: str | None = Field(None, pattern="^[a-z][a-z0-9-]{0,31}$")
    """
    `camera` only: HUD theme from `face.list` (`huds`), or `none` for the bare camera. Default `hunter`.
    """
    loop: bool | None = None
    """
    `video` only: start again at the end. Default false.
    """
    muted: bool | None = None
    """
    `video` only: no sound. Default false.
    """
    duration_ms: int | None = Field(None, ge=0, le=600000, title="CommonDurationMs")
    """
    Return to the face after this time. Omit to hold.
    """


class DisplaySubtitle(Command):
    """
    Text on top of whatever is shown (face, image, video, web page): for a robot without a speaker, or to show an AI answer as it streams in. `replace` shows `text` alone, `append` adds it to what is shown (send tokens as they arrive), `clear` removes it. The newest three lines stay visible. With `mouth` the face's mouth moves with the text at reading pace, as if speaking.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    type: Literal["display.subtitle"] = Field(
        ..., pattern="^[a-z][a-z_]*(\\.[a-z][a-z_]*)?$"
    )
    """
    Message type, e.g. `hello`, `face.set_emotion`, `imu`.
    """
    text: str | None = Field(None, max_length=4000)
    """
    Plain text; a line break starts a new line. Required unless `mode` is `clear`.
    """
    mode: Literal["replace", "append", "clear"] | None = None
    """
    Default `replace`.
    """
    position: Literal["bottom", "top"] | None = None
    """
    Default `bottom`.
    """
    duration_ms: int | None = Field(None, ge=0, le=600000, title="CommonDurationMs")
    """
    Clear this long after the last update. Omit to hold until replaced or cleared.
    """
    mouth: bool | None = None
    """
    Move the mouth with the text at reading pace. Default false; ignored while `face.envelope` is streaming.
    """


class Env(Envelope, EnvFields):
    """
    Barometer, magnetometer and compass, up to 10 Hz. A field is left out when the device lacks the sensor or has no reading yet; the barometer needs Motion & Fitness access, which the first subscription asks for. Magnetic field in the `imu` device frame (+x right, +y up, +z out of the screen, portrait). Every available field is present unless the subscription named `fields`.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    type: Literal["env"] = Field(..., pattern="^[a-z][a-z_]*(\\.[a-z][a-z_]*)?$")
    """
    Message type, e.g. `hello`, `face.set_emotion`, `imu`.
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
    confused: ExpressionsParams | None = None
    shocked: ExpressionsParams | None = None
    excited: ExpressionsParams | None = None
    bored: ExpressionsParams | None = None
    skeptical: ExpressionsParams | None = None
    worried: ExpressionsParams | None = None
    disgusted: ExpressionsParams | None = None
    embarrassed: ExpressionsParams | None = None
    proud: ExpressionsParams | None = None
    determined: ExpressionsParams | None = None
    relieved: ExpressionsParams | None = None
    annoyed: ExpressionsParams | None = None
    suspicious: ExpressionsParams | None = None
    laughing: ExpressionsParams | None = None
    disappointed: ExpressionsParams | None = None
    focused: ExpressionsParams | None = None
    nervous: ExpressionsParams | None = None
    smug: ExpressionsParams | None = None
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
    List installed face themes with their expressions, and HUD themes for the camera view.
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
    huds: list[FaceListHudInfo] | None = None
    """
    HUD themes for `display.show {content: camera}` (0.2).
    """


class FaceLookAt(Command):
    """
    Point the gaze. `screen`: `x`, `y` in [-1, 1] with origin at the screen centre, +x right, +y up. `head`: `yaw`, `pitch` in degrees in the head frame, +yaw left, +pitch up. `face`: follow a detected face (`faces` topic) until another `look_at`: `face_id`, or the locked (largest) face when omitted; the gaze rests when no face is seen. The world frame needs pose and arrives later.
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
    frame: Literal["screen", "head", "face"]
    x: float | None = Field(None, ge=-1.0, le=1.0, title="CommonSignedUnit")
    y: float | None = Field(None, ge=-1.0, le=1.0, title="CommonSignedUnit")
    yaw: float | None = Field(None, ge=-90.0, le=90.0)
    pitch: float | None = Field(None, ge=-90.0, le=90.0)
    face_id: int | None = Field(None, ge=0)
    """
    `face` only: the face to follow; default the locked (largest) face.
    """
    duration_ms: int | None = Field(None, ge=0, le=600000, title="CommonDurationMs")
    """
    Hold the gaze, then return to idle motion. Omit to hold until the next `look_at`.
    """


class FaceSetEmotion(Command):
    """
    Blend towards an emotion, independently of speech (the mouth envelope is added on top). Shared names, defined by every built-in theme: neutral, happy, curious, thinking, surprised, sad, angry, sleepy, scared, mischievous, confused, shocked, excited, bored, skeptical, worried, disgusted, embarrassed, proud, determined, relieved, annoyed, suspicious, laughing, disappointed, focused, nervous, smug. Themes may add extras (see `face.list`). Names the theme lacks fall back to `neutral` with a warning in the log.
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


class Faces(Envelope, FacesFields):
    """
    People in front of the head, up to 15 Hz while mode is `capture` (front camera, several faces, with `box`) or `sensing` (ARKit, one face, no `box`). Angles are in the head frame like `face.look_at`: +bearing to the head's left, +elevation up, in degrees. An empty list means nobody is seen. Every payload field is present unless the subscription named `fields`.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    type: Literal["faces"] = Field(..., pattern="^[a-z][a-z_]*(\\.[a-z][a-z_]*)?$")
    """
    Message type, e.g. `hello`, `face.set_emotion`, `imu`.
    """


class Gps(Envelope, GpsFields):
    """
    Where the head is on Earth, up to 1 Hz and only when there is a new fix, so a head standing still may send nothing for a while (CoreLocation: GNSS where the device has it, otherwise Wi-Fi). Sent only after the user allows location access; the first subscription asks. WGS 84. Every payload field is present unless the subscription named `fields`; `alt_m`, `v_accuracy_m`, `speed_m_s` and `course_deg` are left out when unknown.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    type: Literal["gps"] = Field(..., pattern="^[a-z][a-z_]*(\\.[a-z][a-z_]*)?$")
    """
    Message type, e.g. `hello`, `face.set_emotion`, `imu`.
    """


class Tint(BaseModel):
    """
    Colour laid over the camera image (works over a native camera view too).
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    color: str = Field(..., pattern="^#[0-9a-fA-F]{6}$", title="HudColor")
    opacity: float = Field(..., ge=0.0, le=1.0)


class HudBlock(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )
    at: Literal["top-left", "top-right", "bottom-left", "bottom-right", "left"]
    lines: list[str] = Field(..., max_length=16)
    size: float | None = Field(None, ge=0.5, le=3.0)
    """
    Text size; 1 is about 4.5% of the screen height.
    """
    color: str | None = Field(None, pattern="^#[0-9a-fA-F]{6}$", title="HudColor")
    blink_ms: int | None = Field(None, ge=0, le=5000)


class ImuFields(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )
    q: list[float] | None = Field(None, max_length=4, min_length=4)
    """
    Orientation as unit quaternion [x, y, z, w], relative to a gravity-aligned reference frame.
    """
    gyro: list[float] | None = Field(None, max_length=3, min_length=3, title="ImuVec3")
    """
    Angular rate in rad/s.
    """
    accel: list[float] | None = Field(None, max_length=3, min_length=3, title="ImuVec3")
    """
    Specific force in m/s^2, as a ROS IMU reports it: at rest upright about +9.81 on +y. (iOS CoreMotion reports the opposite sign.)
    """
    frame: Literal["device", "mount"] | None = None
    sensor_time_s: float | None = Field(None, ge=0.0)
    """
    Sensor timestamp in seconds since device boot, for precise intervals between samples.
    """


class ImuPayload(ImuFields):
    """
    Complete payload, as sent when the subscription names no `fields`.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    q: list[float] = Field(..., max_length=4, min_length=4)
    """
    Orientation as unit quaternion [x, y, z, w], relative to a gravity-aligned reference frame.
    """
    gyro: list[float] = Field(..., max_length=3, min_length=3, title="ImuVec3")
    """
    Angular rate in rad/s.
    """
    accel: list[float] = Field(..., max_length=3, min_length=3, title="ImuVec3")
    """
    Specific force in m/s^2, as a ROS IMU reports it: at rest upright about +9.81 on +y. (iOS CoreMotion reports the opposite sign.)
    """
    frame: Literal["device", "mount"]
    sensor_time_s: float = Field(..., ge=0.0)
    """
    Sensor timestamp in seconds since device boot, for precise intervals between samples.
    """


class Log(Envelope, LogFields):
    """
    One structured log line, sent as it happens. Every received command is logged with its `seq` in `seq_ref`. Every payload field is present unless the subscription named `fields`; then only those are.
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
    Choose who owns the cameras. `idle`: no camera (default). `capture`: the front camera runs for the camera view and face detection (`faces` with boxes, several faces); pose only as orientation from `imu`. `sensing`: ARKit owns the cameras: world tracking gives `pose` (position and orientation) and one face is tracked with the depth camera (`faces` without boxes); no camera image. Asks for camera permission the first time; `unsupported` where the device cannot.
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


class Pose(Envelope, PoseFields):
    """
    Where the head is, up to 60 Hz while mode is `sensing` (ARKit world tracking). World frame: origin where tracking started, +y up (against gravity), +x and +z horizontal; position in metres. `q` turns the device frame of `imu` into the world frame ([x, y, z, w]). Every payload field is present unless the subscription named `fields`.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    type: Literal["pose"] = Field(..., pattern="^[a-z][a-z_]*(\\.[a-z][a-z_]*)?$")
    """
    Message type, e.g. `hello`, `face.set_emotion`, `imu`.
    """


class Status(Envelope, StatusFields):
    """
    Device status, up to 1 Hz. Also the result of `system.status`. Every payload field is present unless the subscription named `fields`; then only those are.
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
    topic: Literal["imu", "status", "log", "faces", "pose", "gps", "env"] = Field(
        ..., title="CommonTopic"
    )
    """
    Subscribable stream. `faces` needs mode `capture` or `sensing`, `pose` needs `sensing`; `gps` asks for location access and `env` for Motion & Fitness access on first use.
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
    Read all settings, or set one. `set` needs dev mode. Known keys in 0.1: `name`, `port`, `mount_offset` ([x, y, z, w] quaternion), `offline_theme` (the head's own theme: shown at start and as soon as it is set; a client may switch theme with `face.set_theme`, and the face returns to this one when the last paired client disconnects).
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
    blink_interval_ms: list[int] = Field(
        ..., max_length=2, min_length=2, title="ThemeRangeMs"
    )
    """
    [min, max] in milliseconds; a value is drawn uniformly each time.
    """
    blink_duration_ms: int = Field(..., ge=30, le=2000)
    saccade_interval_ms: list[int] | None = Field(
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
    topic: Literal["imu", "status", "log", "faces", "pose", "gps", "env"] = Field(
        ..., title="CommonTopic"
    )
    """
    Subscribable stream. `faces` needs mode `capture` or `sensing`, `pose` needs `sensing`; `gps` asks for location access and `env` for Motion & Fitness access on first use.
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


class DisplayHud(Command):
    """
    Put your own information on the camera view's HUD, on top of the theme. `values` are variables for templates ({speed}, {task}); they are merged with earlier ones (send null to remove one). `blocks` are extra text blocks and `widgets` extra instruments, as in a HUD theme; each replaces the previous ones sent this way. `clear` removes everything added with this command. Kept until cleared, across HUD themes.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    type: Literal["display.hud"] = Field(
        ..., pattern="^[a-z][a-z_]*(\\.[a-z][a-z_]*)?$"
    )
    """
    Message type, e.g. `hello`, `face.set_emotion`, `imu`.
    """
    values: (
        dict[
            constr(pattern=r"^[a-z][a-z0-9_]{0,31}$"),
            constr(max_length=80) | float | bool | None,
        ]
        | None
    ) = Field(None, max_length=32)
    blocks: list[HudBlock] | None = Field(None, max_length=8)
    widgets: list[HudWidget] | None = Field(None, max_length=6)
    clear: bool | None = None


class Hud(BaseModel):
    """
    A HUD theme (`face/huds/<name>/hud.json`): what is drawn over the camera view. Text lines are templates. Built in: {faces} faces seen, {target} locked face id or NONE, {status} LOCKED or SEARCHING, {id} {conf} {bearing} {elevation} {size} of the locked face, {frame} frame counter, {time} timecode since the view opened, {rand:N} N random digits; from the device: {battery} percent, {charging} YES/NO, {thermal} nominal/fair/serious/critical, {heading} compass degrees, {heading_name} N/NE/E..., {pitch} and {roll} degrees, {x} {y} {z} position in metres and {tracking} (mode sensing), {mode}, {clients}, {lat} {lon} {alt} {gps_acc} (while `gps` runs), {pressure} hPa (while `env` runs). Hosts add their own with `display.hud {values}` and use them the same way, e.g. {speed}. Unknown names show as `-`.
    """

    model_config = ConfigDict(
        extra="ignore",
    )
    name: str = Field(..., pattern="^[a-z][a-z0-9_-]{0,31}$", title="CommonName")
    """
    Lower-case identifier used for themes and emotions.
    """
    title: str
    version: str = Field(
        ..., pattern="^[0-9]+\\.[0-9]+\\.[0-9]+$", title="CommonVersion"
    )
    """
    Semantic version, MAJOR.MINOR.PATCH.
    """
    font: Literal["mono", "sans"] | None = None
    """
    Default mono.
    """
    color: str = Field(..., pattern="^#[0-9a-fA-F]{6}$", title="HudColor")
    """
    Text and boxes.
    """
    accent: str | None = Field(None, pattern="^#[0-9a-fA-F]{6}$", title="HudColor")
    """
    The locked face and highlights.
    """
    shadow: str | None = Field(None, pattern="^#[0-9a-fA-F]{6}$", title="HudColor")
    """
    Glow or shadow behind text and lines.
    """
    tint: Tint | None = None
    """
    Colour laid over the camera image (works over a native camera view too).
    """
    scanlines: Scanlines | None = None
    vignette: float | None = Field(None, ge=0.0, le=1.0)
    """
    Darker corners.
    """
    boxes: Boxes | None = None
    """
    How every detected face is marked.
    """
    lock: Lock | None = None
    """
    How the locked face (the largest, or the one `look_at` follows) is marked.
    """
    blocks: list[HudBlock] | None = Field(None, max_length=8)
    widgets: list[HudWidget] | None = Field(None, max_length=6)
    boot: Boot | None = None
    """
    Lines typed out one by one when the view opens, then kept on screen at the left.
    """


class Imu(Envelope, ImuFields):
    """
    Inertial sample, up to 100 Hz. Right-handed frame: in `device` frame +x is right, +y is up and +z points out of the screen (portrait). `mount` applies the `mount_offset` setting. Every payload field is present unless the subscription named `fields`; then only those are.
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
    capabilities: list[str]
    """
    Feature flags. Known: 0.1 `face`, `display.image`, `display.video`, `display.web`, `display.subtitle`, `imu`, `status`, `log`, `screenshot`; 0.2 `camera`, `faces`, `pose` (where the device supports them); 0.3 `gps`, `env`. Clients ignore unknown values.
    """
    themes: list[str]
    dev_mode: bool
