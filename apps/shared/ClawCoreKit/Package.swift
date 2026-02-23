// swift-tools-version: 6.2

import PackageDescription

let package = Package(
    name: "ClawCoreKit",
    platforms: [
        .iOS(.v18),
        .macOS(.v15),
    ],
    products: [
        .library(name: "ClawCoreProtocol", targets: ["ClawCoreProtocol"]),
        .library(name: "ClawCoreKit", targets: ["ClawCoreKit"]),
        .library(name: "ClawCoreChatUI", targets: ["ClawCoreChatUI"]),
    ],
    dependencies: [
        .package(url: "https://github.com/steipete/ElevenLabsKit", exact: "0.1.0"),
        .package(url: "https://github.com/gonzalezreal/textual", exact: "0.3.1"),
    ],
    targets: [
        .target(
            name: "ClawCoreProtocol",
            path: "Sources/ClawCoreProtocol",
            swiftSettings: [
                .enableUpcomingFeature("StrictConcurrency"),
            ]),
        .target(
            name: "ClawCoreKit",
            dependencies: [
                "ClawCoreProtocol",
                .product(name: "ElevenLabsKit", package: "ElevenLabsKit"),
            ],
            path: "Sources/ClawCoreKit",
            resources: [
                .process("Resources"),
            ],
            swiftSettings: [
                .enableUpcomingFeature("StrictConcurrency"),
            ]),
        .target(
            name: "ClawCoreChatUI",
            dependencies: [
                "ClawCoreKit",
                .product(
                    name: "Textual",
                    package: "textual",
                    condition: .when(platforms: [.macOS, .iOS])),
            ],
            path: "Sources/ClawCoreChatUI",
            swiftSettings: [
                .enableUpcomingFeature("StrictConcurrency"),
            ]),
        .testTarget(
            name: "ClawCoreKitTests",
            dependencies: ["ClawCoreKit", "ClawCoreChatUI"],
            path: "Tests/ClawCoreKitTests",
            swiftSettings: [
                .enableUpcomingFeature("StrictConcurrency"),
                .enableExperimentalFeature("SwiftTesting"),
            ]),
    ])
