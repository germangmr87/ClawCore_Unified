"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.setTelegramRuntime = setTelegramRuntime;
exports.getTelegramRuntime = getTelegramRuntime;
let runtime = null;
function setTelegramRuntime(next) {
    runtime = next;
}
function getTelegramRuntime() {
    if (!runtime) {
        throw new Error("Telegram runtime not initialized");
    }
    return runtime;
}
