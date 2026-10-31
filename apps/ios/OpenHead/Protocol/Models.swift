// Generated from protocol/schema by tools/protocol.py (quicktype). Do not edit.

// This file was generated from JSON Schema using quicktype, do not modify it directly.
// To parse the JSON, add this file to your project and do:
//
//   let openHeadProtocol = try? JSONDecoder().decode(OpenHeadProtocol.self, from: jsonData)


import Foundation

// MARK: - OpenHeadProtocol
public struct OpenHeadProtocol: Codable, Equatable, Sendable {
    public let ack: ACK?
    public let displayClear: DisplayClear?
    public let displayShow: DisplayShow?
    public let displaySubtitle: DisplaySubtitle?
    public let faceBlink: FaceBlink?
    public let faceEnvelope: FaceEnvelope?
    public let faceList: FaceList?
    public let faceListHudInfo: FaceListHudInfo?
    public let faceListResult: FaceListResult?
    public let faceListThemeInfo: FaceListThemeInfo?
    public let faceLookAt: FaceLookAt?
    public let faces: Faces?
    public let facesBox: FacesBox?
    public let faceSetEmotion: FaceSetEmotion?
    public let faceSetTheme: FaceSetTheme?
    public let facesFace: FacesFace?
    public let facesFields: FacesFields?
    public let facesPayload: FacesPayload?
    public let hello: Hello?
    public let hud: Hud?
    public let imu: Imu?
    public let imuFields: ImuFields?
    public let imuPayload: ImuPayload?
    public let log: Log?
    public let logFields: LogFields?
    public let logPayload: LogPayload?
    public let modeGet: ModeGet?
    public let modeGetResult: ModeGetResult?
    public let modeSet: ModeSet?
    public let pair: Pair?
    public let pairRequired: PairRequired?
    public let pose: Pose?
    public let poseFields: PoseFields?
    public let posePayload: PosePayload?
    public let protocolError: ProtocolError?
    public let status: Status?
    public let statusFields: StatusFields?
    public let statusPayload: StatusPayload?
    public let subscribe: Subscribe?
    public let subscribeResult: SubscribeResult?
    public let systemDiagnostics: SystemDiagnostics?
    public let systemDiagnosticsResult: SystemDiagnosticsResult?
    public let systemLogs: SystemLogs?
    public let systemLogsResult: SystemLogsResult?
    public let systemScreenshot: SystemScreenshot?
    public let systemScreenshotResult: SystemScreenshotResult?
    public let systemSettings: SystemSettings?
    public let systemSettingsResult: SystemSettingsResult?
    public let systemStatus: SystemStatus?
    public let unsubscribe: Unsubscribe?
    public let welcome: Welcome?
    public let welcomeDevice: WelcomeDevice?
    public let welcomeInsets: WelcomeInsets?
    public let welcomeScreen: WelcomeScreen?

    public enum CodingKeys: String, CodingKey {
        case ack = "Ack"
        case displayClear = "DisplayClear"
        case displayShow = "DisplayShow"
        case displaySubtitle = "DisplaySubtitle"
        case faceBlink = "FaceBlink"
        case faceEnvelope = "FaceEnvelope"
        case faceList = "FaceList"
        case faceListHudInfo = "FaceListHudInfo"
        case faceListResult = "FaceListResult"
        case faceListThemeInfo = "FaceListThemeInfo"
        case faceLookAt = "FaceLookAt"
        case faces = "Faces"
        case facesBox = "FacesBox"
        case faceSetEmotion = "FaceSetEmotion"
        case faceSetTheme = "FaceSetTheme"
        case facesFace = "FacesFace"
        case facesFields = "FacesFields"
        case facesPayload = "FacesPayload"
        case hello = "Hello"
        case hud = "Hud"
        case imu = "Imu"
        case imuFields = "ImuFields"
        case imuPayload = "ImuPayload"
        case log = "Log"
        case logFields = "LogFields"
        case logPayload = "LogPayload"
        case modeGet = "ModeGet"
        case modeGetResult = "ModeGetResult"
        case modeSet = "ModeSet"
        case pair = "Pair"
        case pairRequired = "PairRequired"
        case pose = "Pose"
        case poseFields = "PoseFields"
        case posePayload = "PosePayload"
        case protocolError = "ProtocolError"
        case status = "Status"
        case statusFields = "StatusFields"
        case statusPayload = "StatusPayload"
        case subscribe = "Subscribe"
        case subscribeResult = "SubscribeResult"
        case systemDiagnostics = "SystemDiagnostics"
        case systemDiagnosticsResult = "SystemDiagnosticsResult"
        case systemLogs = "SystemLogs"
        case systemLogsResult = "SystemLogsResult"
        case systemScreenshot = "SystemScreenshot"
        case systemScreenshotResult = "SystemScreenshotResult"
        case systemSettings = "SystemSettings"
        case systemSettingsResult = "SystemSettingsResult"
        case systemStatus = "SystemStatus"
        case unsubscribe = "Unsubscribe"
        case welcome = "Welcome"
        case welcomeDevice = "WelcomeDevice"
        case welcomeInsets = "WelcomeInsets"
        case welcomeScreen = "WelcomeScreen"
    }

    public init(ack: ACK?, displayClear: DisplayClear?, displayShow: DisplayShow?, displaySubtitle: DisplaySubtitle?, faceBlink: FaceBlink?, faceEnvelope: FaceEnvelope?, faceList: FaceList?, faceListHudInfo: FaceListHudInfo?, faceListResult: FaceListResult?, faceListThemeInfo: FaceListThemeInfo?, faceLookAt: FaceLookAt?, faces: Faces?, facesBox: FacesBox?, faceSetEmotion: FaceSetEmotion?, faceSetTheme: FaceSetTheme?, facesFace: FacesFace?, facesFields: FacesFields?, facesPayload: FacesPayload?, hello: Hello?, hud: Hud?, imu: Imu?, imuFields: ImuFields?, imuPayload: ImuPayload?, log: Log?, logFields: LogFields?, logPayload: LogPayload?, modeGet: ModeGet?, modeGetResult: ModeGetResult?, modeSet: ModeSet?, pair: Pair?, pairRequired: PairRequired?, pose: Pose?, poseFields: PoseFields?, posePayload: PosePayload?, protocolError: ProtocolError?, status: Status?, statusFields: StatusFields?, statusPayload: StatusPayload?, subscribe: Subscribe?, subscribeResult: SubscribeResult?, systemDiagnostics: SystemDiagnostics?, systemDiagnosticsResult: SystemDiagnosticsResult?, systemLogs: SystemLogs?, systemLogsResult: SystemLogsResult?, systemScreenshot: SystemScreenshot?, systemScreenshotResult: SystemScreenshotResult?, systemSettings: SystemSettings?, systemSettingsResult: SystemSettingsResult?, systemStatus: SystemStatus?, unsubscribe: Unsubscribe?, welcome: Welcome?, welcomeDevice: WelcomeDevice?, welcomeInsets: WelcomeInsets?, welcomeScreen: WelcomeScreen?) {
        self.ack = ack
        self.displayClear = displayClear
        self.displayShow = displayShow
        self.displaySubtitle = displaySubtitle
        self.faceBlink = faceBlink
        self.faceEnvelope = faceEnvelope
        self.faceList = faceList
        self.faceListHudInfo = faceListHudInfo
        self.faceListResult = faceListResult
        self.faceListThemeInfo = faceListThemeInfo
        self.faceLookAt = faceLookAt
        self.faces = faces
        self.facesBox = facesBox
        self.faceSetEmotion = faceSetEmotion
        self.faceSetTheme = faceSetTheme
        self.facesFace = facesFace
        self.facesFields = facesFields
        self.facesPayload = facesPayload
        self.hello = hello
        self.hud = hud
        self.imu = imu
        self.imuFields = imuFields
        self.imuPayload = imuPayload
        self.log = log
        self.logFields = logFields
        self.logPayload = logPayload
        self.modeGet = modeGet
        self.modeGetResult = modeGetResult
        self.modeSet = modeSet
        self.pair = pair
        self.pairRequired = pairRequired
        self.pose = pose
        self.poseFields = poseFields
        self.posePayload = posePayload
        self.protocolError = protocolError
        self.status = status
        self.statusFields = statusFields
        self.statusPayload = statusPayload
        self.subscribe = subscribe
        self.subscribeResult = subscribeResult
        self.systemDiagnostics = systemDiagnostics
        self.systemDiagnosticsResult = systemDiagnosticsResult
        self.systemLogs = systemLogs
        self.systemLogsResult = systemLogsResult
        self.systemScreenshot = systemScreenshot
        self.systemScreenshotResult = systemScreenshotResult
        self.systemSettings = systemSettings
        self.systemSettingsResult = systemSettingsResult
        self.systemStatus = systemStatus
        self.unsubscribe = unsubscribe
        self.welcome = welcome
        self.welcomeDevice = welcomeDevice
        self.welcomeInsets = welcomeInsets
        self.welcomeScreen = welcomeScreen
    }
}


/// Successful reply to a command. Commands that return data put it in `result`; its shape is
/// the command schema's `$defs/result`.
// MARK: - ACK
public struct ACK: Codable, Equatable, Sendable {
    public let id: String
    public let result: [String: JSONValue]?
    /// Per-connection, per-direction counter, starting at 0.
    public let seq: Int
    /// Sender clock in milliseconds since the Unix epoch.
    public let ts: Int
    public let type: ACKType

    public enum CodingKeys: String, CodingKey {
        case id = "id"
        case result = "result"
        case seq = "seq"
        case ts = "ts"
        case type = "type"
    }

    public init(id: String, result: [String: JSONValue]?, seq: Int, ts: Int, type: ACKType) {
        self.id = id
        self.result = result
        self.seq = seq
        self.ts = ts
        self.type = type
    }
}

public enum ACKType: String, Codable, Equatable, Sendable {
    case ack = "ack"
}


