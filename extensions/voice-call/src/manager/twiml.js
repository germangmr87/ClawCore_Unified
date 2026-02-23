"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.generateNotifyTwiml = generateNotifyTwiml;
const voice_mapping_js_1 = require("../voice-mapping.js");
function generateNotifyTwiml(message, voice) {
    return `<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="${voice}">${(0, voice_mapping_js_1.escapeXml)(message)}</Say>
  <Hangup/>
</Response>`;
}
