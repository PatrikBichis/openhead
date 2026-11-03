import ARKit
import UIKit
import simd

/// Mode `sensing`: ARKit owns the cameras. World tracking (back camera) gives the head's pose;
/// user face tracking (TrueDepth front camera, iPhone X and later) gives one face with distance.
/// On phones with LiDAR (Pro models, optional, protocol 0.5) it also gives depth (`depth.sample`)
/// and, while someone subscribes to `mesh`, the room as meshes; an iPhone 12 runs as before.
@MainActor
final class ARService: NSObject, ARSessionDelegate {
    let session = ARSession()
    var onFaces: (([SeenFace]) -> Void)?
    private(set) var running = false
    private(set) var latestPose: JSONObject?
    private var lastFaces = 0.0
    /// The newest back-camera image, kept only while a client watches topic `camera`.
    let lastImage = FrameBox()
    var keepImages = false
    /// `depth.sample` calls waiting for the next frame with a depth map.
    private var depthRequests: [(id: UUID, points: [CGPoint], done: CheckedContinuation<JSONObject, Error>)] = []
    /// Mesh anchors changed since the last `mesh` message, and the ids ARKit removed.
    private(set) var changedMeshes: [UUID: ARMeshAnchor] = [:]
    private(set) var removedMeshes: Set<UUID> = []
    var wantsMesh = false {
        didSet { if wantsMesh != oldValue, running { run(reset: false) } }
    }
    /// Device frame (as `imu`: portrait, +z out of the screen) to ARKit's camera frame, which is
    /// fixed to the sensor in landscape-right: camera +x = device -y, camera +y = device +x.
    private let cameraFromDevice = simd_quatf(angle: .pi / 2, axis: SIMD3<Float>(0, 0, 1))

    static var supported: Bool { ARWorldTrackingConfiguration.isSupported }
    static var supportsDepth: Bool { ARWorldTrackingConfiguration.supportsFrameSemantics(.sceneDepth) }
    static var supportsMesh: Bool { ARWorldTrackingConfiguration.supportsSceneReconstruction(.mesh) }

    /// How ARKit's captured image (sensor orientation, landscape right) turns upright on screen.
    static var imageOrientation: CGImagePropertyOrientation {
        switch interfaceOrientation {
        case .landscapeLeft: return .down
        case .portrait: return .right
        case .portraitUpsideDown: return .left
        default: return .up
        }
    }

    private static var interfaceOrientation: UIInterfaceOrientation {
        UIApplication.shared.connectedScenes.compactMap { ($0 as? UIWindowScene)?.interfaceOrientation }.first
            ?? .landscapeRight
    }

    func start() async throws {
        guard Self.supported else { throw LinkError("unsupported", "ARKit world tracking is not supported here") }
        guard await CameraService.authorize() else {
            throw LinkError("unsupported", "camera permission denied; allow it in Settings > OpenHead")
        }
        session.delegate = self
        running = true
        run(reset: true)
    }

    /// (Re)configure the session; without `reset` tracking carries on (turning the mesh on or off).
    private func run(reset: Bool) {
        let config = ARWorldTrackingConfiguration()
        config.worldAlignment = .gravity
        if ARWorldTrackingConfiguration.supportsUserFaceTracking {
            config.userFaceTrackingEnabled = true
        }
        if Self.supportsDepth { config.frameSemantics.insert(.sceneDepth) }
        if wantsMesh, Self.supportsMesh { config.sceneReconstruction = .mesh }
        session.run(config, options: reset ? [.resetTracking, .removeExistingAnchors] : [])
    }

    func stop() {
        guard running else { return }
        session.pause()
        running = false
        latestPose = nil
        lastImage.set(nil)
        changedMeshes = [:]
        removedMeshes = []
        for request in depthRequests {
            request.done.resume(throwing: LinkError("unsupported", "depth.sample needs mode sensing"))
        }
        depthRequests = []
        onFaces?([])
    }

