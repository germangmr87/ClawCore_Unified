"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.expectInboundContextContract = expectInboundContextContract;
const vitest_1 = require("vitest");
const chat_type_js_1 = require("../../src/channels/chat-type.js");
const conversation_label_js_1 = require("../../src/channels/conversation-label.js");
const sender_identity_js_1 = require("../../src/channels/sender-identity.js");
function expectInboundContextContract(ctx) {
    (0, vitest_1.expect)((0, sender_identity_js_1.validateSenderIdentity)(ctx)).toEqual([]);
    (0, vitest_1.expect)(ctx.Body).toBeTypeOf("string");
    (0, vitest_1.expect)(ctx.BodyForAgent).toBeTypeOf("string");
    (0, vitest_1.expect)(ctx.BodyForCommands).toBeTypeOf("string");
    const chatType = (0, chat_type_js_1.normalizeChatType)(ctx.ChatType);
    if (chatType && chatType !== "direct") {
        const label = ctx.ConversationLabel?.trim() || (0, conversation_label_js_1.resolveConversationLabel)(ctx);
        (0, vitest_1.expect)(label).toBeTruthy();
    }
}
