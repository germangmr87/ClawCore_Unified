"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.transitionState = transitionState;
exports.addTranscriptEntry = addTranscriptEntry;
const types_js_1 = require("../types.js");
const ConversationStates = new Set(["speaking", "listening"]);
const StateOrder = [
    "initiated",
    "ringing",
    "answered",
    "active",
    "speaking",
    "listening",
];
function transitionState(call, newState) {
    // No-op for same state or already terminal.
    if (call.state === newState || types_js_1.TerminalStates.has(call.state)) {
        return;
    }
    // Terminal states can always be reached from non-terminal.
    if (types_js_1.TerminalStates.has(newState)) {
        call.state = newState;
        return;
    }
    // Allow cycling between speaking and listening (multi-turn conversations).
    if (ConversationStates.has(call.state) && ConversationStates.has(newState)) {
        call.state = newState;
        return;
    }
    // Only allow forward transitions in state order.
    const currentIndex = StateOrder.indexOf(call.state);
    const newIndex = StateOrder.indexOf(newState);
    if (newIndex > currentIndex) {
        call.state = newState;
    }
}
function addTranscriptEntry(call, speaker, text) {
    const entry = {
        timestamp: Date.now(),
        speaker,
        text,
        isFinal: true,
    };
    call.transcript.push(entry);
}
