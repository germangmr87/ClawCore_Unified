"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.CallManager = void 0;
const node_fs_1 = __importDefault(require("node:fs"));
const node_os_1 = __importDefault(require("node:os"));
const node_path_1 = __importDefault(require("node:path"));
const events_js_1 = require("./manager/events.js");
const lookup_js_1 = require("./manager/lookup.js");
const outbound_js_1 = require("./manager/outbound.js");
const store_js_1 = require("./manager/store.js");
const utils_js_1 = require("./utils.js");
function resolveDefaultStoreBase(config, storePath) {
    const rawOverride = storePath?.trim() || config.store?.trim();
    if (rawOverride) {
        return (0, utils_js_1.resolveUserPath)(rawOverride);
    }
    const preferred = node_path_1.default.join(node_os_1.default.homedir(), ".clawcore", "voice-calls");
    const candidates = [preferred].map((dir) => (0, utils_js_1.resolveUserPath)(dir));
    const existing = candidates.find((dir) => {
        try {
            return node_fs_1.default.existsSync(node_path_1.default.join(dir, "calls.jsonl")) || node_fs_1.default.existsSync(dir);
        }
        catch {
            return false;
        }
    }) ?? (0, utils_js_1.resolveUserPath)(preferred);
    return existing;
}
/**
 * Manages voice calls: state ownership and delegation to manager helper modules.
 */
class CallManager {
    activeCalls = new Map();
    providerCallIdMap = new Map();
    processedEventIds = new Set();
    rejectedProviderCallIds = new Set();
    provider = null;
    config;
    storePath;
    webhookUrl = null;
    transcriptWaiters = new Map();
    maxDurationTimers = new Map();
    constructor(config, storePath) {
        this.config = config;
        this.storePath = resolveDefaultStoreBase(config, storePath);
    }
    /**
     * Initialize the call manager with a provider.
     */
    initialize(provider, webhookUrl) {
        this.provider = provider;
        this.webhookUrl = webhookUrl;
        node_fs_1.default.mkdirSync(this.storePath, { recursive: true });
        const persisted = (0, store_js_1.loadActiveCallsFromStore)(this.storePath);
        this.activeCalls = persisted.activeCalls;
        this.providerCallIdMap = persisted.providerCallIdMap;
        this.processedEventIds = persisted.processedEventIds;
        this.rejectedProviderCallIds = persisted.rejectedProviderCallIds;
    }
    /**
     * Get the current provider.
     */
    getProvider() {
        return this.provider;
    }
    /**
     * Initiate an outbound call.
     */
    async initiateCall(to, sessionKey, options) {
        return (0, outbound_js_1.initiateCall)(this.getContext(), to, sessionKey, options);
    }
    /**
     * Speak to user in an active call.
     */
    async speak(callId, text) {
        return (0, outbound_js_1.speak)(this.getContext(), callId, text);
    }
    /**
     * Speak the initial message for a call (called when media stream connects).
     */
    async speakInitialMessage(providerCallId) {
        return (0, outbound_js_1.speakInitialMessage)(this.getContext(), providerCallId);
    }
    /**
     * Continue call: speak prompt, then wait for user's final transcript.
     */
    async continueCall(callId, prompt) {
        return (0, outbound_js_1.continueCall)(this.getContext(), callId, prompt);
    }
    /**
     * End an active call.
     */
    async endCall(callId) {
        return (0, outbound_js_1.endCall)(this.getContext(), callId);
    }
    getContext() {
        return {
            activeCalls: this.activeCalls,
            providerCallIdMap: this.providerCallIdMap,
            processedEventIds: this.processedEventIds,
            rejectedProviderCallIds: this.rejectedProviderCallIds,
            provider: this.provider,
            config: this.config,
            storePath: this.storePath,
            webhookUrl: this.webhookUrl,
            transcriptWaiters: this.transcriptWaiters,
            maxDurationTimers: this.maxDurationTimers,
            onCallAnswered: (call) => {
                this.maybeSpeakInitialMessageOnAnswered(call);
            },
        };
    }
    /**
     * Process a webhook event.
     */
    processEvent(event) {
        (0, events_js_1.processEvent)(this.getContext(), event);
    }
    maybeSpeakInitialMessageOnAnswered(call) {
        const initialMessage = typeof call.metadata?.initialMessage === "string" ? call.metadata.initialMessage.trim() : "";
        if (!initialMessage) {
            return;
        }
        if (!this.provider || !call.providerCallId) {
            return;
        }
        // Twilio has provider-specific state for speaking (<Say> fallback) and can
        // fail for inbound calls; keep existing Twilio behavior unchanged.
        if (this.provider.name === "twilio") {
            return;
        }
        void this.speakInitialMessage(call.providerCallId);
    }
    /**
     * Get an active call by ID.
     */
    getCall(callId) {
        return this.activeCalls.get(callId);
    }
    /**
     * Get an active call by provider call ID (e.g., Twilio CallSid).
     */
    getCallByProviderCallId(providerCallId) {
        return (0, lookup_js_1.getCallByProviderCallId)({
            activeCalls: this.activeCalls,
            providerCallIdMap: this.providerCallIdMap,
            providerCallId,
        });
    }
    /**
     * Get all active calls.
     */
    getActiveCalls() {
        return Array.from(this.activeCalls.values());
    }
    /**
     * Get call history (from persisted logs).
     */
    async getCallHistory(limit = 50) {
        return (0, store_js_1.getCallHistoryFromStore)(this.storePath, limit);
    }
}
exports.CallManager = CallManager;
