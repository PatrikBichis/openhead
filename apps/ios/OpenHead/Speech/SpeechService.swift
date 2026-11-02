import AVFoundation
import Speech

/// The head's voice and ears (protocol 0.4).
///
/// Speaking: each text segment is rendered to audio with `AVSpeechSynthesizer.write`, played on
/// an `AVAudioEngine`, and its loudness drives the mouth 25 times a second, so the mouth moves
/// with the actual sound. Expressions, laughs and gestures run between the segments, and the
/// voice follows the expression (brighter when happy, calmer when sad or focused).
///
/// Listening: the microphone feeds `SFSpeechRecognizer` (on the device when it can); a pause of
/// `silence_ms` ends an utterance. Recognition is muted while the head speaks, and the input
/// uses Apple's voice processing (echo cancellation), so the head does not hear itself.
@MainActor
final class SpeechService {
    unowned let model: AppModel
    /// Listeners of the `speech` topic, per session.
    var listeners: [UUID: (JSONObject) -> Void] = [:]

    private let engine = AVAudioEngine()
    private let player = AVAudioPlayerNode()
    private let synth = AVSpeechSynthesizer()      // text segments
    private let fxSynth = AVSpeechSynthesizer()    // laughs and sighs, so they never cut a render short
    private let outFormat = AVAudioFormat(standardFormatWithSampleRate: 22050, channels: 1)!
    private var speaking: Task<Void, Never>?
    private var utterances = 0
    private var playbackDone: CheckedContinuation<Void, Never>?
    private var playGeneration = 0
    private var mouth: Timer?
    private var clearSubtitle: Task<Void, Never>?

    // listening
    private let mic = MicBridge()
    private var inputActive = false
    private var recognizer: SFSpeechRecognizer?
    private var task: SFSpeechRecognitionTask?
    private var silence: Timer?
    private var heardText = ""
    private var confidence: Double?
    private var restartDelay = 0.2
    private(set) var listening = false
    private var auto = true
    private var silenceS = 1.0
    private var thinking = false

    init(model: AppModel) {
        self.model = model
        engine.attach(player)
        engine.connect(player, to: engine.mainMixerNode, format: outFormat)
        NotificationCenter.default.addObserver(forName: .AVAudioEngineConfigurationChange, object: engine,
                                               queue: .main) { [weak self] _ in
            MainActor.assumeIsolated { self?.engineChanged() }
        }
    }

    static var microphonePermission: String {
        switch AVAudioApplication.shared.recordPermission {
        case .granted: return "granted"
        case .denied: return "denied"
        default: return "not_determined"
        }
    }

    static var recognitionPermission: String {
        switch SFSpeechRecognizer.authorizationStatus() {
        case .authorized: return "granted"
        case .denied, .restricted: return "denied"
        default: return "not_determined"
        }
    }

    // MARK: - speaking

    /// Start an utterance; returns its id at once. Progress goes to the `speech` topic.
    func say(_ segments: [JSONObject], voice: String?, rate: Double?, pitch: Double?, subtitle: Bool,
             interrupt: Bool) -> String {
        utterances += 1
        let id = "u-\(utterances)"
        let previous = speaking
        if interrupt { stopPlayback() }
        let voice = pickVoice(voice)
        speaking = Task { [weak self] in
            if !interrupt { await previous?.value }
            await self?.run(id, segments, voice: voice, rate: rate ?? 1, pitch: pitch ?? 1, subtitle: subtitle)
        }
        return id
    }

    /// Stop speaking (speech.stop, or the last client left).
    func stop() {
        stopPlayback()
    }

    private func stopPlayback() {
        speaking?.cancel()
        synth.stopSpeaking(at: .immediate)
        fxSynth.stopSpeaking(at: .immediate)
        player.stop()
        finishPlayback(playGeneration)
    }

