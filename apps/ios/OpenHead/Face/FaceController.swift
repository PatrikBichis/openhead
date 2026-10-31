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
    /// The page changed view on its own (a video ended): the new view's name.
    var onView: ((String) -> Void)?

    override init() {
        let config = WKWebViewConfiguration()
        config.setURLSchemeHandler(FaceSchemeHandler(), forURLScheme: FaceSchemeHandler.scheme)
        config.mediaTypesRequiringUserActionForPlayback = []
        config.allowsInlineMediaPlayback = true // video plays in the page, not full screen
        let controller = WKUserContentController()
        config.userContentController = controller
        webView = WKWebView(frame: .zero, configuration: config)
        webView.isOpaque = false
        // Clear: over a native web page only the corner face and subtitles show (screen.ts).
        webView.backgroundColor = .clear
        webView.scrollView.backgroundColor = .clear
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

    // Messages from main.ts: {type: "ready"}, {type: "log", level, message} and
    // {type: "event", event: {type: "view", view, reason}}.
    func userContentController(_ userContentController: WKUserContentController,
                               didReceive message: WKScriptMessage) {
        guard let body = message.body as? [String: Any], let type = body["type"] as? String else { return }
        switch type {
        case "ready":
            ready = true
            onReady?()
        case "log":
            onLog?(body["level"] as? String ?? "info", body["message"] as? String ?? "")
        case "event":
            if let event = body["event"] as? [String: Any], event["type"] as? String == "view",
               let view = event["view"] as? String {
                onView?(view)
            }
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

    // MARK: screen layer (screen.ts): images, video, web pages, subtitles

    /// Load and show `content`; throws (screen unchanged) if it cannot be loaded. Web pages
    /// are drawn natively below the web view (`nativeWeb`), which turns transparent.
    func show(_ content: String, source: String, overlay: String, loop: Bool, muted: Bool) async throws {
        let opts: [String: Any] = ["overlay": overlay, "loop": loop, "muted": muted, "nativeWeb": content == "web"]
        try await call("await window.openhead.show(content, source, opts); return true",
                       ["content": content, "source": source, "opts": opts])
    }

    func clearDisplay() async throws {
        try await call("window.openhead.clear(); return true")
    }

    func subtitle(_ text: String, mode: String, position: String?, durationMs: Int?, mouth: Bool) async throws {
        var opts: [String: Any] = ["mode": mode, "mouth": mouth]
        if let position { opts["position"] = position }
        if let durationMs { opts["durationMs"] = durationMs }
        try await call("window.openhead.subtitle(text, opts); return true", ["text": text, "opts": opts])
    }

    func listThemes() async throws -> [[String: Any]] {
        (try await call("return window.openhead.listThemes()") as? [[String: Any]]) ?? []
    }

    struct State {
        var theme = "cartoon"
        var emotion = "neutral"
        var view = "face"
        var overlay = "none"
        var subtitle = ""
    }

    func state() async throws -> State {
        let s = try await call("const s = window.openhead.state(); " +
                               "return {theme: s.theme, emotion: s.emotion, ...window.openhead.screen()}")
            as? [String: Any] ?? [:]
        return State(theme: s["theme"] as? String ?? "cartoon", emotion: s["emotion"] as? String ?? "neutral",
                     view: s["view"] as? String ?? "face", overlay: s["overlay"] as? String ?? "none",
                     subtitle: s["subtitle"] as? String ?? "")
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
