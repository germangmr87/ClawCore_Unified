"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.resolveUserPath = resolveUserPath;
const node_os_1 = __importDefault(require("node:os"));
const node_path_1 = __importDefault(require("node:path"));
function resolveUserPath(input) {
    const trimmed = input.trim();
    if (!trimmed) {
        return trimmed;
    }
    if (trimmed.startsWith("~")) {
        const expanded = trimmed.replace(/^~(?=$|[\\/])/, node_os_1.default.homedir());
        return node_path_1.default.resolve(expanded);
    }
    return node_path_1.default.resolve(trimmed);
}
