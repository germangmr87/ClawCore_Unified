"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.verifyTwilioProviderWebhook = verifyTwilioProviderWebhook;
const webhook_security_js_1 = require("../../webhook-security.js");
function verifyTwilioProviderWebhook(params) {
    const result = (0, webhook_security_js_1.verifyTwilioWebhook)(params.ctx, params.authToken, {
        publicUrl: params.currentPublicUrl || undefined,
        allowNgrokFreeTierLoopbackBypass: params.options.allowNgrokFreeTierLoopbackBypass ?? false,
        skipVerification: params.options.skipVerification,
        allowedHosts: params.options.webhookSecurity?.allowedHosts,
        trustForwardingHeaders: params.options.webhookSecurity?.trustForwardingHeaders,
        trustedProxyIPs: params.options.webhookSecurity?.trustedProxyIPs,
        remoteIP: params.ctx.remoteAddress,
    });
    if (!result.ok) {
        console.warn(`[twilio] Webhook verification failed: ${result.reason}`);
        if (result.verificationUrl) {
            console.warn(`[twilio] Verification URL: ${result.verificationUrl}`);
        }
    }
    return {
        ok: result.ok,
        reason: result.reason,
    };
}