/// Remove any image or web page and show the face full screen.
// MARK: - DisplayClear
public struct DisplayClear: Codable, Equatable, Sendable {
    /// Client-chosen id, echoed in the reply.
    public let id: String
    /// Per-connection, per-direction counter, starting at 0.
    public let seq: Int
    /// Sender clock in milliseconds since the Unix epoch.
    public let ts: Int
    public let type: DisplayClearType

    public enum CodingKeys: String, CodingKey {
        case id = "id"
        case seq = "seq"
        case ts = "ts"
        case type = "type"
    }

    public init(id: String, seq: Int, ts: Int, type: DisplayClearType) {
        self.id = id
        self.seq = seq
        self.ts = ts
        self.type = type
    }
}

public enum DisplayClearType: String, Codable, Equatable, Sendable {
    case displayClear = "display.clear"
}


/// Change what fills the screen. `content` is named so to avoid clashing with the envelope's
/// `type`. Images (PNG, JPEG, GIF including animated, WebP, SVG) come as an http(s) URL the
/// device fetches, or as a `data:image/...;base64,` URI under 1 MB. Video comes as an
/// http(s) URL (H.264 or HEVC in MP4/MOV; the simulator plays H.264, VP9 and AV1); without
/// `loop` the face returns when it ends. `camera` shows the front camera with a HUD theme
/// (`hud`) drawn over it: boxes around faces, the locked target, text; it switches to mode
/// `capture` if needed. With `overlay: face-corner` the face keeps running in a corner.
// MARK: - DisplayShow
public struct DisplayShow: Codable, Equatable, Sendable {
    public let content: CommonView
    /// Return to the face after this time. Omit to hold.
    public let durationMS: Int?
    /// `camera` only: HUD theme from `face.list` (`huds`), or `none` for the bare camera.
    /// Default `hunter`.
    public let hud: String?
    /// Client-chosen id, echoed in the reply.
    public let id: String
    /// `video` only: start again at the end. Default false.
    public let loop: Bool?
    /// `video` only: no sound. Default false.
    public let muted: Bool?
    /// Default `none`.
    public let overlay: Overlay?
    /// Per-connection, per-direction counter, starting at 0.
    public let seq: Int
    /// Required for `image`, `video` and `web`. `video` and `web` accept http(s) URLs only.
    public let source: String?
    /// Sender clock in milliseconds since the Unix epoch.
    public let ts: Int
    public let type: DisplayShowType

    public enum CodingKeys: String, CodingKey {
        case content = "content"
        case durationMS = "duration_ms"
        case hud = "hud"
        case id = "id"
        case loop = "loop"
        case muted = "muted"
        case overlay = "overlay"
        case seq = "seq"
        case source = "source"
        case ts = "ts"
        case type = "type"
    }

    public init(content: CommonView, durationMS: Int?, hud: String?, id: String, loop: Bool?, muted: Bool?, overlay: Overlay?, seq: Int, source: String?, ts: Int, type: DisplayShowType) {
        self.content = content
        self.durationMS = durationMS
        self.hud = hud
        self.id = id
        self.loop = loop
        self.muted = muted
        self.overlay = overlay
        self.seq = seq
        self.source = source
        self.ts = ts
        self.type = type
    }
}

/// What fills the screen.
public enum CommonView: String, Codable, Equatable, Sendable {
    case camera = "camera"
    case face = "face"
    case image = "image"
    case video = "video"
    case web = "web"
}

/// Default `none`.
public enum Overlay: String, Codable, Equatable, Sendable {
    case faceCorner = "face-corner"
    case none = "none"
}

public enum DisplayShowType: String, Codable, Equatable, Sendable {
    case displayShow = "display.show"
}


/// Text on top of whatever is shown (face, image, video, web page): for a robot without a
/// speaker, or to show an AI answer as it streams in. `replace` shows `text` alone, `append`
/// adds it to what is shown (send tokens as they arrive), `clear` removes it. The newest
/// three lines stay visible. With `mouth` the face's mouth moves with the text at reading
/// pace, as if speaking.
// MARK: - DisplaySubtitle
public struct DisplaySubtitle: Codable, Equatable, Sendable {
    /// Clear this long after the last update. Omit to hold until replaced or cleared.
    public let durationMS: Int?
    /// Client-chosen id, echoed in the reply.
    public let id: String
    /// Default `replace`.
    public let mode: Mode?
    /// Move the mouth with the text at reading pace. Default false; ignored while
    /// `face.envelope` is streaming.
    public let mouth: Bool?
    /// Default `bottom`.
    public let position: Position?
    /// Per-connection, per-direction counter, starting at 0.
    public let seq: Int
    /// Plain text; a line break starts a new line. Required unless `mode` is `clear`.
    public let text: String?
    /// Sender clock in milliseconds since the Unix epoch.
    public let ts: Int
    public let type: DisplaySubtitleType

    public enum CodingKeys: String, CodingKey {
        case durationMS = "duration_ms"
        case id = "id"
        case mode = "mode"
        case mouth = "mouth"
        case position = "position"
        case seq = "seq"
        case text = "text"
        case ts = "ts"
        case type = "type"
    }

    public init(durationMS: Int?, id: String, mode: Mode?, mouth: Bool?, position: Position?, seq: Int, text: String?, ts: Int, type: DisplaySubtitleType) {
        self.durationMS = durationMS
        self.id = id
        self.mode = mode
        self.mouth = mouth
        self.position = position
        self.seq = seq
        self.text = text
        self.ts = ts
        self.type = type
    }
}

/// Default `replace`.
public enum Mode: String, Codable, Equatable, Sendable {
    case append = "append"
    case clear = "clear"
    case replace = "replace"
}

/// Default `bottom`.
public enum Position: String, Codable, Equatable, Sendable {
    case bottom = "bottom"
    case top = "top"
}

public enum DisplaySubtitleType: String, Codable, Equatable, Sendable {
    case displaySubtitle = "display.subtitle"
}


/// Blink once now, in the theme's blink style.
// MARK: - FaceBlink
public struct FaceBlink: Codable, Equatable, Sendable {
    /// Client-chosen id, echoed in the reply.
    public let id: String
    /// Per-connection, per-direction counter, starting at 0.
    public let seq: Int
    /// Sender clock in milliseconds since the Unix epoch.
    public let ts: Int
    public let type: FaceBlinkType

    public enum CodingKeys: String, CodingKey {
        case id = "id"
        case seq = "seq"
        case ts = "ts"
        case type = "type"
    }

    public init(id: String, seq: Int, ts: Int, type: FaceBlinkType) {
        self.id = id
        self.seq = seq
        self.ts = ts
        self.type = type
    }
}

public enum FaceBlinkType: String, Codable, Equatable, Sendable {
    case faceBlink = "face.blink"
}


/// Mouth envelope from the host's speech audio, sent as a stream at 20-30 Hz while speaking.
/// Not a command: no `id` and no reply. The face decays to closed if no update arrives for
/// 200 ms.
// MARK: - FaceEnvelope
public struct FaceEnvelope: Codable, Equatable, Sendable {
    public let level: Double
    /// Per-connection, per-direction counter, starting at 0.
    public let seq: Int
    /// Sender clock in milliseconds since the Unix epoch.
    public let ts: Int
    public let type: FaceEnvelopeType

    public enum CodingKeys: String, CodingKey {
        case level = "level"
        case seq = "seq"
        case ts = "ts"
        case type = "type"
    }

    public init(level: Double, seq: Int, ts: Int, type: FaceEnvelopeType) {
        self.level = level
        self.seq = seq
        self.ts = ts
        self.type = type
    }
}

public enum FaceEnvelopeType: String, Codable, Equatable, Sendable {
    case faceEnvelope = "face.envelope"
}


/// List installed face themes with their expressions, and HUD themes for the camera view.
// MARK: - FaceList
public struct FaceList: Codable, Equatable, Sendable {
    /// Client-chosen id, echoed in the reply.
    public let id: String
    /// Per-connection, per-direction counter, starting at 0.
    public let seq: Int
    /// Sender clock in milliseconds since the Unix epoch.
    public let ts: Int
    public let type: FaceListType

    public enum CodingKeys: String, CodingKey {
        case id = "id"
        case seq = "seq"
        case ts = "ts"
        case type = "type"
    }

    public init(id: String, seq: Int, ts: Int, type: FaceListType) {
        self.id = id
        self.seq = seq
        self.ts = ts
        self.type = type
    }
}

public enum FaceListType: String, Codable, Equatable, Sendable {
    case faceList = "face.list"
}


// MARK: - FaceListHudInfo
public struct FaceListHudInfo: Codable, Equatable, Sendable {
    public let name: String
    public let title: String
    public let version: String?

    public enum CodingKeys: String, CodingKey {
        case name = "name"
        case title = "title"
        case version = "version"
    }

    public init(name: String, title: String, version: String?) {
        self.name = name
        self.title = title
        self.version = version
    }
}


// MARK: - FaceListResult
public struct FaceListResult: Codable, Equatable, Sendable {
    public let active: String
    /// HUD themes for `display.show {content: camera}` (0.2).
    public let huds: [FaceListHudInfo]?
    public let themes: [FaceListThemeInfo]

    public enum CodingKeys: String, CodingKey {
        case active = "active"
        case huds = "huds"
        case themes = "themes"
    }

    public init(active: String, huds: [FaceListHudInfo]?, themes: [FaceListThemeInfo]) {
        self.active = active
        self.huds = huds
        self.themes = themes
    }
}


// MARK: - FaceListThemeInfo
public struct FaceListThemeInfo: Codable, Equatable, Sendable {
    /// Shared emotion names the theme defines.
    public let expressions: [String]
    /// Theme-specific expressions, e.g. `cackle`.
    public let extras: [String]
    public let name: String
    public let title: String?
    public let version: String

    public enum CodingKeys: String, CodingKey {
        case expressions = "expressions"
        case extras = "extras"
        case name = "name"
        case title = "title"
        case version = "version"
    }

    public init(expressions: [String], extras: [String], name: String, title: String?, version: String) {
        self.expressions = expressions
        self.extras = extras
        self.name = name
        self.title = title
        self.version = version
    }
}


