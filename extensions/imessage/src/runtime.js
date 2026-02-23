"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.setIMessageRuntime = setIMessageRuntime;
exports.getIMessageRuntime = getIMessageRuntime;
let runtime = null;
function setIMessageRuntime(next) {
    runtime = next;
}
function getIMessageRuntime() {
    if (!runtime) {
        throw new Error("iMessage runtime not initialized");
    }
    return runtime;
}
