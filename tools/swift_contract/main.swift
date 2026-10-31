// Contract test for the generated Swift models: every example message in
// protocol/examples must decode into its model and encode back to the same JSON.
//
//   swiftc -swift-version 6 -o contract apps/ios/OpenHead/Protocol/*.swift tools/swift_contract/main.swift
//   ./contract protocol/examples
import Foundation

func roundTrip<T: Codable>(_: T.Type, _ data: Data) throws -> Data {
    try JSONEncoder().encode(JSONDecoder().decode(T.self, from: data))
}

let dir = URL(fileURLWithPath: CommandLine.arguments[1])
let files = try FileManager.default
    .contentsOfDirectory(at: dir, includingPropertiesForKeys: nil)
    .filter { $0.pathExtension == "json" }
    .sorted { $0.lastPathComponent < $1.lastPathComponent }

var failures = 0
var covered = Set<String>()
for file in files {
    let data = try Data(contentsOf: file)
    let original = try JSONSerialization.jsonObject(with: data) as! NSDictionary
    let type = original["type"] as! String
    guard let model = messageTypes[type] else {
        print("FAIL \(file.lastPathComponent): no Swift model for type \(type)")
        failures += 1
        continue
    }
    do {
        let encoded = try roundTrip(model, data)
        let back = try JSONSerialization.jsonObject(with: encoded) as! NSDictionary
        if back.isEqual(original) {
            covered.insert(type)
        } else {
            print("FAIL \(file.lastPathComponent): round trip differs\n  in:  \(original)\n  out: \(back)")
            failures += 1
        }
    } catch {
        print("FAIL \(file.lastPathComponent): \(error)")
        failures += 1
    }
}
let missing = Set(messageTypes.keys).subtracting(covered)
if !missing.isEmpty {
    print("FAIL no passing example for: \(missing.sorted().joined(separator: ", "))")
    failures += 1
}
print("\(files.count) examples, \(messageTypes.count) types, protocol \(protocolVersion): \(failures == 0 ? "OK" : "FAILED")")
exit(failures == 0 ? 0 : 1)