/// Point the gaze. `screen`: `x`, `y` in [-1, 1] with origin at the screen centre, +x right,
/// +y up. `head`: `yaw`, `pitch` in degrees in the head frame, +yaw left, +pitch up. `face`:
/// follow a detected face (`faces` topic) until another `look_at`: `face_id`, or the locked
/// (largest) face when omitted; the gaze rests when no face is seen. The world frame needs
/// pose and arrives later.
// MARK: - FaceLookAt
public struct FaceLookAt: Codable, Equatable, Sendable {
    /// Hold the gaze, then return to idle motion. Omit to hold until the next `look_at`.
    public let durationMS: Int?
    /// `face` only: the face to follow; default the locked (largest) face.
    public let faceID: Int?
    public let frame: FaceLookAtFrame
    /// Client-chosen id, echoed in the reply.
    public let id: String
    public let pitch: Double?
    /// Per-connection, per-direction counter, starting at 0.
    public let seq: Int
    /// Sender clock in milliseconds since the Unix epoch.
    public let ts: Int
    public let type: FaceLookAtType
    public let x: Double?
    public let y: Double?
    public let yaw: Double?

    public enum CodingKeys: String, CodingKey {
        case durationMS = "duration_ms"
        case faceID = "face_id"
        case frame = "frame"
        case id = "id"
        case pitch = "pitch"
        case seq = "seq"
        case ts = "ts"
        case type = "type"
        case x = "x"
        case y = "y"
        case yaw = "yaw"
    }

    public init(durationMS: Int?, faceID: Int?, frame: FaceLookAtFrame, id: String, pitch: Double?, seq: Int, ts: Int, type: FaceLookAtType, x: Double?, y: Double?, yaw: Double?) {
        self.durationMS = durationMS
        self.faceID = faceID
        self.frame = frame
        self.id = id
        self.pitch = pitch
        self.seq = seq
        self.ts = ts
        self.type = type
        self.x = x
        self.y = y
        self.yaw = yaw
    }
}

public enum FaceLookAtFrame: String, Codable, Equatable, Sendable {
    case face = "face"
    case head = "head"
    case screen = "screen"
}

public enum FaceLookAtType: String, Codable, Equatable, Sendable {
    case faceLookAt = "face.look_at"
}


/// Blend towards an emotion, independently of speech (the mouth envelope is added on top).
/// Shared names, defined by every built-in theme: neutral, happy, curious, thinking,
/// surprised, sad, angry, sleepy, scared, mischievous, confused, shocked, excited, bored,
/// skeptical, worried, disgusted, embarrassed, proud, determined, relieved, annoyed,
/// suspicious, laughing, disappointed, focused, nervous, smug. Themes may add extras (see
/// `face.list`). Names the theme lacks fall back to `neutral` with a warning in the log.
// MARK: - FaceSetEmotion
public struct FaceSetEmotion: Codable, Equatable, Sendable {
    /// `replace` fades out other emotions; `add` layers on top. Default `replace`.
    public let blend: Blend?
    /// Return to the resting emotion after this time. Omit to hold.
    public let durationMS: Int?
    /// Client-chosen id, echoed in the reply.
    public let id: String
    /// Weight of the emotion. Default 1.
    public let intensity: Double?
    public let name: String
    /// Per-connection, per-direction counter, starting at 0.
    public let seq: Int
    /// Sender clock in milliseconds since the Unix epoch.
    public let ts: Int
    public let type: FaceSetEmotionType

    public enum CodingKeys: String, CodingKey {
        case blend = "blend"
        case durationMS = "duration_ms"
        case id = "id"
        case intensity = "intensity"
        case name = "name"
        case seq = "seq"
        case ts = "ts"
        case type = "type"
    }

    public init(blend: Blend?, durationMS: Int?, id: String, intensity: Double?, name: String, seq: Int, ts: Int, type: FaceSetEmotionType) {
        self.blend = blend
        self.durationMS = durationMS
        self.id = id
        self.intensity = intensity
        self.name = name
        self.seq = seq
        self.ts = ts
        self.type = type
    }
}

/// `replace` fades out other emotions; `add` layers on top. Default `replace`.
public enum Blend: String, Codable, Equatable, Sendable {
    case add = "add"
    case replace = "replace"
}

public enum FaceSetEmotionType: String, Codable, Equatable, Sendable {
    case faceSetEmotion = "face.set_emotion"
}


/// Switch the face to an installed theme. Unknown names give `invalid_params`.
// MARK: - FaceSetTheme
public struct FaceSetTheme: Codable, Equatable, Sendable {
    /// Client-chosen id, echoed in the reply.
    public let id: String
    public let name: String
    /// Per-connection, per-direction counter, starting at 0.
    public let seq: Int
    /// Cross-fade time. Default 300.
    public let transitionMS: Int?
    /// Sender clock in milliseconds since the Unix epoch.
    public let ts: Int
    public let type: FaceSetThemeType

    public enum CodingKeys: String, CodingKey {
        case id = "id"
        case name = "name"
        case seq = "seq"
        case transitionMS = "transition_ms"
        case ts = "ts"
        case type = "type"
    }

    public init(id: String, name: String, seq: Int, transitionMS: Int?, ts: Int, type: FaceSetThemeType) {
        self.id = id
        self.name = name
        self.seq = seq
        self.transitionMS = transitionMS
        self.ts = ts
        self.type = type
    }
}

public enum FaceSetThemeType: String, Codable, Equatable, Sendable {
    case faceSetTheme = "face.set_theme"
}


/// People in front of the head, up to 15 Hz while mode is `capture` (front camera, several
/// faces, with `box`) or `sensing` (ARKit, one face, no `box`). Angles are in the head frame
/// like `face.look_at`: +bearing to the head's left, +elevation up, in degrees. An empty
/// list means nobody is seen. Every payload field is present unless the subscription named
/// `fields`.
// MARK: - Faces
public struct Faces: Codable, Equatable, Sendable {
    public let faces: [FacesFace]?
    public let sensorTimeS: Double?
    /// Per-connection, per-direction counter, starting at 0.
    public let seq: Int
    public let source: Source?
    /// Sender clock in milliseconds since the Unix epoch.
    public let ts: Int
    public let type: FacesType

    public enum CodingKeys: String, CodingKey {
        case faces = "faces"
        case sensorTimeS = "sensor_time_s"
        case seq = "seq"
        case source = "source"
        case ts = "ts"
        case type = "type"
    }

    public init(faces: [FacesFace]?, sensorTimeS: Double?, seq: Int, source: Source?, ts: Int, type: FacesType) {
        self.faces = faces
        self.sensorTimeS = sensorTimeS
        self.seq = seq
        self.source = source
        self.ts = ts
        self.type = type
    }
}


// MARK: - FacesFace
public struct FacesFace: Codable, Equatable, Sendable {
    /// Degrees, + to the head's left.
    public let bearing: Double
    public let box: FacesBox?
    public let confidence: Double
    /// Metres, when the depth camera measures it (`sensing`).
    public let distanceM: Double?
    /// Degrees, + up.
    public let elevation: Double
    /// Stable while the face stays in view.
    public let id: Int
    /// The face the HUD and `look_at {frame: face}` follow.
    public let locked: Bool?
    /// Face width as a share of the camera's field of view: bigger is closer.
    public let size: Double

    public enum CodingKeys: String, CodingKey {
        case bearing = "bearing"
        case box = "box"
        case confidence = "confidence"
        case distanceM = "distance_m"
        case elevation = "elevation"
        case id = "id"
        case locked = "locked"
        case size = "size"
    }

    public init(bearing: Double, box: FacesBox?, confidence: Double, distanceM: Double?, elevation: Double, id: Int, locked: Bool?, size: Double) {
        self.bearing = bearing
        self.box = box
        self.confidence = confidence
        self.distanceM = distanceM
        self.elevation = elevation
        self.id = id
        self.locked = locked
        self.size = size
    }
}


/// Where the face is in the camera view as shown on screen, normalised 0-1, origin top-left.
// MARK: - FacesBox
public struct FacesBox: Codable, Equatable, Sendable {
    public let h: Double
    public let w: Double
    public let x: Double
    public let y: Double

    public enum CodingKeys: String, CodingKey {
        case h = "h"
        case w = "w"
        case x = "x"
        case y = "y"
    }

    public init(h: Double, w: Double, x: Double, y: Double) {
        self.h = h
        self.w = w
        self.x = x
        self.y = y
    }
}

public enum Source: String, Codable, Equatable, Sendable {
    case arkit = "arkit"
    case sim = "sim"
    case vision = "vision"
}

public enum FacesType: String, Codable, Equatable, Sendable {
    case faces = "faces"
}


// MARK: - FacesFields
public struct FacesFields: Codable, Equatable, Sendable {
    public let faces: [FacesFace]?
    public let sensorTimeS: Double?
    public let source: Source?

    public enum CodingKeys: String, CodingKey {
        case faces = "faces"
        case sensorTimeS = "sensor_time_s"
        case source = "source"
    }

    public init(faces: [FacesFace]?, sensorTimeS: Double?, source: Source?) {
        self.faces = faces
        self.sensorTimeS = sensorTimeS
        self.source = source
    }
}


/// Complete payload, as sent when the subscription names no `fields`.
// MARK: - FacesPayload
public struct FacesPayload: Codable, Equatable, Sendable {
    public let faces: [FacesFace]
    public let sensorTimeS: Double
    public let source: Source

    public enum CodingKeys: String, CodingKey {
        case faces = "faces"
        case sensorTimeS = "sensor_time_s"
        case source = "source"
    }

    public init(faces: [FacesFace], sensorTimeS: Double, source: Source) {
        self.faces = faces
        self.sensorTimeS = sensorTimeS
        self.source = source
    }
}


