import CoreLocation

/// Compass heading for the HUD ({heading}, the compass widget). Heading needs no location
/// permission; on devices without a magnetometer it stays nil.
@MainActor
final class HeadingService: NSObject, CLLocationManagerDelegate {
    private let manager = CLLocationManager()
    private(set) var heading: Double?

    func start() {
        guard CLLocationManager.headingAvailable() else { return }
        manager.delegate = self
        manager.headingFilter = 1
        manager.startUpdatingHeading()
    }

    func stop() {
        manager.stopUpdatingHeading()
        heading = nil
    }

    nonisolated func locationManager(_ manager: CLLocationManager, didUpdateHeading newHeading: CLHeading) {
        let value = newHeading.trueHeading >= 0 ? newHeading.trueHeading : newHeading.magneticHeading
        Task { @MainActor in self.heading = value }
    }
}
