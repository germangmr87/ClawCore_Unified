"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.validateTwilioSignature = validateTwilioSignature;
exports.reconstructWebhookUrl = reconstructWebhookUrl;
exports.verifyTelnyxWebhook = verifyTelnyxWebhook;
exports.verifyTwilioWebhook = verifyTwilioWebhook;
exports.verifyPlivoWebhook = verifyPlivoWebhook;
const node_crypto_1 = __importDefault(require("node:crypto"));
/**
 * Validate Twilio webhook signature using HMAC-SHA1.
 *
 * Twilio signs requests by concatenating the URL with sorted POST params,
 * then computing HMAC-SHA1 with the auth token.
 *
 * @see https://www.twilio.com/docs/usage/webhooks/webhooks-security
 */
function validateTwilioSignature(authToken, signature, url, params) {
    if (!signature) {
        return false;
    }
    // Build the string to sign: URL + sorted params (key+value pairs)
    let dataToSign = url;
    // Sort params alphabetically and append key+value
    const sortedParams = Array.from(params.entries()).toSorted((a, b) => a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0);
    for (const [key, value] of sortedParams) {
        dataToSign += key + value;
    }
    // HMAC-SHA1 with auth token, then base64 encode
    const expectedSignature = node_crypto_1.default
        .createHmac("sha1", authToken)
        .update(dataToSign)
        .digest("base64");
    // Use timing-safe comparison to prevent timing attacks
    return timingSafeEqual(signature, expectedSignature);
}
/**
 * Timing-safe string comparison to prevent timing attacks.
 */
function timingSafeEqual(a, b) {
    if (a.length !== b.length) {
        // Still do comparison to maintain constant time
        const dummy = Buffer.from(a);
        node_crypto_1.default.timingSafeEqual(dummy, dummy);
        return false;
    }
    const bufA = Buffer.from(a);
    const bufB = Buffer.from(b);
    return node_crypto_1.default.timingSafeEqual(bufA, bufB);
}
/**
 * Validate that a hostname matches RFC 1123 format.
 * Prevents injection of malformed hostnames.
 */