/// First message on a new connection. Without a valid token the device answers
/// `pair_required`; with one it answers `welcome`. The major version must match the device's.
// MARK: - Hello
public struct Hello: Codable, Equatable, Sendable {
    /// Human-readable client name, shown on the pairing screen and in the client list.
    public let client: String
    public let protocolVersion: String
    /// Per-connection, per-direction counter, starting at 0.
    public let seq: Int
    /// Token from an earlier `welcome`.
    public let token: String?
    /// Sender clock in milliseconds since the Unix epoch.
    public let ts: Int
    public let type: HelloType

    public enum CodingKeys: String, CodingKey {
        case client = "client"
        case protocolVersion = "protocol_version"
        case seq = "seq"
        case token = "token"
        case ts = "ts"
        case type = "type"
    }

    public init(client: String, protocolVersion: String, seq: Int, token: String?, ts: Int, type: HelloType) {
        self.client = client
        self.protocolVersion = protocolVersion
        self.seq = seq
        self.token = token
        self.ts = ts
        self.type = type
    }
}

public enum HelloType: String, Codable, Equatable, Sendable {
    case hello = "hello"
}


/// A HUD theme (`face/huds/<name>/hud.json`): what is drawn over the camera view. Text lines
/// are templates: {faces} faces seen, {target} locked face id or NONE, {status} LOCKED or
/// SEARCHING, {id} {conf} {bearing} {elevation} {size} of the locked face, {frame} frame
/// counter, {time} timecode since the view opened, {rand:N} N random digits (change twice a
/// second).
// MARK: - Hud
public struct Hud: Codable, Equatable, Sendable {
    /// The locked face and highlights.
    public let accent: String?
    public let blocks: [Block]?
    /// Lines typed out one by one when the view opens, then kept on screen at the left.
    public let boot: Boot?
    /// How every detected face is marked.
    public let boxes: Boxes?
    /// Text and boxes.
    public let color: String
    /// Default mono.
    public let font: Font?
    /// How the locked face (the largest, or the one `look_at` follows) is marked.
    public let lock: Lock?
    public let name: String
    public let scanlines: Scanlines?
    /// Glow or shadow behind text and lines.
    public let shadow: String?
    /// Colour laid over the camera image (works over a native camera view too).
    public let tint: Tint?
    public let title: String
    public let version: String
    /// Darker corners.
    public let vignette: Double?

    public enum CodingKeys: String, CodingKey {
        case accent = "accent"
        case blocks = "blocks"
        case boot = "boot"
        case boxes = "boxes"
        case color = "color"
        case font = "font"
        case lock = "lock"
        case name = "name"
        case scanlines = "scanlines"
        case shadow = "shadow"
        case tint = "tint"
        case title = "title"
        case version = "version"
        case vignette = "vignette"
    }

    public init(accent: String?, blocks: [Block]?, boot: Boot?, boxes: Boxes?, color: String, font: Font?, lock: Lock?, name: String, scanlines: Scanlines?, shadow: String?, tint: Tint?, title: String, version: String, vignette: Double?) {
        self.accent = accent
        self.blocks = blocks
        self.boot = boot
        self.boxes = boxes
        self.color = color
        self.font = font
        self.lock = lock
        self.name = name
        self.scanlines = scanlines
        self.shadow = shadow
        self.tint = tint
        self.title = title
        self.version = version
        self.vignette = vignette
    }
}


// MARK: - Block
public struct Block: Codable, Equatable, Sendable {
    public let at: At
    public let blinkMS: Int?
    public let color: String?
    public let lines: [String]
    /// Text size; 1 is about 4.5% of the screen height.
    public let size: Double?

    public enum CodingKeys: String, CodingKey {
        case at = "at"
        case blinkMS = "blink_ms"
        case color = "color"
        case lines = "lines"
        case size = "size"
    }

    public init(at: At, blinkMS: Int?, color: String?, lines: [String], size: Double?) {
        self.at = at
        self.blinkMS = blinkMS
        self.color = color
        self.lines = lines
        self.size = size
    }
}

public enum At: String, Codable, Equatable, Sendable {
    case atLeft = "left"
    case bottomLeft = "bottom-left"
    case bottomRight = "bottom-right"
    case topLeft = "top-left"
    case topRight = "top-right"
}


/// Lines typed out one by one when the view opens, then kept on screen at the left.
// MARK: - Boot
public struct Boot: Codable, Equatable, Sendable {
    public let lines: [String]
    public let msPerLine: Int?

    public enum CodingKeys: String, CodingKey {
        case lines = "lines"
        case msPerLine = "ms_per_line"
    }

    public init(lines: [String], msPerLine: Int?) {
        self.lines = lines
        self.msPerLine = msPerLine
    }
}


/// How every detected face is marked.
// MARK: - Boxes
public struct Boxes: Codable, Equatable, Sendable {
    public let label: String?
    public let style: BoxesStyle
    /// Line width in points.
    public let width: Double?

    public enum CodingKeys: String, CodingKey {
        case label = "label"
        case style = "style"
        case width = "width"
    }

    public init(label: String?, style: BoxesStyle, width: Double?) {
        self.label = label
        self.style = style
        self.width = width
    }
}

public enum BoxesStyle: String, Codable, Equatable, Sendable {
    case bracket = "bracket"
    case corners = "corners"
    case none = "none"
    case rect = "rect"
}

/// Default mono.
public enum Font: String, Codable, Equatable, Sendable {
    case mono = "mono"
    case sans = "sans"
}


/// How the locked face (the largest, or the one `look_at` follows) is marked.
// MARK: - Lock
public struct Lock: Codable, Equatable, Sendable {
    public let blinkMS: Int?
    /// Shown big near the bottom while locked.
    public let label: String?
    public let style: LockStyle

    public enum CodingKeys: String, CodingKey {
        case blinkMS = "blink_ms"
        case label = "label"
        case style = "style"
    }

    public init(blinkMS: Int?, label: String?, style: LockStyle) {
        self.blinkMS = blinkMS
        self.label = label
        self.style = style
    }
}

public enum LockStyle: String, Codable, Equatable, Sendable {
    case corners = "corners"
    case crosshair = "crosshair"
    case none = "none"
    case rect = "rect"
}


// MARK: - Scanlines
public struct Scanlines: Codable, Equatable, Sendable {
    public let opacity: Double
    /// Pixels between lines.
    public let spacing: Double?

    public enum CodingKeys: String, CodingKey {
        case opacity = "opacity"
        case spacing = "spacing"
    }

    public init(opacity: Double, spacing: Double?) {
        self.opacity = opacity
        self.spacing = spacing
    }
}


/// Colour laid over the camera image (works over a native camera view too).
// MARK: - Tint
public struct Tint: Codable, Equatable, Sendable {
    public let color: String
    public let opacity: Double

    public enum CodingKeys: String, CodingKey {
        case color = "color"
        case opacity = "opacity"
    }

    public init(color: String, opacity: Double) {
        self.color = color
        self.opacity = opacity
    }
}


/// Inertial sample, up to 100 Hz. Right-handed frame: in `device` frame +x is right, +y is
/// up and +z points out of the screen (portrait). `mount` applies the `mount_offset`
/// setting. Every payload field is present unless the subscription named `fields`; then only
/// those are.
// MARK: - Imu
public struct Imu: Codable, Equatable, Sendable {
    /// Specific force in m/s^2, as a ROS IMU reports it: at rest upright about +9.81 on +y. (iOS
    /// CoreMotion reports the opposite sign.)
    public let accel: [Double]?
    public let frame: ImuFrame?
    /// Angular rate in rad/s.
    public let gyro: [Double]?
    /// Orientation as unit quaternion [x, y, z, w], relative to a gravity-aligned reference
    /// frame.
    public let q: [Double]?
    /// Sensor timestamp in seconds since device boot, for precise intervals between samples.
    public let sensorTimeS: Double?
    /// Per-connection, per-direction counter, starting at 0.
    public let seq: Int
    /// Sender clock in milliseconds since the Unix epoch.
    public let ts: Int
    public let type: ImuType

    public enum CodingKeys: String, CodingKey {
        case accel = "accel"
        case frame = "frame"
        case gyro = "gyro"
        case q = "q"
        case sensorTimeS = "sensor_time_s"
        case seq = "seq"
        case ts = "ts"
        case type = "type"
    }

    public init(accel: [Double]?, frame: ImuFrame?, gyro: [Double]?, q: [Double]?, sensorTimeS: Double?, seq: Int, ts: Int, type: ImuType) {
        self.accel = accel
        self.frame = frame
        self.gyro = gyro
        self.q = q
        self.sensorTimeS = sensorTimeS
        self.seq = seq
        self.ts = ts
        self.type = type
    }
}

public enum ImuFrame: String, Codable, Equatable, Sendable {
    case device = "device"
    case mount = "mount"
}

public enum ImuType: String, Codable, Equatable, Sendable {
    case imu = "imu"
}


// MARK: - ImuFields
public struct ImuFields: Codable, Equatable, Sendable {
    /// Specific force in m/s^2, as a ROS IMU reports it: at rest upright about +9.81 on +y. (iOS
    /// CoreMotion reports the opposite sign.)
    public let accel: [Double]?
    public let frame: ImuFrame?
    /// Angular rate in rad/s.
    public let gyro: [Double]?
    /// Orientation as unit quaternion [x, y, z, w], relative to a gravity-aligned reference
    /// frame.
    public let q: [Double]?
    /// Sensor timestamp in seconds since device boot, for precise intervals between samples.
    public let sensorTimeS: Double?

    public enum CodingKeys: String, CodingKey {
        case accel = "accel"
        case frame = "frame"
        case gyro = "gyro"
        case q = "q"
        case sensorTimeS = "sensor_time_s"
    }

    public init(accel: [Double]?, frame: ImuFrame?, gyro: [Double]?, q: [Double]?, sensorTimeS: Double?) {
        self.accel = accel
        self.frame = frame
        self.gyro = gyro
        self.q = q
        self.sensorTimeS = sensorTimeS
    }
}


