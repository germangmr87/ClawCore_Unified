"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.setDiscordRuntime = setDiscordRuntime;
exports.getDiscordRuntime = getDiscordRuntime;
let runtime = null;
function setDiscordRuntime(next) {
    runtime = next;
}
function getDiscordRuntime() {
    if (!runtime) {
        throw new Error("Discord runtime not initialized");
    }
    return runtime;
}