function isValidHostname(hostname) {
    if (!hostname || hostname.length > 253) {
        return false;
    }
    // RFC 1123 hostname: alphanumeric, hyphens, dots
    // Also allow ngrok/tunnel subdomains
    const hostnameRegex = /^([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$/;
    return hostnameRegex.test(hostname);
}
/**
 * Safely extract hostname from a host header value.
 * Handles IPv6 addresses and prevents injection via malformed values.
 */
function extractHostname(hostHeader) {
    if (!hostHeader) {
        return null;
    }
    let hostname;
    // Handle IPv6 addresses: [::1]:8080
    if (hostHeader.startsWith("[")) {
        const endBracket = hostHeader.indexOf("]");
        if (endBracket === -1) {
            return null; // Malformed IPv6
        }
        hostname = hostHeader.substring(1, endBracket);
        return hostname.toLowerCase();
    }
    // Handle IPv4/domain with optional port
    // Check for @ which could indicate user info injection attempt
    if (hostHeader.includes("@")) {
        return null; // Reject potential injection: attacker.com:80@legitimate.com
    }
    hostname = hostHeader.split(":")[0];
    // Validate the extracted hostname
    if (!isValidHostname(hostname)) {
        return null;
    }
    return hostname.toLowerCase();
}
function extractHostnameFromHeader(headerValue) {
    const first = headerValue.split(",")[0]?.trim();
    if (!first) {
        return null;
    }
    return extractHostname(first);
}
function normalizeAllowedHosts(allowedHosts) {
    if (!allowedHosts || allowedHosts.length === 0) {
        return null;
    }
    const normalized = new Set();
    for (const host of allowedHosts) {
        const extracted = extractHostname(host.trim());
        if (extracted) {
            normalized.add(extracted);
        }
    }
    return normalized.size > 0 ? normalized : null;
}
/**
 * Reconstruct the public webhook URL from request headers.
 *
 * SECURITY: This function validates host headers to prevent host header
 * injection attacks. When using forwarding headers (X-Forwarded-Host, etc.),
 * always provide allowedHosts to whitelist valid hostnames.
 *
 * When behind a reverse proxy (Tailscale, nginx, ngrok), the original URL
 * used by Twilio differs from the local request URL. We use standard
 * forwarding headers to reconstruct it.
 *
 * Priority order:
 * 1. X-Forwarded-Proto + X-Forwarded-Host (standard proxy headers)
 * 2. X-Original-Host (nginx)
 * 3. Ngrok-Forwarded-Host (ngrok specific)
 * 4. Host header (direct connection)
 */
function reconstructWebhookUrl(ctx, options) {
    const { headers } = ctx;
    // SECURITY: Only trust forwarding headers if explicitly configured.
    // Either allowedHosts must be set (for whitelist validation) or
    // trustForwardingHeaders must be true (explicit opt-in to trust).
    const allowedHosts = normalizeAllowedHosts(options?.allowedHosts);
    const hasAllowedHosts = allowedHosts !== null;
    const explicitlyTrusted = options?.trustForwardingHeaders === true;
    // Also check trusted proxy IPs if configured
    const trustedProxyIPs = options?.trustedProxyIPs?.filter(Boolean) ?? [];
    const hasTrustedProxyIPs = trustedProxyIPs.length > 0;
    const remoteIP = options?.remoteIP ?? ctx.remoteAddress;
    const fromTrustedProxy = !hasTrustedProxyIPs || (remoteIP ? trustedProxyIPs.includes(remoteIP) : false);
    // Only trust forwarding headers if: (has whitelist OR explicitly trusted) AND from trusted proxy
    const shouldTrustForwardingHeaders = (hasAllowedHosts || explicitlyTrusted) && fromTrustedProxy;
    const isAllowedForwardedHost = (host) => !allowedHosts || allowedHosts.has(host);
    // Determine protocol - only trust X-Forwarded-Proto from trusted proxies
    let proto = "https";
    if (shouldTrustForwardingHeaders) {
        const forwardedProto = getHeader(headers, "x-forwarded-proto");
        if (forwardedProto === "http" || forwardedProto === "https") {
            proto = forwardedProto;
        }
    }
    // Determine host - with security validation
    let host = null;
    if (shouldTrustForwardingHeaders) {
        // Try forwarding headers in priority order
        const forwardingHeaders = ["x-forwarded-host", "x-original-host", "ngrok-forwarded-host"];
        for (const headerName of forwardingHeaders) {
            const headerValue = getHeader(headers, headerName);
            if (headerValue) {
                const extracted = extractHostnameFromHeader(headerValue);
                if (extracted && isAllowedForwardedHost(extracted)) {
                    host = extracted;
                    break;
                }
            }
        }
    }
    // Fallback to Host header if no valid forwarding header found
    if (!host) {
        const hostHeader = getHeader(headers, "host");
        if (hostHeader) {
            const extracted = extractHostnameFromHeader(hostHeader);
            if (extracted) {
                host = extracted;
            }
        }
    }
    // Last resort: try to extract from ctx.url
    if (!host) {
        try {
            const parsed = new URL(ctx.url);
            const extracted = extractHostname(parsed.host);
            if (extracted) {
                host = extracted;
            }
        }
        catch {
            // URL parsing failed - use empty string (will result in invalid URL)
            host = "";
        }
    }
    if (!host) {
        host = "";
    }
    // Extract path from the context URL (fallback to "/" on parse failure)
    let path = "/";
    try {
        const parsed = new URL(ctx.url);
        path = parsed.pathname + parsed.search;
    }
    catch {
        // URL parsing failed
    }
    return `${proto}://${host}${path}`;
}
function buildTwilioVerificationUrl(ctx, publicUrl, urlOptions) {
    if (!publicUrl) {
        return reconstructWebhookUrl(ctx, urlOptions);
    }
    try {
        const base = new URL(publicUrl);
        const requestUrl = new URL(ctx.url);
        base.pathname = requestUrl.pathname;
        base.search = requestUrl.search;
        return base.toString();
    }
    catch {
        return publicUrl;
    }
}
/**
 * Get a header value, handling both string and string[] types.
 */
function getHeader(headers, name) {
    const value = headers[name.toLowerCase()];
    if (Array.isArray(value)) {
        return value[0];
    }
    return value;
}
function isLoopbackAddress(address) {
    if (!address) {
        return false;
    }
    if (address === "127.0.0.1" || address === "::1") {
        return true;
    }
    if (address.startsWith("::ffff:127.")) {
        return true;
    }
    return false;
}
function decodeBase64OrBase64Url(input) {
    // Telnyx docs say Base64; some tooling emits Base64URL. Accept both.
    const normalized = input.replace(/-/g, "+").replace(/_/g, "/");
    const padLen = (4 - (normalized.length % 4)) % 4;
    const padded = normalized + "=".repeat(padLen);
    return Buffer.from(padded, "base64");
}
function base64UrlEncode(buf) {
    return buf.toString("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}
function importEd25519PublicKey(publicKey) {
    const trimmed = publicKey.trim();
    // PEM (spki) support.
    if (trimmed.startsWith("-----BEGIN")) {
        return trimmed;
    }
    // Base64-encoded raw Ed25519 key (32 bytes) or Base64-encoded DER SPKI key.
    const decoded = decodeBase64OrBase64Url(trimmed);
    if (decoded.length === 32) {
        // JWK is the easiest portable way to import raw Ed25519 keys in Node crypto.
        return node_crypto_1.default.createPublicKey({
            key: { kty: "OKP", crv: "Ed25519", x: base64UrlEncode(decoded) },
            format: "jwk",
        });
    }
    return node_crypto_1.default.createPublicKey({
        key: decoded,
        format: "der",
        type: "spki",
    });
}
/**
 * Verify Telnyx webhook signature using Ed25519.
 *
 * Telnyx signs `timestamp|payload` and provides:
 * - `telnyx-signature-ed25519` (Base64 signature)
 * - `telnyx-timestamp` (Unix seconds)
 */
function verifyTelnyxWebhook(ctx, publicKey, options) {
    if (options?.skipVerification) {
        return { ok: true, reason: "verification skipped (dev mode)" };
    }
    if (!publicKey) {
        return { ok: false, reason: "Missing telnyx.publicKey (configure to verify webhooks)" };
    }
    const signature = getHeader(ctx.headers, "telnyx-signature-ed25519");
    const timestamp = getHeader(ctx.headers, "telnyx-timestamp");
    if (!signature || !timestamp) {
        return { ok: false, reason: "Missing signature or timestamp header" };
    }
    const eventTimeSec = parseInt(timestamp, 10);
    if (!Number.isFinite(eventTimeSec)) {
        return { ok: false, reason: "Invalid timestamp header" };
    }
    try {
        const signedPayload = `${timestamp}|${ctx.rawBody}`;
        const signatureBuffer = decodeBase64OrBase64Url(signature);
        const key = importEd25519PublicKey(publicKey);
        const isValid = node_crypto_1.default.verify(null, Buffer.from(signedPayload), key, signatureBuffer);
        if (!isValid) {
            return { ok: false, reason: "Invalid signature" };
        }
        const maxSkewMs = options?.maxSkewMs ?? 5 * 60 * 1000;
        const eventTimeMs = eventTimeSec * 1000;
        const now = Date.now();
        if (Math.abs(now - eventTimeMs) > maxSkewMs) {
            return { ok: false, reason: "Timestamp too old" };
        }
        return { ok: true };
    }
    catch (err) {
        return {
            ok: false,
            reason: `Verification error: ${err instanceof Error ? err.message : String(err)}`,
        };
    }
}
/**
 * Verify Twilio webhook with full context and detailed result.
 */
function verifyTwilioWebhook(ctx, authToken, options) {
    // Allow skipping verification for development/testing
    if (options?.skipVerification) {
        return { ok: true, reason: "verification skipped (dev mode)" };
    }
    const signature = getHeader(ctx.headers, "x-twilio-signature");
    if (!signature) {
        return { ok: false, reason: "Missing X-Twilio-Signature header" };
    }
    const isLoopback = isLoopbackAddress(options?.remoteIP ?? ctx.remoteAddress);
    const allowLoopbackForwarding = options?.allowNgrokFreeTierLoopbackBypass && isLoopback;
    // Reconstruct the URL Twilio used
    const verificationUrl = buildTwilioVerificationUrl(ctx, options?.publicUrl, {
        allowedHosts: options?.allowedHosts,
        trustForwardingHeaders: options?.trustForwardingHeaders || allowLoopbackForwarding,
        trustedProxyIPs: options?.trustedProxyIPs,
        remoteIP: options?.remoteIP,
    });
    // Parse the body as URL-encoded params
    const params = new URLSearchParams(ctx.rawBody);
    // Validate signature
    const isValid = validateTwilioSignature(authToken, signature, verificationUrl, params);
    if (isValid) {
        return { ok: true, verificationUrl };
    }
    // Check if this is ngrok free tier - the URL might have different format
    const isNgrokFreeTier = verificationUrl.includes(".ngrok-free.app") || verificationUrl.includes(".ngrok.io");
    return {
        ok: false,
        reason: `Invalid signature for URL: ${verificationUrl}`,
        verificationUrl,
        isNgrokFreeTier,
    };
}
function normalizeSignatureBase64(input) {
    // Canonicalize base64 to match Plivo SDK behavior (decode then re-encode).
    return Buffer.from(input, "base64").toString("base64");
}
function getBaseUrlNoQuery(url) {
    const u = new URL(url);
    return `${u.protocol}//${u.host}${u.pathname}`;
}
function timingSafeEqualString(a, b) {
    if (a.length !== b.length) {
        const dummy = Buffer.from(a);
        node_crypto_1.default.timingSafeEqual(dummy, dummy);
        return false;
    }
    return node_crypto_1.default.timingSafeEqual(Buffer.from(a), Buffer.from(b));
}
function validatePlivoV2Signature(params) {
    const baseUrl = getBaseUrlNoQuery(params.url);
    const digest = node_crypto_1.default
        .createHmac("sha256", params.authToken)
        .update(baseUrl + params.nonce)
        .digest("base64");
    const expected = normalizeSignatureBase64(digest);
    const provided = normalizeSignatureBase64(params.signature);
    return timingSafeEqualString(expected, provided);
}
function toParamMapFromSearchParams(sp) {
    const map = {};
    for (const [key, value] of sp.entries()) {
        if (!map[key]) {
            map[key] = [];
        }
        map[key].push(value);
    }
    return map;
}
function sortedQueryString(params) {
    const parts = [];
    for (const key of Object.keys(params).toSorted()) {
        const values = [...params[key]].toSorted();
        for (const value of values) {
            parts.push(`${key}=${value}`);
        }
    }
    return parts.join("&");
}
function sortedParamsString(params) {
    const parts = [];
    for (const key of Object.keys(params).toSorted()) {
        const values = [...params[key]].toSorted();
        for (const value of values) {
            parts.push(`${key}${value}`);
        }
    }
    return parts.join("");
}
function constructPlivoV3BaseUrl(params) {
    const hasPostParams = Object.keys(params.postParams).length > 0;
    const u = new URL(params.url);
    const baseNoQuery = `${u.protocol}//${u.host}${u.pathname}`;
    const queryMap = toParamMapFromSearchParams(u.searchParams);
    const queryString = sortedQueryString(queryMap);
    // In the Plivo V3 algorithm, the query portion is always sorted, and if we
    // have POST params we add a '.' separator after the query string.
    let baseUrl = baseNoQuery;
    if (queryString.length > 0 || hasPostParams) {
        baseUrl = `${baseNoQuery}?${queryString}`;
    }
    if (queryString.length > 0 && hasPostParams) {
        baseUrl = `${baseUrl}.`;
    }
    if (params.method === "GET") {
        return baseUrl;
    }
    return baseUrl + sortedParamsString(params.postParams);
}
function validatePlivoV3Signature(params) {
    const baseUrl = constructPlivoV3BaseUrl({
        method: params.method,
        url: params.url,
        postParams: params.postParams,
    });
    const hmacBase = `${baseUrl}.${params.nonce}`;
    const digest = node_crypto_1.default.createHmac("sha256", params.authToken).update(hmacBase).digest("base64");
    const expected = normalizeSignatureBase64(digest);
    // Header can contain multiple signatures separated by commas.
    const provided = params.signatureHeader
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean)
        .map((s) => normalizeSignatureBase64(s));
    for (const sig of provided) {
        if (timingSafeEqualString(expected, sig)) {
            return true;
        }
    }
    return false;
}
/**
 * Verify Plivo webhooks using V3 signature if present; fall back to V2.
 *
 * Header names (case-insensitive; Node provides lower-case keys):
 * - V3: X-Plivo-Signature-V3 / X-Plivo-Signature-V3-Nonce
 * - V2: X-Plivo-Signature-V2 / X-Plivo-Signature-V2-Nonce
 */
function verifyPlivoWebhook(ctx, authToken, options) {
    if (options?.skipVerification) {
        return { ok: true, reason: "verification skipped (dev mode)" };
    }
    const signatureV3 = getHeader(ctx.headers, "x-plivo-signature-v3");
    const nonceV3 = getHeader(ctx.headers, "x-plivo-signature-v3-nonce");
    const signatureV2 = getHeader(ctx.headers, "x-plivo-signature-v2");
    const nonceV2 = getHeader(ctx.headers, "x-plivo-signature-v2-nonce");
    const reconstructed = reconstructWebhookUrl(ctx, {
        allowedHosts: options?.allowedHosts,
        trustForwardingHeaders: options?.trustForwardingHeaders,
        trustedProxyIPs: options?.trustedProxyIPs,
        remoteIP: options?.remoteIP,
    });
    let verificationUrl = reconstructed;
    if (options?.publicUrl) {
        try {
            const req = new URL(reconstructed);
            const base = new URL(options.publicUrl);
            base.pathname = req.pathname;
            base.search = req.search;
            verificationUrl = base.toString();
        }
        catch {
            verificationUrl = reconstructed;
        }
    }
    if (signatureV3 && nonceV3) {
        const method = ctx.method === "GET" || ctx.method === "POST" ? ctx.method : null;
        if (!method) {
            return {
                ok: false,
                version: "v3",
                verificationUrl,
                reason: `Unsupported HTTP method for Plivo V3 signature: ${ctx.method}`,
            };
        }
        const postParams = toParamMapFromSearchParams(new URLSearchParams(ctx.rawBody));
        const ok = validatePlivoV3Signature({
            authToken,
            signatureHeader: signatureV3,
            nonce: nonceV3,
            method,
            url: verificationUrl,
            postParams,
        });
        return ok
            ? { ok: true, version: "v3", verificationUrl }
            : {
                ok: false,
                version: "v3",
                verificationUrl,
                reason: "Invalid Plivo V3 signature",
            };
    }
    if (signatureV2 && nonceV2) {
        const ok = validatePlivoV2Signature({
            authToken,
            signature: signatureV2,
            nonce: nonceV2,
            url: verificationUrl,
        });
        return ok
            ? { ok: true, version: "v2", verificationUrl }
            : {
                ok: false,
                version: "v2",
                verificationUrl,
                reason: "Invalid Plivo V2 signature",
            };
    }
    return {
        ok: false,
        reason: "Missing Plivo signature headers (V3 or V2)",
        verificationUrl,
    };
}
