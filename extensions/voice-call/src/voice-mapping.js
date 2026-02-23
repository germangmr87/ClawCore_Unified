"use strict";
/**
 * Voice mapping and XML utilities for voice call providers.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.DEFAULT_POLLY_VOICE = void 0;
exports.escapeXml = escapeXml;
exports.mapVoiceToPolly = mapVoiceToPolly;
exports.isOpenAiVoice = isOpenAiVoice;
exports.getOpenAiVoiceNames = getOpenAiVoiceNames;
/**
 * Escape XML special characters for TwiML and other XML responses.
 */
function escapeXml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&apos;");
}
/**
 * Map of OpenAI voice names to similar Twilio Polly voices.
 */
const OPENAI_TO_POLLY_MAP = {
    alloy: "Polly.Joanna", // neutral, warm
    echo: "Polly.Matthew", // male, warm
    fable: "Polly.Amy", // British, expressive
    onyx: "Polly.Brian", // deep male
    nova: "Polly.Salli", // female, friendly
    shimmer: "Polly.Kimberly", // female, clear
};
/**
 * Default Polly voice when no mapping is found.
 */
exports.DEFAULT_POLLY_VOICE = "Polly.Joanna";
/**
 * Map OpenAI voice names to Twilio Polly equivalents.
 * Falls through if already a valid Polly/Google voice.
 *
 * @param voice - OpenAI voice name (alloy, echo, etc.) or Polly voice name
 * @returns Polly voice name suitable for Twilio TwiML
 */
function mapVoiceToPolly(voice) {
    if (!voice) {
        return exports.DEFAULT_POLLY_VOICE;
    }
    // Already a Polly/Google voice - pass through
    if (voice.startsWith("Polly.") || voice.startsWith("Google.")) {
        return voice;
    }
    // Map OpenAI voices to Polly equivalents
    return OPENAI_TO_POLLY_MAP[voice.toLowerCase()] || exports.DEFAULT_POLLY_VOICE;
}
/**
 * Check if a voice name is a known OpenAI voice.
 */
function isOpenAiVoice(voice) {
    return voice.toLowerCase() in OPENAI_TO_POLLY_MAP;
}
/**
 * Get all supported OpenAI voice names.
 */
function getOpenAiVoiceNames() {
    return Object.keys(OPENAI_TO_POLLY_MAP);
}
