import Foundation

public enum ClawCoreLocationMode: String, Codable, Sendable, CaseIterable {
    case off
    case whileUsing
    case always
}
