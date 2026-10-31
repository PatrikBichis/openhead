import Foundation
import Network

/// One WebSocket client.
@MainActor
final class Session {
    let id = UUID()
    let connection: NWConnection
    private var seq = 0
    var client: String?
    var token: String?
    /// topic -> (fields filter, timer for periodic topics)
    var subscriptions: [String: (fields: [String]?, timer: Timer?)] = [:]

    init(connection: NWConnection) { self.connection = connection }

    func send(_ type: String, _ fields: JSONObject = [:]) {
        var message = fields
        message["type"] = type
        message["ts"] = nowMs()
        message["seq"] = seq
        seq += 1
        guard let data = try? JSONSerialization.data(withJSONObject: message) else { return }
        let metadata = NWProtocolWebSocket.Metadata(opcode: .text)
        let context = NWConnection.ContentContext(identifier: "message", metadata: [metadata])
        connection.send(content: data, contentContext: context, isComplete: true, completion: .idempotent)
    }

    func error(_ id: String?, _ error: LinkError) {
        var fields: JSONObject = ["code": error.code, "message": String(error.message.prefix(1024))]
        if let id { fields["id"] = id }
        send("error", fields)
    }

    /// Host part of our address as this client sees it (for screenshot URLs).
    var localHost: String {
        if case .hostPort(let host, _) = connection.currentPath?.localEndpoint {
            var text = "\(host)"
            if let percent = text.firstIndex(of: "%") { text = String(text[..<percent]) }
            return text.contains(":") ? "[\(text)]" : text
        }
        return "localhost"
    }
}

/// WebSocket server (Network.framework), advertised over mDNS as `_openhead._tcp`.
@MainActor
final class LinkServer {
    unowned let model: AppModel
    private var listener: NWListener?
    private(set) var sessions: [UUID: Session] = [:]
    let shots = ShotServer()
    private var queueTail: Task<Void, Never>?
    private var listening = false

    init(model: AppModel) { self.model = model }

    var log: LogStore { model.logs }

    func start() {
        let settings = model.settings
        let parameters = NWParameters.tcp
        let websocket = NWProtocolWebSocket.Options()
        websocket.autoReplyPing = true
        websocket.maximumMessageSize = 4 * 1024 * 1024
        parameters.defaultProtocolStack.applicationProtocols.insert(websocket, at: 0)
        guard let port = NWEndpoint.Port(rawValue: UInt16(settings.port)),
              let listener = try? NWListener(using: parameters, on: port) else {
            log.log("error", "link", "cannot listen on port \(settings.port)")
            return
        }
        listener.service = NWListener.Service(name: settings.name, type: "_openhead._tcp")
        listener.stateUpdateHandler = { [weak self] state in
            MainActor.assumeIsolated { self?.listenerState(state) }
        }
        listener.newConnectionHandler = { [weak self] connection in
            MainActor.assumeIsolated { self?.accept(connection) }
        }
        listener.start(queue: .main)
        self.listener = listener
        shots.start(port: settings.port + 1, log: log)
    }

    private func listenerState(_ state: NWListener.State) {
        switch state {
        case .ready:
            listening = true
            log.log("info", "link", "listening on port \(model.settings.port) as \(model.settings.name)")
            publish(ready: true)
        case .failed(let error):
            listening = false
            log.log("error", "link", "listener failed: \(error); restarting")
            publish(ready: false)
            listener?.cancel()
            DispatchQueue.main.asyncAfter(deadline: .now() + 2) { [weak self] in
                MainActor.assumeIsolated { self?.start() }
            }
        case .waiting(let error):
            listening = false
            log.log("warning", "link", "listener waiting: \(error)")
            publish(ready: false)
        default:
            break
        }
    }

    private func publish(ready: Bool) {
        model.linkStateChanged(ready: ready, clients: sessions.values.filter { $0.token != nil }.count)
    }

    private func accept(_ connection: NWConnection) {
        let session = Session(connection: connection)
        sessions[session.id] = session
        connection.stateUpdateHandler = { [weak self, weak session] state in
            MainActor.assumeIsolated {
                guard let self, let session else { return }
                switch state {
                case .ready:
                    self.log.log("info", "link", "connection from \(connection.endpoint)")
                    self.receive(session)
                case .failed, .cancelled:
                    self.close(session)
                default:
                    break
                }
            }
        }
        connection.start(queue: .main)
    }

    private func receive(_ session: Session) {
        session.connection.receiveMessage { [weak self, weak session] data, context, _, error in
            MainActor.assumeIsolated {
                guard let self, let session else { return }
                if let error {
                    self.log.log("info", "link", "\(session.client ?? "client") disconnected: \(error)")
                    self.close(session)
                    return
                }
                let metadata = context?.protocolMetadata(definition: NWProtocolWebSocket.definition)
                    as? NWProtocolWebSocket.Metadata
                if metadata?.opcode == .close {
                    self.close(session)
                    return
                }
                if let data, !data.isEmpty, metadata?.opcode == .text || metadata?.opcode == .binary {
                    self.handle(session, data)
                }
                self.receive(session)
            }
        }
    }

