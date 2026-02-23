import CoreLocation
import Foundation
import ClawCoreKit
import UIKit

protocol CameraServicing: Sendable {
    func listDevices() async -> [CameraController.CameraDeviceInfo]
    func snap(params: ClawCoreCameraSnapParams) async throws -> (format: String, base64: String, width: Int, height: Int)
    func clip(params: ClawCoreCameraClipParams) async throws -> (format: String, base64: String, durationMs: Int, hasAudio: Bool)
}

protocol ScreenRecordingServicing: Sendable {
    func record(
        screenIndex: Int?,
        durationMs: Int?,
        fps: Double?,
        includeAudio: Bool?,
        outPath: String?) async throws -> String
}

@MainActor
protocol LocationServicing: Sendable {
    func authorizationStatus() -> CLAuthorizationStatus
    func accuracyAuthorization() -> CLAccuracyAuthorization
    func ensureAuthorization(mode: ClawCoreLocationMode) async -> CLAuthorizationStatus
    func currentLocation(
        params: ClawCoreLocationGetParams,
        desiredAccuracy: ClawCoreLocationAccuracy,
        maxAgeMs: Int?,
        timeoutMs: Int?) async throws -> CLLocation
}

protocol DeviceStatusServicing: Sendable {
    func status() async throws -> ClawCoreDeviceStatusPayload
    func info() -> ClawCoreDeviceInfoPayload
}

protocol PhotosServicing: Sendable {
    func latest(params: ClawCorePhotosLatestParams) async throws -> ClawCorePhotosLatestPayload
}

protocol ContactsServicing: Sendable {
    func search(params: ClawCoreContactsSearchParams) async throws -> ClawCoreContactsSearchPayload
    func add(params: ClawCoreContactsAddParams) async throws -> ClawCoreContactsAddPayload
}

protocol CalendarServicing: Sendable {
    func events(params: ClawCoreCalendarEventsParams) async throws -> ClawCoreCalendarEventsPayload
    func add(params: ClawCoreCalendarAddParams) async throws -> ClawCoreCalendarAddPayload
}

protocol RemindersServicing: Sendable {
    func list(params: ClawCoreRemindersListParams) async throws -> ClawCoreRemindersListPayload
    func add(params: ClawCoreRemindersAddParams) async throws -> ClawCoreRemindersAddPayload
}

protocol MotionServicing: Sendable {
    func activities(params: ClawCoreMotionActivityParams) async throws -> ClawCoreMotionActivityPayload
    func pedometer(params: ClawCorePedometerParams) async throws -> ClawCorePedometerPayload
}

extension CameraController: CameraServicing {}
extension ScreenRecordService: ScreenRecordingServicing {}
extension LocationService: LocationServicing {}
