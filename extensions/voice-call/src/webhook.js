"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.VoiceCallWebhookServer = void 0;
exports.getTailscaleSelfInfo = getTailscaleSelfInfo;
exports.getTailscaleDnsName = getTailscaleDnsName;
exports.setupTailscaleExposureRoute = setupTailscaleExposureRoute;
exports.cleanupTailscaleExposureRoute = cleanupTailscaleExposureRoute;
exports.setupTailscaleExposure = setupTailscaleExposure;
exports.cleanupTailscaleExposure = cleanupTailscaleExposure;
const node_child_process_1 = require("node:child_process");
const node_http_1 = __importDefault(require("node:http"));
const node_url_1 = require("node:url");
const plugin_sdk_1 = require("clawcore/plugin-sdk");
const media_stream_js_1 = require("./media-stream.js");
const stt_openai_realtime_js_1 = require("./providers/stt-openai-realtime.js");
const MAX_WEBHOOK_BODY_BYTES = 1024 * 1024;
/**
 * HTTP server for receiving voice call webhooks from providers.
 * Supports WebSocket upgrades for media streams when streaming is enabled.
 */
class VoiceCallWebhookServer {
    server = null;
    config;
    manager;
    provider;
    coreConfig;
    /** Media stream handler for bidirectional audio (when streaming enabled) */
    mediaStreamHandler = null;
    constructor(config, manager, provider, coreConfig) {
        this.config = config;
        this.manager = manager;
        this.provider = provider;
        this.coreConfig = coreConfig ?? null;
        // Initialize media stream handler if streaming is enabled
        if (config.streaming?.enabled) {
            this.initializeMediaStreaming();
        }
    }
    /**
     * Get the media stream handler (for wiring to provider).
     */
    getMediaStreamHandler() {
        return this.mediaStreamHandler;
    }
    /**
     * Initialize media streaming with OpenAI Realtime STT.
     */
    initializeMediaStreaming() {
        const apiKey = this.config.streaming?.openaiApiKey || process.env.OPENAI_API_KEY;
        if (!apiKey) {
            console.warn("[voice-call] Streaming enabled but no OpenAI API key found");
            return;
        }
        const sttProvider = new stt_openai_realtime_js_1.OpenAIRealtimeSTTProvider({
            apiKey,
            model: this.config.streaming?.sttModel,
            silenceDurationMs: this.config.streaming?.silenceDurationMs,
            vadThreshold: this.config.streaming?.vadThreshold,
        });
        const streamConfig = {
            sttProvider,
            shouldAcceptStream: ({ callId, token }) => {
                const call = this.manager.getCallByProviderCallId(callId);
                if (!call) {
                    return false;
                }
                if (this.provider.name === "twilio") {
                    const twilio = this.provider;
                    if (!twilio.isValidStreamToken(callId, token)) {
                        console.warn(`[voice-call] Rejecting media stream: invalid token for ${callId}`);
                        return false;
                    }
                }
                return true;
            },
            onTranscript: (providerCallId, transcript) => {
                console.log(`[voice-call] Transcript for ${providerCallId}: ${transcript}`);
                // Clear TTS queue on barge-in (user started speaking, interrupt current playback)
                if (this.provider.name === "twilio") {
                    this.provider.clearTtsQueue(providerCallId);
                }
                // Look up our internal call ID from the provider call ID
                const call = this.manager.getCallByProviderCallId(providerCallId);
                if (!call) {
                    console.warn(`[voice-call] No active call found for provider ID: ${providerCallId}`);
                    return;
                }
                // Create a speech event and process it through the manager
                const event = {
                    id: `stream-transcript-${Date.now()}`,
                    type: "call.speech",
                    callId: call.callId,
                    providerCallId,
                    timestamp: Date.now(),
                    transcript,
                    isFinal: true,
                };
                this.manager.processEvent(event);
                // Auto-respond in conversation mode (inbound always, outbound if mode is conversation)
                const callMode = call.metadata?.mode;
                const shouldRespond = call.direction === "inbound" || callMode === "conversation";
                if (shouldRespond) {
                    this.handleInboundResponse(call.callId, transcript).catch((err) => {
                        console.warn(`[voice-call] Failed to auto-respond:`, err);
                    });
                }
            },
            onSpeechStart: (providerCallId) => {
                if (this.provider.name === "twilio") {
                    this.provider.clearTtsQueue(providerCallId);
                }
            },
            onPartialTranscript: (callId, partial) => {
                console.log(`[voice-call] Partial for ${callId}: ${partial}`);
            },
            onConnect: (callId, streamSid) => {
                console.log(`[voice-call] Media stream connected: ${callId} -> ${streamSid}`);
                // Register stream with provider for TTS routing
                if (this.provider.name === "twilio") {
                    this.provider.registerCallStream(callId, streamSid);
                }
                // Speak initial message if one was provided when call was initiated
                // Use setTimeout to allow stream setup to complete
                setTimeout(() => {
                    this.manager.speakInitialMessage(callId).catch((err) => {
                        console.warn(`[voice-call] Failed to speak initial message:`, err);
                    });
                }, 500);
            },
            onDisconnect: (callId) => {
                console.log(`[voice-call] Media stream disconnected: ${callId}`);
                if (this.provider.name === "twilio") {
                    this.provider.unregisterCallStream(callId);
                }
            },
        };
        this.mediaStreamHandler = new media_stream_js_1.MediaStreamHandler(streamConfig);
        console.log("[voice-call] Media streaming initialized");
    }
    /**
     * Start the webhook server.
     */
    async start() {
        const { port, bind, path: webhookPath } = this.config.serve;
        const streamPath = this.config.streaming?.streamPath || "/voice/stream";
        return new Promise((resolve, reject) => {
            this.server = node_http_1.default.createServer((req, res) => {
                this.handleRequest(req, res, webhookPath).catch((err) => {
                    console.error("[voice-call] Webhook error:", err);
                    res.statusCode = 500;
                    res.end("Internal Server Error");
                });
            });
            // Handle WebSocket upgrades for media streams
            if (this.mediaStreamHandler) {
                this.server.on("upgrade", (request, socket, head) => {
                    const url = new node_url_1.URL(request.url || "/", `http://${request.headers.host}`);
                    if (url.pathname === streamPath) {
                        console.log("[voice-call] WebSocket upgrade for media stream");
                        this.mediaStreamHandler?.handleUpgrade(request, socket, head);
                    }
                    else {
                        socket.destroy();
                    }
                });
            }
            this.server.on("error", reject);
            this.server.listen(port, bind, () => {
                const url = `http://${bind}:${port}${webhookPath}`;
                console.log(`[voice-call] Webhook server listening on ${url}`);
                if (this.mediaStreamHandler) {
                    console.log(`[voice-call] Media stream WebSocket on ws://${bind}:${port}${streamPath}`);
                }
                resolve(url);
            });
        });
    }
    /**
     * Stop the webhook server.
     */
    async stop() {
        return new Promise((resolve) => {
            if (this.server) {
                this.server.close(() => {
                    this.server = null;
                    resolve();
                });
            }
            else {
                resolve();
            }
        });
    }
    /**
     * Handle incoming HTTP request.
     */
    async handleRequest(req, res, webhookPath) {
        const url = new node_url_1.URL(req.url || "/", `http://${req.headers.host}`);
        // Check path
        if (!url.pathname.startsWith(webhookPath)) {
            res.statusCode = 404;
            res.end("Not Found");
            return;
        }
        // Only accept POST
        if (req.method !== "POST") {
            res.statusCode = 405;
            res.end("Method Not Allowed");
            return;
        }
        // Read body
        let body = "";
        try {
            body = await this.readBody(req, MAX_WEBHOOK_BODY_BYTES);
        }
        catch (err) {
            if ((0, plugin_sdk_1.isRequestBodyLimitError)(err, "PAYLOAD_TOO_LARGE")) {
                res.statusCode = 413;
                res.end("Payload Too Large");
                return;
            }
            if ((0, plugin_sdk_1.isRequestBodyLimitError)(err, "REQUEST_BODY_TIMEOUT")) {
                res.statusCode = 408;
                res.end((0, plugin_sdk_1.requestBodyErrorToText)("REQUEST_BODY_TIMEOUT"));
                return;
            }
            throw err;
        }
        // Build webhook context
        const ctx = {
            headers: req.headers,
            rawBody: body,
            url: `http://${req.headers.host}${req.url}`,
            method: "POST",
            query: Object.fromEntries(url.searchParams),
            remoteAddress: req.socket.remoteAddress ?? undefined,
        };
        // Verify signature
        const verification = this.provider.verifyWebhook(ctx);
        if (!verification.ok) {
            console.warn(`[voice-call] Webhook verification failed: ${verification.reason}`);
            res.statusCode = 401;
            res.end("Unauthorized");
            return;
        }
        // Parse events
        const result = this.provider.parseWebhookEvent(ctx);
        // Process each event
        for (const event of result.events) {
            try {
                this.manager.processEvent(event);
            }
            catch (err) {
                console.error(`[voice-call] Error processing event ${event.type}:`, err);
            }
        }
        // Send response
        res.statusCode = result.statusCode || 200;
        if (result.providerResponseHeaders) {
            for (const [key, value] of Object.entries(result.providerResponseHeaders)) {
                res.setHeader(key, value);
            }
        }
        res.end(result.providerResponseBody || "OK");
    }
    /**
     * Read request body as string with timeout protection.
     */
    readBody(req, maxBytes, timeoutMs = 30_000) {
        return (0, plugin_sdk_1.readRequestBodyWithLimit)(req, { maxBytes, timeoutMs });
    }
    /**
     * Handle auto-response for inbound calls using the agent system.
     * Supports tool calling for richer voice interactions.
     */
    async handleInboundResponse(callId, userMessage) {
        console.log(`[voice-call] Auto-responding to inbound call ${callId}: "${userMessage}"`);
        // Get call context for conversation history
        const call = this.manager.getCall(callId);
        if (!call) {
            console.warn(`[voice-call] Call ${callId} not found for auto-response`);
            return;
        }
        if (!this.coreConfig) {
            console.warn("[voice-call] Core config missing; skipping auto-response");
            return;
        }
        try {
            const { generateVoiceResponse } = await Promise.resolve().then(() => __importStar(require("./response-generator.js")));
            const result = await generateVoiceResponse({
                voiceConfig: this.config,
                coreConfig: this.coreConfig,
                callId,
                from: call.from,
                transcript: call.transcript,
                userMessage,
            });
            if (result.error) {
                console.error(`[voice-call] Response generation error: ${result.error}`);
                return;
            }
            if (result.text) {
                console.log(`[voice-call] AI response: "${result.text}"`);
                await this.manager.speak(callId, result.text);
            }
        }
        catch (err) {
            console.error(`[voice-call] Auto-response error:`, err);
        }
    }
}
exports.VoiceCallWebhookServer = VoiceCallWebhookServer;
/**
 * Run a tailscale command with timeout, collecting stdout.
 */
