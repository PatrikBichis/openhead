import CoreImage
import ImageIO
import UIKit

/// Small JPEG frames for topic `camera` (protocol 0.5), made from the newest camera image when a
/// subscription asks for one. Nothing is stored; the face page shows "Camera shared" while any
/// paired client subscribes.
enum FrameEncoder {
    private static let context = CIContext()
    private static let sRGB = CGColorSpace(name: CGColorSpace.sRGB)!
    private static let quality = CIImageRepresentationOption(rawValue: kCGImageDestinationLossyCompressionQuality as String)

    /// The frame upright (`orientation`), its longest side `maxPx`, as JPEG; width and height.
    static func jpeg(_ box: FrameBox, maxPx: Int, orientation: CGImagePropertyOrientation) -> (Data, Int, Int)? {
        guard let buffer = box.current else { return nil }
        var image = CIImage(cvPixelBuffer: buffer).oriented(orientation)
        image = image.transformed(by: CGAffineTransform(translationX: -image.extent.minX, y: -image.extent.minY))
        let longest = max(image.extent.width, image.extent.height)
        guard longest > 0 else { return nil }
        let scale = min(1, CGFloat(maxPx) / longest)
        let width = max(1, Int((image.extent.width * scale).rounded()))
        let height = max(1, Int((image.extent.height * scale).rounded()))
        image = image.transformed(by: CGAffineTransform(scaleX: scale, y: scale))
            .cropped(to: CGRect(x: 0, y: 0, width: width, height: height))
        guard let data = context.jpegRepresentation(of: image, colorSpace: sRGB, options: [quality: 0.6]) else {
            return nil
        }
        return (data, width, height)
    }
}

extension AppModel {
    /// Clients subscribed to `camera` changed: the marker on screen, and whether ARKit keeps its
    /// newest image around for them.
    func cameraViewersChanged(_ count: Int) {
        guard count != cameraViewers else { return }
        cameraViewers = count
        ar.keepImages = count > 0
        if count == 0 { ar.lastImage.set(nil) }
        logs.log("info", "camera", count > 0 ? "camera shared with \(count) client(s)" : "camera no longer shared")
        Task { try? await face.setWatching(count) }
    }

    /// One frame for topic `camera`, or nil when no camera runs (idle) or none has arrived yet.
    func cameraFrame(maxPx: Int) async -> JSONObject? {
        let (box, orientation, source): (FrameBox, CGImagePropertyOrientation, String)
        switch mode {
        case "capture":  // already upright and mirrored like the preview
            (box, orientation, source) = (camera.lastFrame, .up, "front")
        case "sensing":
            (box, orientation, source) = (ar.lastImage, ARService.imageOrientation, "back")
        default:
            return nil
        }
        let time = (ProcessInfo.processInfo.systemUptime * 1000).rounded() / 1000
        let encoded = await Task.detached(priority: .userInitiated) {
            FrameEncoder.jpeg(box, maxPx: maxPx, orientation: orientation)
        }.value
        guard let encoded else { return nil }
        let (data, width, height) = encoded
        return ["jpeg": data.base64EncodedString(), "width": width, "height": height, "source": source,
                "sensor_time_s": time]
    }
}
