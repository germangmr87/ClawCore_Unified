"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.normalizeTestText = normalizeTestText;
const ansi_js_1 = require("../../src/terminal/ansi.js");
function normalizeTestText(input) {
    return (0, ansi_js_1.stripAnsi)(input)
        .replaceAll("\r\n", "\n")
        .replaceAll("…", "...")
        .replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g, "?")
        .replace(/[\uD800-\uDFFF]/g, "?");
}