function runTailscaleCommand(args, timeoutMs = 2500) {
    return new Promise((resolve) => {
        const proc = (0, node_child_process_1.spawn)("tailscale", args, {
            stdio: ["ignore", "pipe", "pipe"],
        });
        let stdout = "";
        proc.stdout.on("data", (data) => {
            stdout += data;
        });
        const timer = setTimeout(() => {
            proc.kill("SIGKILL");
            resolve({ code: -1, stdout: "" });
        }, timeoutMs);
        proc.on("close", (code) => {
            clearTimeout(timer);
            resolve({ code: code ?? -1, stdout });
        });
    });
}
async function getTailscaleSelfInfo() {
    const { code, stdout } = await runTailscaleCommand(["status", "--json"]);
    if (code !== 0) {
        return null;
    }
    try {
        const status = JSON.parse(stdout);
        return {
            dnsName: status.Self?.DNSName?.replace(/\.$/, "") || null,
            nodeId: status.Self?.ID || null,
        };
    }
    catch {
        return null;
    }
}
async function getTailscaleDnsName() {
    const info = await getTailscaleSelfInfo();
    return info?.dnsName ?? null;
}
async function setupTailscaleExposureRoute(opts) {
    const dnsName = await getTailscaleDnsName();
    if (!dnsName) {
        console.warn("[voice-call] Could not get Tailscale DNS name");
        return null;
    }
    const { code } = await runTailscaleCommand([
        opts.mode,
        "--bg",
        "--yes",
        "--set-path",
        opts.path,
        opts.localUrl,
    ]);
    if (code === 0) {
        const publicUrl = `https://${dnsName}${opts.path}`;
        console.log(`[voice-call] Tailscale ${opts.mode} active: ${publicUrl}`);
        return publicUrl;
    }
    console.warn(`[voice-call] Tailscale ${opts.mode} failed`);
    return null;
}
async function cleanupTailscaleExposureRoute(opts) {
    await runTailscaleCommand([opts.mode, "off", opts.path]);
}
/**
 * Setup Tailscale serve/funnel for the webhook server.
 * This is a helper that shells out to `tailscale serve` or `tailscale funnel`.
 */
async function setupTailscaleExposure(config) {
    if (config.tailscale.mode === "off") {
        return null;
    }
    const mode = config.tailscale.mode === "funnel" ? "funnel" : "serve";
    // Include the path suffix so tailscale forwards to the correct endpoint
    // (tailscale strips the mount path prefix when proxying)
    const localUrl = `http://127.0.0.1:${config.serve.port}${config.serve.path}`;
    return setupTailscaleExposureRoute({
        mode,
        path: config.tailscale.path,
        localUrl,
    });
}
/**
 * Cleanup Tailscale serve/funnel.
 */
async function cleanupTailscaleExposure(config) {
    if (config.tailscale.mode === "off") {
        return;
    }
    const mode = config.tailscale.mode === "funnel" ? "funnel" : "serve";
    await cleanupTailscaleExposureRoute({ mode, path: config.tailscale.path });
}
