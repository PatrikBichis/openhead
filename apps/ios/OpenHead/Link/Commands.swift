import Foundation
import UIKit

extension LinkServer {
    /// Execute one validated command; returns `ack.result` (nil for none).
    func command(_ session: Session, _ type: String, _ m: JSONObject) async throws -> JSONObject? {
        let face = model.face
        switch type {
        case "subscribe":
            return subscribe(session, m)

        case "unsubscribe":
            if let topic = m.string("topic"), let sub = session.subscriptions.removeValue(forKey: topic) {
                sub.timer?.invalidate()
                if topic == "imu" { model.motion.unsubscribe(session.id) }
                if topic == "log" { model.logs.listeners[session.id] = nil }
            }
            return nil

        case "face.set_theme":
            try await face.setTheme(m.string("name") ?? "", transitionMs: m.int("transition_ms") ?? 300)
            return nil

        case "face.set_emotion":
            try await face.setEmotion(m.string("name") ?? "neutral",
                                      intensity: min(1, max(0, m.double("intensity") ?? 1)),
                                      blend: m.string("blend") ?? "replace",
                                      durationMs: m.int("duration_ms"))
            return nil

        case "face.look_at" where m.string("frame") == "face":
            guard model.mode != "idle" else {
                throw LinkError("invalid_params", "look_at frame face needs mode capture or sensing")
            }
            try await face.followFace(m.int("face_id"))
            model.schedule("gaze", m.int("duration_ms")) { [weak face] in
                Task { try? await face?.followFace(nil, stop: true) }
            }
            return nil

        case "face.look_at":
            try await face.followFace(nil, stop: true)
            let x: Double
            let y: Double
            if m.string("frame") == "screen" {
                guard let mx = m.double("x"), let my = m.double("y") else {
                    throw LinkError("invalid_params", "screen frame needs x and y")
                }
                (x, y) = (mx, my)
            } else {
                guard let yaw = m.double("yaw"), let pitch = m.double("pitch") else {
                    throw LinkError("invalid_params", "head frame needs yaw and pitch")
                }
                // +yaw is the head's left, which is the viewer's right.
                (x, y) = (max(-1, min(1, yaw / 45)), max(-1, min(1, pitch / 45)))
            }
            try await face.setGaze(x: max(-1, min(1, x)), y: max(-1, min(1, y)))
            model.schedule("gaze", m.int("duration_ms")) { [weak face] in
                Task { try? await face?.setGaze(x: 0, y: 0) }
            }
            return nil

        case "face.blink":
            try await face.blink()
            return nil

        case "face.list":
            let state = try await face.state()
            let themes = try await face.listThemes().map { theme -> JSONObject in
                var t: JSONObject = [:]
                for key in ["name", "version", "title", "expressions", "extras"] { t[key] = theme[key] }
                return t
            }
            let huds = try await face.listHuds()
            return ["active": state.theme, "themes": themes, "huds": huds]

        case "display.show":
            let content = m.string("content") ?? "face"
            let overlay = m.string("overlay") ?? "none"
            let duration = m.int("duration_ms")
            let source = m.string("source") ?? ""
            switch content {
            case "image":
                // The web layer loads it (http(s), data: URIs incl. SVG and GIF); a bad source
                // throws before the screen changes.
                try await model.show(.image, source: source, overlay: overlay, durationMs: duration)
            case "video":
                guard source.hasPrefix("http://") || source.hasPrefix("https://") else {
                    throw LinkError("invalid_params", "video content needs an http(s) URL")
                }
                try await model.show(.video, source: source, overlay: overlay, loop: m.bool("loop") ?? false,
                                     muted: m.bool("muted") ?? false, durationMs: duration)
            case "camera":
                if model.mode != "capture" { try await model.setMode("capture") }
                try await model.show(.camera, overlay: overlay, hud: m.string("hud") ?? "hunter", durationMs: duration)
            case "web":
                guard source.hasPrefix("http://") || source.hasPrefix("https://"), let url = URL(string: source) else {
                    throw LinkError("invalid_params", "web content needs an http(s) URL")
                }
                try await model.show(.web(url), source: source, overlay: overlay, durationMs: duration)
            default:
                try await model.show(.face, overlay: "none", durationMs: nil)
            }
            return nil

        case "display.clear":
            try await model.show(.face, overlay: "none", durationMs: nil)
            return nil

        case "display.hud":
            var extras: JSONObject = [:]
            for key in ["values", "blocks", "widgets", "clear"] { extras[key] = m[key] }
            try await face.hudExtras(extras)
            return nil

        case "display.subtitle":
            let mode = m.string("mode") ?? "replace"
            try await model.face.subtitle(m.string("text") ?? "", mode: mode, position: m.string("position"),
                                          durationMs: m.int("duration_ms"), mouth: m.bool("mouth") ?? false)
            model.logs.log("info", "display", "subtitle \(mode)")
            return nil

        case "system.status":
            return await model.status(rttMs: nil)

        case "system.screenshot":
            try requireDev(type)
            let scale = min(1, max(0.05, m.double("scale") ?? 1))
            let (png, width, height) = try await Screenshot.capture(model: model, scale: scale)
            if m.string("delivery") == "inline" {
                return ["width": width, "height": height, "png_base64": png.base64EncodedString()]
            }
            let shot = shots.add(png, token: session.token ?? "")
            return ["width": width, "height": height,
                    "url": "http://\(session.localHost):\(model.settings.port + 1)/shot/\(shot).png",
                    "expires_ms": 60000]

        case "system.logs":
            try requireDev(type)
            let entries = model.logs.recent(m.int("n") ?? 100, minLevel: m.string("level"))
            return ["entries": entries.map(\.json)]

        case "system.diagnostics":
            try requireDev(type)
            return model.diagnostics()

        case "system.settings":
            if m.string("action") == "set" {
                try requireDev(type)
                guard let key = m.string("key"), let value = m["value"] else {
                    throw LinkError("invalid_params", "set needs key and value")
                }
                try model.settings.set(key, value)
                model.motion.mountOffset = model.settings.mountOffset
                model.logs.log("info", "settings", "\(key) set")
            }
            return ["settings": model.settings.all]

        case "mode.set":
            let mode = m.string("mode") ?? "idle"
            if mode == "sensing", !model.supportsSensing {
                throw LinkError("unsupported", "ARKit world tracking is not supported on this device")
            }
            try await model.setMode(mode)
            return nil

        case "mode.get":
            return ["mode": model.mode]

        default:
            throw LinkError("unsupported", "\(type) is not implemented")
        }
    }

