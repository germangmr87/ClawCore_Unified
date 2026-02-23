"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.persistCallRecord = persistCallRecord;
exports.loadActiveCallsFromStore = loadActiveCallsFromStore;
exports.getCallHistoryFromStore = getCallHistoryFromStore;
const node_fs_1 = __importDefault(require("node:fs"));
const promises_1 = __importDefault(require("node:fs/promises"));
const node_path_1 = __importDefault(require("node:path"));
const types_js_1 = require("../types.js");
function persistCallRecord(storePath, call) {
    const logPath = node_path_1.default.join(storePath, "calls.jsonl");
    const line = `${JSON.stringify(call)}\n`;
    // Fire-and-forget async write to avoid blocking event loop.
    promises_1.default.appendFile(logPath, line).catch((err) => {
        console.error("[voice-call] Failed to persist call record:", err);
    });
}
function loadActiveCallsFromStore(storePath) {
    const logPath = node_path_1.default.join(storePath, "calls.jsonl");
    if (!node_fs_1.default.existsSync(logPath)) {
        return {
            activeCalls: new Map(),
            providerCallIdMap: new Map(),
            processedEventIds: new Set(),
            rejectedProviderCallIds: new Set(),
        };
    }
    const content = node_fs_1.default.readFileSync(logPath, "utf-8");
    const lines = content.split("\n");
    const callMap = new Map();
    for (const line of lines) {
        if (!line.trim()) {
            continue;
        }
        try {
            const call = types_js_1.CallRecordSchema.parse(JSON.parse(line));
            callMap.set(call.callId, call);
        }
        catch {
            // Skip invalid lines.
        }
    }
    const activeCalls = new Map();
    const providerCallIdMap = new Map();
    const processedEventIds = new Set();
    const rejectedProviderCallIds = new Set();
    for (const [callId, call] of callMap) {
        if (types_js_1.TerminalStates.has(call.state)) {
            continue;
        }
        activeCalls.set(callId, call);
        if (call.providerCallId) {
            providerCallIdMap.set(call.providerCallId, callId);
        }
        for (const eventId of call.processedEventIds) {
            processedEventIds.add(eventId);
        }
    }
    return { activeCalls, providerCallIdMap, processedEventIds, rejectedProviderCallIds };
}
async function getCallHistoryFromStore(storePath, limit = 50) {
    const logPath = node_path_1.default.join(storePath, "calls.jsonl");
    try {
        await promises_1.default.access(logPath);
    }
    catch {
        return [];
    }
    const content = await promises_1.default.readFile(logPath, "utf-8");
    const lines = content.trim().split("\n").filter(Boolean);
    const calls = [];
    for (const line of lines.slice(-limit)) {
        try {
            const parsed = types_js_1.CallRecordSchema.parse(JSON.parse(line));
            calls.push(parsed);
        }
        catch {
            // Skip invalid lines.
        }
    }
    return calls;
}
