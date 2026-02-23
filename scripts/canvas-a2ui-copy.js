"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.getA2uiPaths = getA2uiPaths;
exports.copyA2uiAssets = copyA2uiAssets;
const promises_1 = __importDefault(require("node:fs/promises"));
const node_path_1 = __importDefault(require("node:path"));
const node_url_1 = require("node:url");
const repoRoot = node_path_1.default.resolve(node_path_1.default.dirname((0, node_url_1.fileURLToPath)(import.meta.url)), "..");
function getA2uiPaths(env = process.env) {
    const srcDir = env.CLAWCORE_A2UI_SRC_DIR ?? node_path_1.default.join(repoRoot, "src", "canvas-host", "a2ui");
    const outDir = env.CLAWCORE_A2UI_OUT_DIR ?? node_path_1.default.join(repoRoot, "dist", "canvas-host", "a2ui");
    return { srcDir, outDir };
}
async function copyA2uiAssets({ srcDir, outDir }) {
    const skipMissing = process.env.CLAWCORE_A2UI_SKIP_MISSING === "1";
    try {
        await promises_1.default.stat(node_path_1.default.join(srcDir, "index.html"));
        await promises_1.default.stat(node_path_1.default.join(srcDir, "a2ui.bundle.js"));
    }
    catch (err) {
        const message = 'Missing A2UI bundle assets. Run "pnpm canvas:a2ui:bundle" and retry.';
        if (skipMissing) {
            console.warn(`${message} Skipping copy (CLAWCORE_A2UI_SKIP_MISSING=1).`);
            return;
        }
        throw new Error(message, { cause: err });
    }
    await promises_1.default.mkdir(node_path_1.default.dirname(outDir), { recursive: true });
    await promises_1.default.cp(srcDir, outDir, { recursive: true });
}
async function main() {
    const { srcDir, outDir } = getA2uiPaths();
    await copyA2uiAssets({ srcDir, outDir });
}
if (import.meta.url === (0, node_url_1.pathToFileURL)(process.argv[1] ?? "").href) {
    main().catch((err) => {
        console.error(String(err));
        process.exit(1);
    });
}
