import AVFoundation
import SwiftUI
import WebKit

/// What fills the screen. Images and video are drawn by the face's web layer (screen.ts);
/// web pages natively, below it.
enum DisplayContent: Equatable {
    case face
    case image
    case video
    case web(URL)
    /// The front camera (native preview below the web view) with a HUD drawn by the page.
    case camera

    var name: String {
        switch self {
        case .face: return "face"
        case .image: return "image"
        case .video: return "video"
        case .web: return "web"
        case .camera: return "camera"
        }
    }
}

struct WebPageView: UIViewRepresentable {
    let url: URL
    func makeUIView(context: Context) -> WKWebView {
        let view = WKWebView()
        view.load(URLRequest(url: url))
        return view
    }
    func updateUIView(_ uiView: WKWebView, context: Context) {
        if uiView.url != url { uiView.load(URLRequest(url: url)) }
    }
}

/// The front camera's preview layer, filling its view (aspect fill, mirrored).
struct CameraPreview: UIViewRepresentable {
    let layer: AVCaptureVideoPreviewLayer

    final class Host: UIView {
        var preview: AVCaptureVideoPreviewLayer?
        override func layoutSubviews() {
            super.layoutSubviews()
            preview?.frame = bounds
        }
    }

    func makeUIView(context: Context) -> Host {
        let view = Host()
        view.backgroundColor = .black
        view.preview = layer
        view.layer.addSublayer(layer)
        return view
    }

    func updateUIView(_ uiView: Host, context: Context) {
        uiView.setNeedsLayout()
    }
}