/// Complete payload, as sent when the subscription names no `fields`.
// MARK: - ImuPayload
public struct ImuPayload: Codable, Equatable, Sendable {
    /// Specific force in m/s^2, as a ROS IMU reports it: at rest upright about +9.81 on +y. (iOS
    /// CoreMotion reports the opposite sign.)
    public let accel: [Double]
    public let frame: ImuFrame
    /// Angular rate in rad/s.
    public let gyro: [Double]
    /// Orientation as unit quaternion [x, y, z, w], relative to a gravity-aligned reference
    /// frame.
    public let q: [Double]
    /// Sensor timestamp in seconds since device boot, for precise intervals between samples.
    public let sensorTimeS: Double

    public enum CodingKeys: String, CodingKey {
        case accel = "accel"
        case frame = "frame"
        case gyro = "gyro"
        case q = "q"
        case sensorTimeS = "sensor_time_s"
    }

    public init(accel: [Double], frame: ImuFrame, gyro: [Double], q: [Double], sensorTimeS: Double) {
        self.accel = accel
        self.frame = frame
        self.gyro = gyro
        self.q = q
        self.sensorTimeS = sensorTimeS
    }
}


/// One structured log line, sent as it happens. Every received command is logged with its
/// `seq` in `seq_ref`. Every payload field is present unless the subscription named
/// `fields`; then only those are.
// MARK: - Log
public struct Log: Codable, Equatable, Sendable {
    public let level: CommonLogLevel?
    public let message: String?
    /// Per-connection, per-direction counter, starting at 0.
    public let seq: Int
    /// `seq` of the received message this line is about.
    public let seqRef: Int?
    /// e.g. `link`, `face`, `display`, `sensors`.
    public let subsystem: String?
    /// When the line was logged.
    public let timeMS: Int?
    /// Sender clock in milliseconds since the Unix epoch.
    public let ts: Int
    public let type: LogType

    public enum CodingKeys: String, CodingKey {
        case level = "level"
        case message = "message"
        case seq = "seq"
        case seqRef = "seq_ref"
        case subsystem = "subsystem"
        case timeMS = "time_ms"
        case ts = "ts"
        case type = "type"
    }

    public init(level: CommonLogLevel?, message: String?, seq: Int, seqRef: Int?, subsystem: String?, timeMS: Int?, ts: Int, type: LogType) {
        self.level = level
        self.message = message
        self.seq = seq
        self.seqRef = seqRef
        self.subsystem = subsystem
        self.timeMS = timeMS
        self.ts = ts
        self.type = type
    }
}

/// Minimum level. Default `debug`.
public enum CommonLogLevel: String, Codable, Equatable, Sendable {
    case debug = "debug"
    case error = "error"
    case fault = "fault"
    case info = "info"
    case notice = "notice"
    case warning = "warning"
}

public enum LogType: String, Codable, Equatable, Sendable {
    case log = "log"
}


// MARK: - LogFields
public struct LogFields: Codable, Equatable, Sendable {
    public let level: CommonLogLevel?
    public let message: String?
    /// `seq` of the received message this line is about.
    public let seqRef: Int?
    /// e.g. `link`, `face`, `display`, `sensors`.
    public let subsystem: String?
    /// When the line was logged.
    public let timeMS: Int?

    public enum CodingKeys: String, CodingKey {
        case level = "level"
        case message = "message"
        case seqRef = "seq_ref"
        case subsystem = "subsystem"
        case timeMS = "time_ms"
    }

    public init(level: CommonLogLevel?, message: String?, seqRef: Int?, subsystem: String?, timeMS: Int?) {
        self.level = level
        self.message = message
        self.seqRef = seqRef
        self.subsystem = subsystem
        self.timeMS = timeMS
    }
}


/// Complete payload, as sent when the subscription names no `fields`.
// MARK: - LogPayload
public struct LogPayload: Codable, Equatable, Sendable {
    public let level: CommonLogLevel
    public let message: String
    /// `seq` of the received message this line is about.
    public let seqRef: Int?
    /// e.g. `link`, `face`, `display`, `sensors`.
    public let subsystem: String
    /// When the line was logged.
    public let timeMS: Int

    public enum CodingKeys: String, CodingKey {
        case level = "level"
        case message = "message"
        case seqRef = "seq_ref"
        case subsystem = "subsystem"
        case timeMS = "time_ms"
    }

    public init(level: CommonLogLevel, message: String, seqRef: Int?, subsystem: String, timeMS: Int) {
        self.level = level
        self.message = message
        self.seqRef = seqRef
        self.subsystem = subsystem
        self.timeMS = timeMS
    }
}


/// Current camera ownership mode.
// MARK: - ModeGet
public struct ModeGet: Codable, Equatable, Sendable {
    /// Client-chosen id, echoed in the reply.
    public let id: String
    /// Per-connection, per-direction counter, starting at 0.
    public let seq: Int
    /// Sender clock in milliseconds since the Unix epoch.
    public let ts: Int
    public let type: ModeGetType

    public enum CodingKeys: String, CodingKey {
        case id = "id"
        case seq = "seq"
        case ts = "ts"
        case type = "type"
    }

    public init(id: String, seq: Int, ts: Int, type: ModeGetType) {
        self.id = id
        self.seq = seq
        self.ts = ts
        self.type = type
    }
}

public enum ModeGetType: String, Codable, Equatable, Sendable {
    case modeGet = "mode.get"
}


// MARK: - ModeGetResult
public struct ModeGetResult: Codable, Equatable, Sendable {
    public let mode: CommonMode

    public enum CodingKeys: String, CodingKey {
        case mode = "mode"
    }

    public init(mode: CommonMode) {
        self.mode = mode
    }
}

/// Camera ownership mode. Only `idle` is supported in 0.1.
public enum CommonMode: String, Codable, Equatable, Sendable {
    case capture = "capture"
    case idle = "idle"
    case sensing = "sensing"
}


/// Choose who owns the cameras. `idle`: no camera (default). `capture`: the front camera
/// runs for the camera view and face detection (`faces` with boxes, several faces); pose
/// only as orientation from `imu`. `sensing`: ARKit owns the cameras: world tracking gives
/// `pose` (position and orientation) and one face is tracked with the depth camera (`faces`
/// without boxes); no camera image. Asks for camera permission the first time; `unsupported`
/// where the device cannot.
// MARK: - ModeSet
public struct ModeSet: Codable, Equatable, Sendable {
    /// Client-chosen id, echoed in the reply.
    public let id: String
    public let mode: CommonMode
    /// Per-connection, per-direction counter, starting at 0.
    public let seq: Int
    /// Sender clock in milliseconds since the Unix epoch.
    public let ts: Int
    public let type: ModeSetType

    public enum CodingKeys: String, CodingKey {
        case id = "id"
        case mode = "mode"
        case seq = "seq"
        case ts = "ts"
        case type = "type"
    }

    public init(id: String, mode: CommonMode, seq: Int, ts: Int, type: ModeSetType) {
        self.id = id
        self.mode = mode
        self.seq = seq
        self.ts = ts
        self.type = type
    }
}

public enum ModeSetType: String, Codable, Equatable, Sendable {
    case modeSet = "mode.set"
}


/// Pairing attempt with the code shown on the device. Answered with `welcome`, or `error`
/// with `unauthorized` (wrong code) or `rate_limited` (locked for five minutes after five
/// failures).
// MARK: - Pair
public struct Pair: Codable, Equatable, Sendable {
    /// Devices show six digits; the simulator accepts `0000` in dev mode.
    public let code: String
    /// Per-connection, per-direction counter, starting at 0.
    public let seq: Int
    /// Sender clock in milliseconds since the Unix epoch.
    public let ts: Int
    public let type: PairType

    public enum CodingKeys: String, CodingKey {
        case code = "code"
        case seq = "seq"
        case ts = "ts"
        case type = "type"
    }

    public init(code: String, seq: Int, ts: Int, type: PairType) {
        self.code = code
        self.seq = seq
        self.ts = ts
        self.type = type
    }
}

public enum PairType: String, Codable, Equatable, Sendable {
    case pair = "pair"
}


/// Sent by the device when `hello` has no valid token. The device shows a pairing code on
/// screen.
// MARK: - PairRequired
public struct PairRequired: Codable, Equatable, Sendable {
    public let attemptsLeft: Int
    /// Where to find the code, e.g. "6-digit code shown on head-01".
    public let codeHint: String
    public let codeLength: Int
    public let expiresInMS: Int
    /// Per-connection, per-direction counter, starting at 0.
    public let seq: Int
    /// Sender clock in milliseconds since the Unix epoch.
    public let ts: Int
    public let type: PairRequiredType

    public enum CodingKeys: String, CodingKey {
        case attemptsLeft = "attempts_left"
        case codeHint = "code_hint"
        case codeLength = "code_length"
        case expiresInMS = "expires_in_ms"
        case seq = "seq"
        case ts = "ts"
        case type = "type"
    }

    public init(attemptsLeft: Int, codeHint: String, codeLength: Int, expiresInMS: Int, seq: Int, ts: Int, type: PairRequiredType) {
        self.attemptsLeft = attemptsLeft
        self.codeHint = codeHint
        self.codeLength = codeLength
        self.expiresInMS = expiresInMS
        self.seq = seq
        self.ts = ts
        self.type = type
    }
}

public enum PairRequiredType: String, Codable, Equatable, Sendable {
    case pairRequired = "pair_required"
}


/// Where the head is, up to 60 Hz while mode is `sensing` (ARKit world tracking). World
/// frame: origin where tracking started, +y up (against gravity), +x and +z horizontal;
/// position in metres. `q` turns the device frame of `imu` into the world frame ([x, y, z,
/// w]). Every payload field is present unless the subscription named `fields`.
// MARK: - Pose
public struct Pose: Codable, Equatable, Sendable {
    public let frame: PoseFrame?
    /// Metres in the world frame.
    public let position: [Double]?
    /// Unit quaternion [x, y, z, w], device frame to world frame.
    public let q: [Double]?
    public let sensorTimeS: Double?
    /// Per-connection, per-direction counter, starting at 0.
    public let seq: Int
    /// Why tracking is `limited`.
    public let trackingReason: TrackingReason?
    public let trackingState: TrackingState?
    /// Sender clock in milliseconds since the Unix epoch.
    public let ts: Int
    public let type: PoseType

