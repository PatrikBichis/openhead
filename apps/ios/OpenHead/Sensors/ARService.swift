import ARKit
import UIKit
import simd

/// Mode `sensing`: ARKit owns the cameras. World tracking (back camera) gives the head's pose;
/// user face tracking (TrueDepth front camera, iPhone X and later) gives one face with distance.
@MainActor
final class ARService: NSObject, ARSessionDelegate {
    let session = ARSession()
    var onFaces: (([SeenFace]) -> Void)?
    private(set) var running = false
    private(set) var latestPose: JSONObject?
    private var lastFaces = 0.0
    /// Device frame (as `imu`: portrait, +z out of the screen) to ARKit's camera frame, which is
    /// fixed to the sensor in landscape-right: camera +x = device -y, camera +y = device +x.
    private let cameraFromDevice = simd_quatf(angle: .pi / 2, axis: SIMD3<Float>(0, 0, 1))

    static var supported: Bool { ARWorldTrackingConfiguration.isSupported }

    func start() async throws {
        guard Self.supported else { throw LinkError("unsupported", "ARKit world tracking is not supported here") }
        guard await CameraService.authorize() else {
            throw LinkError("unsupported", "camera permission denied; allow it in Settings > OpenHead")
        }
        let config = ARWorldTrackingConfiguration()
        config.worldAlignment = .gravity
        if ARWorldTrackingConfiguration.supportsUserFaceTracking {
            config.userFaceTrackingEnabled = true
        }
        session.delegate = self
        session.run(config, options: [.resetTracking, .removeExistingAnchors])
        running = true
    }

    func stop() {
        guard running else { return }
        session.pause()
        running = false
        latestPose = nil
        onFaces?([])
    }

    nonisolated func session(_ session: ARSession, didUpdate frame: ARFrame) {
        // Delegate calls arrive on the main queue (no delegateQueue set); keep no frame around.
        let camera = frame.camera
        let transform = camera.transform
        let tracking = camera.trackingState
        let time = frame.timestamp
        let faces = frame.anchors.compactMap { $0 as? ARFaceAnchor }.filter(\.isTracked).map(\.transform)
        MainActor.assumeIsolated { self.update(transform, tracking, time, faces) }
    }

    private func update(_ t: simd_float4x4, _ tracking: ARCamera.TrackingState, _ time: TimeInterval,
                        _ faceTransforms: [simd_float4x4]) {
        let worldFromDevice = simd_quatf(t) * cameraFromDevice
        let q = worldFromDevice.vector  // x, y, z, w
        func r(_ v: Float, _ places: Float = 10000) -> Double { Double((v * places).rounded() / places) }
        var pose: JSONObject = [
            "position": [r(t.columns.3.x), r(t.columns.3.y), r(t.columns.3.z)],
            "q": [r(q.x, 1e6), r(q.y, 1e6), r(q.z, 1e6), r(q.w, 1e6)],
            "frame": "world",
            "sensor_time_s": (time * 10000).rounded() / 10000,
        ]
        switch tracking {
        case .normal:
            pose["tracking_state"] = "normal"
        case .notAvailable:
            pose["tracking_state"] = "not_available"
        case .limited(let reason):
            pose["tracking_state"] = "limited"
            switch reason {
            case .initializing: pose["tracking_reason"] = "initializing"
            case .excessiveMotion: pose["tracking_reason"] = "excessive_motion"
            case .insufficientFeatures: pose["tracking_reason"] = "insufficient_features"
            case .relocalizing: pose["tracking_reason"] = "relocalizing"
            @unknown default: break
            }
        @unknown default:
            pose["tracking_state"] = "limited"
        }
        latestPose = pose

        guard time - lastFaces >= 1.0 / 15 else { return }
        lastFaces = time
        // Faces in the device frame, then as angles the way a viewer sees the screen.
        let deviceFromWorld = simd_inverse(simd_float4x4(worldFromDevice, translation: t.columns.3))
        let (right, up) = Self.screenAxes()
        let faces: [SeenFace] = faceTransforms.enumerated().compactMap { index, face in
            let p4 = deviceFromWorld * face.columns.3
            let p = SIMD3<Double>(Double(p4.x), Double(p4.y), Double(p4.z))
            guard p.z > 0.05 else { return nil }  // in front of the screen
            let distance = simd_length(p)
            let bearing = atan2(simd_dot(p, right), p.z) * 180 / .pi  // viewer's right = head's left
            let elevation = atan2(simd_dot(p, up), p.z) * 180 / .pi
            let size = min(1, 0.15 / (distance * 2 * tan(34 * Double.pi / 180)))
            return SeenFace(id: index, bearing: bearing, elevation: elevation, size: size,
                            confidence: 1, distance: distance, box: nil)
        }
        onFaces?(faces)
    }

    /// Viewer's right and up on the screen, in the device frame, for the current landscape.
    private static func screenAxes() -> (SIMD3<Double>, SIMD3<Double>) {
        let orientation = UIApplication.shared.connectedScenes
            .compactMap { ($0 as? UIWindowScene)?.interfaceOrientation }.first ?? .landscapeRight
        switch orientation {
        case .landscapeLeft: return (SIMD3(0, 1, 0), SIMD3(-1, 0, 0))
        case .portrait: return (SIMD3(1, 0, 0), SIMD3(0, 1, 0))
        case .portraitUpsideDown: return (SIMD3(-1, 0, 0), SIMD3(0, -1, 0))
        default: return (SIMD3(0, -1, 0), SIMD3(1, 0, 0))  // landscapeRight: top edge on the left
        }
    }
}

private extension simd_float4x4 {
    init(_ rotation: simd_quatf, translation: SIMD4<Float>) {
        self.init(rotation)
        columns.3 = translation
    }
}
