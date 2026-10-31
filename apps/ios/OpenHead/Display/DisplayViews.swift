import SwiftUI
import WebKit

/// Content for `display.show`: an image or a web page; the face is the default.
enum DisplayContent {
    case face
    case image(UIImage)
    case web(URL)

    var name: String {
        switch self {
        case .face: return "face"
        case .image: return "image"
        case .web: return "web"
        }
    }
}

enum ImageLoader {
    /// An http(s) URL the device fetches, or a `data:image/...;base64,` URI.
    static func load(_ source: String) async throws -> UIImage {
        let data: Data
        if source.hasPrefix("data:") {
            guard let comma = source.firstIndex(of: ","),
                  let decoded = Data(base64Encoded: String(source[source.index(after: comma)...]))
            else { throw LinkError("invalid_params", "bad data URI") }
            data = decoded
        } else if let url = URL(string: source) {
            do {
                let (body, response) = try await URLSession.shared.data(from: url)
                if let http = response as? HTTPURLResponse, http.statusCode != 200 {
                    throw LinkError("invalid_params", "image URL answered \(http.statusCode)")
                }
                data = body
            } catch let error as LinkError {
                throw error
            } catch {
                throw LinkError("invalid_params", "could not load image: \(error.localizedDescription)")
            }
        } else {
            throw LinkError("invalid_params", "bad image source")
        }
        guard let image = UIImage(data: data) else {
            throw LinkError("invalid_params", "source is not a PNG, JPEG, GIF or WebP image")
        }
        return image
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