    /// Metres from the back camera at normalised points of the `camera` image (upright, origin
    /// top-left), from the next frame's LiDAR depth map.
    func sampleDepth(_ points: [CGPoint]) async throws -> JSONObject {
        guard Self.supportsDepth else {
            throw LinkError("unsupported", "depth.sample needs a device with LiDAR (capability lidar)")
        }
        guard running else { throw LinkError("unsupported", "depth.sample needs mode sensing") }
        // Commands run one at a time, so never wait long: a frame without depth answers `busy`.
        return try await withCheckedThrowingContinuation { done in
            let id = UUID()
            depthRequests.append((id, points, done))
            DispatchQueue.main.asyncAfter(deadline: .now() + 1) { [weak self] in
                MainActor.assumeIsolated {
                    guard let self, let i = self.depthRequests.firstIndex(where: { $0.id == id }) else { return }
                    self.depthRequests.remove(at: i).done.resume(throwing: LinkError("busy", "no depth map yet; try again"))
                }
            }
        }
    }

    /// Take the mesh changes for the next `mesh` message (at most `limit` bytes of geometry). The
    /// changes are shared: with two `mesh` subscribers each gets a part (one viewer is the use).
    func takeMeshChanges(limit: Int = 900_000) -> (anchors: [JSONObject], removed: [String]) {
        var anchors: [JSONObject] = []
        var bytes = 0
        for (id, anchor) in changedMeshes {
            let json = Self.meshJSON(anchor)
            let size = ((json["vertices"] as? String)?.count ?? 0) + ((json["faces"] as? String)?.count ?? 0)
            if !anchors.isEmpty, bytes + size > limit || anchors.count >= 64 { break }
            anchors.append(json)
            bytes += size
            changedMeshes[id] = nil
        }
        let removed = removedMeshes.map(\.uuidString)
        removedMeshes = []
        return (anchors, removed)
    }

    /// Start the next subscriber from a full map: everything ARKit has counts as changed.
    func resendMeshes() {
        for anchor in session.currentFrame?.anchors.compactMap({ $0 as? ARMeshAnchor }) ?? [] {
            changedMeshes[anchor.identifier] = anchor
        }
    }

    private static func meshJSON(_ anchor: ARMeshAnchor) -> JSONObject {
        let geometry = anchor.geometry
        let vertices = geometry.vertices
        var points = Data(capacity: vertices.count * 12)
        let base = vertices.buffer.contents().advanced(by: vertices.offset)
        for i in 0..<vertices.count {
            points.append(Data(bytes: base.advanced(by: i * vertices.stride), count: 12))  // float3
        }
        let faces = geometry.faces
        var indices = Data(capacity: faces.count * 3 * 4)
        let source = faces.buffer.contents()
        for i in 0..<(faces.count * faces.indexCountPerPrimitive) {
            let index: UInt32 = faces.bytesPerIndex == 2
                ? UInt32(source.load(fromByteOffset: i * 2, as: UInt16.self))
                : source.load(fromByteOffset: i * 4, as: UInt32.self)
            withUnsafeBytes(of: index.littleEndian) { indices.append(contentsOf: $0) }
        }
        let t = anchor.transform
        let q = simd_quatf(t).vector
        func r(_ v: Float) -> Double { Double((v * 10000).rounded() / 10000) }
        return ["id": anchor.identifier.uuidString,
                "position": [r(t.columns.3.x), r(t.columns.3.y), r(t.columns.3.z)],
                "q": [r(q.x), r(q.y), r(q.z), r(q.w)],
                "vertices": points.base64EncodedString(), "faces": indices.base64EncodedString()]
    }

    nonisolated func session(_ session: ARSession, didAdd anchors: [ARAnchor]) {
        let meshes = anchors.compactMap { $0 as? ARMeshAnchor }
        guard !meshes.isEmpty else { return }
        MainActor.assumeIsolated { for m in meshes { self.changedMeshes[m.identifier] = m } }
    }

