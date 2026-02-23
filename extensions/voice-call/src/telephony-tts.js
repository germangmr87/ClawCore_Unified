"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.createTelephonyTtsProvider = createTelephonyTtsProvider;
const telephony_audio_js_1 = require("./telephony-audio.js");
function createTelephonyTtsProvider(params) {
    const { coreConfig, ttsOverride, runtime } = params;
    const mergedConfig = applyTtsOverride(coreConfig, ttsOverride);
    return {
        synthesizeForTelephony: async (text) => {
            const result = await runtime.textToSpeechTelephony({
                text,
                cfg: mergedConfig,
            });
            if (!result.success || !result.audioBuffer || !result.sampleRate) {
                throw new Error(result.error ?? "TTS conversion failed");
            }
            return (0, telephony_audio_js_1.convertPcmToMulaw8k)(result.audioBuffer, result.sampleRate);
        },
    };
}
function applyTtsOverride(coreConfig, override) {
    if (!override) {
        return coreConfig;
    }
    const base = coreConfig.messages?.tts;
    const merged = mergeTtsConfig(base, override);
    if (!merged) {
        return coreConfig;
    }
    return {
        ...coreConfig,
        messages: {
            ...coreConfig.messages,
            tts: merged,
        },
    };
}
function mergeTtsConfig(base, override) {
    if (!base && !override) {
        return undefined;
    }
    if (!override) {
        return base;
    }
    if (!base) {
        return override;
    }
    return deepMerge(base, override);
}
function deepMerge(base, override) {
    if (!isPlainObject(base) || !isPlainObject(override)) {
        return override;
    }
    const result = { ...base };
    for (const [key, value] of Object.entries(override)) {
        if (value === undefined) {
            continue;
        }
        const existing = base[key];
        if (isPlainObject(existing) && isPlainObject(value)) {
            result[key] = deepMerge(existing, value);
        }
        else {
            result[key] = value;
        }
    }
    return result;
}
function isPlainObject(value) {
    return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}
