import SwiftUI
import WebKit

/// Hosts the face engine (face/dist) in a WKWebView and calls its JavaScript API
/// (`window.openhead`). No face logic lives in Swift.
@MainActor
final class FaceController: NSObject, ObservableObject, WKScriptMessageHandler, WKNavigationDelegate {
    let webView: WKWebView
    @Published private(set) var ready = false
    var onLog: ((String, String) -> Void)?
    var onReady: (() -> Void)?

    override init() {
        let config = WKWebViewConfiguration()
        config.setURLSchemeHandler(FaceSchemeHandler(), forURLScheme: FaceSchemeHandler.scheme)
        config.mediaTypesRequiringUserActionForPlayback = []
        let controller = WKUserContentController()
        config.userContentController = controller
        webView = WKWebView(frame: .zero, configuration: config)
        webView.isOpaque = false
        webView.backgroundColor = .black
        webView.scrollView.isScrollEnabled = false
        webView.scrollView.contentInsetAdjustmentBehavior = .never
        super.init()
        controller.add(WeakMessageHandler(self), name: "openhead")
        webView.navigationDelegate = self
    }

    func load(theme: String) {
        ready = false
        let url = URL(string: "\(FaceSchemeHandler.scheme)://face/index.html?theme=\(theme)")!
        webView.load(URLRequest(url: url))
    }

    // Messages from main.ts: {type: "ready"} and {type: "log", level, message}.
    func userContentController(_ userContentController: WKUserContentController,
                               didReceive message: WKScriptMessage) {
        guard let body = message.body as? [String: Any], let type = body["type"] as? String else { return }
        switch type {
        case "ready":
            ready = true
            onReady?()
        case "log":
            onLog?(body["level"] as? String ?? "info", body["message"] as? String ?? "")
        default:
            break
        }
    }

    func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
        onLog?("error", "face failed to load: \(error.localizedDescription)")
    }

    func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!,
                 withError error: Error) {
        onLog?("error", "face failed to load: \(error.localizedDescription)")
    }

    func webViewWebContentProcessDidTerminate(_ webView: WKWebView) {
        onLog?("error", "face web content process terminated; reloading")
        webView.reload()
    }

    // MARK: - engine API

    @discardableResult
    func call(_ body: String, _ arguments: [String: Any] = [:]) async throws -> Any? {
        guard ready else { throw LinkError("busy", "face engine is still loading") }
        // Completion-handler form: the async overlay traps when the script returns nothing.
        return try await withCheckedThrowingContinuation { continuation in
            webView.callAsyncJavaScript(body, arguments: arguments, in: nil, in: .page) { result in
                switch result {
                case .success(let value):
                    continuation.resume(returning: value)
                case .failure(let error):
                    let ns = error as NSError
                    let message = ns.userInfo["WKJavaScriptExceptionMessage"] as? String ?? ns.localizedDescription
                    continuation.resume(throwing: LinkError("invalid_params",
                                                            message.replacingOccurrences(of: "Error: ", with: "")))
                }
            }
        }
    }

    func setTheme(_ name: String, transitionMs: Int) async throws {
        try await call("await window.openhead.setTheme(name, ms); return true", ["name": name, "ms": transitionMs])
    }

    func setEmotion(_ name: String, intensity: Double, blend: String, durationMs: Int?) async throws {
        var args: [String: Any] = ["name": name, "intensity": intensity, "blend": blend]
        if let durationMs { args["duration"] = durationMs }
        try await call("window.openhead.setEmotion(name, intensity, blend, " +
                       "typeof duration === 'undefined' ? undefined : duration); return true", args)
    }

    func setGaze(x: Double, y: Double) async throws {
        try await call("window.openhead.setGaze(x, y); return true", ["x": x, "y": y])
    }

    func blink() async throws {
        try await call("window.openhead.blink(); return true")
    }

    /// Mouth envelope at 20-30 Hz: fire and forget, no round trip.
    func envelope(_ level: Double) {
        guard ready else { return }
        webView.evaluateJavaScript("window.openhead.setEnvelope(\(max(0, min(1, level))))")
    }

    func listThemes() async throws -> [[String: Any]] {
        (try await call("return window.openhead.listThemes()") as? [[String: Any]]) ?? []
    }

    func state() async throws -> (theme: String, emotion: String) {
        let s = try await call("const s = window.openhead.state(); return {theme: s.theme, emotion: s.emotion}")
            as? [String: Any]
        return (s?["theme"] as? String ?? "cartoon", s?["emotion"] as? String ?? "neutral")
    }
}

/// Breaks the retain cycle WKUserContentController -> handler -> web view.
@MainActor
private final class WeakMessageHandler: NSObject, WKScriptMessageHandler {
    weak var target: WKScriptMessageHandler?
    init(_ target: WKScriptMessageHandler) { self.target = target }
    func userContentController(_ controller: WKUserContentController, didReceive message: WKScriptMessage) {
        target?.userContentController(controller, didReceive: message)
    }
}

struct FaceView: UIViewRepresentable {
    let face: FaceController
    func makeUIView(context: Context) -> WKWebView { face.webView }
    func updateUIView(_ uiView: WKWebView, context: Context) {}
}
