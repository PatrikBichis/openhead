import Foundation

/// A protocol error answered with `error {code, message}`.
struct LinkError: Error {
    let code: String
    let message: String
    init(_ code: String, _ message: String) {
        self.code = code
        self.message = message
    }
}

typealias JSONObject = [String: Any]

extension Dictionary where Key == String, Value == Any {
    func string(_ key: String) -> String? { self[key] as? String }
    func double(_ key: String) -> Double? { (self[key] as? NSNumber)?.doubleValue }
    func int(_ key: String) -> Int? { (self[key] as? NSNumber)?.intValue }
}

/// Decode with the generated model: the router uses it to reject malformed messages.
func decodeMessage<T: Decodable>(_ type: T.Type, _ data: Data) throws -> T {
    try JSONDecoder().decode(T.self, from: data)
}

func describe(_ error: Error) -> String {
    switch error {
    case DecodingError.keyNotFound(let key, _): return "missing field \(key.stringValue)"
    case DecodingError.typeMismatch(_, let ctx), DecodingError.valueNotFound(_, let ctx),
         DecodingError.dataCorrupted(let ctx):
        let path = ctx.codingPath.map(\.stringValue).joined(separator: "/")
        return "\(path.isEmpty ? "message" : path): \(ctx.debugDescription)"
    default: return String(describing: error)
    }
}
