"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.signalPlugin = void 0;
const plugin_sdk_1 = require("clawcore/plugin-sdk");
const runtime_js_1 = require("./runtime.js");
const signalMessageActions = {
    listActions: (ctx) => (0, runtime_js_1.getSignalRuntime)().channel.signal.messageActions?.listActions?.(ctx) ?? [],
    supportsAction: (ctx) => (0, runtime_js_1.getSignalRuntime)().channel.signal.messageActions?.supportsAction?.(ctx) ?? false,
    handleAction: async (ctx) => {
        const ma = (0, runtime_js_1.getSignalRuntime)().channel.signal.messageActions;
        if (!ma?.handleAction) {
            throw new Error("Signal message actions not available");
        }
        return ma.handleAction(ctx);
    },
};
const meta = (0, plugin_sdk_1.getChatChannelMeta)("signal");
exports.signalPlugin = {
    id: "signal",
    meta: {
        ...meta,
    },
    onboarding: plugin_sdk_1.signalOnboardingAdapter,
    pairing: {
        idLabel: "signalNumber",
        normalizeAllowEntry: (entry) => entry.replace(/^signal:/i, ""),
        notifyApproval: async ({ id }) => {
            await (0, runtime_js_1.getSignalRuntime)().channel.signal.sendMessageSignal(id, plugin_sdk_1.PAIRING_APPROVED_MESSAGE);
        },
    },
    capabilities: {
        chatTypes: ["direct", "group"],
        media: true,
        reactions: true,
    },
    actions: signalMessageActions,
    streaming: {
        blockStreamingCoalesceDefaults: { minChars: 1500, idleMs: 1000 },
    },
    reload: { configPrefixes: ["channels.signal"] },
    configSchema: (0, plugin_sdk_1.buildChannelConfigSchema)(plugin_sdk_1.SignalConfigSchema),
    config: {
        listAccountIds: (cfg) => (0, plugin_sdk_1.listSignalAccountIds)(cfg),
        resolveAccount: (cfg, accountId) => (0, plugin_sdk_1.resolveSignalAccount)({ cfg, accountId }),
        defaultAccountId: (cfg) => (0, plugin_sdk_1.resolveDefaultSignalAccountId)(cfg),
        setAccountEnabled: ({ cfg, accountId, enabled }) => (0, plugin_sdk_1.setAccountEnabledInConfigSection)({
            cfg,
            sectionKey: "signal",
            accountId,
            enabled,
            allowTopLevel: true,
        }),
        deleteAccount: ({ cfg, accountId }) => (0, plugin_sdk_1.deleteAccountFromConfigSection)({
            cfg,
            sectionKey: "signal",
            accountId,
            clearBaseFields: ["account", "httpUrl", "httpHost", "httpPort", "cliPath", "name"],
        }),
        isConfigured: (account) => account.configured,
        describeAccount: (account) => ({
            accountId: account.accountId,
            name: account.name,
            enabled: account.enabled,
            configured: account.configured,
            baseUrl: account.baseUrl,
        }),
        resolveAllowFrom: ({ cfg, accountId }) => ((0, plugin_sdk_1.resolveSignalAccount)({ cfg, accountId }).config.allowFrom ?? []).map((entry) => String(entry)),
        formatAllowFrom: ({ allowFrom }) => allowFrom
            .map((entry) => String(entry).trim())
            .filter(Boolean)
            .map((entry) => (entry === "*" ? "*" : (0, plugin_sdk_1.normalizeE164)(entry.replace(/^signal:/i, ""))))
            .filter(Boolean),
    },
    security: {
        resolveDmPolicy: ({ cfg, accountId, account }) => {
            const resolvedAccountId = accountId ?? account.accountId ?? plugin_sdk_1.DEFAULT_ACCOUNT_ID;
            const useAccountPath = Boolean(cfg.channels?.signal?.accounts?.[resolvedAccountId]);
            const basePath = useAccountPath
                ? `channels.signal.accounts.${resolvedAccountId}.`
                : "channels.signal.";
            return {
                policy: account.config.dmPolicy ?? "pairing",
                allowFrom: account.config.allowFrom ?? [],
                policyPath: `${basePath}dmPolicy`,
                allowFromPath: basePath,
                approveHint: (0, plugin_sdk_1.formatPairingApproveHint)("signal"),
                normalizeEntry: (raw) => (0, plugin_sdk_1.normalizeE164)(raw.replace(/^signal:/i, "").trim()),
            };
        },
        collectWarnings: ({ account, cfg }) => {
            const defaultGroupPolicy = cfg.channels?.defaults?.groupPolicy;
            const groupPolicy = account.config.groupPolicy ?? defaultGroupPolicy ?? "allowlist";
            if (groupPolicy !== "open") {
                return [];
            }
            return [
                `- Signal groups: groupPolicy="open" allows any member to trigger the bot. Set channels.signal.groupPolicy="allowlist" + channels.signal.groupAllowFrom to restrict senders.`,
            ];
        },
    },
    messaging: {
        normalizeTarget: plugin_sdk_1.normalizeSignalMessagingTarget,
        targetResolver: {
            looksLikeId: plugin_sdk_1.looksLikeSignalTargetId,
            hint: "<E.164|uuid:ID|group:ID|signal:group:ID|signal:+E.164>",
        },
    },
    setup: {
        resolveAccountId: ({ accountId }) => (0, plugin_sdk_1.normalizeAccountId)(accountId),
        applyAccountName: ({ cfg, accountId, name }) => (0, plugin_sdk_1.applyAccountNameToChannelSection)({
            cfg,
            channelKey: "signal",
            accountId,
            name,
        }),
        validateInput: ({ input }) => {
            if (!input.signalNumber &&
                !input.httpUrl &&
                !input.httpHost &&
                !input.httpPort &&
                !input.cliPath) {
                return "Signal requires --signal-number or --http-url/--http-host/--http-port/--cli-path.";
            }
            return null;
        },
        applyAccountConfig: ({ cfg, accountId, input }) => {
            const namedConfig = (0, plugin_sdk_1.applyAccountNameToChannelSection)({
                cfg,
                channelKey: "signal",
                accountId,
                name: input.name,
            });
            const next = accountId !== plugin_sdk_1.DEFAULT_ACCOUNT_ID
                ? (0, plugin_sdk_1.migrateBaseNameToDefaultAccount)({
                    cfg: namedConfig,
                    channelKey: "signal",
                })
                : namedConfig;
            if (accountId === plugin_sdk_1.DEFAULT_ACCOUNT_ID) {
                return {
                    ...next,
                    channels: {
                        ...next.channels,
                        signal: {
                            ...next.channels?.signal,
                            enabled: true,
                            ...(input.signalNumber ? { account: input.signalNumber } : {}),
                            ...(input.cliPath ? { cliPath: input.cliPath } : {}),
                            ...(input.httpUrl ? { httpUrl: input.httpUrl } : {}),
                            ...(input.httpHost ? { httpHost: input.httpHost } : {}),
                            ...(input.httpPort ? { httpPort: Number(input.httpPort) } : {}),
                        },
                    },
                };
            }
            return {
                ...next,
                channels: {
                    ...next.channels,
                    signal: {
                        ...next.channels?.signal,
                        enabled: true,
                        accounts: {
                            ...next.channels?.signal?.accounts,
                            [accountId]: {
                                ...next.channels?.signal?.accounts?.[accountId],
                                enabled: true,
                                ...(input.signalNumber ? { account: input.signalNumber } : {}),
                                ...(input.cliPath ? { cliPath: input.cliPath } : {}),
                                ...(input.httpUrl ? { httpUrl: input.httpUrl } : {}),
                                ...(input.httpHost ? { httpHost: input.httpHost } : {}),
                                ...(input.httpPort ? { httpPort: Number(input.httpPort) } : {}),
                            },
                        },
                    },
                },
            };
        },
    },
    outbound: {
        deliveryMode: "direct",
        chunker: (text, limit) => (0, runtime_js_1.getSignalRuntime)().channel.text.chunkText(text, limit),
        chunkerMode: "text",
        textChunkLimit: 4000,
        sendText: async ({ cfg, to, text, accountId, deps }) => {
            const send = deps?.sendSignal ?? (0, runtime_js_1.getSignalRuntime)().channel.signal.sendMessageSignal;
            const maxBytes = (0, plugin_sdk_1.resolveChannelMediaMaxBytes)({
                cfg,
                resolveChannelLimitMb: ({ cfg, accountId }) => cfg.channels?.signal?.accounts?.[accountId]?.mediaMaxMb ??
                    cfg.channels?.signal?.mediaMaxMb,
                accountId,
            });
            const result = await send(to, text, {
                maxBytes,
                accountId: accountId ?? undefined,
            });
            return { channel: "signal", ...result };
        },
        sendMedia: async ({ cfg, to, text, mediaUrl, accountId, deps }) => {
            const send = deps?.sendSignal ?? (0, runtime_js_1.getSignalRuntime)().channel.signal.sendMessageSignal;
            const maxBytes = (0, plugin_sdk_1.resolveChannelMediaMaxBytes)({
                cfg,
                resolveChannelLimitMb: ({ cfg, accountId }) => cfg.channels?.signal?.accounts?.[accountId]?.mediaMaxMb ??
                    cfg.channels?.signal?.mediaMaxMb,
                accountId,
            });
            const result = await send(to, text, {
                mediaUrl,
                maxBytes,
                accountId: accountId ?? undefined,
            });
            return { channel: "signal", ...result };
        },
    },
    status: {
        defaultRuntime: (0, plugin_sdk_1.createDefaultChannelRuntimeState)(plugin_sdk_1.DEFAULT_ACCOUNT_ID),
        collectStatusIssues: (accounts) => (0, plugin_sdk_1.collectStatusIssuesFromLastError)("signal", accounts),
        buildChannelSummary: ({ snapshot }) => ({
            ...(0, plugin_sdk_1.buildBaseChannelStatusSummary)(snapshot),
            baseUrl: snapshot.baseUrl ?? null,
            probe: snapshot.probe,
            lastProbeAt: snapshot.lastProbeAt ?? null,
        }),
        probeAccount: async ({ account, timeoutMs }) => {
            const baseUrl = account.baseUrl;
            return await (0, runtime_js_1.getSignalRuntime)().channel.signal.probeSignal(baseUrl, timeoutMs);
        },
        buildAccountSnapshot: ({ account, runtime, probe }) => ({
            accountId: account.accountId,
            name: account.name,
            enabled: account.enabled,
            configured: account.configured,
            baseUrl: account.baseUrl,
            running: runtime?.running ?? false,
            lastStartAt: runtime?.lastStartAt ?? null,
            lastStopAt: runtime?.lastStopAt ?? null,
            lastError: runtime?.lastError ?? null,
            probe,
            lastInboundAt: runtime?.lastInboundAt ?? null,
            lastOutboundAt: runtime?.lastOutboundAt ?? null,
        }),
    },
    gateway: {
        startAccount: async (ctx) => {
            const account = ctx.account;
            ctx.setStatus({
                accountId: account.accountId,
                baseUrl: account.baseUrl,
            });
            ctx.log?.info(`[${account.accountId}] starting provider (${account.baseUrl})`);
            // Lazy import: the monitor pulls the reply pipeline; avoid ESM init cycles.
            return (0, runtime_js_1.getSignalRuntime)().channel.signal.monitorSignalProvider({
                accountId: account.accountId,
                config: ctx.cfg,
                runtime: ctx.runtime,
                abortSignal: ctx.abortSignal,
                mediaMaxMb: account.config.mediaMaxMb,
            });
        },
    },
};
