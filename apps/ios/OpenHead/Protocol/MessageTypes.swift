// Generated from protocol/schema by tools/protocol.py (quicktype). Do not edit.

public let protocolVersion = "0.2.0"

/// Message `type` to its generated model.
public let messageTypes: [String: any Codable.Type] = [
    "ack": ACK.self,
    "display.clear": DisplayClear.self,
    "display.show": DisplayShow.self,
    "display.subtitle": DisplaySubtitle.self,
    "error": ProtocolError.self,
    "face.blink": FaceBlink.self,
    "face.envelope": FaceEnvelope.self,
    "face.list": FaceList.self,
    "face.look_at": FaceLookAt.self,
    "face.set_emotion": FaceSetEmotion.self,
    "face.set_theme": FaceSetTheme.self,
    "faces": Faces.self,
    "hello": Hello.self,
    "imu": Imu.self,
    "log": Log.self,
    "mode.get": ModeGet.self,
    "mode.set": ModeSet.self,
    "pair": Pair.self,
    "pair_required": PairRequired.self,
    "pose": Pose.self,
    "status": Status.self,
    "subscribe": Subscribe.self,
    "system.diagnostics": SystemDiagnostics.self,
    "system.logs": SystemLogs.self,
    "system.screenshot": SystemScreenshot.self,
    "system.settings": SystemSettings.self,
    "system.status": SystemStatus.self,
    "unsubscribe": Unsubscribe.self,
    "welcome": Welcome.self,
]
