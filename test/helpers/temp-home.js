"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.withTempHome = withTempHome;
const promises_1 = __importDefault(require("node:fs/promises"));
const node_os_1 = __importDefault(require("node:os"));
const node_path_1 = __importDefault(require("node:path"));
function snapshotEnv() {
    return {
        home: process.env.HOME,
        userProfile: process.env.USERPROFILE,
        homeDrive: process.env.HOMEDRIVE,
        homePath: process.env.HOMEPATH,
        clawcoreHome: process.env.CLAWCORE_HOME,
        stateDir: process.env.CLAWCORE_STATE_DIR,
    };
}
function restoreEnv(snapshot) {
    const restoreKey = (key, value) => {
        if (value === undefined) {
            delete process.env[key];
        }
        else {
            process.env[key] = value;
        }
    };
    restoreKey("HOME", snapshot.home);
    restoreKey("USERPROFILE", snapshot.userProfile);
    restoreKey("HOMEDRIVE", snapshot.homeDrive);
    restoreKey("HOMEPATH", snapshot.homePath);
    restoreKey("CLAWCORE_HOME", snapshot.clawcoreHome);
    restoreKey("CLAWCORE_STATE_DIR", snapshot.stateDir);
}
function snapshotExtraEnv(keys) {
    const snapshot = {};
    for (const key of keys) {
        snapshot[key] = process.env[key];
    }
    return snapshot;
}
function restoreExtraEnv(snapshot) {
    for (const [key, value] of Object.entries(snapshot)) {
        if (value === undefined) {
            delete process.env[key];
        }
        else {
            process.env[key] = value;
        }
    }
}
function setTempHome(base) {
    process.env.HOME = base;
    process.env.USERPROFILE = base;
    // Ensure tests using HOME isolation aren't affected by leaked CLAWCORE_HOME.
    delete process.env.CLAWCORE_HOME;
    process.env.CLAWCORE_STATE_DIR = node_path_1.default.join(base, ".clawcore");
    if (process.platform !== "win32") {
        return;
    }
    const match = base.match(/^([A-Za-z]:)(.*)$/);
    if (!match) {
        return;
    }
    process.env.HOMEDRIVE = match[1];
    process.env.HOMEPATH = match[2] || "\\";
}
async function withTempHome(fn, opts = {}) {
    const base = await promises_1.default.mkdtemp(node_path_1.default.join(node_os_1.default.tmpdir(), opts.prefix ?? "clawcore-test-home-"));
    const snapshot = snapshotEnv();
    const envKeys = Object.keys(opts.env ?? {});
    for (const key of envKeys) {
        if (key === "HOME" || key === "USERPROFILE" || key === "HOMEDRIVE" || key === "HOMEPATH") {
            throw new Error(`withTempHome: use built-in home env (got ${key})`);
        }
    }
    const envSnapshot = snapshotExtraEnv(envKeys);
    setTempHome(base);
    await promises_1.default.mkdir(node_path_1.default.join(base, ".clawcore", "agents", "main", "sessions"), { recursive: true });
    if (opts.env) {
        for (const [key, raw] of Object.entries(opts.env)) {
            const value = typeof raw === "function" ? raw(base) : raw;
            if (value === undefined) {
                delete process.env[key];
            }
            else {
                process.env[key] = value;
            }
        }
    }
    try {
        return await fn(base);
    }
    finally {
        restoreExtraEnv(envSnapshot);
        restoreEnv(snapshot);
        try {
            if (process.platform === "win32") {
                await promises_1.default.rm(base, {
                    recursive: true,
                    force: true,
                    maxRetries: 10,
                    retryDelay: 50,
                });
            }
            else {
                await promises_1.default.rm(base, {
                    recursive: true,
                    force: true,
                });
            }
        }
        catch {
            // ignore cleanup failures in tests
        }
    }
}