    private func run(_ id: String, _ segments: [JSONObject], voice: AVSpeechSynthesisVoice?, rate: Double,
                     pitch: Double, subtitle: Bool) async {
        emit(["event": "say_start", "utterance_id": id])
        clearSubtitle?.cancel()
        muteForSpeech(true)
        if thinking, segments.first?["emotion"] == nil { setEmotion("neutral", 1) }
        thinking = false

        // The voice of each text segment follows the expression in force there.
        var style = Self.style(for: (try? await model.face.state().emotion) ?? "neutral")
        var plans: [(text: String, rate: Double, pitch: Double)] = []
        for seg in segments {
            if let name = seg["emotion"] as? String { style = Self.style(for: name) }
            if let text = seg["say"] as? String { plans.append((text, rate * style.rate, pitch * style.pitch)) }
        }
        var renders: [Task<[AVAudioPCMBuffer], Never>?] = Array(repeating: nil, count: plans.count)
        func startRender(_ i: Int) {
            guard i < plans.count, renders[i] == nil else { return }
            let p = plans[i]
            renders[i] = Task { await self.render(p.text, with: self.synth, voice: voice, rate: p.rate, pitch: p.pitch) }
        }
        startRender(0)

        var said = false
        var spoken = 0
        for seg in segments {
            if Task.isCancelled { break }
            if let text = seg["say"] as? String {
                startRender(spoken)
                let buffers = await renders[spoken]?.value ?? []
                startRender(spoken + 1)              // render the next one while this one plays
                spoken += 1
                if Task.isCancelled { break }
                if subtitle {
                    try? await model.face.subtitle(said ? " " + text : text, mode: said ? "append" : "replace",
                                                   position: nil, durationMs: nil, mouth: false)
                }
                said = true
                await play(buffers)
            } else if let name = seg["emotion"] as? String {
                emit(["event": "cue", "utterance_id": id, "cue_type": "emotion", "cue": name])
                setEmotion(name, seg["intensity"] as? Double ?? 1)
            } else if let action = seg["action"] as? String {
                emit(["event": "cue", "utterance_id": id, "cue_type": "action", "cue": action])
                await perform(action, seconds: seg["seconds"] as? Double ?? 0.5, voice: voice, rate: rate, pitch: pitch)
            } else if let gesture = seg["gesture"] as? String {
                emit(["event": "cue", "utterance_id": id, "cue_type": "gesture", "cue": gesture])
            }
        }
        let interrupted = Task.isCancelled
        renders.forEach { $0?.cancel() }
        model.face.envelope(0)
        emit(["event": "say_end", "utterance_id": id, "interrupted": interrupted])
        model.logs.log("info", "speech", "\(id) \(interrupted ? "interrupted" : "done")")
        if said, subtitle, !interrupted {
            clearSubtitle = Task { [weak self] in
                try? await Task.sleep(nanoseconds: 2_500_000_000)
                guard !Task.isCancelled else { return }
                try? await self?.model.face.subtitle("", mode: "clear", position: nil, durationMs: nil, mouth: false)
            }
        }
        // Listen again, unless a newer utterance took over (it keeps the microphone muted).
        if id == "u-\(utterances)" { muteForSpeech(false) }
    }

    private func perform(_ action: String, seconds: Double, voice: AVSpeechSynthesisVoice?, rate: Double,
                         pitch: Double) async {
        switch action {
        case "laugh":
            let before = (try? await model.face.state().emotion) ?? "neutral"
            setEmotion("laughing", 1)
            await play(await render("Ha ha ha!", with: fxSynth, voice: voice, rate: rate * 1.15, pitch: pitch * 1.25))
            if !Task.isCancelled { setEmotion(before, 1) }
        case "sigh":
            await play(await render("Haah.", with: fxSynth, voice: voice, rate: rate * 0.8, pitch: pitch * 0.8))
        case "pause":
            try? await Task.sleep(nanoseconds: UInt64(max(0, min(5, seconds)) * 1_000_000_000))
        default:
            try? await model.face.blink()
        }
    }

    private func setEmotion(_ name: String, _ intensity: Double) {
        Task { try? await model.face.setEmotion(name, intensity: intensity, blend: "replace", durationMs: nil) }
    }

    /// Rate and pitch relative to normal for an expression.
    static func style(for emotion: String) -> (rate: Double, pitch: Double) {
        switch emotion {
        case "happy", "excited", "laughing", "proud", "mischievous", "smug", "relieved": return (1.05, 1.12)
        case "surprised", "shocked", "scared", "nervous": return (1.1, 1.15)
        case "sad", "disappointed", "bored", "sleepy", "worried", "embarrassed": return (0.9, 0.9)
        case "angry", "annoyed", "determined", "focused", "skeptical", "suspicious": return (0.95, 0.95)
        default: return (1, 1)
        }
    }

    /// A voice identifier, or the best installed voice for a language (default en-US).
    private func pickVoice(_ wanted: String?) -> AVSpeechSynthesisVoice? {
        let wanted = wanted ?? "en-US"
        if wanted.contains("."), let voice = AVSpeechSynthesisVoice(identifier: wanted) { return voice }
        let matching = AVSpeechSynthesisVoice.speechVoices().filter { $0.language == wanted }
        return matching.max { $0.quality.rawValue < $1.quality.rawValue } ?? AVSpeechSynthesisVoice(language: wanted)
    }

