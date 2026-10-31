import Foundation

/// Bonjour advertising of `_openhead._tcp`, separate from the WebSocket listener: when the
/// mDNS daemon connection drops (`DefunctConnection`, e.g. as ARKit stops), only the
/// advertisement is published again; the listener and its clients are not touched.
@MainActor
final class Advertiser: NSObject, NetServiceDelegate {
    private var service: NetService?
    private var name = ""
    private var port = 0
    private weak var log: LogStore?

    func start(name: String, port: Int, log: LogStore) {
        self.name = name
        self.port = port
        self.log = log
        publish()
    }

    private func publish() {
        service?.stop()
        let service = NetService(domain: "local.", type: "_openhead._tcp.", name: name, port: Int32(port))
        service.delegate = self
        service.publish()
        self.service = service
    }

    nonisolated func netServiceDidPublish(_ sender: NetService) {
        Task { @MainActor in self.log?.log("info", "link", "advertised as \(self.name) (_openhead._tcp)") }
    }

    nonisolated func netService(_ sender: NetService, didNotPublish errorDict: [String: NSNumber]) {
        Task { @MainActor in
            self.log?.log("warning", "link", "mDNS advertising failed (\(errorDict)); retrying in 3 s")
            try? await Task.sleep(for: .seconds(3))
            self.publish()
        }
    }

    nonisolated func netServiceDidStop(_ sender: NetService) {
        // Stopped by the system (daemon restart) rather than by us: advertise again.
        Task { @MainActor in
            guard self.service === sender else { return }
            self.log?.log("notice", "link", "mDNS advertising stopped; publishing again")
            try? await Task.sleep(for: .seconds(1))
            self.publish()
        }
    }
}
