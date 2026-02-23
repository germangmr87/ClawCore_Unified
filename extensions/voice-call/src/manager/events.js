"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.processEvent = processEvent;
const node_crypto_1 = __importDefault(require("node:crypto"));
const allowlist_js_1 = require("../allowlist.js");
const lookup_js_1 = require("./lookup.js");
const outbound_js_1 = require("./outbound.js");
const state_js_1 = require("./state.js");
const store_js_1 = require("./store.js");
const timers_js_1 = require("./timers.js");
function shouldAcceptInbound(config, from) {
    const { inboundPolicy: policy, allowFrom } = config;
    switch (policy) {
        case "disabled":
            console.log("[voice-call] Inbound call rejected: policy is disabled");
            return false;
        case "open":
            console.log("[voice-call] Inbound call accepted: policy is open");
            return true;
        case "allowlist":
        case "pairing": {
            const normalized = (0, allowlist_js_1.normalizePhoneNumber)(from);
            if (!normalized) {
                console.log("[voice-call] Inbound call rejected: missing caller ID");
                return false;
            }
            const allowed = (0, allowlist_js_1.isAllowlistedCaller)(normalized, allowFrom);
            const status = allowed ? "accepted" : "rejected";
            console.log(`[voice-call] Inbound call ${status}: ${from} ${allowed ? "is in" : "not in"} allowlist`);
            return allowed;
        }
        default:
            return false;
    }
}
function createInboundCall(params) {
    const callId = node_crypto_1.default.randomUUID();
    const callRecord = {
        callId,
        providerCallId: params.providerCallId,
        provider: params.ctx.provider?.name || "twilio",
        direction: "inbound",
        state: "ringing",
        from: params.from,
        to: params.to,
        startedAt: Date.now(),
        transcript: [],
        processedEventIds: [],
        metadata: {
            initialMessage: params.ctx.config.inboundGreeting || "Hello! How can I help you today?",
        },
    };
    params.ctx.activeCalls.set(callId, callRecord);
    params.ctx.providerCallIdMap.set(params.providerCallId, callId);
    (0, store_js_1.persistCallRecord)(params.ctx.storePath, callRecord);
    console.log(`[voice-call] Created inbound call record: ${callId} from ${params.from}`);
    return callRecord;
}
function processEvent(ctx, event) {
    if (ctx.processedEventIds.has(event.id)) {
        return;
    }
    ctx.processedEventIds.add(event.id);
    let call = (0, lookup_js_1.findCall)({
        activeCalls: ctx.activeCalls,
        providerCallIdMap: ctx.providerCallIdMap,
        callIdOrProviderCallId: event.callId,
    });
    if (!call && event.direction === "inbound" && event.providerCallId) {
        if (!shouldAcceptInbound(ctx.config, event.from)) {
            const pid = event.providerCallId;
            if (!ctx.provider) {
                console.warn(`[voice-call] Inbound call rejected by policy but no provider to hang up (providerCallId: ${pid}, from: ${event.from}); call will time out on provider side.`);
                return;
            }
            if (ctx.rejectedProviderCallIds.has(pid)) {
                return;
            }
            ctx.rejectedProviderCallIds.add(pid);
            const callId = event.callId ?? pid;
            console.log(`[voice-call] Rejecting inbound call by policy: ${pid}`);
            void ctx.provider
                .hangupCall({
                callId,
                providerCallId: pid,
                reason: "hangup-bot",
            })
                .catch((err) => {
                const message = err instanceof Error ? err.message : String(err);
                console.warn(`[voice-call] Failed to reject inbound call ${pid}:`, message);
            });
            return;
        }
        call = createInboundCall({
            ctx,
            providerCallId: event.providerCallId,
            from: event.from || "unknown",
            to: event.to || ctx.config.fromNumber || "unknown",
        });
        // Normalize event to internal ID for downstream consumers.
        event.callId = call.callId;
    }
    if (!call) {
        return;
    }
    if (event.providerCallId && event.providerCallId !== call.providerCallId) {
        const previousProviderCallId = call.providerCallId;
        call.providerCallId = event.providerCallId;
        ctx.providerCallIdMap.set(event.providerCallId, call.callId);
        if (previousProviderCallId) {
            const mapped = ctx.providerCallIdMap.get(previousProviderCallId);
            if (mapped === call.callId) {
                ctx.providerCallIdMap.delete(previousProviderCallId);
            }
        }
    }
    call.processedEventIds.push(event.id);
    switch (event.type) {
        case "call.initiated":
            (0, state_js_1.transitionState)(call, "initiated");
            break;
        case "call.ringing":
            (0, state_js_1.transitionState)(call, "ringing");
            break;
        case "call.answered":
            call.answeredAt = event.timestamp;
            (0, state_js_1.transitionState)(call, "answered");
            (0, timers_js_1.startMaxDurationTimer)({
                ctx,
                callId: call.callId,
                onTimeout: async (callId) => {
                    await (0, outbound_js_1.endCall)(ctx, callId);
                },
            });
            ctx.onCallAnswered?.(call);
            break;
        case "call.active":
            (0, state_js_1.transitionState)(call, "active");
            break;
        case "call.speaking":
            (0, state_js_1.transitionState)(call, "speaking");
            break;
        case "call.speech":
            if (event.isFinal) {
                (0, state_js_1.addTranscriptEntry)(call, "user", event.transcript);
                (0, timers_js_1.resolveTranscriptWaiter)(ctx, call.callId, event.transcript);
            }
            (0, state_js_1.transitionState)(call, "listening");
            break;
        case "call.ended":
            call.endedAt = event.timestamp;
            call.endReason = event.reason;
            (0, state_js_1.transitionState)(call, event.reason);
            (0, timers_js_1.clearMaxDurationTimer)(ctx, call.callId);
            (0, timers_js_1.rejectTranscriptWaiter)(ctx, call.callId, `Call ended: ${event.reason}`);
            ctx.activeCalls.delete(call.callId);
            if (call.providerCallId) {
                ctx.providerCallIdMap.delete(call.providerCallId);
            }
            break;
        case "call.error":
            if (!event.retryable) {
                call.endedAt = event.timestamp;
                call.endReason = "error";
                (0, state_js_1.transitionState)(call, "error");
                (0, timers_js_1.clearMaxDurationTimer)(ctx, call.callId);
                (0, timers_js_1.rejectTranscriptWaiter)(ctx, call.callId, `Call error: ${event.error}`);
                ctx.activeCalls.delete(call.callId);
                if (call.providerCallId) {
                    ctx.providerCallIdMap.delete(call.providerCallId);
                }
            }
            break;
    }
    (0, store_js_1.persistCallRecord)(ctx.storePath, call);
}
