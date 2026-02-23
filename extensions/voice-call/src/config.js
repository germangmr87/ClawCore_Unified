"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.VoiceCallConfigSchema = exports.VoiceCallStreamingConfigSchema = exports.OutboundConfigSchema = exports.CallModeSchema = exports.VoiceCallWebhookSecurityConfigSchema = exports.VoiceCallTunnelConfigSchema = exports.VoiceCallTailscaleConfigSchema = exports.VoiceCallServeConfigSchema = exports.TtsProviderSchema = exports.TtsModeSchema = exports.TtsConfigSchema = exports.TtsAutoSchema = exports.SttConfigSchema = exports.PlivoConfigSchema = exports.TwilioConfigSchema = exports.TelnyxConfigSchema = exports.InboundPolicySchema = exports.E164Schema = void 0;
exports.resolveVoiceCallConfig = resolveVoiceCallConfig;
exports.validateProviderConfig = validateProviderConfig;
const plugin_sdk_1 = require("clawcore/plugin-sdk");
Object.defineProperty(exports, "TtsAutoSchema", { enumerable: true, get: function () { return plugin_sdk_1.TtsAutoSchema; } });
Object.defineProperty(exports, "TtsConfigSchema", { enumerable: true, get: function () { return plugin_sdk_1.TtsConfigSchema; } });
Object.defineProperty(exports, "TtsModeSchema", { enumerable: true, get: function () { return plugin_sdk_1.TtsModeSchema; } });
Object.defineProperty(exports, "TtsProviderSchema", { enumerable: true, get: function () { return plugin_sdk_1.TtsProviderSchema; } });
const zod_1 = require("zod");
// -----------------------------------------------------------------------------
// Phone Number Validation
// -----------------------------------------------------------------------------
/**
 * E.164 phone number format: +[country code][number]
 * Examples use 555 prefix (reserved for fictional numbers)
 */
exports.E164Schema = zod_1.z
    .string()
    .regex(/^\+[1-9]\d{1,14}$/, "Expected E.164 format, e.g. +15550001234");
// -----------------------------------------------------------------------------
// Inbound Policy
// -----------------------------------------------------------------------------
/**
 * Controls how inbound calls are handled:
 * - "disabled": Block all inbound calls (outbound only)
 * - "allowlist": Only accept calls from numbers in allowFrom
 * - "pairing": Unknown callers can request pairing (future)
 * - "open": Accept all inbound calls (dangerous!)
 */
exports.InboundPolicySchema = zod_1.z.enum(["disabled", "allowlist", "pairing", "open"]);
// -----------------------------------------------------------------------------
// Provider-Specific Configuration
// -----------------------------------------------------------------------------
exports.TelnyxConfigSchema = zod_1.z
    .object({
    /** Telnyx API v2 key */
    apiKey: zod_1.z.string().min(1).optional(),
    /** Telnyx connection ID (from Call Control app) */
    connectionId: zod_1.z.string().min(1).optional(),
    /** Public key for webhook signature verification */
    publicKey: zod_1.z.string().min(1).optional(),
})
    .strict();
exports.TwilioConfigSchema = zod_1.z
    .object({
    /** Twilio Account SID */
    accountSid: zod_1.z.string().min(1).optional(),
    /** Twilio Auth Token */
    authToken: zod_1.z.string().min(1).optional(),
})
    .strict();
exports.PlivoConfigSchema = zod_1.z
    .object({
    /** Plivo Auth ID (starts with MA/SA) */
    authId: zod_1.z.string().min(1).optional(),
    /** Plivo Auth Token */
    authToken: zod_1.z.string().min(1).optional(),
})
    .strict();
// -----------------------------------------------------------------------------
// STT/TTS Configuration
// -----------------------------------------------------------------------------
exports.SttConfigSchema = zod_1.z
    .object({
    /** STT provider (currently only OpenAI supported) */
    provider: zod_1.z.literal("openai").default("openai"),
    /** Whisper model to use */
    model: zod_1.z.string().min(1).default("whisper-1"),
})
    .strict()
    .default({ provider: "openai", model: "whisper-1" });
// -----------------------------------------------------------------------------
// Webhook Server Configuration
// -----------------------------------------------------------------------------
exports.VoiceCallServeConfigSchema = zod_1.z
    .object({
    /** Port to listen on */
    port: zod_1.z.number().int().positive().default(3334),
    /** Bind address */
    bind: zod_1.z.string().default("127.0.0.1"),
    /** Webhook path */
    path: zod_1.z.string().min(1).default("/voice/webhook"),
})
    .strict()
    .default({ port: 3334, bind: "127.0.0.1", path: "/voice/webhook" });
