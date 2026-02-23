import Foundation

public enum ClawCoreCameraCommand: String, Codable, Sendable {
    case list = "camera.list"
    case snap = "camera.snap"
    case clip = "camera.clip"
}

public enum ClawCoreCameraFacing: String, Codable, Sendable {
    case back
    case front
}

public enum ClawCoreCameraImageFormat: String, Codable, Sendable {
    case jpg
    case jpeg
}

public enum ClawCoreCameraVideoFormat: String, Codable, Sendable {
    case mp4
}

public struct ClawCoreCameraSnapParams: Codable, Sendable, Equatable {
    public var facing: ClawCoreCameraFacing?
    public var maxWidth: Int?
    public var quality: Double?
    public var format: ClawCoreCameraImageFormat?
    public var deviceId: String?
    public var delayMs: Int?

    public init(
        facing: ClawCoreCameraFacing? = nil,
        maxWidth: Int? = nil,
        quality: Double? = nil,
        format: ClawCoreCameraImageFormat? = nil,
        deviceId: String? = nil,
        delayMs: Int? = nil)
    {
        self.facing = facing
        self.maxWidth = maxWidth
        self.quality = quality
        self.format = format
        self.deviceId = deviceId
        self.delayMs = delayMs
    }
}

public struct ClawCoreCameraClipParams: Codable, Sendable, Equatable {
    public var facing: ClawCoreCameraFacing?
    public var durationMs: Int?
    public var includeAudio: Bool?
    public var format: ClawCoreCameraVideoFormat?
    public var deviceId: String?

    public init(
        facing: ClawCoreCameraFacing? = nil,
        durationMs: Int? = nil,
        includeAudio: Bool? = nil,
        format: ClawCoreCameraVideoFormat? = nil,
        deviceId: String? = nil)
    {
        self.facing = facing
        self.durationMs = durationMs
        self.includeAudio = includeAudio
        self.format = format
        self.deviceId = deviceId
    }
}
