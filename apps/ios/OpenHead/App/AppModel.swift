import ARKit
import SwiftUI

/// Everything the head is: face, display state, sensors, settings and the link.
@MainActor
final class AppModel: ObservableObject {
    let logs = LogStore()
    let settings = SettingsStore()
    let pairing = Pairing()
    let face = FaceController()
    let motion = MotionService()
    let camera = CameraService()
    let ar = ARService()
    let heading = HeadingService()
    private(set) lazy var link = LinkServer(model: self)

    @Published var display: DisplayContent = .face
    @Published var overlay = "none"
    @Published var showSettings = false
    /// Who owns the cameras: idle, capture (front camera, faces) or sensing (ARKit). See AppModel+Sensing.
    @Published var mode = "idle"
    var faces: [SeenFace] = []
    var facesSource = "vision"
    var lastFacesToPage = 0.0
    var tilt: (pitch: Double, roll: Double)?
    var hudTimer: Timer?
    let hudMotionId = UUID()
    @Published private(set) var clients = 0
    @Published private(set) var linkReady = false
    @Published private(set) var thermalState = ProcessInfo.ThermalState.nominal
    @Published private(set) var themeNames: [String] = []
    private(set) var themes: [[String: Any]] = []
    let started = Date()
    private var started_ = false
    private var fps = FrameCounter()
    private var timers: [String: Timer] = [:]

    var appVersion: String {
        let info = Bundle.main.infoDictionary
        return "\(info?["CFBundleShortVersionString"] as? String ?? "?") (\(info?["CFBundleVersion"] as? String ?? "?"))"
    }

    func start() {
        guard !started_ else { return }
        started_ = true
        UIApplication.shared.isIdleTimerDisabled = true
        UIDevice.current.isBatteryMonitoringEnabled = true
        logs.log("info", "app", "OpenHead \(appVersion) starting on \(DeviceInfo.model)")
        face.onLog = { [weak self] level, message in self?.logs.log(level, "face", message) }
        face.onReady = { [weak self] in self?.faceReady() }
        face.onView = { [weak self] view in self?.pageChangedView(view) }
        camera.onFaces = { [weak self] faces in self?.facesChanged(faces, source: "vision") }
        ar.onFaces = { [weak self] faces in self?.facesChanged(faces, source: "arkit") }
        face.load(theme: settings.offlineTheme)
        fps.start()
        NotificationCenter.default.addObserver(forName: ProcessInfo.thermalStateDidChangeNotification,
                                               object: nil, queue: .main) { [weak self] _ in
            MainActor.assumeIsolated { self?.thermalChanged() }
        }
        thermalChanged()
    }

    private func faceReady() {
        logs.log("info", "face", "engine ready")
        Task {
            themes = (try? await face.listThemes()) ?? []
            themeNames = themes.compactMap { $0["name"] as? String }
            if !linkReady { link.start() }
        }
    }

    func linkStateChanged(ready: Bool, clients: Int) {
        linkReady = ready
        self.clients = clients
    }

    private func thermalChanged() {
        thermalState = ProcessInfo.processInfo.thermalState
        if thermalState == .serious || thermalState == .critical {
            logs.log("warning", "app", "thermal state \(thermalName)")
        }
    }

    var thermalName: String {
        switch thermalState {
        case .nominal: return "nominal"
        case .fair: return "fair"
        case .serious: return "serious"
        case .critical: return "critical"
        @unknown default: return "nominal"
        }
    }

    // MARK: - display

    /// Show `content` (loaded by the web layer first, so a bad source changes nothing).
    func show(_ content: DisplayContent, source: String = "", overlay: String, loop: Bool = false,
              muted: Bool = false, hud: String = "hunter", durationMs: Int?) async throws {
        if content == .face {
            try await face.clearDisplay()
        } else {
            try await face.show(content.name, source: source, overlay: overlay, loop: loop, muted: muted, hud: hud)
        }
        if content == .camera, display != .camera { startHudFeed() }
        if content != .camera, display == .camera { stopHudFeed() }
        display = content
        self.overlay = content == .face ? "none" : overlay
        logs.log("info", "display", "view=\(content.name) overlay=\(self.overlay)")
        schedule("display", durationMs) { [weak self] in self?.showFace() }
    }

    func showFace() {
        Task { try? await show(.face, overlay: "none", durationMs: nil) }
    }

    /// The page went back to the face by itself (a video ended).
    private func pageChangedView(_ view: String) {
        guard view == "face", display != .face else { return }
        schedule("display", nil) {}
        if display == .camera { stopHudFeed() }
        display = .face
        overlay = "none"
    }

    /// Run `action` after `ms` (replacing an earlier one with the same key); nil cancels.
    func schedule(_ key: String, _ ms: Int?, _ action: @escaping @MainActor () -> Void) {
        timers[key]?.invalidate()
        timers[key] = nil
        guard let ms else { return }
        timers[key] = Timer.scheduledTimer(withTimeInterval: Double(ms) / 1000, repeats: false) { _ in
            MainActor.assumeIsolated { action() }
        }
    }

    // MARK: - status and diagnostics

    func status(rttMs: Double?) async -> JSONObject {
        let state = (try? await face.state()) ?? FaceController.State(theme: settings.offlineTheme)
        let device = UIDevice.current
        var status: JSONObject = [
            "charging": device.batteryState == .charging || device.batteryState == .full,
            "thermal_state": thermalName,
            "view": display.name,
            "overlay": overlay,
            "theme": state.theme,
            "emotion": state.emotion,
            "mode": mode,
            "dev_mode": settings.devMode,
            "clients": clients,
            "uptime_s": (Date().timeIntervalSince(started) * 10).rounded() / 10,
        ]
        if !state.subtitle.isEmpty { status["subtitle"] = String(state.subtitle.suffix(4000)) }
        if mode != "idle" { status["faces"] = faces.count }
        if device.batteryLevel >= 0 { status["battery_level"] = Double(device.batteryLevel) }
        if let rttMs { status["rtt_ms"] = rttMs }
        return status
    }

    func diagnostics() -> JSONObject {
        [
            "uptime_s": (Date().timeIntervalSince(started) * 10).rounded() / 10,
            "thermal_state": thermalName,
            "memory_mb": DeviceInfo.memoryFootprintMB,
            "frame_rate": fps.rate,
            "permissions": [
                "local_network": linkReady ? "granted" : "not_determined",
                "motion": "not_required",
                "camera": CameraService.permission,
            ],
            "arkit": [
                "world_tracking": ARWorldTrackingConfiguration.isSupported,
                "face_tracking": ARWorldTrackingConfiguration.supportsUserFaceTracking,
            ],
        ]
    }
}

/// Frames per second of the app's display loop, for diagnostics.
@MainActor
final class FrameCounter: NSObject {
    private var link: CADisplayLink?
    private var frames = 0
    private var windowStart = CACurrentMediaTime()
    private(set) var rate: Double = 0

    func start() {
        link = CADisplayLink(target: self, selector: #selector(tick))
        link?.add(to: .main, forMode: .common)
    }

    @objc private func tick() {
        frames += 1
        let now = CACurrentMediaTime()
        if now - windowStart >= 1 {
            rate = (Double(frames) / (now - windowStart) * 10).rounded() / 10
            frames = 0
            windowStart = now
        }
    }
}
