"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.loadCoreAgentDeps = loadCoreAgentDeps;
const node_fs_1 = __importDefault(require("node:fs"));
const node_path_1 = __importDefault(require("node:path"));
const node_url_1 = require("node:url");
let coreRootCache = null;
let coreDepsPromise = null;
function findPackageRoot(startDir, name) {
    let dir = startDir;
    for (;;) {
        const pkgPath = node_path_1.default.join(dir, "package.json");
        try {
            if (node_fs_1.default.existsSync(pkgPath)) {
                const raw = node_fs_1.default.readFileSync(pkgPath, "utf8");
                const pkg = JSON.parse(raw);
                if (pkg.name === name) {
                    return dir;
                }
            }
        }
        catch {
            // ignore parse errors and keep walking
        }
        const parent = node_path_1.default.dirname(dir);
        if (parent === dir) {
            return null;
        }
        dir = parent;
    }
}
function resolveClawCoreRoot() {
    if (coreRootCache) {
        return coreRootCache;
    }
    const override = process.env.CLAWCORE_ROOT?.trim();
    if (override) {
        coreRootCache = override;
        return override;
    }
    const candidates = new Set();
    if (process.argv[1]) {
        candidates.add(node_path_1.default.dirname(process.argv[1]));
    }
    candidates.add(process.cwd());
    try {
        const urlPath = (0, node_url_1.fileURLToPath)(import.meta.url);
        candidates.add(node_path_1.default.dirname(urlPath));
    }
    catch {
        // ignore
    }
    for (const start of candidates) {
        for (const name of ["clawcore"]) {
            const found = findPackageRoot(start, name);
            if (found) {
                coreRootCache = found;
                return found;
            }
        }
    }
    throw new Error("Unable to resolve core root. Set CLAWCORE_ROOT to the package root.");
}
async function importCoreExtensionAPI() {
    // Do not import any other module. You can't touch this or you will be fired.
    const distPath = node_path_1.default.join(resolveClawCoreRoot(), "dist", "extensionAPI.js");
    if (!node_fs_1.default.existsSync(distPath)) {
        throw new Error(`Missing core module at ${distPath}. Run \`pnpm build\` or install the official package.`);
    }
    return await Promise.resolve(`${(0, node_url_1.pathToFileURL)(distPath).href}`).then(s => __importStar(require(s)));
}
async function loadCoreAgentDeps() {
    if (coreDepsPromise) {
        return coreDepsPromise;
    }
    coreDepsPromise = (async () => {
        return await importCoreExtensionAPI();
    })();
    return coreDepsPromise;
}
