import CoreMotion

/// Barometer and magnetometer for the `env` topic (protocol 0.3); the compass comes from
/// HeadingService. Runs while any session subscribes. The barometer asks for Motion & Fitness
/// access the first time. A separate CMMotionManager keeps the IMU stream untouched.
@MainActor
final class EnvService {
    private let altimeter = CMAltimeter()
    private let motion = CMMotionManager()
    private var users: Set<UUID> = []
    private var pressure: Double?
    private var relativeAltitude: Double?
    private var field: [Double]?

    static var permission: String {
        guard CMAltimeter.isRelativeAltitudeAvailable() else { return "not_required" }
        switch CMAltimeter.authorizationStatus() {
        case .authorized: return "granted"
        case .denied, .restricted: return "denied"
        default: return "not_determined"
        }
    }

    func start(_ id: UUID) {
        users.insert(id)
        guard users.count == 1 else { return }
        if CMAltimeter.isRelativeAltitudeAvailable() {
            altimeter.startRelativeAltitudeUpdates(to: .main) { [weak self] data, _ in
                guard let data else { return }
                MainActor.assumeIsolated {
                    self?.pressure = data.pressure.doubleValue  // kPa
                    self?.relativeAltitude = data.relativeAltitude.doubleValue
                }
            }
        }
        if motion.isMagnetometerAvailable {
            motion.magnetometerUpdateInterval = 0.1
            motion.startMagnetometerUpdates(to: .main) { [weak self] data, _ in
                guard let f = data?.magneticField else { return }
                MainActor.assumeIsolated { self?.field = [f.x, f.y, f.z] }
            }
        }
    }

    func stop(_ id: UUID) {
        guard users.remove(id) != nil, users.isEmpty else { return }
        altimeter.stopRelativeAltitudeUpdates()
        motion.stopMagnetometerUpdates()
        pressure = nil
        relativeAltitude = nil
        field = nil
    }

    /// Every reading there is, or nil before the first one.
    func payload(heading: HeadingService) -> JSONObject? {
        func round(_ v: Double, _ places: Double) -> Double { (v * places).rounded() / places }
        var p: JSONObject = [:]
        if let pressure { p["pressure_kpa"] = round(pressure, 1e4) }
        if let relativeAltitude { p["relative_altitude_m"] = round(relativeAltitude, 100) }
        if let field { p["magnetic_field_ut"] = field.map { round($0, 100) } }
        if let value = heading.heading {
            p["heading_deg"] = round(value, 10)
            p["heading_ref"] = heading.isTrue ? "true" : "magnetic"
            if let accuracy = heading.accuracy { p["heading_accuracy_deg"] = round(accuracy, 10) }
        }
        guard !p.isEmpty else { return nil }
        p["sensor_time_s"] = round(ProcessInfo.processInfo.systemUptime, 1000)
        return p
    }

    /// For the HUD's {pressure}: hPa to one decimal.
    var pressureHpa: Double? { pressure.map { ($0 * 100).rounded() / 10 } }
}
