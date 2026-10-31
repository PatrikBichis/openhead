import Foundation

/// Persistent settings (UserDefaults). Readable over `system.settings`; writable there in dev mode.
@MainActor
final class SettingsStore: ObservableObject {
    private let defaults = UserDefaults.standard

    @Published var name: String { didSet { defaults.set(name, forKey: "name") } }
    @Published var port: Int { didSet { defaults.set(port, forKey: "port") } }
    @Published var devMode: Bool { didSet { defaults.set(devMode, forKey: "dev_mode") } }
    /// Quaternion [x, y, z, w] from the device frame to the mount frame.
    @Published var mountOffset: [Double] { didSet { defaults.set(mountOffset, forKey: "mount_offset") } }
    @Published var offlineTheme: String { didSet { defaults.set(offlineTheme, forKey: "offline_theme") } }

    init() {
        name = defaults.string(forKey: "name") ?? "openhead"
        let storedPort = defaults.integer(forKey: "port")
        port = storedPort == 0 ? 8765 : storedPort
        devMode = defaults.bool(forKey: "dev_mode")
        mountOffset = (defaults.array(forKey: "mount_offset") as? [Double]) ?? [0, 0, 0, 1]
        offlineTheme = defaults.string(forKey: "offline_theme") ?? "cartoon"
    }

    var all: [String: Any] {
        ["name": name, "port": port, "mount_offset": mountOffset, "offline_theme": offlineTheme]
    }

    func set(_ key: String, _ value: Any) throws {
        switch key {
        case "name":
            guard let v = value as? String, !v.isEmpty, v.count <= 64 else { throw bad(key) }
            name = v
        case "port":
            guard let v = value as? Int, (1024...65534).contains(v) else { throw bad(key) }
            port = v
        case "mount_offset":
            guard let v = value as? [Double], v.count == 4 else { throw bad(key) }
            mountOffset = v
        case "offline_theme":
            guard let v = value as? String else { throw bad(key) }
            offlineTheme = v
        default:
            throw LinkError("invalid_params", "unknown setting \(key)")
        }
    }

    private func bad(_ key: String) -> LinkError { LinkError("invalid_params", "invalid value for \(key)") }
}
