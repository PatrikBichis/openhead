import Foundation
import Security

struct ClientRecord: Codable {
    var name: String
    var lastSeen: Double
}

/// Paired clients, kept in the Keychain as one JSON item (token -> client).
enum TokenKeychain {
    private static let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrService as String: "se.bichis.openhead.tokens",
        kSecAttrAccount as String: "clients",
    ]

    static func load() -> [String: ClientRecord] {
        var q = query
        q[kSecReturnData as String] = true
        q[kSecMatchLimit as String] = kSecMatchLimitOne
        var item: CFTypeRef?
        guard SecItemCopyMatching(q as CFDictionary, &item) == errSecSuccess,
              let data = item as? Data,
              let clients = try? JSONDecoder().decode([String: ClientRecord].self, from: data)
        else { return [:] }
        return clients
    }

    static func save(_ clients: [String: ClientRecord]) {
        guard let data = try? JSONEncoder().encode(clients) else { return }
        let update: [String: Any] = [kSecValueData as String: data]
        if SecItemUpdate(query as CFDictionary, update as CFDictionary) == errSecItemNotFound {
            var add = query
            add[kSecValueData as String] = data
            add[kSecAttrAccessible as String] = kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly
            SecItemAdd(add as CFDictionary, nil)
        }
    }
}

/// Pairing: a 6-digit code shown on screen for 60 s; 5 wrong codes lock pairing for 5 minutes.
@MainActor
final class Pairing: ObservableObject {
    @Published private(set) var code: String?
    @Published private(set) var requester: String?
    @Published private(set) var clients: [String: ClientRecord]
    private var expires = Date.distantPast
    private var failures = 0
    private var lockedUntil = Date.distantPast
    private var hideTimer: Timer?
    static let maxFailures = 5

    init() { clients = TokenKeychain.load() }

    var locked: Bool { Date() < lockedUntil }
    var attemptsLeft: Int { Pairing.maxFailures - failures }
    var expiresInMs: Int { max(0, Int(expires.timeIntervalSinceNow * 1000)) }

    func isValid(_ token: String) -> Bool { clients[token] != nil }

    func touch(_ token: String) {
        guard var record = clients[token] else { return }
        record.lastSeen = Date().timeIntervalSince1970
        clients[token] = record
        TokenKeychain.save(clients)
    }

    /// Show a code for `client` (reusing a still-valid one).
    func request(by client: String) {
        if code == nil || Date() > expires {
            let n = String(Int.random(in: 0..<1_000_000))
            code = String(repeating: "0", count: 6 - n.count) + n
            expires = Date().addingTimeInterval(60)
        }
        requester = client
        hideTimer?.invalidate()
        hideTimer = Timer.scheduledTimer(withTimeInterval: expires.timeIntervalSinceNow,
                                         repeats: false) { _ in
            MainActor.assumeIsolated { self.clearCode() }
        }
    }

    /// Returns a new token, or throws `unauthorized` / `rate_limited`.
    func attempt(_ given: String, client: String) throws -> String {
        if locked {
            throw LinkError("rate_limited", "pairing locked for \(Int(lockedUntil.timeIntervalSinceNow)) s")
        }
        guard let code, Date() <= expires else {
            throw LinkError("unauthorized", "no pairing code active; send hello again")
        }
        if given == code {
            var bytes = [UInt8](repeating: 0, count: 32)
            _ = SecRandomCopyBytes(kSecRandomDefault, bytes.count, &bytes)
            let token = Data(bytes).base64EncodedString()
                .replacingOccurrences(of: "+", with: "-").replacingOccurrences(of: "/", with: "_")
                .replacingOccurrences(of: "=", with: "")
            clients[token] = ClientRecord(name: client, lastSeen: Date().timeIntervalSince1970)
            TokenKeychain.save(clients)
            failures = 0
            clearCode()
            return token
        }
        failures += 1
        if failures >= Pairing.maxFailures {
            failures = 0
            lockedUntil = Date().addingTimeInterval(300)
            clearCode()
            throw LinkError("rate_limited", "too many wrong codes; pairing locked for 300 s")
        }
        throw LinkError("unauthorized", "wrong code; \(attemptsLeft) attempts left")
    }

    func revoke(_ token: String) {
        clients[token] = nil
        TokenKeychain.save(clients)
    }

    private func clearCode() {
        code = nil
        requester = nil
        hideTimer?.invalidate()
    }
}
