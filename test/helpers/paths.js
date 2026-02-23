"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.isPathWithinBase = isPathWithinBase;
const node_path_1 = __importDefault(require("node:path"));
function isPathWithinBase(base, target) {
    if (process.platform === "win32") {
        const normalizedBase = node_path_1.default.win32.normalize(node_path_1.default.win32.resolve(base));
        const normalizedTarget = node_path_1.default.win32.normalize(node_path_1.default.win32.resolve(target));
        const rel = node_path_1.default.win32.relative(normalizedBase.toLowerCase(), normalizedTarget.toLowerCase());
        return rel === "" || (!rel.startsWith("..") && !node_path_1.default.win32.isAbsolute(rel));
    }
    const normalizedBase = node_path_1.default.resolve(base);
    const normalizedTarget = node_path_1.default.resolve(target);
    const rel = node_path_1.default.relative(normalizedBase, normalizedTarget);
    return rel === "" || (!rel.startsWith("..") && !node_path_1.default.isAbsolute(rel));
}
