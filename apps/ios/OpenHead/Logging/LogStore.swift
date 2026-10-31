import Foundation
import os

func nowMs() -> Int64 { Int64(Date().timeIntervalSince1970 * 1000) }

struct LogEntry {
    let timeMs: Int64
    let level: String
    let subsystem: String
    let message: String
    let seqRef: Int?

    var json: [String: Any] {
        var d: [String: Any] = ["time_ms": timeMs, "level": level, "subsystem": subsystem,
                                "message": message]
        if let seqRef { d["seq_ref"] = seqRef }
        return d
    }
}

/// Structured log: OSLog per subsystem, a 2000-line ring buffer for `system.logs`,
/// and listeners for the `log` topic.
@MainActor
final class LogStore {
    static let levels = ["debug", "info", "notice", "warning", "error", "fault"]
    private(set) var entries: [LogEntry] = []
    private let capacity = 2000
    private var loggers: [String: Logger] = [:]
    var listeners: [UUID: (LogEntry) -> Void] = [:]

    func log(_ level: String, _ subsystem: String, _ message: String, seqRef: Int? = nil) {
        let entry = LogEntry(timeMs: nowMs(), level: level, subsystem: subsystem,
                             message: String(message.prefix(4096)), seqRef: seqRef)
        entries.append(entry)
        if entries.count > capacity { entries.removeFirst(entries.count - capacity) }
        let logger = loggers[subsystem] ?? Logger(subsystem: "se.bichis.openhead", category: subsystem)
        loggers[subsystem] = logger
        switch level {
        case "debug": logger.debug("\(message, privacy: .public)")
        case "info": logger.info("\(message, privacy: .public)")
        case "notice": logger.notice("\(message, privacy: .public)")
        case "warning": logger.warning("\(message, privacy: .public)")
        case "error": logger.error("\(message, privacy: .public)")
        default: logger.fault("\(message, privacy: .public)")
        }
        for listener in listeners.values { listener(entry) }
    }

    func recent(_ n: Int, minLevel: String?) -> [LogEntry] {
        let floor = LogStore.levels.firstIndex(of: minLevel ?? "debug") ?? 0
        let matching = entries.filter { (LogStore.levels.firstIndex(of: $0.level) ?? 0) >= floor }
        return Array(matching.suffix(n))
    }
}
