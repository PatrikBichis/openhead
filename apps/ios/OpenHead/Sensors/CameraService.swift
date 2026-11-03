import AVFoundation
import UIKit

/// A face seen by the camera (`capture`) or ARKit (`sensing`), in the protocol's terms:
/// angles in degrees in the head frame (+bearing to the head's left, +elevation up).
struct SeenFace {
    var id: Int
    var bearing: Double
    var elevation: Double
    var size: Double
    var confidence: Double
    var distance: Double?
    /// Normalised 0-1 in the camera view as shown on screen, origin top-left.
    var box: CGRect?
    var locked = false

    var json: JSONObject {
        func r(_ v: Double, _ places: Double = 100) -> Double { (v * places).rounded() / places }
        var out: JSONObject = ["id": id, "bearing": r(bearing), "elevation": r(elevation),
                               "size": r(size, 1000), "confidence": r(confidence), "locked": locked]
        if let distance { out["distance_m"] = r(distance) }
        if let box {
            out["box"] = ["x": r(box.minX, 1e4), "y": r(box.minY, 1e4),
                          "w": r(box.width, 1e4), "h": r(box.height, 1e4)]
        }
        return out
    }
}

/// The latest camera frame, for screenshots (the preview layer is not captured by them).
final class FrameBox: @unchecked Sendable {
    private let lock = NSLock()
    private var buffer: CVPixelBuffer?

    func set(_ new: CVPixelBuffer?) {
        lock.lock()
        buffer = new
        lock.unlock()
    }

    var current: CVPixelBuffer? {
        lock.lock()
        defer { lock.unlock() }
        return buffer
    }

    func image() -> UIImage? {
        guard let current = self.current else { return nil }
        let ci = CIImage(cvPixelBuffer: current)
        guard let cg = CIContext().createCGImage(ci, from: ci.extent) else { return nil }
        return UIImage(cgImage: cg)
    }
}

/// Mode `capture`: the front camera for the camera view, with faces from AVFoundation's face
/// detector (several faces, stable ids). Boxes come from the preview layer, so they match what
/// is on screen (mirrored, aspect fill).
@MainActor
final class CameraService: NSObject {
    let session = AVCaptureSession()
    let previewLayer: AVCaptureVideoPreviewLayer
    let lastFrame = FrameBox()
    var onFaces: (([SeenFace]) -> Void)?
    private(set) var running = false
    private var configured = false
    private var horizontalFov = 68.0
    private let sessionQueue = DispatchQueue(label: "se.bichis.openhead.camera")
    private let framesQueue = DispatchQueue(label: "se.bichis.openhead.camera.frames")
    private let metadata = AVCaptureMetadataOutput()
    private let frames = AVCaptureVideoDataOutput()
    private var rotation: AVCaptureDevice.RotationCoordinator?
    private var rotationObservation: NSKeyValueObservation?

    override init() {
        previewLayer = AVCaptureVideoPreviewLayer(session: session)
        previewLayer.videoGravity = .resizeAspectFill
        super.init()
    }

    static var permission: String {
        switch AVCaptureDevice.authorizationStatus(for: .video) {
        case .authorized: return "granted"
        case .denied, .restricted: return "denied"
        default: return "not_determined"
        }
    }

    /// Ask for camera access the first time; false when the user said no.
    static func authorize() async -> Bool {
        switch AVCaptureDevice.authorizationStatus(for: .video) {
        case .authorized: return true
        case .notDetermined: return await AVCaptureDevice.requestAccess(for: .video)
        default: return false
        }
    }

    func start() async throws {
        guard await Self.authorize() else {
            throw LinkError("unsupported", "camera permission denied; allow it in Settings > OpenHead")
        }
        if !configured { try configure() }
        let session = self.session
        await withCheckedContinuation { (done: CheckedContinuation<Void, Never>) in
            sessionQueue.async {
                session.startRunning()
                done.resume()
            }
        }
        running = true
    }

    func stop() {
        guard running else { return }
        let session = self.session
        sessionQueue.async { session.stopRunning() }
        running = false
        lastFrame.set(nil)
        onFaces?([])
    }

