import SwiftUI

/// The whole screen: display content, the face (full screen or in a corner), the status
/// strip, the pairing code and, after a long press, the settings.
struct RootView: View {
    @EnvironmentObject private var model: AppModel
    @EnvironmentObject private var pairing: Pairing

    var body: some View {
        GeometryReader { geo in
            ZStack {
                Color.black
                content
                // geo.size is the safe area; the face fills the whole screen (edge to edge,
                // under the Dynamic Island), so add the insets back.
                face(in: CGSize(
                    width: geo.size.width + geo.safeAreaInsets.leading + geo.safeAreaInsets.trailing,
                    height: geo.size.height + geo.safeAreaInsets.top + geo.safeAreaInsets.bottom))
                StatusStrip()
                    .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topTrailing)
                    .padding(.top, 8)
                    .padding(.trailing, max(12, geo.safeAreaInsets.trailing))
                if let code = pairing.code {
                    PairingCard(code: code, client: pairing.requester ?? "a client")
                }
                // Touches go nowhere else on a robot head; a long press opens settings.
                Color.clear
                    .contentShape(Rectangle())
                    .onLongPressGesture(minimumDuration: 1.5) { model.showSettings = true }
            }
            .ignoresSafeArea()
        }
        .sheet(isPresented: $model.showSettings) {
            SettingsView().environmentObject(model).environmentObject(model.settings)
                .environmentObject(model.pairing)
        }
    }

    /// Web pages are native and sit below the face's web view, which turns transparent for
    /// them; images, video, the corner face and subtitles are all drawn in that web view.
    @ViewBuilder private var content: some View {
        if case .web(let url) = model.display {
            WebPageView(url: url)
        }
    }

    private func face(in size: CGSize) -> some View {
        FaceView(face: model.face)
            .frame(width: size.width, height: size.height)
            .allowsHitTesting(false)
    }
}

/// Small icons: link state, connected clients, dev mode, thermal warning.
struct StatusStrip: View {
    @EnvironmentObject private var model: AppModel
    @EnvironmentObject private var settings: SettingsStore

    var body: some View {
        HStack(spacing: 10) {
            if !model.linkReady {
                Image(systemName: "wifi.exclamationmark").foregroundStyle(.orange)
            }
            if model.clients > 0 {
                Label("\(model.clients)", systemImage: "person.2.fill")
            }
            if settings.devMode {
                Image(systemName: "hammer.fill")
            }
            if model.thermalState == .serious || model.thermalState == .critical {
                Image(systemName: "thermometer.high").foregroundStyle(.red)
            }
        }
        .font(.caption)
        .foregroundStyle(.white.opacity(0.7))
        .padding(.horizontal, 8)
        .padding(.vertical, 4)
        .background(.black.opacity(0.25), in: Capsule())
        .opacity(model.linkReady && model.clients == 0 && !settings.devMode ? 0 : 1)
    }
}

struct PairingCard: View {
    let code: String
    let client: String

    var body: some View {
        VStack(spacing: 12) {
            Text("Pair \(client)").font(.headline)
            Text(code)
                .font(.system(size: 64, weight: .bold, design: .monospaced))
                .kerning(8)
            Text("Enter this code on the robot. It expires in 60 seconds.")
                .font(.footnote)
                .foregroundStyle(.secondary)
        }
        .padding(28)
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 24))
        .environment(\.colorScheme, .dark)
    }
}
