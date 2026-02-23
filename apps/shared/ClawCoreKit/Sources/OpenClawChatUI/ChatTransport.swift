import Foundation

public enum ClawCoreChatTransportEvent: Sendable {
    case health(ok: Bool)
    case tick
    case chat(ClawCoreChatEventPayload)
    case agent(ClawCoreAgentEventPayload)
    case seqGap
}

public protocol ClawCoreChatTransport: Sendable {
    func requestHistory(sessionKey: String) async throws -> ClawCoreChatHistoryPayload
    func sendMessage(
        sessionKey: String,
        message: String,
        thinking: String,
        idempotencyKey: String,
        attachments: [ClawCoreChatAttachmentPayload]) async throws -> ClawCoreChatSendResponse

    func abortRun(sessionKey: String, runId: String) async throws
    func listSessions(limit: Int?) async throws -> ClawCoreChatSessionsListResponse

    func requestHealth(timeoutMs: Int) async throws -> Bool
    func events() -> AsyncStream<ClawCoreChatTransportEvent>

    func setActiveSessionKey(_ sessionKey: String) async throws
}

extension ClawCoreChatTransport {
    public func setActiveSessionKey(_: String) async throws {}

    public func abortRun(sessionKey _: String, runId _: String) async throws {
        throw NSError(
            domain: "ClawCoreChatTransport",
            code: 0,
            userInfo: [NSLocalizedDescriptionKey: "chat.abort not supported by this transport"])
    }

    public func listSessions(limit _: Int?) async throws -> ClawCoreChatSessionsListResponse {
        throw NSError(
            domain: "ClawCoreChatTransport",
            code: 0,
            userInfo: [NSLocalizedDescriptionKey: "sessions.list not supported by this transport"])
    }
}
