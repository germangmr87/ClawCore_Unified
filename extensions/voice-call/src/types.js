"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CallRecordSchema = exports.TranscriptEntrySchema = exports.CallDirectionSchema = exports.NormalizedEventSchema = exports.EndReasonSchema = exports.TerminalStates = exports.CallStateSchema = exports.ProviderNameSchema = void 0;
const zod_1 = require("zod");
// -----------------------------------------------------------------------------
// Provider Identifiers
// -----------------------------------------------------------------------------
exports.ProviderNameSchema = zod_1.z.enum(["telnyx", "twilio", "plivo", "mock"]);
// -----------------------------------------------------------------------------
// Call Lifecycle States
// -----------------------------------------------------------------------------
exports.CallStateSchema = zod_1.z.enum([
    // Non-terminal states
    "initiated",
    "ringing",
    "answered",
    "active",
    "speaking",
    "listening",
    // Terminal states
    "completed",
    "hangup-user",
    "hangup-bot",
    "timeout",
    "error",
    "failed",
    "no-answer",
    "busy",
    "voicemail",
]);
exports.TerminalStates = new Set([
    "completed",
    "hangup-user",
    "hangup-bot",
    "timeout",
    "error",
    "failed",
    "no-answer",
    "busy",
    "voicemail",
]);
exports.EndReasonSchema = zod_1.z.enum([
    "completed",
    "hangup-user",
    "hangup-bot",
    "timeout",
    "error",
    "failed",
    "no-answer",
    "busy",
    "voicemail",
]);
// -----------------------------------------------------------------------------
// Normalized Call Events
// -----------------------------------------------------------------------------
const BaseEventSchema = zod_1.z.object({
    id: zod_1.z.string(),
    callId: zod_1.z.string(),
    providerCallId: zod_1.z.string().optional(),
    timestamp: zod_1.z.number(),
    // Optional fields for inbound call detection
    direction: zod_1.z.enum(["inbound", "outbound"]).optional(),
    from: zod_1.z.string().optional(),
    to: zod_1.z.string().optional(),
});
exports.NormalizedEventSchema = zod_1.z.discriminatedUnion("type", [
    BaseEventSchema.extend({
        type: zod_1.z.literal("call.initiated"),
    }),
    BaseEventSchema.extend({
        type: zod_1.z.literal("call.ringing"),
    }),
    BaseEventSchema.extend({
        type: zod_1.z.literal("call.answered"),
    }),
    BaseEventSchema.extend({
        type: zod_1.z.literal("call.active"),
    }),
    BaseEventSchema.extend({
        type: zod_1.z.literal("call.speaking"),
        text: zod_1.z.string(),
    }),
    BaseEventSchema.extend({
        type: zod_1.z.literal("call.speech"),
        transcript: zod_1.z.string(),
        isFinal: zod_1.z.boolean(),
        confidence: zod_1.z.number().min(0).max(1).optional(),
    }),
    BaseEventSchema.extend({
        type: zod_1.z.literal("call.silence"),
        durationMs: zod_1.z.number(),
    }),
    BaseEventSchema.extend({
        type: zod_1.z.literal("call.dtmf"),
        digits: zod_1.z.string(),
    }),
    BaseEventSchema.extend({
        type: zod_1.z.literal("call.ended"),
        reason: exports.EndReasonSchema,
    }),
    BaseEventSchema.extend({
        type: zod_1.z.literal("call.error"),
        error: zod_1.z.string(),
        retryable: zod_1.z.boolean().optional(),
    }),
]);
// -----------------------------------------------------------------------------
// Call Direction
// -----------------------------------------------------------------------------
exports.CallDirectionSchema = zod_1.z.enum(["outbound", "inbound"]);
// -----------------------------------------------------------------------------
// Call Record
// -----------------------------------------------------------------------------
exports.TranscriptEntrySchema = zod_1.z.object({
    timestamp: zod_1.z.number(),
    speaker: zod_1.z.enum(["bot", "user"]),
    text: zod_1.z.string(),
    isFinal: zod_1.z.boolean().default(true),
});
exports.CallRecordSchema = zod_1.z.object({
    callId: zod_1.z.string(),
    providerCallId: zod_1.z.string().optional(),
    provider: exports.ProviderNameSchema,
    direction: exports.CallDirectionSchema,
    state: exports.CallStateSchema,
    from: zod_1.z.string(),
    to: zod_1.z.string(),
    sessionKey: zod_1.z.string().optional(),
    startedAt: zod_1.z.number(),
    answeredAt: zod_1.z.number().optional(),
    endedAt: zod_1.z.number().optional(),
    endReason: exports.EndReasonSchema.optional(),
    transcript: zod_1.z.array(exports.TranscriptEntrySchema).default([]),
    processedEventIds: zod_1.z.array(zod_1.z.string()).default([]),
    metadata: zod_1.z.record(zod_1.z.string(), zod_1.z.unknown()).optional(),
});
