"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.createMockBaileys = createMockBaileys;
const node_events_1 = require("node:events");
const vitest_1 = require("vitest");
function createMockBaileys() {
    const sockets = [];
    const makeWASocket = vitest_1.vi.fn((_opts) => {
        const ev = new node_events_1.EventEmitter();
        const sock = {
            ev,
            ws: { close: vitest_1.vi.fn() },
            sendPresenceUpdate: vitest_1.vi.fn().mockResolvedValue(undefined),
            sendMessage: vitest_1.vi.fn().mockResolvedValue({ key: { id: "msg123" } }),
            readMessages: vitest_1.vi.fn().mockResolvedValue(undefined),
            user: { id: "123@s.whatsapp.net" },
        };
        setImmediate(() => ev.emit("connection.update", { connection: "open" }));
        sockets.push(sock);
        return sock;
    });
    const mod = {
        DisconnectReason: { loggedOut: 401 },
        fetchLatestBaileysVersion: vitest_1.vi.fn().mockResolvedValue({ version: [1, 2, 3] }),
        makeCacheableSignalKeyStore: vitest_1.vi.fn((keys) => keys),
        makeWASocket,
        useMultiFileAuthState: vitest_1.vi.fn(async () => ({
            state: { creds: {}, keys: {} },
            saveCreds: vitest_1.vi.fn(),
        })),
        jidToE164: (jid) => jid.replace(/@.*$/, "").replace(/^/, "+"),
        downloadMediaMessage: vitest_1.vi.fn().mockResolvedValue(Buffer.from("img")),
    };
    return {
        mod,
        lastSocket: () => {
            const last = sockets.at(-1);
            if (!last) {
                throw new Error("No Baileys sockets created");
            }
            return last;
        },
    };
}