    private func close(_ session: Session) {
        guard sessions[session.id] != nil else { return }
        stopSubscriptions(session)
        sessions[session.id] = nil
        session.connection.cancel()
        log.log("info", "link", "\(session.client ?? "client") disconnected")
        publish(ready: listening)
    }

    func stopSubscriptions(_ session: Session) {
        for (topic, sub) in session.subscriptions {
            sub.timer?.invalidate()
            if topic == "imu" { model.motion.unsubscribe(session.id) }
            if topic == "log" { model.logs.listeners[session.id] = nil }
        }
        session.subscriptions.removeAll()
    }

    // MARK: - messages

    private static let deviceMessages: Set<String> = ["ack", "error", "welcome", "pair_required",
                                                      "imu", "status", "log"]

    private func handle(_ session: Session, _ data: Data) {
        guard let message = (try? JSONSerialization.jsonObject(with: data)) as? JSONObject else {
            session.error(nil, LinkError("invalid_params", "message must be a JSON object"))
            return
        }
        let type = message.string("type") ?? ""
        let id = message.string("id")
        if type != "face.envelope" {
            log.log("info", "link", "recv \(type)" + (id.map { " id=\($0)" } ?? ""), seqRef: message.int("seq"))
        }
        guard !Self.deviceMessages.contains(type), let contract = messageTypes[type] else {
            session.error(id, LinkError("unsupported", "unsupported message type \(type)"))
            return
        }
        do {
            _ = try decodeMessage(contract, data)  // the generated model is the contract
        } catch {
            session.error(id, LinkError("invalid_params", describe(error)))
            return
        }
        switch type {
        case "hello":
            hello(session, message)
        case "pair":
            pair(session, message)
        case _ where session.token == nil:
            session.error(id, LinkError("unauthorized", "send hello with a token, or pair first"))
        case "face.envelope":
            model.face.envelope(message.double("level") ?? 0)
        default:
            // Commands run one at a time, in arrival order.
            let previous = queueTail
            queueTail = Task { [weak self] in
                await previous?.value
                await self?.run(session, type, id, message)
            }
        }
    }

    private func run(_ session: Session, _ type: String, _ id: String?, _ message: JSONObject) async {
        do {
            let result = try await command(session, type, message)
            var fields: JSONObject = ["id": id ?? ""]
            if let result { fields["result"] = result }
            session.send("ack", fields)
        } catch let error as LinkError {
            log.log("warning", "link", "\(type) id=\(id ?? "-"): \(error.code): \(error.message)",
                    seqRef: message.int("seq"))
            session.error(id, error)
        } catch {
            session.error(id, LinkError("invalid_params", error.localizedDescription))
        }
    }

    // MARK: - handshake

    private func hello(_ session: Session, _ message: JSONObject) {
        let version = message.string("protocol_version") ?? ""
        guard version.split(separator: ".").first == protocolVersion.split(separator: ".").first else {
            session.error(nil, LinkError("unsupported", "protocol \(version) not supported; device speaks \(protocolVersion)"))
            return
        }
        let client = message.string("client") ?? "client"
        session.client = client
        let pairing = model.pairing
        if let token = message.string("token"), pairing.isValid(token) {
            session.token = token
            pairing.touch(token)
            log.log("info", "link", "\(client) authenticated")
            welcome(session)
            return
        }
        if pairing.locked {
            session.error(nil, LinkError("rate_limited", "pairing locked after repeated failures"))
            return
        }
        pairing.request(by: client)
        log.log("notice", "link", "pairing requested by \(client); code shown on screen")
        session.send("pair_required", [
            "code_hint": "6-digit code shown on \(model.settings.name)",
            "code_length": 6,
            "expires_in_ms": pairing.expiresInMs,
            "attempts_left": pairing.attemptsLeft,
        ])
    }

    private func pair(_ session: Session, _ message: JSONObject) {
        guard let client = session.client else {
            session.error(nil, LinkError("unauthorized", "send hello first"))
            return
        }
        do {
            session.token = try model.pairing.attempt(message.string("code") ?? "", client: client)
            log.log("info", "link", "paired \(client)")
            welcome(session)
        } catch let error as LinkError {
            session.error(nil, error)
        } catch {}
    }

    private func welcome(_ session: Session) {
        let screen = UIScreenInfo.current
        session.send("welcome", [
            "token": session.token ?? "",
            "protocol_version": protocolVersion,
            "device": [
                "name": model.settings.name,
                "platform": screen.isPad ? "ipados" : "ios",
                "model": DeviceInfo.model,
                "os_version": screen.osVersion,
                "app_version": model.appVersion,
                "screen": ["width": screen.width, "height": screen.height, "scale": screen.scale,
                           "safe_area": screen.safeArea],
            ],
            "capabilities": ["face", "display.image", "display.video", "display.web", "display.subtitle", "imu", "status", "log", "screenshot"],
            "themes": model.themeNames,
            "dev_mode": model.settings.devMode,
        ])
        publish(ready: listening)
    }
}
