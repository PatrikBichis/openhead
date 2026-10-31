import SwiftUI
import WebKit

/// What fills the screen. Images and video are drawn by the face's web layer (screen.ts);
/// web pages natively, below it.
enum DisplayContent: Equatable {
    case face
    case image
    case video
    case web(URL)

    var name: String {
        switch self {
        case .face: return "face"
        case .image: return "image"
        case .video: return "video"
        case .web: return "web"
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