    public enum CodingKeys: String, CodingKey {
        case frame = "frame"
        case position = "position"
        case q = "q"
        case sensorTimeS = "sensor_time_s"
        case seq = "seq"
        case trackingReason = "tracking_reason"
        case trackingState = "tracking_state"
        case ts = "ts"
        case type = "type"
    }

    public init(frame: PoseFrame?, position: [Double]?, q: [Double]?, sensorTimeS: Double?, seq: Int, trackingReason: TrackingReason?, trackingState: TrackingState?, ts: Int, type: PoseType) {
        self.frame = frame
        self.position = position
        self.q = q
        self.sensorTimeS = sensorTimeS
        self.seq = seq
        self.trackingReason = trackingReason
        self.trackingState = trackingState
        self.ts = ts
        self.type = type
    }
}

public enum PoseFrame: String, Codable, Equatable, Sendable {
    case world = "world"
}

/// Why tracking is `limited`.
public enum TrackingReason: String, Codable, Equatable, Sendable {
    case excessiveMotion = "excessive_motion"
    case initializing = "initializing"
    case insufficientFeatures = "insufficient_features"
    case relocalizing = "relocalizing"
}

public enum TrackingState: String, Codable, Equatable, Sendable {
    case limited = "limited"
    case normal = "normal"
    case notAvailable = "not_available"
}

public enum PoseType: String, Codable, Equatable, Sendable {
    case pose = "pose"
}


// MARK: - PoseFields
public struct PoseFields: Codable, Equatable, Sendable {
    public let frame: PoseFrame?
    /// Metres in the world frame.
    public let position: [Double]?
    /// Unit quaternion [x, y, z, w], device frame to world frame.
    public let q: [Double]?
    public let sensorTimeS: Double?
    /// Why tracking is `limited`.
    public let trackingReason: TrackingReason?
    public let trackingState: TrackingState?

    public enum CodingKeys: String, CodingKey {
        case frame = "frame"
        case position = "position"
        case q = "q"
        case sensorTimeS = "sensor_time_s"
        case trackingReason = "tracking_reason"
        case trackingState = "tracking_state"
    }

    public init(frame: PoseFrame?, position: [Double]?, q: [Double]?, sensorTimeS: Double?, trackingReason: TrackingReason?, trackingState: TrackingState?) {
        self.frame = frame
        self.position = position
        self.q = q
        self.sensorTimeS = sensorTimeS
        self.trackingReason = trackingReason
        self.trackingState = trackingState
    }
}


/// Complete payload, as sent when the subscription names no `fields`.
// MARK: - PosePayload
public struct PosePayload: Codable, Equatable, Sendable {
    public let frame: PoseFrame
    /// Metres in the world frame.
    public let position: [Double]
    /// Unit quaternion [x, y, z, w], device frame to world frame.
    public let q: [Double]
    public let sensorTimeS: Double
    /// Why tracking is `limited`.
    public let trackingReason: TrackingReason?
    public let trackingState: TrackingState

    public enum CodingKeys: String, CodingKey {
        case frame = "frame"
        case position = "position"
        case q = "q"
        case sensorTimeS = "sensor_time_s"
        case trackingReason = "tracking_reason"
        case trackingState = "tracking_state"
    }

    public init(frame: PoseFrame, position: [Double], q: [Double], sensorTimeS: Double, trackingReason: TrackingReason?, trackingState: TrackingState) {
        self.frame = frame
        self.position = position
        self.q = q
        self.sensorTimeS = sensorTimeS
        self.trackingReason = trackingReason
        self.trackingState = trackingState
    }
}


/// Failed command (with `id`) or failed handshake (without).
// MARK: - ProtocolError
public struct ProtocolError: Codable, Equatable, Sendable {
    public let code: Code
    public let details: [String: JSONValue]?
    public let id: String?
    public let message: String
    /// Per-connection, per-direction counter, starting at 0.
    public let seq: Int
    /// Sender clock in milliseconds since the Unix epoch.
    public let ts: Int
    public let type: ProtocolErrorType

    public enum CodingKeys: String, CodingKey {
        case code = "code"
        case details = "details"
        case id = "id"
        case message = "message"
        case seq = "seq"
        case ts = "ts"
        case type = "type"
    }

    public init(code: Code, details: [String: JSONValue]?, id: String?, message: String, seq: Int, ts: Int, type: ProtocolErrorType) {
        self.code = code
        self.details = details
        self.id = id
        self.message = message
        self.seq = seq
        self.ts = ts
        self.type = type
    }
}

public enum Code: String, Codable, Equatable, Sendable {
    case busy = "busy"
    case devModeRequired = "dev_mode_required"
    case invalidParams = "invalid_params"
    case rateLimited = "rate_limited"
    case unauthorized = "unauthorized"
    case unsupported = "unsupported"
}

public enum ProtocolErrorType: String, Codable, Equatable, Sendable {
    case error = "error"
}


/// Device status, up to 1 Hz. Also the result of `system.status`. Every payload field is
/// present unless the subscription named `fields`; then only those are.
// MARK: - Status
public struct Status: Codable, Equatable, Sendable {
    /// Omitted when unknown (e.g. simulator).
    public let batteryLevel: Double?
    public let charging: Bool?
    /// Connected, authenticated clients.
    public let clients: Int?
    public let devMode: Bool?
    public let emotion: String?
    /// Faces seen now (modes `capture` and `sensing`). Omitted in `idle`.
    public let faces: Int?
    public let mode: CommonMode?
    public let overlay: Overlay?
    /// Round-trip time to the receiving client, from WebSocket ping. Omitted until measured.
    public let rttMS: Double?
    /// Per-connection, per-direction counter, starting at 0.
    public let seq: Int
    /// Subtitle text on screen. Omitted when none.
    public let subtitle: String?
    public let theme: String?
    public let thermalState: CommonThermalState?
    /// Sender clock in milliseconds since the Unix epoch.
    public let ts: Int
    public let type: StatusType
    public let uptimeS: Double?
    public let view: CommonView?

    public enum CodingKeys: String, CodingKey {
        case batteryLevel = "battery_level"
        case charging = "charging"
        case clients = "clients"
        case devMode = "dev_mode"
        case emotion = "emotion"
        case faces = "faces"
        case mode = "mode"
        case overlay = "overlay"
        case rttMS = "rtt_ms"
        case seq = "seq"
        case subtitle = "subtitle"
        case theme = "theme"
        case thermalState = "thermal_state"
        case ts = "ts"
        case type = "type"
        case uptimeS = "uptime_s"
        case view = "view"
    }

    public init(batteryLevel: Double?, charging: Bool?, clients: Int?, devMode: Bool?, emotion: String?, faces: Int?, mode: CommonMode?, overlay: Overlay?, rttMS: Double?, seq: Int, subtitle: String?, theme: String?, thermalState: CommonThermalState?, ts: Int, type: StatusType, uptimeS: Double?, view: CommonView?) {
        self.batteryLevel = batteryLevel
        self.charging = charging
        self.clients = clients
        self.devMode = devMode
        self.emotion = emotion
        self.faces = faces
        self.mode = mode
        self.overlay = overlay
        self.rttMS = rttMS
        self.seq = seq
        self.subtitle = subtitle
        self.theme = theme
        self.thermalState = thermalState
        self.ts = ts
        self.type = type
        self.uptimeS = uptimeS
        self.view = view
    }
}

public enum CommonThermalState: String, Codable, Equatable, Sendable {
    case critical = "critical"
    case fair = "fair"
    case nominal = "nominal"
    case serious = "serious"
}

public enum StatusType: String, Codable, Equatable, Sendable {
    case status = "status"
}


// MARK: - StatusFields
public struct StatusFields: Codable, Equatable, Sendable {
    /// Omitted when unknown (e.g. simulator).
    public let batteryLevel: Double?
    public let charging: Bool?
    /// Connected, authenticated clients.
    public let clients: Int?
    public let devMode: Bool?
    public let emotion: String?
    /// Faces seen now (modes `capture` and `sensing`). Omitted in `idle`.
    public let faces: Int?
    public let mode: CommonMode?
    public let overlay: Overlay?
    /// Round-trip time to the receiving client, from WebSocket ping. Omitted until measured.
    public let rttMS: Double?
    /// Subtitle text on screen. Omitted when none.
    public let subtitle: String?
    public let theme: String?
    public let thermalState: CommonThermalState?
    public let uptimeS: Double?
    public let view: CommonView?

    public enum CodingKeys: String, CodingKey {
        case batteryLevel = "battery_level"
        case charging = "charging"
        case clients = "clients"
        case devMode = "dev_mode"
        case emotion = "emotion"
        case faces = "faces"
        case mode = "mode"
        case overlay = "overlay"
        case rttMS = "rtt_ms"
        case subtitle = "subtitle"
        case theme = "theme"
        case thermalState = "thermal_state"
        case uptimeS = "uptime_s"
        case view = "view"
    }

    public init(batteryLevel: Double?, charging: Bool?, clients: Int?, devMode: Bool?, emotion: String?, faces: Int?, mode: CommonMode?, overlay: Overlay?, rttMS: Double?, subtitle: String?, theme: String?, thermalState: CommonThermalState?, uptimeS: Double?, view: CommonView?) {
        self.batteryLevel = batteryLevel
        self.charging = charging
        self.clients = clients
        self.devMode = devMode
        self.emotion = emotion
        self.faces = faces
        self.mode = mode
        self.overlay = overlay
        self.rttMS = rttMS
        self.subtitle = subtitle
        self.theme = theme
        self.thermalState = thermalState
        self.uptimeS = uptimeS
        self.view = view
    }
}


