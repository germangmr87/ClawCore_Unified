import Foundation
import Testing
@testable import ClawCore

@Suite(.serialized)
struct ClawCoreConfigFileTests {
    @Test
    func configPathRespectsEnvOverride() async {
        let override = FileManager().temporaryDirectory
            .appendingPathComponent("clawcore-config-\(UUID().uuidString)")
            .appendingPathComponent("clawcore.json")
            .path

        await TestIsolation.withEnvValues(["CLAWCORE_CONFIG_PATH": override]) {
            #expect(ClawCoreConfigFile.url().path == override)
        }
    }

    @MainActor
    @Test
    func remoteGatewayPortParsesAndMatchesHost() async {
        let override = FileManager().temporaryDirectory
            .appendingPathComponent("clawcore-config-\(UUID().uuidString)")
            .appendingPathComponent("clawcore.json")
            .path

        await TestIsolation.withEnvValues(["CLAWCORE_CONFIG_PATH": override]) {
            ClawCoreConfigFile.saveDict([
                "gateway": [
                    "remote": [
                        "url": "ws://gateway.ts.net:19999",
                    ],
                ],
            ])
            #expect(ClawCoreConfigFile.remoteGatewayPort() == 19999)
            #expect(ClawCoreConfigFile.remoteGatewayPort(matchingHost: "gateway.ts.net") == 19999)
            #expect(ClawCoreConfigFile.remoteGatewayPort(matchingHost: "gateway") == 19999)
            #expect(ClawCoreConfigFile.remoteGatewayPort(matchingHost: "other.ts.net") == nil)
        }
    }

    @MainActor
    @Test
    func setRemoteGatewayUrlPreservesScheme() async {
        let override = FileManager().temporaryDirectory
            .appendingPathComponent("clawcore-config-\(UUID().uuidString)")
            .appendingPathComponent("clawcore.json")
            .path

        await TestIsolation.withEnvValues(["CLAWCORE_CONFIG_PATH": override]) {
            ClawCoreConfigFile.saveDict([
                "gateway": [
                    "remote": [
                        "url": "wss://old-host:111",
                    ],
                ],
            ])
            ClawCoreConfigFile.setRemoteGatewayUrl(host: "new-host", port: 2222)
            let root = ClawCoreConfigFile.loadDict()
            let url = ((root["gateway"] as? [String: Any])?["remote"] as? [String: Any])?["url"] as? String
            #expect(url == "wss://new-host:2222")
        }
    }

    @Test
    func stateDirOverrideSetsConfigPath() async {
        let dir = FileManager().temporaryDirectory
            .appendingPathComponent("clawcore-state-\(UUID().uuidString)", isDirectory: true)
            .path

        await TestIsolation.withEnvValues([
            "CLAWCORE_CONFIG_PATH": nil,
            "CLAWCORE_STATE_DIR": dir,
        ]) {
            #expect(ClawCoreConfigFile.stateDirURL().path == dir)
            #expect(ClawCoreConfigFile.url().path == "\(dir)/clawcore.json")
        }
    }

    @MainActor
    @Test
    func saveDictAppendsConfigAuditLog() async throws {
        let stateDir = FileManager().temporaryDirectory
            .appendingPathComponent("clawcore-state-\(UUID().uuidString)", isDirectory: true)
        let configPath = stateDir.appendingPathComponent("clawcore.json")
        let auditPath = stateDir.appendingPathComponent("logs/config-audit.jsonl")

        defer { try? FileManager().removeItem(at: stateDir) }

        try await TestIsolation.withEnvValues([
            "CLAWCORE_STATE_DIR": stateDir.path,
            "CLAWCORE_CONFIG_PATH": configPath.path,
        ]) {
            ClawCoreConfigFile.saveDict([
                "gateway": ["mode": "local"],
            ])

            let configData = try Data(contentsOf: configPath)
            let configRoot = try JSONSerialization.jsonObject(with: configData) as? [String: Any]
            #expect((configRoot?["meta"] as? [String: Any]) != nil)

            let rawAudit = try String(contentsOf: auditPath, encoding: .utf8)
            let lines = rawAudit
                .split(whereSeparator: \.isNewline)
                .map(String.init)
            #expect(!lines.isEmpty)
            guard let last = lines.last else {
                Issue.record("Missing config audit line")
                return
            }
            let auditRoot = try JSONSerialization.jsonObject(with: Data(last.utf8)) as? [String: Any]
            #expect(auditRoot?["source"] as? String == "macos-clawcore-config-file")
            #expect(auditRoot?["event"] as? String == "config.write")
            #expect(auditRoot?["result"] as? String == "success")
            #expect(auditRoot?["configPath"] as? String == configPath.path)
        }
    }
}
