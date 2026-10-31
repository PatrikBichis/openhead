import CoreMotion
import Foundation

struct MotionSample {
    let q: [Double]      // x, y, z, w
    let gyro: [Double]   // rad/s
    let accel: [Double]  // specific force, m/s^2 (+9.81 on +y at rest upright)
    let frame: String
    let time: Double     // seconds since boot

    var json: JSONObject {
        ["q": q, "gyro": gyro, "accel": accel, "frame": frame, "sensor_time_s": time]
    }
}

/// CoreMotion device motion at the highest rate any subscriber asked for (<= 100 Hz),
/// converted to the protocol's conventions and the configured mounting offset.
@MainActor
final class MotionService {
    private let manager = CMMotionManager()
    private var listeners: [UUID: (rate: Double, last: Double, handler: (MotionSample) -> Void)] = [:]
    var mountOffset: [Double] = [0, 0, 0, 1]

    func subscribe(_ id: UUID, rate: Double, handler: @escaping (MotionSample) -> Void) {
        listeners[id] = (rate, 0, handler)
        restart()
    }

    func unsubscribe(_ id: UUID) {
        listeners[id] = nil
        restart()
    }

    private func restart() {
        guard manager.isDeviceMotionAvailable else { return }
        guard let fastest = listeners.values.map(\.rate).max() else {
            manager.stopDeviceMotionUpdates()
            return
        }
        manager.deviceMotionUpdateInterval = 1 / fastest
        if !manager.isDeviceMotionActive {
            manager.startDeviceMotionUpdates(using: .xArbitraryZVertical, to: .main) { [weak self] motion, _ in
                guard let motion else { return }
                MainActor.assumeIsolated { self?.deliver(motion) }
            }
        }
    }

    private func deliver(_ motion: CMDeviceMotion) {
        let sample = convert(motion)
        for (id, listener) in listeners where sample.time - listener.last >= 0.95 / listener.rate {
            listeners[id]?.last = sample.time
            listener.handler(sample)
        }
    }

    private func convert(_ m: CMDeviceMotion) -> MotionSample {
        let a = m.attitude.quaternion
        var q = [a.x, a.y, a.z, a.w]
        var gyro = [m.rotationRate.x, m.rotationRate.y, m.rotationRate.z]
        // CoreMotion reports acceleration in g with gravity pointing down; the protocol (like ROS)
        // wants specific force, i.e. the opposite sign.
        var accel = [-(m.gravity.x + m.userAcceleration.x) * 9.81,
                     -(m.gravity.y + m.userAcceleration.y) * 9.81,
                     -(m.gravity.z + m.userAcceleration.z) * 9.81]
        let identity = mountOffset == [0, 0, 0, 1]
        if !identity {
            let inverse = [-mountOffset[0], -mountOffset[1], -mountOffset[2], mountOffset[3]]
            q = Quat.multiply(q, mountOffset)
            gyro = Quat.rotate(inverse, gyro)
            accel = Quat.rotate(inverse, accel)
        }
        func round(_ v: [Double], _ places: Double) -> [Double] { v.map { ($0 * places).rounded() / places } }
        return MotionSample(q: round(q, 1e6), gyro: round(gyro, 1e6), accel: round(accel, 1e5),
                            frame: identity ? "device" : "mount", time: m.timestamp)
    }
}

enum Quat {
    static func multiply(_ a: [Double], _ b: [Double]) -> [Double] {
        [a[3] * b[0] + a[0] * b[3] + a[1] * b[2] - a[2] * b[1],
         a[3] * b[1] - a[0] * b[2] + a[1] * b[3] + a[2] * b[0],
         a[3] * b[2] + a[0] * b[1] - a[1] * b[0] + a[2] * b[3],
         a[3] * b[3] - a[0] * b[0] - a[1] * b[1] - a[2] * b[2]]
    }

    static func rotate(_ q: [Double], _ v: [Double]) -> [Double] {
        let r = multiply(multiply(q, [v[0], v[1], v[2], 0]), [-q[0], -q[1], -q[2], q[3]])
        return [r[0], r[1], r[2]]
    }
}