/// Complete payload, as sent when the subscription names no `fields`.
// MARK: - StatusPayload
public struct StatusPayload: Codable, Equatable, Sendable {
    /// Omitted when unknown (e.g. simulator).
    public let batteryLevel: Double?
    public let charging: Bool
    /// Connected, authenticated clients.
    public let clients: Int
    public let devMode: Bool
    public let emotion: String
    /// Faces seen now (modes `capture` and `sensing`). Omitted in `idle`.
    public let faces: Int?
    public let mode: CommonMode
    public let overlay: Overlay
    /// Round-trip time to the receiving client, from WebSocket ping. Omitted until measured.
    public let rttMS: Double?
    /// Subtitle text on screen. Omitted when none.
    public let subtitle: String?
    public let theme: String
    public let thermalState: CommonThermalState
    public let uptimeS: Double
    public let view: CommonView

    public enum CodingKeys: String, CodingKey {
        case batteryLevel = "battery_level"
        case charging = "charging"
        case clients = "clients"
        case devMode = "dev_mode"
        case emotion = "emotion"
        case faces = "faces"
        case mode = "mode"
        case overlay = "overlay"
        case rttMS = "rtt_ms"
        case subtitle = "subtitle"
        case theme = "theme"
        case thermalState = "thermal_state"
        case uptimeS = "uptime_s"
        case view = "view"
    }

    public init(batteryLevel: Double?, charging: Bool, clients: Int, devMode: Bool, emotion: String, faces: Int?, mode: CommonMode, overlay: Overlay, rttMS: Double?, subtitle: String?, theme: String, thermalState: CommonThermalState, uptimeS: Double, view: CommonView) {
        self.batteryLevel = batteryLevel
        self.charging = charging
        self.clients = clients
        self.devMode = devMode
        self.emotion = emotion
        self.faces = faces
        self.mode = mode
        self.overlay = overlay
        self.rttMS = rttMS
        self.subtitle = subtitle
        self.theme = theme
        self.thermalState = thermalState
        self.uptimeS = uptimeS
        self.view = view
    }
}


/// Open a stream. The device clamps `rate_hz` to what it supports and returns the actual
/// rate. Subscribing again to the same topic replaces the earlier subscription.
// MARK: - Subscribe
public struct Subscribe: Codable, Equatable, Sendable {
    /// Only send these payload fields. Omit for all.
    public let fields: [String]?
    /// Client-chosen id, echoed in the reply.
    public let id: String
    /// Requested rate. Ignored for event-driven topics such as `log`.
    public let rateHz: Double?
    /// Per-connection, per-direction counter, starting at 0.
    public let seq: Int
    public let topic: CommonTopic
    /// Sender clock in milliseconds since the Unix epoch.
    public let ts: Int
    public let type: SubscribeType

    public enum CodingKeys: String, CodingKey {
        case fields = "fields"
        case id = "id"
        case rateHz = "rate_hz"
        case seq = "seq"
        case topic = "topic"
        case ts = "ts"
        case type = "type"
    }

    public init(fields: [String]?, id: String, rateHz: Double?, seq: Int, topic: CommonTopic, ts: Int, type: SubscribeType) {
        self.fields = fields
        self.id = id
        self.rateHz = rateHz
        self.seq = seq
        self.topic = topic
        self.ts = ts
        self.type = type
    }
}

/// Subscribable stream. `faces` needs mode `capture` or `sensing`, `pose` needs `sensing`;
/// `gps` and `env` arrive later.
public enum CommonTopic: String, Codable, Equatable, Sendable {
    case faces = "faces"
    case imu = "imu"
    case log = "log"
    case pose = "pose"
    case status = "status"
}

public enum SubscribeType: String, Codable, Equatable, Sendable {
    case subscribe = "subscribe"
}


// MARK: - SubscribeResult
public struct SubscribeResult: Codable, Equatable, Sendable {
    /// Actual rate; 0 for event-driven topics.
    public let rateHz: Double
    public let topic: CommonTopic

    public enum CodingKeys: String, CodingKey {
        case rateHz = "rate_hz"
        case topic = "topic"
    }

    public init(rateHz: Double, topic: CommonTopic) {
        self.rateHz = rateHz
        self.topic = topic
    }
}


/// Health snapshot for debugging. Dev mode only.
// MARK: - SystemDiagnostics
public struct SystemDiagnostics: Codable, Equatable, Sendable {
    /// Client-chosen id, echoed in the reply.
    public let id: String
    /// Per-connection, per-direction counter, starting at 0.
    public let seq: Int
    /// Sender clock in milliseconds since the Unix epoch.
    public let ts: Int
    public let type: SystemDiagnosticsType

    public enum CodingKeys: String, CodingKey {
        case id = "id"
        case seq = "seq"
        case ts = "ts"
        case type = "type"
    }

    public init(id: String, seq: Int, ts: Int, type: SystemDiagnosticsType) {
        self.id = id
        self.seq = seq
        self.ts = ts
        self.type = type
    }
}

public enum SystemDiagnosticsType: String, Codable, Equatable, Sendable {
    case systemDiagnostics = "system.diagnostics"
}


// MARK: - SystemDiagnosticsResult
public struct SystemDiagnosticsResult: Codable, Equatable, Sendable {
    public let arkit: DiagnosticsArkit
    /// Face render rate over the last second.
    public let frameRate: Double
    public let lastCrash: DiagnosticsLastCrash?
    /// Memory used by the app.
    public let memoryMB: Double
    public let permissions: DiagnosticsPermissions
    public let thermalState: CommonThermalState
    public let uptimeS: Double

    public enum CodingKeys: String, CodingKey {
        case arkit = "arkit"
        case frameRate = "frame_rate"
        case lastCrash = "last_crash"
        case memoryMB = "memory_mb"
        case permissions = "permissions"
        case thermalState = "thermal_state"
        case uptimeS = "uptime_s"
    }

    public init(arkit: DiagnosticsArkit, frameRate: Double, lastCrash: DiagnosticsLastCrash?, memoryMB: Double, permissions: DiagnosticsPermissions, thermalState: CommonThermalState, uptimeS: Double) {
        self.arkit = arkit
        self.frameRate = frameRate
        self.lastCrash = lastCrash
        self.memoryMB = memoryMB
        self.permissions = permissions
        self.thermalState = thermalState
        self.uptimeS = uptimeS
    }
}


// MARK: - DiagnosticsArkit
public struct DiagnosticsArkit: Codable, Equatable, Sendable {
    /// Front-camera face tracking concurrent with world tracking.
    public let faceTracking: Bool
    public let worldTracking: Bool

    public enum CodingKeys: String, CodingKey {
        case faceTracking = "face_tracking"
        case worldTracking = "world_tracking"
    }

    public init(faceTracking: Bool, worldTracking: Bool) {
        self.faceTracking = faceTracking
        self.worldTracking = worldTracking
    }
}


// MARK: - DiagnosticsLastCrash
public struct DiagnosticsLastCrash: Codable, Equatable, Sendable {
    public let reason: String
    public let timeMS: Int

    public enum CodingKeys: String, CodingKey {
        case reason = "reason"
        case timeMS = "time_ms"
    }

    public init(reason: String, timeMS: Int) {
        self.reason = reason
        self.timeMS = timeMS
    }
}


// MARK: - DiagnosticsPermissions
public struct DiagnosticsPermissions: Codable, Equatable, Sendable {
    public let camera: SystemDiagnosticsPermission
    public let localNetwork: SystemDiagnosticsPermission
    public let motion: SystemDiagnosticsPermission

    public enum CodingKeys: String, CodingKey {
        case camera = "camera"
        case localNetwork = "local_network"
        case motion = "motion"
    }

    public init(camera: SystemDiagnosticsPermission, localNetwork: SystemDiagnosticsPermission, motion: SystemDiagnosticsPermission) {
        self.camera = camera
        self.localNetwork = localNetwork
        self.motion = motion
    }
}

public enum SystemDiagnosticsPermission: String, Codable, Equatable, Sendable {
    case denied = "denied"
    case granted = "granted"
    case notDetermined = "not_determined"
    case notRequired = "not_required"
}


/// Most recent lines from the device's log ring buffer (2000 lines), oldest first. Dev mode
/// only.
// MARK: - SystemLogs
public struct SystemLogs: Codable, Equatable, Sendable {
    /// Client-chosen id, echoed in the reply.
    public let id: String
    /// Minimum level. Default `debug`.
    public let level: CommonLogLevel?
    /// Default 100.
    public let n: Int?
    /// Per-connection, per-direction counter, starting at 0.
    public let seq: Int
    /// Sender clock in milliseconds since the Unix epoch.
    public let ts: Int
    public let type: SystemLogsType

    public enum CodingKeys: String, CodingKey {
        case id = "id"
        case level = "level"
        case n = "n"
        case seq = "seq"
        case ts = "ts"
        case type = "type"
    }

    public init(id: String, level: CommonLogLevel?, n: Int?, seq: Int, ts: Int, type: SystemLogsType) {
        self.id = id
        self.level = level
        self.n = n
        self.seq = seq
        self.ts = ts
        self.type = type
    }
}

public enum SystemLogsType: String, Codable, Equatable, Sendable {
    case systemLogs = "system.logs"
}


// MARK: - SystemLogsResult
public struct SystemLogsResult: Codable, Equatable, Sendable {
    public let entries: [LogPayload]

    public enum CodingKeys: String, CodingKey {
        case entries = "entries"
    }

    public init(entries: [LogPayload]) {
        self.entries = entries
    }
}


/// PNG of what is on screen. Dev mode only. With `delivery: url` the image is served by the
/// device's HTTP server (WebSocket port + 1) for 60 s and must be fetched with the token in
/// an `Authorization: Bearer` header.
// MARK: - SystemScreenshot
public struct SystemScreenshot: Codable, Equatable, Sendable {
    /// Default `url`.
    public let delivery: Delivery?
    /// Client-chosen id, echoed in the reply.
    public let id: String
    /// Fraction of native resolution. Default 1.
    public let scale: Double?
    /// Per-connection, per-direction counter, starting at 0.
    public let seq: Int
    /// Sender clock in milliseconds since the Unix epoch.
    public let ts: Int
    public let type: SystemScreenshotType

