"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.initiateCall = initiateCall;
exports.speak = speak;
exports.speakInitialMessage = speakInitialMessage;
exports.continueCall = continueCall;
exports.endCall = endCall;
const node_crypto_1 = __importDefault(require("node:crypto"));
const types_js_1 = require("../types.js");
const voice_mapping_js_1 = require("../voice-mapping.js");
const lookup_js_1 = require("./lookup.js");
const state_js_1 = require("./state.js");
const store_js_1 = require("./store.js");
const timers_js_1 = require("./timers.js");
const twiml_js_1 = require("./twiml.js");
async function initiateCall(ctx, to, sessionKey, options) {
    const opts = typeof options === "string" ? { message: options } : (options ?? {});
    const initialMessage = opts.message;
    const mode = opts.mode ?? ctx.config.outbound.defaultMode;
    if (!ctx.provider) {
        return { callId: "", success: false, error: "Provider not initialized" };
    }
    if (!ctx.webhookUrl) {
        return { callId: "", success: false, error: "Webhook URL not configured" };
    }
    if (ctx.activeCalls.size >= ctx.config.maxConcurrentCalls) {
        return {
            callId: "",
            success: false,
            error: `Maximum concurrent calls (${ctx.config.maxConcurrentCalls}) reached`,
        };
    }
    const callId = node_crypto_1.default.randomUUID();
    const from = ctx.config.fromNumber || (ctx.provider?.name === "mock" ? "+15550000000" : undefined);
    if (!from) {
        return { callId: "", success: false, error: "fromNumber not configured" };
    }
    const callRecord = {
        callId,
        provider: ctx.provider.name,
        direction: "outbound",
        state: "initiated",
        from,
        to,
        sessionKey,
        startedAt: Date.now(),
        transcript: [],
        processedEventIds: [],
        metadata: {
            ...(initialMessage && { initialMessage }),
            mode,
        },
    };
    ctx.activeCalls.set(callId, callRecord);
    (0, store_js_1.persistCallRecord)(ctx.storePath, callRecord);
    try {
        // For notify mode with a message, use inline TwiML with <Say>.
        let inlineTwiml;
        if (mode === "notify" && initialMessage) {
            const pollyVoice = (0, voice_mapping_js_1.mapVoiceToPolly)(ctx.config.tts?.openai?.voice);
            inlineTwiml = (0, twiml_js_1.generateNotifyTwiml)(initialMessage, pollyVoice);
            console.log(`[voice-call] Using inline TwiML for notify mode (voice: ${pollyVoice})`);
        }
        const result = await ctx.provider.initiateCall({
            callId,
            from,
            to,
            webhookUrl: ctx.webhookUrl,
            inlineTwiml,
        });
        callRecord.providerCallId = result.providerCallId;
        ctx.providerCallIdMap.set(result.providerCallId, callId);
        (0, store_js_1.persistCallRecord)(ctx.storePath, callRecord);
        return { callId, success: true };
    }
    catch (err) {
        callRecord.state = "failed";
        callRecord.endedAt = Date.now();
        callRecord.endReason = "failed";
        (0, store_js_1.persistCallRecord)(ctx.storePath, callRecord);
        ctx.activeCalls.delete(callId);
        if (callRecord.providerCallId) {
            ctx.providerCallIdMap.delete(callRecord.providerCallId);
        }
        return {
            callId,
            success: false,
            error: err instanceof Error ? err.message : String(err),
        };
    }
}
async function speak(ctx, callId, text) {
    const call = ctx.activeCalls.get(callId);
    if (!call) {
        return { success: false, error: "Call not found" };
    }
    if (!ctx.provider || !call.providerCallId) {
        return { success: false, error: "Call not connected" };
    }
    if (types_js_1.TerminalStates.has(call.state)) {
        return { success: false, error: "Call has ended" };
    }
    try {
        (0, state_js_1.transitionState)(call, "speaking");
        (0, store_js_1.persistCallRecord)(ctx.storePath, call);
        (0, state_js_1.addTranscriptEntry)(call, "bot", text);
        const voice = ctx.provider?.name === "twilio" ? ctx.config.tts?.openai?.voice : undefined;
        await ctx.provider.playTts({
            callId,
            providerCallId: call.providerCallId,
            text,
            voice,
        });
        return { success: true };
    }
    catch (err) {
        return { success: false, error: err instanceof Error ? err.message : String(err) };
    }
}
async function speakInitialMessage(ctx, providerCallId) {
    const call = (0, lookup_js_1.getCallByProviderCallId)({
        activeCalls: ctx.activeCalls,
        providerCallIdMap: ctx.providerCallIdMap,
        providerCallId,
    });
    if (!call) {
        console.warn(`[voice-call] speakInitialMessage: no call found for ${providerCallId}`);
        return;
    }
    const initialMessage = call.metadata?.initialMessage;
    const mode = call.metadata?.mode ?? "conversation";
    if (!initialMessage) {
        console.log(`[voice-call] speakInitialMessage: no initial message for ${call.callId}`);
        return;
    }
    // Clear so we don't speak it again if the provider reconnects.
    if (call.metadata) {
        delete call.metadata.initialMessage;
        (0, store_js_1.persistCallRecord)(ctx.storePath, call);
    }
    console.log(`[voice-call] Speaking initial message for call ${call.callId} (mode: ${mode})`);
    const result = await speak(ctx, call.callId, initialMessage);
    if (!result.success) {
        console.warn(`[voice-call] Failed to speak initial message: ${result.error}`);
        return;
    }
    if (mode === "notify") {
        const delaySec = ctx.config.outbound.notifyHangupDelaySec;
        console.log(`[voice-call] Notify mode: auto-hangup in ${delaySec}s for call ${call.callId}`);
        setTimeout(async () => {
            const currentCall = ctx.activeCalls.get(call.callId);
            if (currentCall && !types_js_1.TerminalStates.has(currentCall.state)) {
                console.log(`[voice-call] Notify mode: hanging up call ${call.callId}`);
                await endCall(ctx, call.callId);
            }
        }, delaySec * 1000);
    }
}
async function continueCall(ctx, callId, prompt) {
    const call = ctx.activeCalls.get(callId);
    if (!call) {
        return { success: false, error: "Call not found" };
    }
    if (!ctx.provider || !call.providerCallId) {
        return { success: false, error: "Call not connected" };
    }
    if (types_js_1.TerminalStates.has(call.state)) {
        return { success: false, error: "Call has ended" };
    }
    try {
        await speak(ctx, callId, prompt);
        (0, state_js_1.transitionState)(call, "listening");
        (0, store_js_1.persistCallRecord)(ctx.storePath, call);
        await ctx.provider.startListening({ callId, providerCallId: call.providerCallId });
        const transcript = await (0, timers_js_1.waitForFinalTranscript)(ctx, callId);
        // Best-effort: stop listening after final transcript.
        await ctx.provider.stopListening({ callId, providerCallId: call.providerCallId });
        return { success: true, transcript };
    }
    catch (err) {
        return { success: false, error: err instanceof Error ? err.message : String(err) };
    }
    finally {
        (0, timers_js_1.clearTranscriptWaiter)(ctx, callId);
    }
}
async function endCall(ctx, callId) {
    const call = ctx.activeCalls.get(callId);
    if (!call) {
        return { success: false, error: "Call not found" };
    }
    if (!ctx.provider || !call.providerCallId) {
        return { success: false, error: "Call not connected" };
    }
    if (types_js_1.TerminalStates.has(call.state)) {
        return { success: true };
    }
    try {
        await ctx.provider.hangupCall({
            callId,
            providerCallId: call.providerCallId,
            reason: "hangup-bot",
        });
        call.state = "hangup-bot";
        call.endedAt = Date.now();
        call.endReason = "hangup-bot";
        (0, store_js_1.persistCallRecord)(ctx.storePath, call);
        (0, timers_js_1.clearMaxDurationTimer)(ctx, callId);
        (0, timers_js_1.rejectTranscriptWaiter)(ctx, callId, "Call ended: hangup-bot");
        ctx.activeCalls.delete(callId);
        if (call.providerCallId) {
            ctx.providerCallIdMap.delete(call.providerCallId);
        }
        return { success: true };
    }
    catch (err) {
        return { success: false, error: err instanceof Error ? err.message : String(err) };
    }
}
