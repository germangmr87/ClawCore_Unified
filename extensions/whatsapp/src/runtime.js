"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.setWhatsAppRuntime = setWhatsAppRuntime;
exports.getWhatsAppRuntime = getWhatsAppRuntime;
let runtime = null;
function setWhatsAppRuntime(next) {
    runtime = next;
}
function getWhatsAppRuntime() {
    if (!runtime) {
        throw new Error("WhatsApp runtime not initialized");
    }
    return runtime;
}
