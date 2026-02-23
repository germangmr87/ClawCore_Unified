import Foundation

public enum ClawCoreDeviceCommand: String, Codable, Sendable {
    case status = "device.status"
    case info = "device.info"
}

public enum ClawCoreBatteryState: String, Codable, Sendable {
    case unknown
    case unplugged
    case charging
    case full
}

public enum ClawCoreThermalState: String, Codable, Sendable {
    case nominal
    case fair
    case serious
    case critical
}

public enum ClawCoreNetworkPathStatus: String, Codable, Sendable {
    case satisfied
    case unsatisfied
    case requiresConnection
}

public enum ClawCoreNetworkInterfaceType: String, Codable, Sendable {
    case wifi
    case cellular
    case wired
    case other
}

public struct ClawCoreBatteryStatusPayload: Codable, Sendable, Equatable {
    public var level: Double?
    public var state: ClawCoreBatteryState
    public var lowPowerModeEnabled: Bool

    public init(level: Double?, state: ClawCoreBatteryState, lowPowerModeEnabled: Bool) {
        self.level = level
        self.state = state
        self.lowPowerModeEnabled = lowPowerModeEnabled
    }
}

public struct ClawCoreThermalStatusPayload: Codable, Sendable, Equatable {
    public var state: ClawCoreThermalState

    public init(state: ClawCoreThermalState) {
        self.state = state
    }
}

public struct ClawCoreStorageStatusPayload: Codable, Sendable, Equatable {
    public var totalBytes: Int64
    public var freeBytes: Int64
    public var usedBytes: Int64

    public init(totalBytes: Int64, freeBytes: Int64, usedBytes: Int64) {
        self.totalBytes = totalBytes
        self.freeBytes = freeBytes
        self.usedBytes = usedBytes
    }
}

public struct ClawCoreNetworkStatusPayload: Codable, Sendable, Equatable {
    public var status: ClawCoreNetworkPathStatus
    public var isExpensive: Bool
    public var isConstrained: Bool
    public var interfaces: [ClawCoreNetworkInterfaceType]

    public init(
        status: ClawCoreNetworkPathStatus,
        isExpensive: Bool,
        isConstrained: Bool,
        interfaces: [ClawCoreNetworkInterfaceType])
    {
        self.status = status
        self.isExpensive = isExpensive
        self.isConstrained = isConstrained
        self.interfaces = interfaces
    }
}

public struct ClawCoreDeviceStatusPayload: Codable, Sendable, Equatable {
    public var battery: ClawCoreBatteryStatusPayload
    public var thermal: ClawCoreThermalStatusPayload
    public var storage: ClawCoreStorageStatusPayload
    public var network: ClawCoreNetworkStatusPayload
    public var uptimeSeconds: Double

    public init(
        battery: ClawCoreBatteryStatusPayload,
        thermal: ClawCoreThermalStatusPayload,
        storage: ClawCoreStorageStatusPayload,
        network: ClawCoreNetworkStatusPayload,
        uptimeSeconds: Double)
    {
        self.battery = battery
        self.thermal = thermal
        self.storage = storage
        self.network = network
        self.uptimeSeconds = uptimeSeconds
    }
}

public struct ClawCoreDeviceInfoPayload: Codable, Sendable, Equatable {
    public var deviceName: String
    public var modelIdentifier: String
    public var systemName: String
    public var systemVersion: String
    public var appVersion: String
    public var appBuild: String
    public var locale: String

    public init(
        deviceName: String,
        modelIdentifier: String,
        systemName: String,
        systemVersion: String,
        appVersion: String,
        appBuild: String,
        locale: String)
    {
        self.deviceName = deviceName
        self.modelIdentifier = modelIdentifier
        self.systemName = systemName
        self.systemVersion = systemVersion
        self.appVersion = appVersion
        self.appBuild = appBuild
        self.locale = locale
    }
}