exports.VoiceCallTailscaleConfigSchema = zod_1.z
    .object({
    /**
     * Tailscale exposure mode:
     * - "off": No Tailscale exposure
     * - "serve": Tailscale serve (private to tailnet)
     * - "funnel": Tailscale funnel (public HTTPS)
     */
    mode: zod_1.z.enum(["off", "serve", "funnel"]).default("off"),
    /** Path for Tailscale serve/funnel (should usually match serve.path) */
    path: zod_1.z.string().min(1).default("/voice/webhook"),
})
    .strict()
    .default({ mode: "off", path: "/voice/webhook" });
// -----------------------------------------------------------------------------
// Tunnel Configuration (unified ngrok/tailscale)
// -----------------------------------------------------------------------------
exports.VoiceCallTunnelConfigSchema = zod_1.z
    .object({
    /**
     * Tunnel provider:
     * - "none": No tunnel (use publicUrl if set, or manual setup)
     * - "ngrok": Use ngrok for public HTTPS tunnel
     * - "tailscale-serve": Tailscale serve (private to tailnet)
     * - "tailscale-funnel": Tailscale funnel (public HTTPS)
     */
    provider: zod_1.z.enum(["none", "ngrok", "tailscale-serve", "tailscale-funnel"]).default("none"),
    /** ngrok auth token (optional, enables longer sessions and more features) */
    ngrokAuthToken: zod_1.z.string().min(1).optional(),
    /** ngrok custom domain (paid feature, e.g., "myapp.ngrok.io") */
    ngrokDomain: zod_1.z.string().min(1).optional(),
    /**
     * Allow ngrok free tier compatibility mode.
     * When true, forwarded headers may be trusted for loopback requests
     * to reconstruct the public ngrok URL used for signing.
     *
     * IMPORTANT: This does NOT bypass signature verification.
     */
    allowNgrokFreeTierLoopbackBypass: zod_1.z.boolean().default(false),
})
    .strict()
    .default({ provider: "none", allowNgrokFreeTierLoopbackBypass: false });
// -----------------------------------------------------------------------------
// Webhook Security Configuration
// -----------------------------------------------------------------------------
exports.VoiceCallWebhookSecurityConfigSchema = zod_1.z
    .object({
    /**
     * Allowed hostnames for webhook URL reconstruction.
     * Only these hosts are accepted from forwarding headers.
     */
    allowedHosts: zod_1.z.array(zod_1.z.string().min(1)).default([]),
    /**
     * Trust X-Forwarded-* headers without a hostname allowlist.
     * WARNING: Only enable if you trust your proxy configuration.
     */
    trustForwardingHeaders: zod_1.z.boolean().default(false),
    /**
     * Trusted proxy IP addresses. Forwarded headers are only trusted when
     * the remote IP matches one of these addresses.
     */
    trustedProxyIPs: zod_1.z.array(zod_1.z.string().min(1)).default([]),
})
    .strict()
    .default({ allowedHosts: [], trustForwardingHeaders: false, trustedProxyIPs: [] });
// -----------------------------------------------------------------------------
// Outbound Call Configuration
// -----------------------------------------------------------------------------
/**
 * Call mode determines how outbound calls behave:
 * - "notify": Deliver message and auto-hangup after delay (one-way notification)
 * - "conversation": Stay open for back-and-forth until explicit end or timeout
 */
exports.CallModeSchema = zod_1.z.enum(["notify", "conversation"]);
exports.OutboundConfigSchema = zod_1.z
    .object({
    /** Default call mode for outbound calls */
    defaultMode: exports.CallModeSchema.default("notify"),
    /** Seconds to wait after TTS before auto-hangup in notify mode */
    notifyHangupDelaySec: zod_1.z.number().int().nonnegative().default(3),
})
    .strict()
    .default({ defaultMode: "notify", notifyHangupDelaySec: 3 });
