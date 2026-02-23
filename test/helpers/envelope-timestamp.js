"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.escapeRegExp = void 0;
exports.formatEnvelopeTimestamp = formatEnvelopeTimestamp;
exports.formatLocalEnvelopeTimestamp = formatLocalEnvelopeTimestamp;
const format_datetime_js_1 = require("../../src/infra/format-time/format-datetime.js");
var utils_js_1 = require("../../src/utils.js");
Object.defineProperty(exports, "escapeRegExp", { enumerable: true, get: function () { return utils_js_1.escapeRegExp; } });
function formatEnvelopeTimestamp(date, zone = "utc") {
    const trimmedZone = zone.trim();
    const normalized = trimmedZone.toLowerCase();
    const weekday = (() => {
        try {
            if (normalized === "utc" || normalized === "gmt") {
                return new Intl.DateTimeFormat("en-US", { timeZone: "UTC", weekday: "short" }).format(date);
            }
            if (normalized === "local" || normalized === "host") {
                return new Intl.DateTimeFormat("en-US", { weekday: "short" }).format(date);
            }
            return new Intl.DateTimeFormat("en-US", { timeZone: trimmedZone, weekday: "short" }).format(date);
        }
        catch {
            return undefined;
        }
    })();
    if (normalized === "utc" || normalized === "gmt") {
        const ts = (0, format_datetime_js_1.formatUtcTimestamp)(date);
        return weekday ? `${weekday} ${ts}` : ts;
    }
    if (normalized === "local" || normalized === "host") {
        const ts = (0, format_datetime_js_1.formatZonedTimestamp)(date) ?? (0, format_datetime_js_1.formatUtcTimestamp)(date);
        return weekday ? `${weekday} ${ts}` : ts;
    }
    const ts = (0, format_datetime_js_1.formatZonedTimestamp)(date, { timeZone: trimmedZone }) ?? (0, format_datetime_js_1.formatUtcTimestamp)(date);
    return weekday ? `${weekday} ${ts}` : ts;
}
function formatLocalEnvelopeTimestamp(date) {
    return formatEnvelopeTimestamp(date, "local");
}
