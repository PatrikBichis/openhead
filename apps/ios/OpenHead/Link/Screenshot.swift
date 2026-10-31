import Network
import UIKit
import WebKit

/// Screen geometry and OS facts for `welcome`.
struct UIScreenInfo {
    let width: Double
    let height: Double
    let scale: Double
    let safeArea: JSONObject
    let isPad: Bool
    let osVersion: String

    @MainActor static var current: UIScreenInfo {
        let window = Screenshot.keyWindow
        let bounds = window?.bounds ?? CGRect(x: 0, y: 0, width: 844, height: 390)
        let insets = window?.safeAreaInsets ?? .zero
        return UIScreenInfo(
            width: bounds.width, height: bounds.height, scale: Double(window?.screen.scale ?? 3),
            safeArea: ["top": insets.top, "left": insets.left, "bottom": insets.bottom, "right": insets.right],
            isPad: UIDevice.current.userInterfaceIdiom == .pad,
            osVersion: UIDevice.current.systemVersion)
    }
}

@MainActor
enum Screenshot {
    static var keyWindow: UIWindow? {
        UIApplication.shared.connectedScenes
            .compactMap { ($0 as? UIWindowScene)?.keyWindow }
            .first
    }

    /// The window as drawn, with the face web view (face, image, video, subtitles; transparent
    /// over a native web page) composited from its own snapshot, since WebKit content is not
    /// always captured by drawHierarchy.
    static func capture(model: AppModel, scale: Double) async throws -> (Data, Int, Int) {
        guard let window = keyWindow else { throw LinkError("busy", "no window to capture") }
        let webView = model.face.webView
        let faceImage = try? await webView.takeSnapshot(configuration: nil)
        let faceFrame = webView.convert(webView.bounds, to: window)
        let format = UIGraphicsImageRendererFormat()
        format.scale = window.screen.scale * scale
        format.opaque = true
        let image = UIGraphicsImageRenderer(bounds: window.bounds, format: format).image { _ in
            window.drawHierarchy(in: window.bounds, afterScreenUpdates: false)
            faceImage?.draw(in: faceFrame)
        }
        guard let png = image.pngData() else { throw LinkError("busy", "could not encode screenshot") }
        return (png, Int(image.size.width * image.scale), Int(image.size.height * image.scale))
    }
}

/// HTTP server on port + 1 for screenshot URLs: `GET /shot/<id>.png` with the requesting
/// client's token as `Authorization: Bearer`; URLs expire after 60 s.
@MainActor
final class ShotServer {
    private var listener: NWListener?
    private var shots: [String: (png: Data, token: String, expires: Date)] = [:]
    private weak var log: LogStore?

    /// Idempotent: keeps a running listener (the link server calls this on every restart).
    func start(port: Int, log: LogStore) {
        self.log = log
        if let listener, listener.state == .ready || listener.state == .setup { return }
        listener?.cancel()
        guard let nwPort = NWEndpoint.Port(rawValue: UInt16(port)),
              let listener = try? NWListener(using: .tcp, on: nwPort) else {
            log.log("error", "link", "cannot serve screenshots on port \(port)")
            return
        }
        listener.stateUpdateHandler = { [weak self] state in
            MainActor.assumeIsolated {
                guard case .failed(let error) = state, let self else { return }
                self.log?.log("error", "link", "screenshot listener failed: \(error); restarting")
                self.listener?.cancel()
                self.listener = nil
                DispatchQueue.main.asyncAfter(deadline: .now() + 1) { [weak self] in
                    MainActor.assumeIsolated {
                        guard let self, let log = self.log else { return }
                        self.start(port: port, log: log)
                    }
                }
            }
        }
        listener.newConnectionHandler = { [weak self] connection in
            MainActor.assumeIsolated { self?.serve(connection) }
        }
        listener.start(queue: .main)
        self.listener = listener
    }

    func add(_ png: Data, token: String) -> String {
        let now = Date()
        shots = shots.filter { $0.value.expires > now }
        let id = UUID().uuidString.replacingOccurrences(of: "-", with: "").lowercased()
        shots[id] = (png, token, now.addingTimeInterval(60))
        return id
    }

    private func serve(_ connection: NWConnection) {
        connection.start(queue: .main)
        connection.receive(minimumIncompleteLength: 1, maximumLength: 16 * 1024) { [weak self] data, _, _, _ in
            MainActor.assumeIsolated {
                let request = String(decoding: data ?? Data(), as: UTF8.self)
                let response = self?.respond(to: request) ?? (404, "text/plain", Data("not found".utf8))
                var head = "HTTP/1.1 \(response.0) \(response.0 == 200 ? "OK" : "Error")\r\n"
                head += "Content-Type: \(response.1)\r\nContent-Length: \(response.2.count)\r\nConnection: close\r\n\r\n"
                connection.send(content: Data(head.utf8) + response.2,
                                completion: .contentProcessed { _ in connection.cancel() })
            }
        }
    }

    private func respond(to request: String) -> (Int, String, Data) {
        let lines = request.components(separatedBy: "\r\n")
        let parts = lines.first?.split(separator: " ") ?? []
        guard parts.count >= 2, parts[0] == "GET" else { return (405, "text/plain", Data("GET only".utf8)) }
        let path = String(parts[1])
        guard path.hasPrefix("/shot/"), path.hasSuffix(".png") else { return (404, "text/plain", Data("not found".utf8)) }
        let id = String(path.dropFirst("/shot/".count).dropLast(".png".count))
        guard let shot = shots[id] else { return (404, "text/plain", Data("unknown screenshot".utf8)) }
        guard shot.expires > Date() else { return (410, "text/plain", Data("screenshot URL expired".utf8)) }
        let auth = lines.first { $0.lowercased().hasPrefix("authorization:") }
        guard auth?.split(separator: ":", maxSplits: 1).last?.trimmingCharacters(in: .whitespaces)
                == "Bearer \(shot.token)" else {
            return (401, "text/plain", Data("bearer token required".utf8))
        }
        return (200, "image/png", shot.png)
    }
}