// -----------------------------------------------------------------------------
// Streaming Configuration (OpenAI Realtime STT)
// -----------------------------------------------------------------------------
exports.VoiceCallStreamingConfigSchema = zod_1.z
    .object({
    /** Enable real-time audio streaming (requires WebSocket support) */
    enabled: zod_1.z.boolean().default(false),
    /** STT provider for real-time transcription */
    sttProvider: zod_1.z.enum(["openai-realtime"]).default("openai-realtime"),
    /** OpenAI API key for Realtime API (uses OPENAI_API_KEY env if not set) */
    openaiApiKey: zod_1.z.string().min(1).optional(),
    /** OpenAI transcription model (default: gpt-4o-transcribe) */
    sttModel: zod_1.z.string().min(1).default("gpt-4o-transcribe"),
    /** VAD silence duration in ms before considering speech ended */
    silenceDurationMs: zod_1.z.number().int().positive().default(800),
    /** VAD threshold 0-1 (higher = less sensitive) */
    vadThreshold: zod_1.z.number().min(0).max(1).default(0.5),
    /** WebSocket path for media stream connections */
    streamPath: zod_1.z.string().min(1).default("/voice/stream"),
})
    .strict()
    .default({
    enabled: false,
    sttProvider: "openai-realtime",
    sttModel: "gpt-4o-transcribe",
    silenceDurationMs: 800,
    vadThreshold: 0.5,
    streamPath: "/voice/stream",
});
// -----------------------------------------------------------------------------
// Main Voice Call Configuration
// -----------------------------------------------------------------------------
exports.VoiceCallConfigSchema = zod_1.z
    .object({
    /** Enable voice call functionality */
    enabled: zod_1.z.boolean().default(false),
    /** Active provider (telnyx, twilio, plivo, or mock) */
    provider: zod_1.z.enum(["telnyx", "twilio", "plivo", "mock"]).optional(),
    /** Telnyx-specific configuration */
    telnyx: exports.TelnyxConfigSchema.optional(),
    /** Twilio-specific configuration */
    twilio: exports.TwilioConfigSchema.optional(),
    /** Plivo-specific configuration */
    plivo: exports.PlivoConfigSchema.optional(),
    /** Phone number to call from (E.164) */
    fromNumber: exports.E164Schema.optional(),
    /** Default phone number to call (E.164) */
    toNumber: exports.E164Schema.optional(),
    /** Inbound call policy */
    inboundPolicy: exports.InboundPolicySchema.default("disabled"),
    /** Allowlist of phone numbers for inbound calls (E.164) */
    allowFrom: zod_1.z.array(exports.E164Schema).default([]),
    /** Greeting message for inbound calls */
    inboundGreeting: zod_1.z.string().optional(),
    /** Outbound call configuration */
    outbound: exports.OutboundConfigSchema,
    /** Maximum call duration in seconds */
    maxDurationSeconds: zod_1.z.number().int().positive().default(300),
    /** Silence timeout for end-of-speech detection (ms) */
    silenceTimeoutMs: zod_1.z.number().int().positive().default(800),
    /** Timeout for user transcript (ms) */
    transcriptTimeoutMs: zod_1.z.number().int().positive().default(180000),
    /** Ring timeout for outbound calls (ms) */
    ringTimeoutMs: zod_1.z.number().int().positive().default(30000),
    /** Maximum concurrent calls */
    maxConcurrentCalls: zod_1.z.number().int().positive().default(1),
    /** Webhook server configuration */
    serve: exports.VoiceCallServeConfigSchema,
    /** Tailscale exposure configuration (legacy, prefer tunnel config) */
    tailscale: exports.VoiceCallTailscaleConfigSchema,
    /** Tunnel configuration (unified ngrok/tailscale) */
    tunnel: exports.VoiceCallTunnelConfigSchema,
    /** Webhook signature reconstruction and proxy trust configuration */
    webhookSecurity: exports.VoiceCallWebhookSecurityConfigSchema,
    /** Real-time audio streaming configuration */
    streaming: exports.VoiceCallStreamingConfigSchema,
    /** Public webhook URL override (if set, bypasses tunnel auto-detection) */
    publicUrl: zod_1.z.string().url().optional(),
    /** Skip webhook signature verification (development only, NOT for production) */
    skipSignatureVerification: zod_1.z.boolean().default(false),
    /** STT configuration */
    stt: exports.SttConfigSchema,
    /** TTS override (deep-merges with core messages.tts) */
    tts: plugin_sdk_1.TtsConfigSchema,
    /** Store path for call logs */
    store: zod_1.z.string().optional(),
    /** Model for generating voice responses (e.g., "anthropic/claude-sonnet-4", "openai/gpt-4o") */
    responseModel: zod_1.z.string().default("openai/gpt-4o-mini"),
    /** System prompt for voice responses */
    responseSystemPrompt: zod_1.z.string().optional(),
    /** Timeout for response generation in ms (default 30s) */
    responseTimeoutMs: zod_1.z.number().int().positive().default(30000),
})
    .strict();
// -----------------------------------------------------------------------------
// Configuration Helpers
// -----------------------------------------------------------------------------
/**
 * Resolves the configuration by merging environment variables into missing fields.
 * Returns a new configuration object with environment variables applied.
 */
