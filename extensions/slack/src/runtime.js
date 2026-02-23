"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.setSlackRuntime = setSlackRuntime;
exports.getSlackRuntime = getSlackRuntime;
let runtime = null;
function setSlackRuntime(next) {
    runtime = next;
}
function getSlackRuntime() {
    if (!runtime) {
        throw new Error("Slack runtime not initialized");
    }
    return runtime;
}
