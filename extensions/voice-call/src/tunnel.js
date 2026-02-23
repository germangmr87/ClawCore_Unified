"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.startNgrokTunnel = startNgrokTunnel;
exports.isNgrokAvailable = isNgrokAvailable;
exports.startTailscaleTunnel = startTailscaleTunnel;
exports.startTunnel = startTunnel;
const node_child_process_1 = require("node:child_process");
const webhook_js_1 = require("./webhook.js");
/**
 * Start an ngrok tunnel to expose the local webhook server.
 *
 * Uses the ngrok CLI which must be installed: https://ngrok.com/download
 *
 * @example
 * const tunnel = await startNgrokTunnel({ port: 3334, path: '/voice/webhook' });
 * console.log('Public URL:', tunnel.publicUrl);
 * // Later: await tunnel.stop();
 */
async function startNgrokTunnel(config) {
    // Set auth token if provided
    if (config.authToken) {
        await runNgrokCommand(["config", "add-authtoken", config.authToken]);
    }
    // Build ngrok command args
    const args = ["http", String(config.port), "--log", "stdout", "--log-format", "json"];
    // Add custom domain if provided (paid ngrok feature)
    if (config.domain) {
        args.push("--domain", config.domain);
    }
    return new Promise((resolve, reject) => {
        const proc = (0, node_child_process_1.spawn)("ngrok", args, {
            stdio: ["ignore", "pipe", "pipe"],
        });
        let resolved = false;
        let publicUrl = null;
        let outputBuffer = "";
        const timeout = setTimeout(() => {
            if (!resolved) {
                resolved = true;
                proc.kill("SIGTERM");
                reject(new Error("ngrok startup timed out (30s)"));
            }
        }, 30000);
        const processLine = (line) => {
            try {
                const log = JSON.parse(line);
                // ngrok logs the public URL in a 'started tunnel' message
                if (log.msg === "started tunnel" && log.url) {
                    publicUrl = log.url;
                }
                // Also check for the URL field directly
                if (log.addr && log.url && !publicUrl) {
                    publicUrl = log.url;
                }
                // Check for ready state
                if (publicUrl && !resolved) {
                    resolved = true;
                    clearTimeout(timeout);
                    // Add path to the public URL
                    const fullUrl = publicUrl + config.path;
                    console.log(`[voice-call] ngrok tunnel active: ${fullUrl}`);
                    resolve({
                        publicUrl: fullUrl,
                        provider: "ngrok",
                        stop: async () => {
                            proc.kill("SIGTERM");
                            await new Promise((res) => {
                                proc.on("close", () => res());
                                setTimeout(res, 2000); // Fallback timeout
                            });
                        },
                    });
                }
            }
            catch {
                // Not JSON, might be startup message
            }
        };
        proc.stdout.on("data", (data) => {
            outputBuffer += data.toString();
            const lines = outputBuffer.split("\n");
            outputBuffer = lines.pop() || "";
            for (const line of lines) {
                if (line.trim()) {
                    processLine(line);
                }
            }
        });
        proc.stderr.on("data", (data) => {
            const msg = data.toString();
            // Check for common errors
            if (msg.includes("ERR_NGROK")) {
                if (!resolved) {
                    resolved = true;
                    clearTimeout(timeout);
                    reject(new Error(`ngrok error: ${msg}`));
                }
            }
        });
        proc.on("error", (err) => {
            if (!resolved) {
                resolved = true;
                clearTimeout(timeout);
                reject(new Error(`Failed to start ngrok: ${err.message}`));
            }
        });
        proc.on("close", (code) => {
            if (!resolved) {
                resolved = true;
                clearTimeout(timeout);
                reject(new Error(`ngrok exited unexpectedly with code ${code}`));
            }
        });
    });
}
/**
 * Run an ngrok command and wait for completion.
 */
async function runNgrokCommand(args) {
    return new Promise((resolve, reject) => {
        const proc = (0, node_child_process_1.spawn)("ngrok", args, {
            stdio: ["ignore", "pipe", "pipe"],
        });
        let stdout = "";
        let stderr = "";
        proc.stdout.on("data", (data) => {
            stdout += data.toString();
        });
        proc.stderr.on("data", (data) => {
            stderr += data.toString();
        });
        proc.on("close", (code) => {
            if (code === 0) {
                resolve(stdout);
            }
            else {
                reject(new Error(`ngrok command failed: ${stderr || stdout}`));
            }
        });
        proc.on("error", reject);
    });
}
/**
 * Check if ngrok is installed and available.
 */
async function isNgrokAvailable() {
    return new Promise((resolve) => {
        const proc = (0, node_child_process_1.spawn)("ngrok", ["version"], {
            stdio: ["ignore", "pipe", "pipe"],
        });
        proc.on("close", (code) => {
            resolve(code === 0);
        });
        proc.on("error", () => {
            resolve(false);
        });
    });
}
/**
 * Start a Tailscale serve/funnel tunnel.
 */
async function startTailscaleTunnel(config) {
    // Get Tailscale DNS name
    const dnsName = await (0, webhook_js_1.getTailscaleDnsName)();
    if (!dnsName) {
        throw new Error("Could not get Tailscale DNS name. Is Tailscale running?");
    }
    const path = config.path.startsWith("/") ? config.path : `/${config.path}`;
    const localUrl = `http://127.0.0.1:${config.port}${path}`;
    return new Promise((resolve, reject) => {
        const proc = (0, node_child_process_1.spawn)("tailscale", [config.mode, "--bg", "--yes", "--set-path", path, localUrl], {
            stdio: ["ignore", "pipe", "pipe"],
        });
        const timeout = setTimeout(() => {
            proc.kill("SIGKILL");
            reject(new Error(`Tailscale ${config.mode} timed out`));
        }, 10000);
        proc.on("close", (code) => {
            clearTimeout(timeout);
            if (code === 0) {
                const publicUrl = `https://${dnsName}${path}`;
                console.log(`[voice-call] Tailscale ${config.mode} active: ${publicUrl}`);
                resolve({
                    publicUrl,
                    provider: `tailscale-${config.mode}`,
                    stop: async () => {
                        await stopTailscaleTunnel(config.mode, path);
                    },
                });
            }
            else {
                reject(new Error(`Tailscale ${config.mode} failed with code ${code}`));
            }
        });
        proc.on("error", (err) => {
            clearTimeout(timeout);
            reject(err);
        });
    });
}
/**
 * Stop a Tailscale serve/funnel tunnel.
 */
async function stopTailscaleTunnel(mode, path) {
    return new Promise((resolve) => {
        const proc = (0, node_child_process_1.spawn)("tailscale", [mode, "off", path], {
            stdio: "ignore",
        });
        const timeout = setTimeout(() => {
            proc.kill("SIGKILL");
            resolve();
        }, 5000);
        proc.on("close", () => {
            clearTimeout(timeout);
            resolve();
        });
    });
}
/**
 * Start a tunnel based on configuration.
 */
async function startTunnel(config) {
    switch (config.provider) {
        case "ngrok":
            return startNgrokTunnel({
                port: config.port,
                path: config.path,
                authToken: config.ngrokAuthToken,
                domain: config.ngrokDomain,
            });
        case "tailscale-serve":
            return startTailscaleTunnel({
                mode: "serve",
                port: config.port,
                path: config.path,
            });
        case "tailscale-funnel":
            return startTailscaleTunnel({
                mode: "funnel",
                port: config.port,
                path: config.path,
            });
        default:
            return null;
    }
}
