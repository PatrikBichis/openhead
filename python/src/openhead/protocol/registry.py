# Generated from protocol/schema by tools/protocol.py. Do not edit.
"""Map of message `type` to its generated model."""

from pydantic import BaseModel

from . import models

PROTOCOL_VERSION = "0.2.0"

MESSAGE_TYPES: dict[str, type[BaseModel]] = {
    "ack": models.Ack,
    "display.clear": models.DisplayClear,
    "display.show": models.DisplayShow,
    "display.subtitle": models.DisplaySubtitle,
    "error": models.Error,
    "face.blink": models.FaceBlink,
    "face.envelope": models.FaceEnvelope,
    "face.list": models.FaceList,
    "face.look_at": models.FaceLookAt,
    "face.set_emotion": models.FaceSetEmotion,
    "face.set_theme": models.FaceSetTheme,
    "faces": models.Faces,
    "hello": models.Hello,
    "imu": models.Imu,
    "log": models.Log,
    "mode.get": models.ModeGet,
    "mode.set": models.ModeSet,
    "pair": models.Pair,
    "pair_required": models.PairRequired,
    "pose": models.Pose,
    "status": models.Status,
    "subscribe": models.Subscribe,
    "system.diagnostics": models.SystemDiagnostics,
    "system.logs": models.SystemLogs,
    "system.screenshot": models.SystemScreenshot,
    "system.settings": models.SystemSettings,
    "system.status": models.SystemStatus,
    "unsubscribe": models.Unsubscribe,
    "welcome": models.Welcome,
}
