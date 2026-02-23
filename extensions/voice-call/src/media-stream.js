"use strict";
/**
 * Media Stream Handler
 *
 * Handles bidirectional audio streaming between Twilio and the AI services.
 * - Receives mu-law audio from Twilio via WebSocket
 * - Forwards to OpenAI Realtime STT for transcription
 * - Sends TTS audio back to Twilio
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.MediaStreamHandler = void 0;
const ws_1 = require("ws");
/**
 * Manages WebSocket connections for Twilio media streams.
 */
class MediaStreamHandler {
    wss = null;
    sessions = new Map();
    config;
    /** TTS playback queues per stream (serialize audio to prevent overlap) */
    ttsQueues = new Map();
    /** Whether TTS is currently playing per stream */
    ttsPlaying = new Map();
    /** Active TTS playback controllers per stream */
    ttsActiveControllers = new Map();
    constructor(config) {
        this.config = config;
    }
    /**
     * Handle WebSocket upgrade for media stream connections.
     */
    handleUpgrade(request, socket, head) {
        if (!this.wss) {
            this.wss = new ws_1.WebSocketServer({ noServer: true });
            this.wss.on("connection", (ws, req) => this.handleConnection(ws, req));
        }
        this.wss.handleUpgrade(request, socket, head, (ws) => {
            this.wss?.emit("connection", ws, request);
        });
    }
    /**
     * Handle new WebSocket connection from Twilio.
     */
    async handleConnection(ws, _request) {
        let session = null;
        const streamToken = this.getStreamToken(_request);
        ws.on("message", async (data) => {
            try {
                const message = JSON.parse(data.toString());
                switch (message.event) {
                    case "connected":
                        console.log("[MediaStream] Twilio connected");
                        break;
                    case "start":
                        session = await this.handleStart(ws, message, streamToken);
                        break;
                    case "media":
                        if (session && message.media?.payload) {
                            // Forward audio to STT
                            const audioBuffer = Buffer.from(message.media.payload, "base64");
                            session.sttSession.sendAudio(audioBuffer);
                        }
                        break;
                    case "stop":
                        if (session) {
                            this.handleStop(session);
                            session = null;
                        }
                        break;
                }
            }
            catch (error) {
                console.error("[MediaStream] Error processing message:", error);
            }
        });
        ws.on("close", () => {
            if (session) {
                this.handleStop(session);
            }
        });
        ws.on("error", (error) => {
            console.error("[MediaStream] WebSocket error:", error);
        });
    }
    /**
     * Handle stream start event.
     */
    async handleStart(ws, message, streamToken) {
        const streamSid = message.streamSid || "";
        const callSid = message.start?.callSid || "";
        // Prefer token from start message customParameters (set via TwiML <Parameter>),
        // falling back to query string token. Twilio strips query params from WebSocket
        // URLs but reliably delivers <Parameter> values in customParameters.
        const effectiveToken = message.start?.customParameters?.token ?? streamToken;
        console.log(`[MediaStream] Stream started: ${streamSid} (call: ${callSid})`);
        if (!callSid) {
            console.warn("[MediaStream] Missing callSid; closing stream");
            ws.close(1008, "Missing callSid");
            return null;
        }
        if (this.config.shouldAcceptStream &&
            !this.config.shouldAcceptStream({ callId: callSid, streamSid, token: effectiveToken })) {
            console.warn(`[MediaStream] Rejecting stream for unknown call: ${callSid}`);
            ws.close(1008, "Unknown call");
            return null;
        }
        // Create STT session
        const sttSession = this.config.sttProvider.createSession();
        // Set up transcript callbacks
        sttSession.onPartial((partial) => {
            this.config.onPartialTranscript?.(callSid, partial);
        });
        sttSession.onTranscript((transcript) => {
            this.config.onTranscript?.(callSid, transcript);
        });
        sttSession.onSpeechStart(() => {
            this.config.onSpeechStart?.(callSid);
        });
        const session = {
            callId: callSid,
            streamSid,
            ws,
            sttSession,
        };
        this.sessions.set(streamSid, session);
        // Notify connection BEFORE STT connect so TTS can work even if STT fails
        this.config.onConnect?.(callSid, streamSid);
        // Connect to OpenAI STT (non-blocking, log errors but don't fail the call)
        sttSession.connect().catch((err) => {
            console.warn(`[MediaStream] STT connection failed (TTS still works):`, err.message);
        });
        return session;
    }
    /**
     * Handle stream stop event.
     */
    handleStop(session) {
        console.log(`[MediaStream] Stream stopped: ${session.streamSid}`);
        this.clearTtsState(session.streamSid);
        session.sttSession.close();
        this.sessions.delete(session.streamSid);
        this.config.onDisconnect?.(session.callId);
    }
    getStreamToken(request) {
        if (!request.url || !request.headers.host) {
            return undefined;
        }
        try {
            const url = new URL(request.url, `http://${request.headers.host}`);
            return url.searchParams.get("token") ?? undefined;
        }
        catch {
            return undefined;
        }
    }
    /**
     * Get an active session with an open WebSocket, or undefined if unavailable.
     */
    getOpenSession(streamSid) {
        const session = this.sessions.get(streamSid);
        return session?.ws.readyState === ws_1.WebSocket.OPEN ? session : undefined;
    }
    /**
     * Send a message to a stream's WebSocket if available.
     */
    sendToStream(streamSid, message) {
        const session = this.getOpenSession(streamSid);
        session?.ws.send(JSON.stringify(message));
    }
    /**
     * Send audio to a specific stream (for TTS playback).
     * Audio should be mu-law encoded at 8kHz mono.
     */
    sendAudio(streamSid, muLawAudio) {
        this.sendToStream(streamSid, {
            event: "media",
            streamSid,
            media: { payload: muLawAudio.toString("base64") },
        });
    }
    /**
     * Send a mark event to track audio playback position.
     */
    sendMark(streamSid, name) {
        this.sendToStream(streamSid, {
            event: "mark",
            streamSid,
            mark: { name },
        });
    }
    /**
     * Clear audio buffer (interrupt playback).
     */
    clearAudio(streamSid) {
        this.sendToStream(streamSid, { event: "clear", streamSid });
    }
    /**
     * Queue a TTS operation for sequential playback.
     * Only one TTS operation plays at a time per stream to prevent overlap.
     */
    async queueTts(streamSid, playFn) {
        const queue = this.getTtsQueue(streamSid);
        let resolveEntry;
        let rejectEntry;
        const promise = new Promise((resolve, reject) => {
            resolveEntry = resolve;
            rejectEntry = reject;
        });
        queue.push({
            playFn,
            controller: new AbortController(),
            resolve: resolveEntry,
            reject: rejectEntry,
        });
        if (!this.ttsPlaying.get(streamSid)) {
            void this.processQueue(streamSid);
        }
        return promise;
    }
    /**
     * Clear TTS queue and interrupt current playback (barge-in).
     */
    clearTtsQueue(streamSid) {
        const queue = this.getTtsQueue(streamSid);
        queue.length = 0;
        this.ttsActiveControllers.get(streamSid)?.abort();
        this.clearAudio(streamSid);
    }
    /**
     * Get active session by call ID.
     */
    getSessionByCallId(callId) {
        return [...this.sessions.values()].find((session) => session.callId === callId);
    }
    /**
     * Close all sessions.
     */
    closeAll() {
        for (const session of this.sessions.values()) {
            this.clearTtsState(session.streamSid);
            session.sttSession.close();
            session.ws.close();
        }
        this.sessions.clear();
    }
    getTtsQueue(streamSid) {
        const existing = this.ttsQueues.get(streamSid);
        if (existing) {
            return existing;
        }
        const queue = [];
        this.ttsQueues.set(streamSid, queue);
        return queue;
    }
    /**
     * Process the TTS queue for a stream.
     * Uses iterative approach to avoid stack accumulation from recursion.
     */
    async processQueue(streamSid) {
        this.ttsPlaying.set(streamSid, true);
        while (true) {
            const queue = this.ttsQueues.get(streamSid);
            if (!queue || queue.length === 0) {
                this.ttsPlaying.set(streamSid, false);
                this.ttsActiveControllers.delete(streamSid);
                return;
            }
            const entry = queue.shift();
            this.ttsActiveControllers.set(streamSid, entry.controller);
            try {
                await entry.playFn(entry.controller.signal);
                entry.resolve();
            }
            catch (error) {
                if (entry.controller.signal.aborted) {
                    entry.resolve();
                }
                else {
                    console.error("[MediaStream] TTS playback error:", error);
                    entry.reject(error);
                }
            }
            finally {
                if (this.ttsActiveControllers.get(streamSid) === entry.controller) {
                    this.ttsActiveControllers.delete(streamSid);
                }
            }
        }
    }
    clearTtsState(streamSid) {
        const queue = this.ttsQueues.get(streamSid);
        if (queue) {
            queue.length = 0;
        }
        this.ttsActiveControllers.get(streamSid)?.abort();
        this.ttsActiveControllers.delete(streamSid);
        this.ttsPlaying.delete(streamSid);
        this.ttsQueues.delete(streamSid);
    }
}
exports.MediaStreamHandler = MediaStreamHandler;