    /// Text to audio in `outFormat`, without playing it. Ends early (with what it has) if cancelled.
    private func render(_ text: String, with synth: AVSpeechSynthesizer, voice: AVSpeechSynthesisVoice?,
                        rate: Double, pitch: Double) async -> [AVAudioPCMBuffer] {
        let utterance = AVSpeechUtterance(string: text)
        utterance.voice = voice
        let base = Double(AVSpeechUtteranceDefaultSpeechRate)
        utterance.rate = Float(min(Double(AVSpeechUtteranceMaximumSpeechRate),
                                   max(Double(AVSpeechUtteranceMinimumSpeechRate), base * rate)))
        utterance.pitchMultiplier = Float(min(2, max(0.5, pitch)))
        let box = RenderBox(format: outFormat)
        return await withTaskCancellationHandler {
            await withCheckedContinuation { (cont: CheckedContinuation<[AVAudioPCMBuffer], Never>) in
                box.continuation = cont
                synth.write(utterance) { buffer in box.take(buffer) }
                // A voice that never sends its closing empty buffer must not hang the utterance.
                DispatchQueue.main.asyncAfter(deadline: .now() + 15) { box.finish() }
            }
        } onCancel: {
            box.finish()
        }
    }

    /// Play the buffers and move the mouth with their loudness; returns when played.
    private func play(_ buffers: [AVAudioPCMBuffer]) async {
        guard !buffers.isEmpty, !Task.isCancelled else { return }
        startOutput()
        let levels = Self.envelope(buffers)
        playGeneration += 1
        let generation = playGeneration
        await withCheckedContinuation { (cont: CheckedContinuation<Void, Never>) in
            playbackDone = cont
            for (i, buffer) in buffers.enumerated() {
                if i == buffers.count - 1 {
                    player.scheduleBuffer(buffer, completionCallbackType: .dataPlayedBack) { [weak self] _ in
                        Task { @MainActor in self?.finishPlayback(generation) }
                    }
                } else {
                    player.scheduleBuffer(buffer, completionHandler: nil)
                }
            }
            player.play()
            startMouth(levels)
        }
        mouth?.invalidate()
        mouth = nil
        model.face.envelope(0)
    }

    /// Ends the current play() — only for the playback it belongs to (a stopped player calls
    /// back late, and must not end the next segment early).
    private func finishPlayback(_ generation: Int) {
        guard generation == playGeneration else { return }
        playbackDone?.resume()
        playbackDone = nil
    }

    private func startMouth(_ levels: [Double]) {
        mouth?.invalidate()
        let start = CACurrentMediaTime()
        mouth = Timer.scheduledTimer(withTimeInterval: 1.0 / 25, repeats: true) { [weak self] timer in
            MainActor.assumeIsolated {
                let i = Int((CACurrentMediaTime() - start) * 25)
                guard i < levels.count else { timer.invalidate(); self?.model.face.envelope(0); return }
                self?.model.face.envelope(levels[i])
            }
        }
    }

    /// Loudness per 40 ms, 0-1, against the 95th percentile (as the Python demo does).
    static func envelope(_ buffers: [AVAudioPCMBuffer]) -> [Double] {
        var samples: [Float] = []
        for b in buffers {
            guard let data = b.floatChannelData?[0] else { continue }
            samples.append(contentsOf: UnsafeBufferPointer(start: data, count: Int(b.frameLength)))
        }
        let step = 22050 / 25
        var rms: [Double] = []
        var i = 0
        while i + step <= samples.count {
            var sum: Float = 0
            for k in i..<(i + step) { sum += samples[k] * samples[k] }
            rms.append(Double(sqrt(sum / Float(step))))
            i += step
        }
        guard !rms.isEmpty else { return [] }
        let peak = max(rms.sorted()[Int(Double(rms.count - 1) * 0.95)], 1e-4)
        return rms.map { $0 > peak * 0.08 ? min(1, pow($0 / peak, 0.8)) : 0 }
    }

    private func startOutput() {
        guard !engine.isRunning else { return }
        if !inputActive {
            try? AVAudioSession.sharedInstance().setCategory(.playback, mode: .spokenAudio)
            try? AVAudioSession.sharedInstance().setActive(true)
        }
        engine.prepare()
        do { try engine.start() } catch {
            model.logs.log("warning", "speech", "audio engine: \(error.localizedDescription)")
        }
    }