function resolveVoiceCallConfig(config) {
    const resolved = JSON.parse(JSON.stringify(config));
    // Telnyx
    if (resolved.provider === "telnyx") {
        resolved.telnyx = resolved.telnyx ?? {};
        resolved.telnyx.apiKey = resolved.telnyx.apiKey ?? process.env.TELNYX_API_KEY;
        resolved.telnyx.connectionId = resolved.telnyx.connectionId ?? process.env.TELNYX_CONNECTION_ID;
        resolved.telnyx.publicKey = resolved.telnyx.publicKey ?? process.env.TELNYX_PUBLIC_KEY;
    }
    // Twilio
    if (resolved.provider === "twilio") {
        resolved.twilio = resolved.twilio ?? {};
        resolved.twilio.accountSid = resolved.twilio.accountSid ?? process.env.TWILIO_ACCOUNT_SID;
        resolved.twilio.authToken = resolved.twilio.authToken ?? process.env.TWILIO_AUTH_TOKEN;
    }
    // Plivo
    if (resolved.provider === "plivo") {
        resolved.plivo = resolved.plivo ?? {};
        resolved.plivo.authId = resolved.plivo.authId ?? process.env.PLIVO_AUTH_ID;
        resolved.plivo.authToken = resolved.plivo.authToken ?? process.env.PLIVO_AUTH_TOKEN;
    }
    // Tunnel Config
    resolved.tunnel = resolved.tunnel ?? {
        provider: "none",
        allowNgrokFreeTierLoopbackBypass: false,
    };
    resolved.tunnel.allowNgrokFreeTierLoopbackBypass =
        resolved.tunnel.allowNgrokFreeTierLoopbackBypass ?? false;
    resolved.tunnel.ngrokAuthToken = resolved.tunnel.ngrokAuthToken ?? process.env.NGROK_AUTHTOKEN;
    resolved.tunnel.ngrokDomain = resolved.tunnel.ngrokDomain ?? process.env.NGROK_DOMAIN;
    // Webhook Security Config
    resolved.webhookSecurity = resolved.webhookSecurity ?? {
        allowedHosts: [],
        trustForwardingHeaders: false,
        trustedProxyIPs: [],
    };
    resolved.webhookSecurity.allowedHosts = resolved.webhookSecurity.allowedHosts ?? [];
    resolved.webhookSecurity.trustForwardingHeaders =
        resolved.webhookSecurity.trustForwardingHeaders ?? false;
    resolved.webhookSecurity.trustedProxyIPs = resolved.webhookSecurity.trustedProxyIPs ?? [];
    return resolved;
}
/**
 * Validate that the configuration has all required fields for the selected provider.
 */
function validateProviderConfig(config) {
    const errors = [];
    if (!config.enabled) {
        return { valid: true, errors: [] };
    }
    if (!config.provider) {
        errors.push("plugins.entries.voice-call.config.provider is required");
    }
    if (!config.fromNumber && config.provider !== "mock") {
        errors.push("plugins.entries.voice-call.config.fromNumber is required");
    }
    if (config.provider === "telnyx") {
        if (!config.telnyx?.apiKey) {
            errors.push("plugins.entries.voice-call.config.telnyx.apiKey is required (or set TELNYX_API_KEY env)");
        }
        if (!config.telnyx?.connectionId) {
            errors.push("plugins.entries.voice-call.config.telnyx.connectionId is required (or set TELNYX_CONNECTION_ID env)");
        }
        if (!config.skipSignatureVerification && !config.telnyx?.publicKey) {
            errors.push("plugins.entries.voice-call.config.telnyx.publicKey is required (or set TELNYX_PUBLIC_KEY env)");
        }
    }
    if (config.provider === "twilio") {
        if (!config.twilio?.accountSid) {
            errors.push("plugins.entries.voice-call.config.twilio.accountSid is required (or set TWILIO_ACCOUNT_SID env)");
        }
        if (!config.twilio?.authToken) {
            errors.push("plugins.entries.voice-call.config.twilio.authToken is required (or set TWILIO_AUTH_TOKEN env)");
        }
    }
    if (config.provider === "plivo") {
        if (!config.plivo?.authId) {
            errors.push("plugins.entries.voice-call.config.plivo.authId is required (or set PLIVO_AUTH_ID env)");
        }
        if (!config.plivo?.authToken) {
            errors.push("plugins.entries.voice-call.config.plivo.authToken is required (or set PLIVO_AUTH_TOKEN env)");
        }
    }
    return { valid: errors.length === 0, errors };
}
