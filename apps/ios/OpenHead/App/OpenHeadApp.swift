import SwiftUI

@main
struct OpenHeadApp: App {
    @StateObject private var model = AppModel()

    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(model)
                .environmentObject(model.pairing)
                .environmentObject(model.settings)
                .statusBarHidden(true)
                .persistentSystemOverlays(.hidden)
                .onAppear { model.start() }
        }
    }
}
