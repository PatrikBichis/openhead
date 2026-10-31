import SwiftUI
import UIKit

/// Modes (`capture`, `sensing`), faces and the HUD's device readings (protocol 0.2).
extension AppModel {
    var supportsSensing: Bool { ARService.supported }

    /// Switch who owns the cameras. Throws (mode unchanged) when the camera is denied or
    /// the device cannot do it.
    func setMode(_ new: String) async throws {
        guard new != mode else { return }
        switch new {
        case "capture":
            ar.stop()
            try await camera.start()
        case "sensing":
            camera.stop()
            try await ar.start()
        default:
            camera.stop()
            ar.stop()
        }
        let old = mode
        mode = new
        faces = []
        try? await face.setFaces([])
        if new != "capture", display == .camera {
            try? await show(.face, overlay: "none", durationMs: nil)
        }
        if new == "idle" { try? await face.followFace(nil, stop: true) }
        logs.log("info", "sensors", "mode \(old) -> \(new)")
    }

    /// Faces from the camera or ARKit: kept for the `faces` topic and passed to the page
    /// (HUD boxes, gaze following) at most 15 times a second.
    func facesChanged(_ new: [SeenFace], source: String) {
        var marked = new
        if let largest = marked.indices.max(by: { marked[$0].size < marked[$1].size }) {
            marked[largest].locked = true
        }
        faces = marked
        facesSource = source
        let now = CACurrentMediaTime()
        guard now - lastFacesToPage >= 1.0 / 15 || new.isEmpty else { return }
        lastFacesToPage = now
        let json = marked.map(\.json)
        Task { try? await face.setFaces(json) }
    }

    var facesPayload: JSONObject? {
        guard mode != "idle" else { return nil }
        return ["faces": faces.map(\.json), "source": facesSource,
                "sensor_time_s": (ProcessInfo.processInfo.systemUptime * 1000).rounded() / 1000]
    }

    /// Battery, thermal state, heading, tilt and position for the HUD, 10 times a second
    /// while the camera view shows.
    func startHudFeed() {
        heading.start()
        motion.subscribe(hudMotionId, rate: 10) { [weak self] sample in self?.tilt = Self.tiltFrom(sample.accel) }
        hudTimer?.invalidate()
        hudTimer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { [weak self] _ in
            MainActor.assumeIsolated { self?.feedHud() }
        }
    }

    func stopHudFeed() {
        hudTimer?.invalidate()
        hudTimer = nil
        heading.stop()
        motion.unsubscribe(hudMotionId)
    }

    private func feedHud() {
        let device = UIDevice.current
        var values: JSONObject = [
            "charging": device.batteryState == .charging || device.batteryState == .full,
            "thermal": thermalName, "mode": mode, "clients": clients,
        ]
        if device.batteryLevel >= 0 { values["battery"] = (Double(device.batteryLevel) * 100).rounded() }
        if let heading = heading.heading { values["heading"] = (heading * 10).rounded() / 10 }
        if let tilt {
            values["pitch"] = tilt.pitch
            values["roll"] = tilt.roll
        }
        if let pose = ar.latestPose, let p = pose["position"] as? [Double], p.count == 3 {
            values["x"] = p[0]
            values["y"] = p[1]
            values["z"] = p[2]
            values["tracking"] = pose["tracking_state"]
        }
        Task { try? await face.setHudValues(values) }
    }

    /// Pitch and roll in degrees as a viewer sees the screen, from the specific force in the
    /// device frame (pitch + when the screen tilts up, roll + when it turns clockwise).
    static func tiltFrom(_ accel: [Double]) -> (pitch: Double, roll: Double) {
        let orientation = UIApplication.shared.connectedScenes
            .compactMap { ($0 as? UIWindowScene)?.interfaceOrientation }.first ?? .landscapeRight
        let (up, right): (Double, Double)
        switch orientation {
        case .landscapeLeft: (up, right) = (-accel[0], accel[1])
        case .portrait: (up, right) = (accel[1], accel[0])
        case .portraitUpsideDown: (up, right) = (-accel[1], -accel[0])
        default: (up, right) = (accel[0], -accel[1])  // landscapeRight
        }
        let roll = atan2(right, up) * 180 / .pi
        let pitch = atan2(accel[2], (up * up + right * right).squareRoot()) * 180 / .pi
        return ((pitch * 10).rounded() / 10, (roll * 10).rounded() / 10)
    }
}
