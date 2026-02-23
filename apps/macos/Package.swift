// swift-tools-version: 6.2
// Package manifest for the ClawCore macOS companion (menu bar app + IPC library).

import PackageDescription

let package = Package(
    name: "ClawCore",
    platforms: [
        .macOS(.v15),
    ],
    products: [
        .library(name: "ClawCoreIPC", targets: ["ClawCoreIPC"]),
        .library(name: "ClawCoreDiscovery", targets: ["ClawCoreDiscovery"]),
        .executable(name: "ClawCore", targets: ["ClawCore"]),
        .executable(name: "clawcore-mac", targets: ["ClawCoreMacCLI"]),
    ],
    dependencies: [
        .package(url: "https://github.com/orchetect/MenuBarExtraAccess", exact: "1.2.2"),
        .package(url: "https://github.com/swiftlang/swift-subprocess.git", from: "0.1.0"),
        .package(url: "https://github.com/apple/swift-log.git", from: "1.8.0"),
        .package(url: "https://github.com/sparkle-project/Sparkle", from: "2.8.1"),
        .package(url: "https://github.com/steipete/Peekaboo.git", branch: "main"),
        .package(path: "../shared/ClawCoreKit"),
        .package(path: "../../Swabble"),
    ],
    targets: [
        .target(
            name: "ClawCoreIPC",
            dependencies: [],
            swiftSettings: [
                .enableUpcomingFeature("StrictConcurrency"),
            ]),
        .target(
            name: "ClawCoreDiscovery",
            dependencies: [
                .product(name: "ClawCoreKit", package: "ClawCoreKit"),
            ],
            path: "Sources/ClawCoreDiscovery",
            swiftSettings: [
                .enableUpcomingFeature("StrictConcurrency"),
            ]),
        .executableTarget(
            name: "ClawCore",
            dependencies: [
                "ClawCoreIPC",
                "ClawCoreDiscovery",
                .product(name: "ClawCoreKit", package: "ClawCoreKit"),
                .product(name: "ClawCoreChatUI", package: "ClawCoreKit"),
                .product(name: "ClawCoreProtocol", package: "ClawCoreKit"),
                .product(name: "SwabbleKit", package: "swabble"),
                .product(name: "MenuBarExtraAccess", package: "MenuBarExtraAccess"),
                .product(name: "Subprocess", package: "swift-subprocess"),
                .product(name: "Logging", package: "swift-log"),
                .product(name: "Sparkle", package: "Sparkle"),
                .product(name: "PeekabooBridge", package: "Peekaboo"),
                .product(name: "PeekabooAutomationKit", package: "Peekaboo"),
            ],
            exclude: [
                "Resources/Info.plist",
            ],
            resources: [
                .copy("Resources/ClawCore.icns"),
                .copy("Resources/DeviceModels"),
            ],
            swiftSettings: [
                .enableUpcomingFeature("StrictConcurrency"),
            ]),
        .executableTarget(
            name: "ClawCoreMacCLI",
            dependencies: [
                "ClawCoreDiscovery",
                .product(name: "ClawCoreKit", package: "ClawCoreKit"),
                .product(name: "ClawCoreProtocol", package: "ClawCoreKit"),
            ],
            path: "Sources/ClawCoreMacCLI",
            swiftSettings: [
                .enableUpcomingFeature("StrictConcurrency"),
            ]),
        .testTarget(
            name: "ClawCoreIPCTests",
            dependencies: [
                "ClawCoreIPC",
                "ClawCore",
                "ClawCoreDiscovery",
                .product(name: "ClawCoreProtocol", package: "ClawCoreKit"),
                .product(name: "SwabbleKit", package: "swabble"),
            ],
            swiftSettings: [
                .enableUpcomingFeature("StrictConcurrency"),
                .enableExperimentalFeature("SwiftTesting"),
            ]),
    ])