    nonisolated func session(_ session: ARSession, didUpdate anchors: [ARAnchor]) {
        let meshes = anchors.compactMap { $0 as? ARMeshAnchor }
        guard !meshes.isEmpty else { return }
        MainActor.assumeIsolated { for m in meshes { self.changedMeshes[m.identifier] = m } }
    }

    nonisolated func session(_ session: ARSession, didRemove anchors: [ARAnchor]) {
        let ids = anchors.compactMap { ($0 as? ARMeshAnchor)?.identifier }
        guard !ids.isEmpty else { return }
        MainActor.assumeIsolated {
            for id in ids {
                self.changedMeshes[id] = nil
                self.removedMeshes.insert(id)
            }
        }
    }

    nonisolated func session(_ session: ARSession, didUpdate frame: ARFrame) {
        // Delegate calls arrive on the main queue (no delegateQueue set); keep no frame around.
        let camera = frame.camera
        let transform = camera.transform
        let tracking = camera.trackingState
        let time = frame.timestamp
        let faces = frame.anchors.compactMap { $0 as? ARFaceAnchor }.filter(\.isTracked).map(\.transform)
        let image = frame.capturedImage
        let depth = frame.sceneDepth
        MainActor.assumeIsolated {
            if self.keepImages { self.lastImage.set(image) }
            if !self.depthRequests.isEmpty, let depth { self.answerDepth(depth, time) }
            self.update(transform, tracking, time, faces)
        }
    }

    private func answerDepth(_ depth: ARDepthData, _ time: TimeInterval) {
        let map = depth.depthMap
        CVPixelBufferLockBaseAddress(map, .readOnly)
        defer { CVPixelBufferUnlockBaseAddress(map, .readOnly) }
        let confidence = depth.confidenceMap
        if let confidence { CVPixelBufferLockBaseAddress(confidence, .readOnly) }
        defer { if let confidence { CVPixelBufferUnlockBaseAddress(confidence, .readOnly) } }
        let width = CVPixelBufferGetWidth(map)
        let height = CVPixelBufferGetHeight(map)
        let orientation = Self.imageOrientation
        for request in depthRequests {
            var depths: [Any] = []
            var levels: [String] = []
            for p in request.points {
                // From the upright image back to the sensor's own orientation.
                let (px, py) = (Double(p.x), Double(p.y))
                let (sx, sy): (Double, Double)
                switch orientation {
                case .down: (sx, sy) = (1 - px, 1 - py)
                case .right: (sx, sy) = (py, 1 - px)
                case .left: (sx, sy) = (1 - py, px)
                default: (sx, sy) = (px, py)
                }
                let x = min(width - 1, max(0, Int(sx * Double(width))))
                let y = min(height - 1, max(0, Int(sy * Double(height))))
                guard let base = CVPixelBufferGetBaseAddress(map) else { depths.append(NSNull()); continue }
                let row = base.advanced(by: y * CVPixelBufferGetBytesPerRow(map))
                let metres = Double(row.load(fromByteOffset: x * 4, as: Float32.self))
                if metres.isFinite, metres > 0 {
                    depths.append((metres * 1000).rounded() / 1000)
                } else {
                    depths.append(NSNull())
                }
                if let confidence, let cbase = CVPixelBufferGetBaseAddress(confidence) {
                    let level = cbase.advanced(by: y * CVPixelBufferGetBytesPerRow(confidence))
                        .load(fromByteOffset: x, as: UInt8.self)
                    levels.append(level >= 2 ? "high" : level == 1 ? "medium" : "low")
                }
            }
            var result: JSONObject = ["depths_m": depths, "sensor_time_s": (time * 10000).rounded() / 10000]
            if levels.count == depths.count { result["confidence"] = levels }
            request.done.resume(returning: result)
        }
        depthRequests = []
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
        switch interfaceOrientation {
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
