"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.MockProvider = void 0;
const node_crypto_1 = __importDefault(require("node:crypto"));
/**
 * Mock voice call provider for local testing.
 *
 * Events are driven via webhook POST with JSON body:
 * - { events: NormalizedEvent[] } for bulk events
 * - { event: NormalizedEvent } for single event
 */
class MockProvider {
    name = "mock";
    verifyWebhook(_ctx) {
        return { ok: true };
    }
    parseWebhookEvent(ctx) {
        try {
            const payload = JSON.parse(ctx.rawBody);
            const events = [];
            if (Array.isArray(payload.events)) {
                for (const evt of payload.events) {
                    const normalized = this.normalizeEvent(evt);
                    if (normalized) {
                        events.push(normalized);
                    }
                }
            }
            else if (payload.event) {
                const normalized = this.normalizeEvent(payload.event);
                if (normalized) {
                    events.push(normalized);
                }
            }
            return { events, statusCode: 200 };
        }
        catch {
            return { events: [], statusCode: 400 };
        }
    }
    normalizeEvent(evt) {
        if (!evt.type || !evt.callId) {
            return null;
        }
        const base = {
            id: evt.id || node_crypto_1.default.randomUUID(),
            callId: evt.callId,
            providerCallId: evt.providerCallId,
            timestamp: evt.timestamp || Date.now(),
        };
        switch (evt.type) {
            case "call.initiated":
            case "call.ringing":
            case "call.answered":
            case "call.active":
                return { ...base, type: evt.type };
            case "call.speaking": {
                const payload = evt;
                return {
                    ...base,
                    type: evt.type,
                    text: payload.text || "",
                };
            }
            case "call.speech": {
                const payload = evt;
                return {
                    ...base,
                    type: evt.type,
                    transcript: payload.transcript || "",
                    isFinal: payload.isFinal ?? true,
                    confidence: payload.confidence,
                };
            }
            case "call.silence": {
                const payload = evt;
                return {
                    ...base,
                    type: evt.type,
                    durationMs: payload.durationMs || 0,
                };
            }
            case "call.dtmf": {
                const payload = evt;
                return {
                    ...base,
                    type: evt.type,
                    digits: payload.digits || "",
                };
            }
            case "call.ended": {
                const payload = evt;
                return {
                    ...base,
                    type: evt.type,
                    reason: payload.reason || "completed",
                };
            }
            case "call.error": {
                const payload = evt;
                return {
                    ...base,
                    type: evt.type,
                    error: payload.error || "unknown error",
                    retryable: payload.retryable,
                };
            }
            default:
                return null;
        }
    }
    async initiateCall(input) {
        return {
            providerCallId: `mock-${input.callId}`,
            status: "initiated",
        };
    }
    async hangupCall(_input) {
        // No-op for mock
    }
    async playTts(_input) {
        // No-op for mock
    }
    async startListening(_input) {
        // No-op for mock
    }
    async stopListening(_input) {
        // No-op for mock
    }
}
exports.MockProvider = MockProvider;
