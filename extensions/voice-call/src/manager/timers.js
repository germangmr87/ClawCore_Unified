"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.clearMaxDurationTimer = clearMaxDurationTimer;
exports.startMaxDurationTimer = startMaxDurationTimer;
exports.clearTranscriptWaiter = clearTranscriptWaiter;
exports.rejectTranscriptWaiter = rejectTranscriptWaiter;
exports.resolveTranscriptWaiter = resolveTranscriptWaiter;
exports.waitForFinalTranscript = waitForFinalTranscript;
const types_js_1 = require("../types.js");
const store_js_1 = require("./store.js");
function clearMaxDurationTimer(ctx, callId) {
    const timer = ctx.maxDurationTimers.get(callId);
    if (timer) {
        clearTimeout(timer);
        ctx.maxDurationTimers.delete(callId);
    }
}
function startMaxDurationTimer(params) {
    clearMaxDurationTimer(params.ctx, params.callId);
    const maxDurationMs = params.ctx.config.maxDurationSeconds * 1000;
    console.log(`[voice-call] Starting max duration timer (${params.ctx.config.maxDurationSeconds}s) for call ${params.callId}`);
    const timer = setTimeout(async () => {
        params.ctx.maxDurationTimers.delete(params.callId);
        const call = params.ctx.activeCalls.get(params.callId);
        if (call && !types_js_1.TerminalStates.has(call.state)) {
            console.log(`[voice-call] Max duration reached (${params.ctx.config.maxDurationSeconds}s), ending call ${params.callId}`);
            call.endReason = "timeout";
            (0, store_js_1.persistCallRecord)(params.ctx.storePath, call);
            await params.onTimeout(params.callId);
        }
    }, maxDurationMs);
    params.ctx.maxDurationTimers.set(params.callId, timer);
}
function clearTranscriptWaiter(ctx, callId) {
    const waiter = ctx.transcriptWaiters.get(callId);
    if (!waiter) {
        return;
    }
    clearTimeout(waiter.timeout);
    ctx.transcriptWaiters.delete(callId);
}
function rejectTranscriptWaiter(ctx, callId, reason) {
    const waiter = ctx.transcriptWaiters.get(callId);
    if (!waiter) {
        return;
    }
    clearTranscriptWaiter(ctx, callId);
    waiter.reject(new Error(reason));
}
function resolveTranscriptWaiter(ctx, callId, transcript) {
    const waiter = ctx.transcriptWaiters.get(callId);
    if (!waiter) {
        return;
    }
    clearTranscriptWaiter(ctx, callId);
    waiter.resolve(transcript);
}
function waitForFinalTranscript(ctx, callId) {
    // Only allow one in-flight waiter per call.
    rejectTranscriptWaiter(ctx, callId, "Transcript waiter replaced");
    const timeoutMs = ctx.config.transcriptTimeoutMs;
    return new Promise((resolve, reject) => {
        const timeout = setTimeout(() => {
            ctx.transcriptWaiters.delete(callId);
            reject(new Error(`Timed out waiting for transcript after ${timeoutMs}ms`));
        }, timeoutMs);
        ctx.transcriptWaiters.set(callId, { resolve, reject, timeout });
    });
}
