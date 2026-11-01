import CoreLocation

/// Location fixes for the `gps` topic (protocol 0.3). Runs while any session subscribes; the
/// first start asks for When In Use access. GNSS where the device has it, else Wi-Fi.
@MainActor
final class LocationService: NSObject, CLLocationManagerDelegate {
    private let manager = CLLocationManager()
    private var users: Set<UUID> = []
    private(set) var latest: JSONObject?
    private var sent: [UUID: Double] = [:]  // sensor_time_s of the last fix each session got
    var onDenied: (() -> Void)?

    override init() {
        super.init()
        manager.delegate = self
        manager.desiredAccuracy = kCLLocationAccuracyBest
    }

    var permission: String {
        switch manager.authorizationStatus {
        case .authorizedAlways, .authorizedWhenInUse: return "granted"
        case .denied, .restricted: return "denied"
        default: return "not_determined"
        }
    }

    func start(_ id: UUID) {
        users.insert(id)
        guard users.count == 1 else { return }
        if manager.authorizationStatus == .notDetermined { manager.requestWhenInUseAuthorization() }
        manager.startUpdatingLocation()
    }

    /// The latest fix if this session has not had it yet; a phone standing still sends nothing new.
    func newFix(for id: UUID) -> JSONObject? {
        guard let latest, let time = latest["sensor_time_s"] as? Double, sent[id] != time else { return nil }
        sent[id] = time
        return latest
    }

    func stop(_ id: UUID) {
        sent[id] = nil
        guard users.remove(id) != nil, users.isEmpty else { return }
        manager.stopUpdatingLocation()
        latest = nil
    }

    nonisolated func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let fix = locations.last, fix.horizontalAccuracy >= 0 else { return }
        Task { @MainActor in self.latest = Self.payload(fix) }
    }

    nonisolated func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        let status = manager.authorizationStatus
        Task { @MainActor in
            if status == .denied || status == .restricted, !self.users.isEmpty { self.onDenied?() }
        }
    }

    private static func payload(_ fix: CLLocation) -> JSONObject {
        func round(_ v: Double, _ places: Double) -> Double { (v * places).rounded() / places }
        let age = Date().timeIntervalSince(fix.timestamp)
        var p: JSONObject = [
            "lat": round(fix.coordinate.latitude, 1e7),
            "lon": round(fix.coordinate.longitude, 1e7),
            "h_accuracy_m": round(fix.horizontalAccuracy, 10),
            "sensor_time_s": round(max(0, ProcessInfo.processInfo.systemUptime - age), 1000),
        ]
        if fix.verticalAccuracy >= 0 {
            p["alt_m"] = round(fix.altitude, 10)
            p["v_accuracy_m"] = round(fix.verticalAccuracy, 10)
        }
        if fix.speed >= 0 { p["speed_m_s"] = round(fix.speed, 100) }
        if fix.course >= 0 { p["course_deg"] = round(fix.course, 10) }
        return p
    }
}
