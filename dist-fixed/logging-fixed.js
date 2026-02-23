"use strict";
// logging-fixed.ts - Versión CommonJS corregida
// Solución al problema "exports is not defined in ES module scope"
Object.defineProperty(exports, "__esModule", { value: true });
exports.DEFAULT_LOG_FILE = exports.DEFAULT_LOG_DIR = void 0;
exports.isFileLogLevelEnabled = isFileLogLevelEnabled;
exports.getLogger = getLogger;
exports.getChildLogger = getChildLogger;
exports.toPinoLikeLogger = toPinoLikeLogger;
const path_1 = require("path");
// CommonJS exports en lugar de ES module exports
exports.DEFAULT_LOG_DIR = process.env.CLAWCORE_LOG_DIR || path_1.default.join(process.cwd(), 'logs');
exports.DEFAULT_LOG_FILE = path_1.default.join(exports.DEFAULT_LOG_DIR, 'clawcore.log');
function isFileLogLevelEnabled(level) {
    return ['debug', 'info', 'warn', 'error'].includes(level.toLowerCase());
}
function getLogger(name) {
    return {
        debug: (msg) => console.debug(),
        info: (msg) => console.log(),
        warn: (msg) => console.warn(),
        error: (msg) => console.error()
    };
}
function getChildLogger(parent, name) {
    return getLogger();
}
function toPinoLikeLogger(logger) {
    return logger;
}
// Exportación CommonJS compatible
module.exports = {
    DEFAULT_LOG_DIR: exports.DEFAULT_LOG_DIR,
    DEFAULT_LOG_FILE: exports.DEFAULT_LOG_FILE,
    isFileLogLevelEnabled,
    getLogger,
    getChildLogger,
    toPinoLikeLogger
};
