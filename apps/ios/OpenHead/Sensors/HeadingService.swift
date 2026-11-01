import CoreLocation
import UIKit

/// Compass heading for the HUD ({heading}, the compass widget) and the `env` topic. Runs while
/// anyone uses it. Heading needs no location permission; with it, a coarse location fix lets
/// CoreLocation report true north. On devices without a magnetometer it stays nil.
@MainActor
final class HeadingService: NSObject, CLLocationManagerDelegate {
    private let manager = CLLocationManager()
    private var users: Set<String> = []
    private(set) var heading: Double?
    private(set) var isTrue = false
    private(set) var accuracy: Double?

    func start(_ user: String) {
        users.insert(user)
        guard users.count == 1, CLLocationManager.headingAvailable() else { return }
        manager.delegate = self
        manager.headingFilter = 1
        manager.headingOrientation = Self.mountedOrientation
        if [.authorizedWhenInUse, .authorizedAlways].contains(manager.authorizationStatus) {
            manager.desiredAccuracy = kCLLocationAccuracyKilometer  // enough for true north
            manager.startUpdatingLocation()
        }
        manager.startUpdatingHeading()
    }

    func stop(_ user: String) {
        guard users.remove(user) != nil, users.isEmpty else { return }
        manager.stopUpdatingHeading()
        manager.stopUpdatingLocation()
        heading = nil
        accuracy = nil
    }

    /// The heading of the screen's top edge as the head is mounted (landscape).
    private static var mountedOrientation: CLDeviceOrientation {
        let interface = UIApplication.shared.connectedScenes
            .compactMap { ($0 as? UIWindowScene)?.interfaceOrientation }.first ?? .landscapeRight
        switch interface {
        case .landscapeLeft: return .landscapeRight  // interface left = device turned right
        case .landscapeRight: return .landscapeLeft
        case .portraitUpsideDown: return .portraitUpsideDown
        default: return .portrait
        }
    }

    nonisolated func locationManager(_ manager: CLLocationManager, didUpdateHeading newHeading: CLHeading) {
        let isTrue = newHeading.trueHeading >= 0
        let value = isTrue ? newHeading.trueHeading : newHeading.magneticHeading
        let accuracy = newHeading.headingAccuracy
        Task { @MainActor in
            self.heading = value
            self.isTrue = isTrue
            self.accuracy = accuracy >= 0 ? accuracy : nil
        }
    }

    nonisolated func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {}
}
