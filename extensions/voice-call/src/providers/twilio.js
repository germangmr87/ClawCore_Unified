"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.TwilioProvider = void 0;
const node_crypto_1 = __importDefault(require("node:crypto"));
const telephony_audio_js_1 = require("../telephony-audio.js");
const voice_mapping_js_1 = require("../voice-mapping.js");
const api_js_1 = require("./twilio/api.js");
const webhook_js_1 = require("./twilio/webhook.js");
class TwilioProvider {
    name = "twilio";
    accountSid;
    authToken;
    baseUrl;
    callWebhookUrls = new Map();
    options;
    /** Current public webhook URL (set when tunnel starts or from config) */
    currentPublicUrl = null;
    /** Optional telephony TTS provider for streaming TTS */
    ttsProvider = null;
    /** Optional media stream handler for sending audio */
    mediaStreamHandler = null;
    /** Map of call SID to stream SID for media streams */
    callStreamMap = new Map();
    /** Per-call tokens for media stream authentication */
    streamAuthTokens = new Map();
    /** Storage for TwiML content (for notify mode with URL-based TwiML) */
    twimlStorage = new Map();
    /** Track notify-mode calls to avoid streaming on follow-up callbacks */
    notifyCalls = new Set();
    /**
     * Delete stored TwiML for a given `callId`.
     *
     * We keep TwiML in-memory only long enough to satisfy the initial Twilio
     * webhook request (notify mode). Subsequent webhooks should not reuse it.
     */
    deleteStoredTwiml(callId) {
        this.twimlStorage.delete(callId);
        this.notifyCalls.delete(callId);
    }
    /**
     * Delete stored TwiML for a call, addressed by Twilio's provider call SID.
     *
     * This is used when we only have `providerCallId` (e.g. hangup).
     */
    deleteStoredTwimlForProviderCall(providerCallId) {
        const webhookUrl = this.callWebhookUrls.get(providerCallId);
        if (!webhookUrl) {
            return;
        }
        const callIdMatch = webhookUrl.match(/callId=([^&]+)/);
        if (!callIdMatch) {
            return;
        }
        this.deleteStoredTwiml(callIdMatch[1]);
        this.streamAuthTokens.delete(providerCallId);
    }
    constructor(config, options = {}) {
        if (!config.accountSid) {
            throw new Error("Twilio Account SID is required");
        }
        if (!config.authToken) {
            throw new Error("Twilio Auth Token is required");
        }
        this.accountSid = config.accountSid;
        this.authToken = config.authToken;
        this.baseUrl = `https://api.twilio.com/2010-04-01/Accounts/${this.accountSid}`;
        this.options = options;
        if (options.publicUrl) {
            this.currentPublicUrl = options.publicUrl;
        }
    }
    setPublicUrl(url) {
        this.currentPublicUrl = url;
    }
    getPublicUrl() {
        return this.currentPublicUrl;
    }
    setTTSProvider(provider) {
        this.ttsProvider = provider;
    }
    setMediaStreamHandler(handler) {
        this.mediaStreamHandler = handler;
    }
    registerCallStream(callSid, streamSid) {
        this.callStreamMap.set(callSid, streamSid);
    }
    unregisterCallStream(callSid) {
        this.callStreamMap.delete(callSid);
    }
    isValidStreamToken(callSid, token) {
        const expected = this.streamAuthTokens.get(callSid);
        if (!expected || !token) {
            return false;
        }
        if (expected.length !== token.length) {
            const dummy = Buffer.from(expected);
            node_crypto_1.default.timingSafeEqual(dummy, dummy);
            return false;
        }
        return node_crypto_1.default.timingSafeEqual(Buffer.from(expected), Buffer.from(token));
    }
    /**
     * Clear TTS queue for a call (barge-in).
     * Used when user starts speaking to interrupt current TTS playback.
     */
    clearTtsQueue(callSid) {
        const streamSid = this.callStreamMap.get(callSid);
        if (streamSid && this.mediaStreamHandler) {
            this.mediaStreamHandler.clearTtsQueue(streamSid);
        }
    }
    /**
     * Make an authenticated request to the Twilio API.
     */
    async apiRequest(endpoint, params, options) {
        return await (0, api_js_1.twilioApiRequest)({
            baseUrl: this.baseUrl,
            accountSid: this.accountSid,
            authToken: this.authToken,
            endpoint,
            body: params,
            allowNotFound: options?.allowNotFound,
        });
    }
    /**
     * Verify Twilio webhook signature using HMAC-SHA1.
     *
     * Handles reverse proxy scenarios (Tailscale, nginx, ngrok) by reconstructing
     * the public URL from forwarding headers.
     *
     * @see https://www.twilio.com/docs/usage/webhooks/webhooks-security
     */
    verifyWebhook(ctx) {
        return (0, webhook_js_1.verifyTwilioProviderWebhook)({
            ctx,
            authToken: this.authToken,
            currentPublicUrl: this.currentPublicUrl,
            options: this.options,
        });
    }
    /**
     * Parse Twilio webhook event into normalized format.
     */
    parseWebhookEvent(ctx) {
        try {
            const params = new URLSearchParams(ctx.rawBody);
            const callIdFromQuery = typeof ctx.query?.callId === "string" && ctx.query.callId.trim()
                ? ctx.query.callId.trim()
                : undefined;
            const event = this.normalizeEvent(params, callIdFromQuery);
            // For Twilio, we must return TwiML. Most actions are driven by Calls API updates,
            // so the webhook response is typically a pause to keep the call alive.
            const twiml = this.generateTwimlResponse(ctx);
            return {
                events: event ? [event] : [],
                providerResponseBody: twiml,
                providerResponseHeaders: { "Content-Type": "application/xml" },
                statusCode: 200,
            };
        }
        catch {
            return { events: [], statusCode: 400 };
        }
    }
    /**
     * Parse Twilio direction to normalized format.
     */
    static parseDirection(direction) {
        if (direction === "inbound") {
            return "inbound";
        }
        if (direction === "outbound-api" || direction === "outbound-dial") {
            return "outbound";
        }
        return undefined;
    }
    /**
     * Convert Twilio webhook params to normalized event format.
     */
    normalizeEvent(params, callIdOverride) {
        const callSid = params.get("CallSid") || "";
        const baseEvent = {
            id: node_crypto_1.default.randomUUID(),
            callId: callIdOverride || callSid,
            providerCallId: callSid,
            timestamp: Date.now(),
            direction: TwilioProvider.parseDirection(params.get("Direction")),
            from: params.get("From") || undefined,
            to: params.get("To") || undefined,
        };
        // Handle speech result (from <Gather>)
        const speechResult = params.get("SpeechResult");
        if (speechResult) {
            return {
                ...baseEvent,
                type: "call.speech",
                transcript: speechResult,
                isFinal: true,
                confidence: parseFloat(params.get("Confidence") || "0.9"),
            };
        }
        // Handle DTMF
        const digits = params.get("Digits");
        if (digits) {
            return { ...baseEvent, type: "call.dtmf", digits };
        }
        // Handle call status changes
        const callStatus = params.get("CallStatus");
        switch (callStatus) {
            case "initiated":
                return { ...baseEvent, type: "call.initiated" };
            case "ringing":
                return { ...baseEvent, type: "call.ringing" };
            case "in-progress":
                return { ...baseEvent, type: "call.answered" };
            case "completed":
            case "busy":
            case "no-answer":
            case "failed":
                this.streamAuthTokens.delete(callSid);
                if (callIdOverride) {
                    this.deleteStoredTwiml(callIdOverride);
                }
                return { ...baseEvent, type: "call.ended", reason: callStatus };
            case "canceled":
                this.streamAuthTokens.delete(callSid);
                if (callIdOverride) {
                    this.deleteStoredTwiml(callIdOverride);
                }
                return { ...baseEvent, type: "call.ended", reason: "hangup-bot" };
            default:
                return null;
        }
    }
    static EMPTY_TWIML = '<?xml version="1.0" encoding="UTF-8"?><Response></Response>';
    static PAUSE_TWIML = `<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Pause length="30"/>
</Response>`;
    /**
     * Generate TwiML response for webhook.
     * When a call is answered, connects to media stream for bidirectional audio.
     */
    generateTwimlResponse(ctx) {
        if (!ctx) {
            return TwilioProvider.EMPTY_TWIML;
        }
        const params = new URLSearchParams(ctx.rawBody);
        const type = typeof ctx.query?.type === "string" ? ctx.query.type.trim() : undefined;
        const isStatusCallback = type === "status";
        const callStatus = params.get("CallStatus");
        const direction = params.get("Direction");
        const isOutbound = direction?.startsWith("outbound") ?? false;
        const callSid = params.get("CallSid") || undefined;
        const callIdFromQuery = typeof ctx.query?.callId === "string" && ctx.query.callId.trim()
            ? ctx.query.callId.trim()
            : undefined;
        // Avoid logging webhook params/TwiML (may contain PII).
        // Handle initial TwiML request (when Twilio first initiates the call)
        // Check if we have stored TwiML for this call (notify mode)
        if (callIdFromQuery && !isStatusCallback) {
            const storedTwiml = this.twimlStorage.get(callIdFromQuery);
            if (storedTwiml) {
                // Clean up after serving (one-time use)
                this.deleteStoredTwiml(callIdFromQuery);
                return storedTwiml;
            }
            if (this.notifyCalls.has(callIdFromQuery)) {
                return TwilioProvider.EMPTY_TWIML;
            }
            // Conversation mode: return streaming TwiML immediately for outbound calls.
            if (isOutbound) {
                const streamUrl = callSid ? this.getStreamUrlForCall(callSid) : null;
                return streamUrl ? this.getStreamConnectXml(streamUrl) : TwilioProvider.PAUSE_TWIML;
            }
        }
        // Status callbacks should not receive TwiML.
        if (isStatusCallback) {
            return TwilioProvider.EMPTY_TWIML;
        }
        // Handle subsequent webhook requests (status callbacks, etc.)
        // For inbound calls, answer immediately with stream
        if (direction === "inbound") {
            const streamUrl = callSid ? this.getStreamUrlForCall(callSid) : null;
            return streamUrl ? this.getStreamConnectXml(streamUrl) : TwilioProvider.PAUSE_TWIML;
        }
        // For outbound calls, only connect to stream when call is in-progress
        if (callStatus !== "in-progress") {
            return TwilioProvider.EMPTY_TWIML;
        }
        const streamUrl = callSid ? this.getStreamUrlForCall(callSid) : null;
        return streamUrl ? this.getStreamConnectXml(streamUrl) : TwilioProvider.PAUSE_TWIML;
    }
    /**
     * Get the WebSocket URL for media streaming.
     * Derives from the public URL origin + stream path.
     */
    getStreamUrl() {
        if (!this.currentPublicUrl || !this.options.streamPath) {
            return null;
        }
        // Extract just the origin (host) from the public URL, ignoring any path
        const url = new URL(this.currentPublicUrl);
        const origin = url.origin;
        // Convert https:// to wss:// for WebSocket
        const wsOrigin = origin.replace(/^https:\/\//, "wss://").replace(/^http:\/\//, "ws://");
        // Append the stream path
        const path = this.options.streamPath.startsWith("/")
            ? this.options.streamPath
            : `/${this.options.streamPath}`;
        return `${wsOrigin}${path}`;
    }
    getStreamAuthToken(callSid) {
        const existing = this.streamAuthTokens.get(callSid);
        if (existing) {
            return existing;
        }
        const token = node_crypto_1.default.randomBytes(16).toString("base64url");
        this.streamAuthTokens.set(callSid, token);
        return token;
    }
    getStreamUrlForCall(callSid) {
        const baseUrl = this.getStreamUrl();
        if (!baseUrl) {
            return null;
        }
        const token = this.getStreamAuthToken(callSid);
        const url = new URL(baseUrl);
        url.searchParams.set("token", token);
        return url.toString();
    }
    /**
     * Generate TwiML to connect a call to a WebSocket media stream.
     * This enables bidirectional audio streaming for real-time STT/TTS.
     *
     * @param streamUrl - WebSocket URL (wss://...) for the media stream
     */
    getStreamConnectXml(streamUrl) {
        // Extract token from URL and pass via <Parameter> instead of query string.
        // Twilio strips query params from WebSocket URLs, but delivers <Parameter>
        // values in the "start" message's customParameters field.
        const parsed = new URL(streamUrl);
        const token = parsed.searchParams.get("token");
        parsed.searchParams.delete("token");
        const cleanUrl = parsed.toString();
        const paramXml = token ? `\n      <Parameter name="token" value="${(0, voice_mapping_js_1.escapeXml)(token)}" />` : "";
        return `<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Connect>
    <Stream url="${(0, voice_mapping_js_1.escapeXml)(cleanUrl)}">${paramXml}
    </Stream>
  </Connect>
</Response>`;
    }
    /**
     * Initiate an outbound call via Twilio API.
     * If inlineTwiml is provided, uses that directly (for notify mode).
     * Otherwise, uses webhook URL for dynamic TwiML.
     */
    async initiateCall(input) {
        const url = new URL(input.webhookUrl);
        url.searchParams.set("callId", input.callId);
        // Create separate URL for status callbacks (required by Twilio)
        const statusUrl = new URL(input.webhookUrl);
        statusUrl.searchParams.set("callId", input.callId);
        statusUrl.searchParams.set("type", "status"); // Differentiate from TwiML requests
        // Store TwiML content if provided (for notify mode)
        // We now serve it from the webhook endpoint instead of sending inline
        if (input.inlineTwiml) {
            this.twimlStorage.set(input.callId, input.inlineTwiml);
            this.notifyCalls.add(input.callId);
        }
        // Build request params - always use URL-based TwiML.
        // Twilio silently ignores `StatusCallback` when using the inline `Twiml` parameter.
        const params = {
            To: input.to,
            From: input.from,
            Url: url.toString(), // TwiML serving endpoint
            StatusCallback: statusUrl.toString(), // Separate status callback endpoint
            StatusCallbackEvent: ["initiated", "ringing", "answered", "completed"],
            Timeout: "30",
        };
        const result = await this.apiRequest("/Calls.json", params);
        this.callWebhookUrls.set(result.sid, url.toString());
        return {
            providerCallId: result.sid,
            status: result.status === "queued" ? "queued" : "initiated",
        };
    }
    /**
     * Hang up a call via Twilio API.
     */
    async hangupCall(input) {
        this.deleteStoredTwimlForProviderCall(input.providerCallId);
        this.callWebhookUrls.delete(input.providerCallId);
        this.streamAuthTokens.delete(input.providerCallId);
        await this.apiRequest(`/Calls/${input.providerCallId}.json`, { Status: "completed" }, { allowNotFound: true });
    }
    /**
     * Play TTS audio via Twilio.
     *
     * Two modes:
     * 1. Core TTS + Media Streams: If TTS provider and media stream are available,
     *    generates audio via core TTS and streams it through WebSocket (preferred).
     * 2. TwiML <Say>: Falls back to Twilio's native TTS with Polly voices.
     *    Note: This may not work on all Twilio accounts.
     */
    async playTts(input) {
        // Try telephony TTS via media stream first (if configured)
        const streamSid = this.callStreamMap.get(input.providerCallId);
        if (this.ttsProvider && this.mediaStreamHandler && streamSid) {
            try {
                await this.playTtsViaStream(input.text, streamSid);
                return;
            }
            catch (err) {
                console.warn(`[voice-call] Telephony TTS failed, falling back to Twilio <Say>:`, err instanceof Error ? err.message : err);
                // Fall through to TwiML <Say> fallback
            }
        }
        // Fall back to TwiML <Say> (may not work on all accounts)
        const webhookUrl = this.callWebhookUrls.get(input.providerCallId);
        if (!webhookUrl) {
            throw new Error("Missing webhook URL for this call (provider state not initialized)");
        }
        console.warn("[voice-call] Using TwiML <Say> fallback - telephony TTS not configured or media stream not active");
        const pollyVoice = (0, voice_mapping_js_1.mapVoiceToPolly)(input.voice);
        const twiml = `<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="${pollyVoice}" language="${input.locale || "en-US"}">${(0, voice_mapping_js_1.escapeXml)(input.text)}</Say>
  <Gather input="speech" speechTimeout="auto" action="${(0, voice_mapping_js_1.escapeXml)(webhookUrl)}" method="POST">
    <Say>.</Say>
  </Gather>
</Response>`;
        await this.apiRequest(`/Calls/${input.providerCallId}.json`, {
            Twiml: twiml,
        });
    }
    /**
     * Play TTS via core TTS and Twilio Media Streams.
     * Generates audio with core TTS, converts to mu-law, and streams via WebSocket.
     * Uses a queue to serialize playback and prevent overlapping audio.
     */
    async playTtsViaStream(text, streamSid) {
        if (!this.ttsProvider || !this.mediaStreamHandler) {
            throw new Error("TTS provider and media stream handler required");
        }
        // Stream audio in 20ms chunks (160 bytes at 8kHz mu-law)
        const CHUNK_SIZE = 160;
        const CHUNK_DELAY_MS = 20;
        const handler = this.mediaStreamHandler;
        const ttsProvider = this.ttsProvider;
        await handler.queueTts(streamSid, async (signal) => {
            // Generate audio with core TTS (returns mu-law at 8kHz)
            const muLawAudio = await ttsProvider.synthesizeForTelephony(text);
            for (const chunk of (0, telephony_audio_js_1.chunkAudio)(muLawAudio, CHUNK_SIZE)) {
                if (signal.aborted) {
                    break;
                }
                handler.sendAudio(streamSid, chunk);
                // Pace the audio to match real-time playback
                await new Promise((resolve) => setTimeout(resolve, CHUNK_DELAY_MS));
                if (signal.aborted) {
                    break;
                }
            }
            if (!signal.aborted) {
                // Send a mark to track when audio finishes
                handler.sendMark(streamSid, `tts-${Date.now()}`);
            }
        });
    }
    /**
     * Start listening for speech via Twilio <Gather>.
     */
    async startListening(input) {
        const webhookUrl = this.callWebhookUrls.get(input.providerCallId);
        if (!webhookUrl) {
            throw new Error("Missing webhook URL for this call (provider state not initialized)");
        }
        const twiml = `<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Gather input="speech" speechTimeout="auto" language="${input.language || "en-US"}" action="${(0, voice_mapping_js_1.escapeXml)(webhookUrl)}" method="POST">
  </Gather>
</Response>`;
        await this.apiRequest(`/Calls/${input.providerCallId}.json`, {
            Twiml: twiml,
        });
    }
    /**
     * Stop listening - for Twilio this is a no-op as <Gather> auto-ends.
     */
    async stopListening(_input) {
        // Twilio's <Gather> automatically stops on speech end
        // No explicit action needed
    }
}
exports.TwilioProvider = TwilioProvider;
