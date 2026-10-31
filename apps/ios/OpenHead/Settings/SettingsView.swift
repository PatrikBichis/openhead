import SwiftUI

struct SettingsView: View {
    @EnvironmentObject private var model: AppModel
    @EnvironmentObject private var settings: SettingsStore
    @EnvironmentObject private var pairing: Pairing
    @Environment(\.dismiss) private var dismiss

    private struct Mount: Hashable {
        let name: String
        let quaternion: [Double]
    }

    private let mounts = [
        Mount(name: "As is", quaternion: [0, 0, 0, 1]),
        Mount(name: "Rotated 90°", quaternion: [0, 0, 0.7071068, 0.7071068]),
        Mount(name: "Rotated 180°", quaternion: [0, 0, 1, 0]),
        Mount(name: "Rotated 270°", quaternion: [0, 0, -0.7071068, 0.7071068]),
    ]

    var body: some View {
        NavigationStack {
            Form {
                Section("Connection") {
                    LabeledContent("Name") {
                        TextField("Name", text: $settings.name).multilineTextAlignment(.trailing)
                    }
                    LabeledContent("Port") {
                        TextField("Port", value: $settings.port, format: .number.grouping(.never))
                            .keyboardType(.numberPad)
                            .multilineTextAlignment(.trailing)
                    }
                    LabeledContent("Addresses", value: DeviceInfo.ipAddresses.joined(separator: ", "))
                    Text("Name and port changes apply after restarting the app.")
                        .font(.footnote).foregroundStyle(.secondary)
                }
                Section("Head") {
                    Picker("Theme when offline", selection: $settings.offlineTheme) {
                        ForEach(model.themeNames, id: \.self) { Text($0).tag($0) }
                    }
                    Picker("IMU mounting", selection: $settings.mountOffset) {
                        ForEach(mounts, id: \.self) { Text($0.name).tag($0.quaternion) }
                    }
                }
                Section {
                    Toggle("Dev mode", isOn: $settings.devMode)
                } footer: {
                    Text("Allows screenshots, logs, diagnostics and changing settings over the network.")
                }
                Section("Paired clients") {
                    if pairing.clients.isEmpty {
                        Text("None").foregroundStyle(.secondary)
                    }
                    ForEach(pairing.clients.sorted { $0.value.lastSeen > $1.value.lastSeen }, id: \.key) { entry in
                        VStack(alignment: .leading) {
                            Text(entry.value.name)
                            Text("Last seen \(Date(timeIntervalSince1970: entry.value.lastSeen).formatted(.relative(presentation: .named)))")
                                .font(.caption).foregroundStyle(.secondary)
                        }
                        .swipeActions {
                            Button("Revoke", role: .destructive) { pairing.revoke(entry.key) }
                        }
                    }
                }
                Section("About") {
                    LabeledContent("Version", value: model.appVersion)
                    LabeledContent("Protocol", value: protocolVersion)
                    LabeledContent("Device", value: DeviceInfo.model)
                }
            }
            .navigationTitle("OpenHead")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar { Button("Done") { dismiss() } }
        }
    }
}
