"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.imessagePlugin = void 0;
const plugin_sdk_1 = require("clawcore/plugin-sdk");
const runtime_js_1 = require("./runtime.js");
const meta = (0, plugin_sdk_1.getChatChannelMeta)("imessage");
exports.imessagePlugin = {
    id: "imessage",
    meta: {
        ...meta,
        aliases: ["imsg"],
        showConfigured: false,
    },
    onboarding: plugin_sdk_1.imessageOnboardingAdapter,
    pairing: {
        idLabel: "imessageSenderId",
        notifyApproval: async ({ id }) => {
            await (0, runtime_js_1.getIMessageRuntime)().channel.imessage.sendMessageIMessage(id, plugin_sdk_1.PAIRING_APPROVED_MESSAGE);
        },
    },
    capabilities: {
        chatTypes: ["direct", "group"],
        media: true,
    },
    reload: { configPrefixes: ["channels.imessage"] },
    configSchema: (0, plugin_sdk_1.buildChannelConfigSchema)(plugin_sdk_1.IMessageConfigSchema),
    config: {
        listAccountIds: (cfg) => (0, plugin_sdk_1.listIMessageAccountIds)(cfg),
        resolveAccount: (cfg, accountId) => (0, plugin_sdk_1.resolveIMessageAccount)({ cfg, accountId }),
        defaultAccountId: (cfg) => (0, plugin_sdk_1.resolveDefaultIMessageAccountId)(cfg),
        setAccountEnabled: ({ cfg, accountId, enabled }) => (0, plugin_sdk_1.setAccountEnabledInConfigSection)({
            cfg,
            sectionKey: "imessage",
            accountId,
            enabled,
            allowTopLevel: true,
        }),
        deleteAccount: ({ cfg, accountId }) => (0, plugin_sdk_1.deleteAccountFromConfigSection)({
            cfg,
            sectionKey: "imessage",
            accountId,
            clearBaseFields: ["cliPath", "dbPath", "service", "region", "name"],
        }),
        isConfigured: (account) => account.configured,
        describeAccount: (account) => ({
            accountId: account.accountId,
            name: account.name,
            enabled: account.enabled,
            configured: account.configured,
        }),
        resolveAllowFrom: ({ cfg, accountId }) => ((0, plugin_sdk_1.resolveIMessageAccount)({ cfg, accountId }).config.allowFrom ?? []).map((entry) => String(entry)),
        formatAllowFrom: ({ allowFrom }) => allowFrom.map((entry) => String(entry).trim()).filter(Boolean),
    },
    security: {
        resolveDmPolicy: ({ cfg, accountId, account }) => {
            const resolvedAccountId = accountId ?? account.accountId ?? plugin_sdk_1.DEFAULT_ACCOUNT_ID;
            const useAccountPath = Boolean(cfg.channels?.imessage?.accounts?.[resolvedAccountId]);
            const basePath = useAccountPath
                ? `channels.imessage.accounts.${resolvedAccountId}.`
                : "channels.imessage.";
            return {
                policy: account.config.dmPolicy ?? "pairing",
                allowFrom: account.config.allowFrom ?? [],
                policyPath: `${basePath}dmPolicy`,
                allowFromPath: basePath,
                approveHint: (0, plugin_sdk_1.formatPairingApproveHint)("imessage"),
            };
        },
        collectWarnings: ({ account, cfg }) => {
            const defaultGroupPolicy = cfg.channels?.defaults?.groupPolicy;
            const groupPolicy = account.config.groupPolicy ?? defaultGroupPolicy ?? "allowlist";
            if (groupPolicy !== "open") {
                return [];
            }
            return [
                `- iMessage groups: groupPolicy="open" allows any member to trigger the bot. Set channels.imessage.groupPolicy="allowlist" + channels.imessage.groupAllowFrom to restrict senders.`,
            ];
        },
    },
    groups: {
        resolveRequireMention: plugin_sdk_1.resolveIMessageGroupRequireMention,
        resolveToolPolicy: plugin_sdk_1.resolveIMessageGroupToolPolicy,
    },
    messaging: {
        normalizeTarget: plugin_sdk_1.normalizeIMessageMessagingTarget,
        targetResolver: {
            looksLikeId: plugin_sdk_1.looksLikeIMessageTargetId,
            hint: "<handle|chat_id:ID>",
        },
    },
    setup: {
        resolveAccountId: ({ accountId }) => (0, plugin_sdk_1.normalizeAccountId)(accountId),
        applyAccountName: ({ cfg, accountId, name }) => (0, plugin_sdk_1.applyAccountNameToChannelSection)({
            cfg,
            channelKey: "imessage",
            accountId,
            name,
        }),
        applyAccountConfig: ({ cfg, accountId, input }) => {
            const namedConfig = (0, plugin_sdk_1.applyAccountNameToChannelSection)({
                cfg,
                channelKey: "imessage",
                accountId,
                name: input.name,
            });
            const next = accountId !== plugin_sdk_1.DEFAULT_ACCOUNT_ID
                ? (0, plugin_sdk_1.migrateBaseNameToDefaultAccount)({
                    cfg: namedConfig,
                    channelKey: "imessage",
                })
                : namedConfig;
            if (accountId === plugin_sdk_1.DEFAULT_ACCOUNT_ID) {
                return {
                    ...next,
                    channels: {
                        ...next.channels,
                        imessage: {
                            ...next.channels?.imessage,
                            enabled: true,
                            ...(input.cliPath ? { cliPath: input.cliPath } : {}),
                            ...(input.dbPath ? { dbPath: input.dbPath } : {}),
                            ...(input.service ? { service: input.service } : {}),
                            ...(input.region ? { region: input.region } : {}),
                        },
                    },
                };
            }
            return {
                ...next,
                channels: {
                    ...next.channels,
                    imessage: {
                        ...next.channels?.imessage,
                        enabled: true,
                        accounts: {
                            ...next.channels?.imessage?.accounts,
                            [accountId]: {
                                ...next.channels?.imessage?.accounts?.[accountId],
                                enabled: true,
                                ...(input.cliPath ? { cliPath: input.cliPath } : {}),
                                ...(input.dbPath ? { dbPath: input.dbPath } : {}),
                                ...(input.service ? { service: input.service } : {}),
                                ...(input.region ? { region: input.region } : {}),
                            },
                        },
                    },
                },
            };
        },
    },
    outbound: {
        deliveryMode: "direct",
        chunker: (text, limit) => (0, runtime_js_1.getIMessageRuntime)().channel.text.chunkText(text, limit),
        chunkerMode: "text",
        textChunkLimit: 4000,
        sendText: async ({ cfg, to, text, accountId, deps }) => {
            const send = deps?.sendIMessage ?? (0, runtime_js_1.getIMessageRuntime)().channel.imessage.sendMessageIMessage;
            const maxBytes = (0, plugin_sdk_1.resolveChannelMediaMaxBytes)({
                cfg,
                resolveChannelLimitMb: ({ cfg, accountId }) => cfg.channels?.imessage?.accounts?.[accountId]?.mediaMaxMb ??
                    cfg.channels?.imessage?.mediaMaxMb,
                accountId,
            });
            const result = await send(to, text, {
                maxBytes,
                accountId: accountId ?? undefined,
            });
            return { channel: "imessage", ...result };
        },
        sendMedia: async ({ cfg, to, text, mediaUrl, accountId, deps }) => {
            const send = deps?.sendIMessage ?? (0, runtime_js_1.getIMessageRuntime)().channel.imessage.sendMessageIMessage;
            const maxBytes = (0, plugin_sdk_1.resolveChannelMediaMaxBytes)({
                cfg,
                resolveChannelLimitMb: ({ cfg, accountId }) => cfg.channels?.imessage?.accounts?.[accountId]?.mediaMaxMb ??
                    cfg.channels?.imessage?.mediaMaxMb,
                accountId,
            });
            const result = await send(to, text, {
                mediaUrl,
                maxBytes,
                accountId: accountId ?? undefined,
            });
            return { channel: "imessage", ...result };
        },
    },
    status: {
        defaultRuntime: {
            accountId: plugin_sdk_1.DEFAULT_ACCOUNT_ID,
            running: false,
            lastStartAt: null,
            lastStopAt: null,
            lastError: null,
            cliPath: null,
            dbPath: null,
        },
        collectStatusIssues: (accounts) => accounts.flatMap((account) => {
            const lastError = typeof account.lastError === "string" ? account.lastError.trim() : "";
            if (!lastError) {
                return [];
            }
            return [
                {
                    channel: "imessage",
                    accountId: account.accountId,
                    kind: "runtime",
                    message: `Channel error: ${lastError}`,
                },
            ];
        }),
        buildChannelSummary: ({ snapshot }) => ({
            configured: snapshot.configured ?? false,
            running: snapshot.running ?? false,
            lastStartAt: snapshot.lastStartAt ?? null,
            lastStopAt: snapshot.lastStopAt ?? null,
            lastError: snapshot.lastError ?? null,
            cliPath: snapshot.cliPath ?? null,
            dbPath: snapshot.dbPath ?? null,
            probe: snapshot.probe,
            lastProbeAt: snapshot.lastProbeAt ?? null,
        }),
        probeAccount: async ({ timeoutMs }) => (0, runtime_js_1.getIMessageRuntime)().channel.imessage.probeIMessage(timeoutMs),
        buildAccountSnapshot: ({ account, runtime, probe }) => ({
            accountId: account.accountId,
            name: account.name,
            enabled: account.enabled,
            configured: account.configured,
            running: runtime?.running ?? false,
            lastStartAt: runtime?.lastStartAt ?? null,
            lastStopAt: runtime?.lastStopAt ?? null,
            lastError: runtime?.lastError ?? null,
            cliPath: runtime?.cliPath ?? account.config.cliPath ?? null,
            dbPath: runtime?.dbPath ?? account.config.dbPath ?? null,
            probe,
            lastInboundAt: runtime?.lastInboundAt ?? null,
            lastOutboundAt: runtime?.lastOutboundAt ?? null,
        }),
        resolveAccountState: ({ enabled }) => (enabled ? "enabled" : "disabled"),
    },
    gateway: {
        startAccount: async (ctx) => {
            const account = ctx.account;
            const cliPath = account.config.cliPath?.trim() || "imsg";
            const dbPath = account.config.dbPath?.trim();
            ctx.setStatus({
                accountId: account.accountId,
                cliPath,
                dbPath: dbPath ?? null,
            });
            ctx.log?.info(`[${account.accountId}] starting provider (${cliPath}${dbPath ? ` db=${dbPath}` : ""})`);
            return (0, runtime_js_1.getIMessageRuntime)().channel.imessage.monitorIMessageProvider({
                accountId: account.accountId,
                config: ctx.cfg,
                runtime: ctx.runtime,
                abortSignal: ctx.abortSignal,
            });
        },
    },
};