    private func configure() throws {
        session.beginConfiguration()
        defer { session.commitConfiguration() }
        session.sessionPreset = .hd1280x720
        guard let device = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .front),
              let input = try? AVCaptureDeviceInput(device: device), session.canAddInput(input) else {
            throw LinkError("unsupported", "no front camera")
        }
        session.addInput(input)
        if session.canAddOutput(metadata) {
            session.addOutput(metadata)
            if metadata.availableMetadataObjectTypes.contains(.face) {
                metadata.metadataObjectTypes = [.face]
            }
            metadata.setMetadataObjectsDelegate(self, queue: .main)
        }
        frames.alwaysDiscardsLateVideoFrames = true
        frames.videoSettings = [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA]
        if session.canAddOutput(frames) {
            session.addOutput(frames)
            frames.setSampleBufferDelegate(self, queue: framesQueue)
        }
        horizontalFov = Double(device.activeFormat.videoFieldOfView)
        let coordinator = AVCaptureDevice.RotationCoordinator(device: device, previewLayer: previewLayer)
        rotation = coordinator
        rotationObservation = coordinator.observe(\.videoRotationAngleForHorizonLevelPreview,
                                                  options: [.new]) { [weak self] _, _ in
            Task { @MainActor in self?.applyRotation() }
        }
        applyRotation()
        configured = true
    }

    /// Keep the preview and the saved frames upright in whichever landscape the phone is in.
    private func applyRotation() {
        guard let rotation else { return }
        let preview = rotation.videoRotationAngleForHorizonLevelPreview
        if let connection = previewLayer.connection, connection.isVideoRotationAngleSupported(preview) {
            connection.videoRotationAngle = preview
        }
        let capture = rotation.videoRotationAngleForHorizonLevelCapture
        if let connection = frames.connection(with: .video) {
            if connection.isVideoRotationAngleSupported(capture) { connection.videoRotationAngle = capture }
            if connection.isVideoMirroringSupported {
                connection.automaticallyAdjustsVideoMirroring = false
                connection.isVideoMirrored = true  // like the preview: a mirror
            }
        }
    }

    fileprivate func handle(_ objects: [AVMetadataObject]) {
        let bounds = previewLayer.bounds
        guard bounds.width > 0, bounds.height > 0 else { return }
        let tanH = tan(horizontalFov / 2 * .pi / 180)
        let tanV = tanH * Double(bounds.height / bounds.width)  // aspect fill keeps the full width
        let faces: [SeenFace] = objects.compactMap { object in
            guard let face = object as? AVMetadataFaceObject,
                  let shown = previewLayer.transformedMetadataObject(for: face) else { return nil }
            let r = shown.bounds
            let box = CGRect(x: r.minX / bounds.width, y: r.minY / bounds.height,
                             width: r.width / bounds.width, height: r.height / bounds.height)
                .intersection(CGRect(x: 0, y: 0, width: 1, height: 1))
            guard !box.isNull, box.width > 0 else { return nil }
            // The preview is mirrored: someone on the head's left appears on the right.
            let bearing = atan((Double(box.midX) - 0.5) * 2 * tanH) * 180 / .pi
            let elevation = atan((0.5 - Double(box.midY)) * 2 * tanV) * 180 / .pi
            return SeenFace(id: max(0, face.faceID), bearing: bearing, elevation: elevation,
                            size: Double(box.width), confidence: 1, distance: nil, box: box)
        }
        onFaces?(faces)
    }
}

extension CameraService: AVCaptureMetadataOutputObjectsDelegate {
    nonisolated func metadataOutput(_ output: AVCaptureMetadataOutput, didOutput metadataObjects: [AVMetadataObject],
                                    from connection: AVCaptureConnection) {
        MainActor.assumeIsolated { self.handle(metadataObjects) }  // delegate queue is main
    }
}

extension CameraService: AVCaptureVideoDataOutputSampleBufferDelegate {
    nonisolated func captureOutput(_ output: AVCaptureOutput, didOutput sampleBuffer: CMSampleBuffer,
                                   from connection: AVCaptureConnection) {
        // Runs on the frames queue; FrameBox is thread-safe.
        guard let buffer = CMSampleBufferGetImageBuffer(sampleBuffer) else { return }
        lastFrame.set(buffer)
    }
}