    private func engineChanged() {
        // A route change (Bluetooth speaker, headphones) stops the engine; start it again.
        model.logs.log("info", "speech", "audio route changed")
        guard listening || playbackDone != nil else { return }
        engine.prepare()
        try? engine.start()
    }

    // MARK: - listening

    func listen(on: Bool, locale: String, auto: Bool, silenceMs: Int) async throws -> JSONObject {
        guard on else {
            stopListening()
            return ["listening": false]
        }
        self.auto = auto
        silenceS = Double(silenceMs) / 1000
        if listening, let recognizer, recognizer.locale.identifier.replacingOccurrences(of: "_", with: "-") == locale {
            return ["listening": true, "locale": locale, "on_device": recognizer.supportsOnDeviceRecognition]
        }
        guard await AVAudioApplication.requestRecordPermission() else {
            throw LinkError("unsupported", "microphone access denied; allow it in Settings > OpenHead")
        }
        let status = await withCheckedContinuation { (c: CheckedContinuation<SFSpeechRecognizerAuthorizationStatus, Never>) in
            SFSpeechRecognizer.requestAuthorization { c.resume(returning: $0) }
        }
        guard status == .authorized else {
            throw LinkError("unsupported", "speech recognition denied; allow it in Settings > OpenHead")
        }
        guard let rec = SFSpeechRecognizer(locale: Locale(identifier: locale)), rec.isAvailable else {
            throw LinkError("unsupported", "speech recognition for \(locale) is not available")
        }
        task?.cancel()
        task = nil
        recognizer = rec
        try startInput()
        listening = true
        startTask()
        model.logs.log("info", "speech", "listening \(locale), on device: \(rec.supportsOnDeviceRecognition)")
        return ["listening": true, "locale": locale, "on_device": rec.supportsOnDeviceRecognition]
    }

    /// Microphone off (the indicator goes out); speaking keeps working.
    func stopListening() {
        guard listening || inputActive else { return }
        listening = false
        thinking = false
        silence?.invalidate()
        task?.cancel()
        task = nil
        mic.request = nil
        if inputActive {
            let input = engine.inputNode
            input.removeTap(onBus: 0)
            engine.stop()
            try? input.setVoiceProcessingEnabled(false)
            inputActive = false
            try? AVAudioSession.sharedInstance().setCategory(.playback, mode: .spokenAudio)
        }
        model.logs.log("info", "speech", "listening off")
    }

    private func startInput() throws {
        guard !inputActive else { return }
        engine.stop()
        let session = AVAudioSession.sharedInstance()
        try session.setCategory(.playAndRecord, mode: .default, options: [.defaultToSpeaker, .allowBluetoothA2DP])
        try session.setActive(true)
        let input = engine.inputNode
        do { try input.setVoiceProcessingEnabled(true) } catch {
            model.logs.log("warning", "speech", "no echo cancellation: \(error.localizedDescription)")
        }
        let format = input.outputFormat(forBus: 0)
        let bridge = mic
        input.installTap(onBus: 0, bufferSize: 1024, format: format) { buffer, _ in
            bridge.append(buffer)
        }
        engine.prepare()
        try engine.start()
        inputActive = true
    }

    /// While the head speaks, nothing from the microphone reaches recognition.
    private func muteForSpeech(_ speakingNow: Bool) {
        guard listening else { return }
        if speakingNow {
            mic.muted = true
            if !heardText.isEmpty { finishUtterance() }  // someone was talking: keep what they said
            task?.cancel()
            task = nil
            mic.request = nil
        } else if mic.muted {
            mic.muted = false
            startTask()
        }
    }

    private func startTask() {
        guard listening, let recognizer else { return }
        let request = SFSpeechAudioBufferRecognitionRequest()
        request.shouldReportPartialResults = true
        request.requiresOnDeviceRecognition = recognizer.supportsOnDeviceRecognition
        request.addsPunctuation = true
        heardText = ""
        confidence = nil
        mic.request = request
        task = recognizer.recognitionTask(with: request) { [weak self] result, error in
            let text = result?.bestTranscription.formattedString
            let segments = result?.bestTranscription.segments ?? []
            let conf = segments.isEmpty ? nil : Double(segments.map(\.confidence).reduce(0, +)) / Double(segments.count)
            let isFinal = result?.isFinal ?? false
            let failed = error != nil
            Task { @MainActor in self?.recognized(request, text: text, confidence: conf, isFinal: isFinal, failed: failed) }
        }
    }

