"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.createVoiceCallRuntime = createVoiceCallRuntime;
const config_js_1 = require("./config.js");
const manager_js_1 = require("./manager.js");
const mock_js_1 = require("./providers/mock.js");
const plivo_js_1 = require("./providers/plivo.js");
const telnyx_js_1 = require("./providers/telnyx.js");
const twilio_js_1 = require("./providers/twilio.js");
const telephony_tts_js_1 = require("./telephony-tts.js");
const tunnel_js_1 = require("./tunnel.js");
const webhook_js_1 = require("./webhook.js");
function isLoopbackBind(bind) {
    if (!bind) {
        return false;
    }
    return bind === "127.0.0.1" || bind === "::1" || bind === "localhost";
}
function resolveProvider(config) {
    const allowNgrokFreeTierLoopbackBypass = config.tunnel?.provider === "ngrok" &&
        isLoopbackBind(config.serve?.bind) &&
        (config.tunnel?.allowNgrokFreeTierLoopbackBypass ?? false);
    switch (config.provider) {
        case "telnyx":
            return new telnyx_js_1.TelnyxProvider({
                apiKey: config.telnyx?.apiKey,
                connectionId: config.telnyx?.connectionId,
                publicKey: config.telnyx?.publicKey,
            }, {
                skipVerification: config.skipSignatureVerification,
            });
        case "twilio":
            return new twilio_js_1.TwilioProvider({
                accountSid: config.twilio?.accountSid,
                authToken: config.twilio?.authToken,
            }, {
                allowNgrokFreeTierLoopbackBypass,
                publicUrl: config.publicUrl,
                skipVerification: config.skipSignatureVerification,
                streamPath: config.streaming?.enabled ? config.streaming.streamPath : undefined,
                webhookSecurity: config.webhookSecurity,
            });
        case "plivo":
            return new plivo_js_1.PlivoProvider({
                authId: config.plivo?.authId,
                authToken: config.plivo?.authToken,
            }, {
                publicUrl: config.publicUrl,
                skipVerification: config.skipSignatureVerification,
                ringTimeoutSec: Math.max(1, Math.floor(config.ringTimeoutMs / 1000)),
                webhookSecurity: config.webhookSecurity,
            });
        case "mock":
            return new mock_js_1.MockProvider();
        default:
            throw new Error(`Unsupported voice-call provider: ${String(config.provider)}`);
    }
}
async function createVoiceCallRuntime(params) {
    const { config: rawConfig, coreConfig, ttsRuntime, logger } = params;
    const log = logger ?? {
        info: console.log,
        warn: console.warn,
        error: console.error,
        debug: console.debug,
    };
    const config = (0, config_js_1.resolveVoiceCallConfig)(rawConfig);
    if (!config.enabled) {
        throw new Error("Voice call disabled. Enable the plugin entry in config.");
    }
    if (config.skipSignatureVerification) {
        log.warn("[voice-call] SECURITY WARNING: skipSignatureVerification=true disables webhook signature verification (development only). Do not use in production.");
    }
    const validation = (0, config_js_1.validateProviderConfig)(config);
    if (!validation.valid) {
        throw new Error(`Invalid voice-call config: ${validation.errors.join("; ")}`);
    }
    const provider = resolveProvider(config);
    const manager = new manager_js_1.CallManager(config);
    const webhookServer = new webhook_js_1.VoiceCallWebhookServer(config, manager, provider, coreConfig);
    const localUrl = await webhookServer.start();
    // Determine public URL - priority: config.publicUrl > tunnel > legacy tailscale
    let publicUrl = config.publicUrl ?? null;
    let tunnelResult = null;
    if (!publicUrl && config.tunnel?.provider && config.tunnel.provider !== "none") {
        try {
            tunnelResult = await (0, tunnel_js_1.startTunnel)({
                provider: config.tunnel.provider,
                port: config.serve.port,
                path: config.serve.path,
                ngrokAuthToken: config.tunnel.ngrokAuthToken,
                ngrokDomain: config.tunnel.ngrokDomain,
            });
            publicUrl = tunnelResult?.publicUrl ?? null;
        }
        catch (err) {
            log.error(`[voice-call] Tunnel setup failed: ${err instanceof Error ? err.message : String(err)}`);
        }
    }
    if (!publicUrl && config.tailscale?.mode !== "off") {
        publicUrl = await (0, webhook_js_1.setupTailscaleExposure)(config);
    }
    const webhookUrl = publicUrl ?? localUrl;
    if (publicUrl && provider.name === "twilio") {
        provider.setPublicUrl(publicUrl);
    }
    if (provider.name === "twilio" && config.streaming?.enabled) {
        const twilioProvider = provider;
        if (ttsRuntime?.textToSpeechTelephony) {
            try {
                const ttsProvider = (0, telephony_tts_js_1.createTelephonyTtsProvider)({
                    coreConfig,
                    ttsOverride: config.tts,
                    runtime: ttsRuntime,
                });
                twilioProvider.setTTSProvider(ttsProvider);
                log.info("[voice-call] Telephony TTS provider configured");
            }
            catch (err) {
                log.warn(`[voice-call] Failed to initialize telephony TTS: ${err instanceof Error ? err.message : String(err)}`);
            }
        }
        else {
            log.warn("[voice-call] Telephony TTS unavailable; streaming TTS disabled");
        }
        const mediaHandler = webhookServer.getMediaStreamHandler();
        if (mediaHandler) {
            twilioProvider.setMediaStreamHandler(mediaHandler);
            log.info("[voice-call] Media stream handler wired to provider");
        }
    }
    manager.initialize(provider, webhookUrl);
    const stop = async () => {
        if (tunnelResult) {
            await tunnelResult.stop();
        }
        await (0, webhook_js_1.cleanupTailscaleExposure)(config);
        await webhookServer.stop();
    };
    log.info("[voice-call] Runtime initialized");
    log.info(`[voice-call] Webhook URL: ${webhookUrl}`);
    if (publicUrl) {
        log.info(`[voice-call] Public URL: ${publicUrl}`);
    }
    return {
        config,
        provider,
        manager,
        webhookServer,
        webhookUrl,
        publicUrl,
        stop,
    };
}