    private func requireDev(_ type: String) throws {
        guard model.settings.devMode else { throw LinkError("dev_mode_required", "\(type) needs dev mode") }
    }

    private func subscribe(_ session: Session, _ m: JSONObject) -> JSONObject {
        let topic = m.string("topic") ?? ""
        let fields = m["fields"] as? [String]
        if let old = session.subscriptions.removeValue(forKey: topic) {
            old.timer?.invalidate()
        }
        func filtered(_ payload: JSONObject) -> JSONObject {
            guard let fields else { return payload }
            return payload.filter { fields.contains($0.key) }
        }
        switch topic {
        case "imu":
            let rate = min(m.double("rate_hz") ?? 50, 100)
            model.motion.mountOffset = model.settings.mountOffset
            model.motion.subscribe(session.id, rate: rate) { [weak session] sample in
                session?.send("imu", filtered(sample.json))
            }
            session.subscriptions[topic] = (fields, nil)
            return ["topic": topic, "rate_hz": rate]
        case "faces", "pose":
            let maximum = topic == "faces" ? 15.0 : 60.0
            let rate = min(m.double("rate_hz") ?? (topic == "faces" ? 15 : 30), maximum)
            let timer = Timer.scheduledTimer(withTimeInterval: 1 / rate, repeats: true) { [weak self, weak session] _ in
                MainActor.assumeIsolated {
                    guard let self, let session else { return }
                    let payload = topic == "faces" ? self.model.facesPayload : self.model.ar.latestPose
                    if let payload { session.send(topic, filtered(payload)) }  // nothing in other modes
                }
            }
            session.subscriptions[topic] = (fields, timer)
            return ["topic": topic, "rate_hz": rate]
        case "status":
            let rate = min(m.double("rate_hz") ?? 1, 1)
            let timer = Timer.scheduledTimer(withTimeInterval: 1 / rate, repeats: true) { [weak self, weak session] _ in
                MainActor.assumeIsolated {
                    guard let self, let session else { return }
                    Task {
                        let status = await self.model.status(rttMs: nil)
                        session.send("status", filtered(status))
                    }
                }
            }
            session.subscriptions[topic] = (fields, timer)
            return ["topic": topic, "rate_hz": rate]
        default:  // log: event driven
            model.logs.listeners[session.id] = { [weak session] entry in
                session?.send("log", filtered(entry.json))
            }
            session.subscriptions[topic] = (fields, nil)
            return ["topic": topic, "rate_hz": 0]
        }
    }
}