    public enum CodingKeys: String, CodingKey {
        case delivery = "delivery"
        case id = "id"
        case scale = "scale"
        case seq = "seq"
        case ts = "ts"
        case type = "type"
    }

    public init(delivery: Delivery?, id: String, scale: Double?, seq: Int, ts: Int, type: SystemScreenshotType) {
        self.delivery = delivery
        self.id = id
        self.scale = scale
        self.seq = seq
        self.ts = ts
        self.type = type
    }
}

/// Default `url`.
public enum Delivery: String, Codable, Equatable, Sendable {
    case inline = "inline"
    case url = "url"
}

public enum SystemScreenshotType: String, Codable, Equatable, Sendable {
    case systemScreenshot = "system.screenshot"
}


// MARK: - SystemScreenshotResult
public struct SystemScreenshotResult: Codable, Equatable, Sendable {
    public let expiresMS: Int?
    /// Pixels.
    public let height: Int
    public let pngBase64: String?
    public let url: String?
    /// Pixels.
    public let width: Int

    public enum CodingKeys: String, CodingKey {
        case expiresMS = "expires_ms"
        case height = "height"
        case pngBase64 = "png_base64"
        case url = "url"
        case width = "width"
    }

    public init(expiresMS: Int?, height: Int, pngBase64: String?, url: String?, width: Int) {
        self.expiresMS = expiresMS
        self.height = height
        self.pngBase64 = pngBase64
        self.url = url
        self.width = width
    }
}


/// Read all settings, or set one. `set` needs dev mode. Known keys in 0.1: `name`, `port`,
/// `mount_offset` ([x, y, z, w] quaternion), `offline_theme`.
// MARK: - SystemSettings
public struct SystemSettings: Codable, Equatable, Sendable {
    public let action: Action
    /// Client-chosen id, echoed in the reply.
    public let id: String
    public let key: String?
    /// Per-connection, per-direction counter, starting at 0.
    public let seq: Int
    /// Sender clock in milliseconds since the Unix epoch.
    public let ts: Int
    public let type: SystemSettingsType
    /// Any JSON value valid for the key.
    public let value: JSONValue?

    public enum CodingKeys: String, CodingKey {
        case action = "action"
        case id = "id"
        case key = "key"
        case seq = "seq"
        case ts = "ts"
        case type = "type"
        case value = "value"
    }

    public init(action: Action, id: String, key: String?, seq: Int, ts: Int, type: SystemSettingsType, value: JSONValue?) {
        self.action = action
        self.id = id
        self.key = key
        self.seq = seq
        self.ts = ts
        self.type = type
        self.value = value
    }
}

public enum Action: String, Codable, Equatable, Sendable {
    case actionGet = "get"
    case actionSet = "set"
}

public enum SystemSettingsType: String, Codable, Equatable, Sendable {
    case systemSettings = "system.settings"
}


// MARK: - SystemSettingsResult
public struct SystemSettingsResult: Codable, Equatable, Sendable {
    /// All settings after the command.
    public let settings: [String: JSONValue]

    public enum CodingKeys: String, CodingKey {
        case settings = "settings"
    }

    public init(settings: [String: JSONValue]) {
        self.settings = settings
    }
}


/// Current status, same content as the `status` topic.
// MARK: - SystemStatus
public struct SystemStatus: Codable, Equatable, Sendable {
    /// Client-chosen id, echoed in the reply.
    public let id: String
    /// Per-connection, per-direction counter, starting at 0.
    public let seq: Int
    /// Sender clock in milliseconds since the Unix epoch.
    public let ts: Int
    public let type: SystemStatusType

    public enum CodingKeys: String, CodingKey {
        case id = "id"
        case seq = "seq"
        case ts = "ts"
        case type = "type"
    }

    public init(id: String, seq: Int, ts: Int, type: SystemStatusType) {
        self.id = id
        self.seq = seq
        self.ts = ts
        self.type = type
    }
}

public enum SystemStatusType: String, Codable, Equatable, Sendable {
    case systemStatus = "system.status"
}


/// Close a stream. Acknowledged even if the topic was not subscribed.
// MARK: - Unsubscribe
public struct Unsubscribe: Codable, Equatable, Sendable {
    /// Client-chosen id, echoed in the reply.
    public let id: String
    /// Per-connection, per-direction counter, starting at 0.
    public let seq: Int
    public let topic: CommonTopic
    /// Sender clock in milliseconds since the Unix epoch.
    public let ts: Int
    public let type: UnsubscribeType

    public enum CodingKeys: String, CodingKey {
        case id = "id"
        case seq = "seq"
        case topic = "topic"
        case ts = "ts"
        case type = "type"
    }

    public init(id: String, seq: Int, topic: CommonTopic, ts: Int, type: UnsubscribeType) {
        self.id = id
        self.seq = seq
        self.topic = topic
        self.ts = ts
        self.type = type
    }
}

public enum UnsubscribeType: String, Codable, Equatable, Sendable {
    case unsubscribe = "unsubscribe"
}


/// Session accepted. Carries the client's token (new after pairing, unchanged on reconnect),
/// the device description and what it supports.
// MARK: - Welcome
public struct Welcome: Codable, Equatable, Sendable {
    /// Feature flags. Known: 0.1 `face`, `display.image`, `display.video`, `display.web`,
    /// `display.subtitle`, `imu`, `status`, `log`, `screenshot`; 0.2 `camera`, `faces`, `pose`
    /// (where the device supports them). Clients ignore unknown values.
    public let capabilities: [String]
    public let devMode: Bool
    public let device: WelcomeDevice
    public let protocolVersion: String
    /// Per-connection, per-direction counter, starting at 0.
    public let seq: Int
    public let themes: [String]
    public let token: String
    /// Sender clock in milliseconds since the Unix epoch.
    public let ts: Int
    public let type: WelcomeType

    public enum CodingKeys: String, CodingKey {
        case capabilities = "capabilities"
        case devMode = "dev_mode"
        case device = "device"
        case protocolVersion = "protocol_version"
        case seq = "seq"
        case themes = "themes"
        case token = "token"
        case ts = "ts"
        case type = "type"
    }

    public init(capabilities: [String], devMode: Bool, device: WelcomeDevice, protocolVersion: String, seq: Int, themes: [String], token: String, ts: Int, type: WelcomeType) {
        self.capabilities = capabilities
        self.devMode = devMode
        self.device = device
        self.protocolVersion = protocolVersion
        self.seq = seq
        self.themes = themes
        self.token = token
        self.ts = ts
        self.type = type
    }
}


// MARK: - WelcomeDevice
public struct WelcomeDevice: Codable, Equatable, Sendable {
    public let appVersion: String
    /// Hardware identifier, e.g. `iPhone13,2`.
    public let model: String
    public let name: String
    public let osVersion: String
    public let platform: Platform
    public let screen: WelcomeScreen

    public enum CodingKeys: String, CodingKey {
        case appVersion = "app_version"
        case model = "model"
        case name = "name"
        case osVersion = "os_version"
        case platform = "platform"
        case screen = "screen"
    }

    public init(appVersion: String, model: String, name: String, osVersion: String, platform: Platform, screen: WelcomeScreen) {
        self.appVersion = appVersion
        self.model = model
        self.name = name
        self.osVersion = osVersion
        self.platform = platform
        self.screen = screen
    }
}

public enum Platform: String, Codable, Equatable, Sendable {
    case android = "android"
    case ios = "ios"
    case ipados = "ipados"
    case sim = "sim"
}


// MARK: - WelcomeScreen
public struct WelcomeScreen: Codable, Equatable, Sendable {
    /// Points.
    public let height: Double
    public let safeArea: WelcomeInsets
    public let scale: Double
    /// Points.
    public let width: Double

    public enum CodingKeys: String, CodingKey {
        case height = "height"
        case safeArea = "safe_area"
        case scale = "scale"
        case width = "width"
    }

    public init(height: Double, safeArea: WelcomeInsets, scale: Double, width: Double) {
        self.height = height
        self.safeArea = safeArea
        self.scale = scale
        self.width = width
    }
}


/// Safe-area insets in points.
// MARK: - WelcomeInsets
public struct WelcomeInsets: Codable, Equatable, Sendable {
    public let bottom: Double
    public let welcomeInsetsLeft: Double
    public let welcomeInsetsRight: Double
    public let top: Double

    public enum CodingKeys: String, CodingKey {
        case bottom = "bottom"
        case welcomeInsetsLeft = "left"
        case welcomeInsetsRight = "right"
        case top = "top"
    }

    public init(bottom: Double, welcomeInsetsLeft: Double, welcomeInsetsRight: Double, top: Double) {
        self.bottom = bottom
        self.welcomeInsetsLeft = welcomeInsetsLeft
        self.welcomeInsetsRight = welcomeInsetsRight
        self.top = top
    }
}

public enum WelcomeType: String, Codable, Equatable, Sendable {
    case welcome = "welcome"
}

// MARK: - JSONValue

/// Any JSON value, for schema fields without a fixed type (e.g. `ack.result`, settings).
public enum JSONValue: Codable, Hashable, Sendable {
    case null
    case bool(Bool)
    case number(Double)
    case string(String)
    case array([JSONValue])
    case object([String: JSONValue])

    public init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        if container.decodeNil() {
            self = .null
        } else if let value = try? container.decode(Bool.self) {
            self = .bool(value)
        } else if let value = try? container.decode(Double.self) {
            self = .number(value)
        } else if let value = try? container.decode(String.self) {
            self = .string(value)
        } else if let value = try? container.decode([JSONValue].self) {
            self = .array(value)
        } else {
            self = .object(try container.decode([String: JSONValue].self))
        }
    }

    public func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        switch self {
        case .null: try container.encodeNil()
        case .bool(let value): try container.encode(value)
        case .number(let value): try container.encode(value)
        case .string(let value): try container.encode(value)
        case .array(let value): try container.encode(value)
        case .object(let value): try container.encode(value)
        }
    }
}
