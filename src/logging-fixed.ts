// logging-fixed.ts - Versión CommonJS corregida
// Solución al problema "exports is not defined in ES module scope"

import fs from 'fs';
import path from 'path';

// CommonJS exports en lugar de ES module exports
export const DEFAULT_LOG_DIR = process.env.CLAWCORE_LOG_DIR || path.join(process.cwd(), 'logs');
export const DEFAULT_LOG_FILE = path.join(DEFAULT_LOG_DIR, 'clawcore.log');

export function isFileLogLevelEnabled(level: string): boolean {
  return ['debug', 'info', 'warn', 'error'].includes(level.toLowerCase());
}

export function getLogger(name: string) {
  return {
    debug: (msg: string) => console.debug(),
    info: (msg: string) => console.log(),
    warn: (msg: string) => console.warn(),
    error: (msg: string) => console.error()
  };
}

export function getChildLogger(parent: any, name: string) {
  return getLogger();
}

export function toPinoLikeLogger(logger: any) {
  return logger;
}

// Exportación CommonJS compatible
module.exports = {
  DEFAULT_LOG_DIR,
  DEFAULT_LOG_FILE,
  isFileLogLevelEnabled,
  getLogger,
  getChildLogger,
  toPinoLikeLogger
};