    private func recognized(_ request: SFSpeechAudioBufferRecognitionRequest, text: String?, confidence: Double?,
                            isFinal: Bool, failed: Bool) {
        guard request === mic.request else { return }        // a stale task
        if let text, !text.isEmpty, text != heardText {
            if heardText.isEmpty, auto { setEmotion("curious", 0.6) }
            heardText = text
            if let confidence, confidence > 0 { self.confidence = confidence }
            emit(["event": "partial", "text": text])
            restartDelay = 0.2
            silence?.invalidate()
            silence = Timer.scheduledTimer(withTimeInterval: silenceS, repeats: false) { [weak self] _ in
                MainActor.assumeIsolated { self?.finishUtterance() }
            }
        }
        if isFinal || failed {
            if !heardText.isEmpty { finishUtterance() } else if failed { restartAfterError() }
        }
    }

    /// The speaker paused: send what they said and listen for the next utterance.
    private func finishUtterance() {
        silence?.invalidate()
        let text = heardText
        heardText = ""
        task?.cancel()
        task = nil
        mic.request = nil
        if !text.isEmpty {
            var event: JSONObject = ["event": "heard", "text": text]
            if let confidence { event["confidence"] = (confidence * 100).rounded() / 100 }
            emit(event)
            model.logs.log("info", "speech", "heard \(text.count) chars")
            if auto {
                setEmotion("thinking", 0.8)
                thinking = true
            }
        }
        if !mic.muted { startTask() }
    }

    private func restartAfterError() {
        task = nil
        mic.request = nil
        let delay = restartDelay
        restartDelay = min(restartDelay * 2, 5)
        Task { [weak self] in
            try? await Task.sleep(nanoseconds: UInt64(delay * 1_000_000_000))
            guard let self, self.listening, !self.mic.muted, self.mic.request == nil else { return }
            self.startTask()
        }
    }

    // MARK: - events

    private func emit(_ event: JSONObject) {
        var payload = event
        payload["sensor_time_s"] = (ProcessInfo.processInfo.systemUptime * 1000).rounded() / 1000
        for listener in listeners.values { listener(payload) }
    }
}

/// Collects a synthesizer's buffers (on its thread), converted to the engine's format.
private final class RenderBox: @unchecked Sendable {
    private let lock = NSLock()
    private let format: AVAudioFormat
    private var converter: AVAudioConverter?
    private var buffers: [AVAudioPCMBuffer] = []
    private var _continuation: CheckedContinuation<[AVAudioPCMBuffer], Never>?

    init(format: AVAudioFormat) { self.format = format }

    var continuation: CheckedContinuation<[AVAudioPCMBuffer], Never>? {
        get { lock.lock(); defer { lock.unlock() }; return _continuation }
        set { lock.lock(); _continuation = newValue; lock.unlock() }
    }

    func take(_ buffer: AVAudioBuffer) {
        guard let pcm = buffer as? AVAudioPCMBuffer else { return }
        if pcm.frameLength == 0 { finish(); return }
        lock.lock()
        defer { lock.unlock() }
        if converter == nil { converter = AVAudioConverter(from: pcm.format, to: format) }
        guard let converter else { return }
        let capacity = AVAudioFrameCount(Double(pcm.frameLength) * format.sampleRate / pcm.format.sampleRate) + 32
        guard let out = AVAudioPCMBuffer(pcmFormat: format, frameCapacity: capacity) else { return }
        var fed = false
        var error: NSError?
        converter.convert(to: out, error: &error) { _, status in
            if fed {
                status.pointee = .noDataNow
                return nil
            }
            fed = true
            status.pointee = .haveData
            return pcm
        }
        if error == nil, out.frameLength > 0 { buffers.append(out) }
    }

    func finish() {
        lock.lock()
        let cont = _continuation
        _continuation = nil
        let result = buffers
        lock.unlock()
        cont?.resume(returning: result)
    }
}

/// Microphone buffers (on the audio thread) to the current recognition request.
private final class MicBridge: @unchecked Sendable {
    private let lock = NSLock()
    private var _request: SFSpeechAudioBufferRecognitionRequest?
    private var _muted = false

    var request: SFSpeechAudioBufferRecognitionRequest? {
        get { lock.lock(); defer { lock.unlock() }; return _request }
        set { lock.lock(); _request = newValue; lock.unlock() }
    }

    var muted: Bool {
        get { lock.lock(); defer { lock.unlock() }; return _muted }
        set { lock.lock(); _muted = newValue; lock.unlock() }
    }

    func append(_ buffer: AVAudioPCMBuffer) {
        lock.lock()
        let request = _muted ? nil : _request
        lock.unlock()
        request?.append(buffer)
    }
}
