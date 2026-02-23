"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.slackPlugin = void 0;
const plugin_sdk_1 = require("clawcore/plugin-sdk");
const runtime_js_1 = require("./runtime.js");
const meta = (0, plugin_sdk_1.getChatChannelMeta)("slack");
// Select the appropriate Slack token for read/write operations.
function getTokenForOperation(account, operation) {
    const userToken = account.config.userToken?.trim() || undefined;
    const botToken = account.botToken?.trim();
    const allowUserWrites = account.config.userTokenReadOnly === false;
    if (operation === "read") {
        return userToken ?? botToken;
    }
    if (!allowUserWrites) {
        return botToken;
    }
    return botToken ?? userToken;
}
exports.slackPlugin = {
    id: "slack",
    meta: {
        ...meta,
    },
    onboarding: plugin_sdk_1.slackOnboardingAdapter,
    pairing: {
        idLabel: "slackUserId",
        normalizeAllowEntry: (entry) => entry.replace(/^(slack|user):/i, ""),
        notifyApproval: async ({ id }) => {
            const cfg = (0, runtime_js_1.getSlackRuntime)().config.loadConfig();
            const account = (0, plugin_sdk_1.resolveSlackAccount)({
                cfg,
                accountId: plugin_sdk_1.DEFAULT_ACCOUNT_ID,
            });
            const token = getTokenForOperation(account, "write");
            const botToken = account.botToken?.trim();
            const tokenOverride = token && token !== botToken ? token : undefined;
            if (tokenOverride) {
                await (0, runtime_js_1.getSlackRuntime)().channel.slack.sendMessageSlack(`user:${id}`, plugin_sdk_1.PAIRING_APPROVED_MESSAGE, {
                    token: tokenOverride,
                });
            }
            else {
                await (0, runtime_js_1.getSlackRuntime)().channel.slack.sendMessageSlack(`user:${id}`, plugin_sdk_1.PAIRING_APPROVED_MESSAGE);
            }
        },
    },
    capabilities: {
        chatTypes: ["direct", "channel", "thread"],
        reactions: true,
        threads: true,
        media: true,
        nativeCommands: true,
    },
    streaming: {
        blockStreamingCoalesceDefaults: { minChars: 1500, idleMs: 1000 },
    },
    reload: { configPrefixes: ["channels.slack"] },
    configSchema: (0, plugin_sdk_1.buildChannelConfigSchema)(plugin_sdk_1.SlackConfigSchema),
    config: {
        listAccountIds: (cfg) => (0, plugin_sdk_1.listSlackAccountIds)(cfg),
        resolveAccount: (cfg, accountId) => (0, plugin_sdk_1.resolveSlackAccount)({ cfg, accountId }),
        defaultAccountId: (cfg) => (0, plugin_sdk_1.resolveDefaultSlackAccountId)(cfg),
        setAccountEnabled: ({ cfg, accountId, enabled }) => (0, plugin_sdk_1.setAccountEnabledInConfigSection)({
            cfg,
            sectionKey: "slack",
            accountId,
            enabled,
            allowTopLevel: true,
        }),
        deleteAccount: ({ cfg, accountId }) => (0, plugin_sdk_1.deleteAccountFromConfigSection)({
            cfg,
            sectionKey: "slack",
            accountId,
            clearBaseFields: ["botToken", "appToken", "name"],
        }),
        isConfigured: (account) => Boolean(account.botToken && account.appToken),
        describeAccount: (account) => ({
            accountId: account.accountId,
            name: account.name,
            enabled: account.enabled,
            configured: Boolean(account.botToken && account.appToken),
            botTokenSource: account.botTokenSource,
            appTokenSource: account.appTokenSource,
        }),
        resolveAllowFrom: ({ cfg, accountId }) => ((0, plugin_sdk_1.resolveSlackAccount)({ cfg, accountId }).dm?.allowFrom ?? []).map((entry) => String(entry)),
        formatAllowFrom: ({ allowFrom }) => allowFrom
            .map((entry) => String(entry).trim())
            .filter(Boolean)
            .map((entry) => entry.toLowerCase()),
    },
    security: {
        resolveDmPolicy: ({ cfg, accountId, account }) => {
            const resolvedAccountId = accountId ?? account.accountId ?? plugin_sdk_1.DEFAULT_ACCOUNT_ID;
            const useAccountPath = Boolean(cfg.channels?.slack?.accounts?.[resolvedAccountId]);
            const allowFromPath = useAccountPath
                ? `channels.slack.accounts.${resolvedAccountId}.dm.`
                : "channels.slack.dm.";
            return {
                policy: account.dm?.policy ?? "pairing",
                allowFrom: account.dm?.allowFrom ?? [],
                allowFromPath,
                approveHint: (0, plugin_sdk_1.formatPairingApproveHint)("slack"),
                normalizeEntry: (raw) => raw.replace(/^(slack|user):/i, ""),
            };
        },
        collectWarnings: ({ account, cfg }) => {
            const warnings = [];
            const defaultGroupPolicy = cfg.channels?.defaults?.groupPolicy;
            const groupPolicy = account.config.groupPolicy ?? defaultGroupPolicy ?? "open";
            const channelAllowlistConfigured = Boolean(account.config.channels) && Object.keys(account.config.channels ?? {}).length > 0;
            if (groupPolicy === "open") {
                if (channelAllowlistConfigured) {
                    warnings.push(`- Slack channels: groupPolicy="open" allows any channel not explicitly denied to trigger (mention-gated). Set channels.slack.groupPolicy="allowlist" and configure channels.slack.channels.`);
                }
                else {
                    warnings.push(`- Slack channels: groupPolicy="open" with no channel allowlist; any channel can trigger (mention-gated). Set channels.slack.groupPolicy="allowlist" and configure channels.slack.channels.`);
                }
            }
            return warnings;
        },
    },
    groups: {
        resolveRequireMention: plugin_sdk_1.resolveSlackGroupRequireMention,
        resolveToolPolicy: plugin_sdk_1.resolveSlackGroupToolPolicy,
    },
    threading: {
        resolveReplyToMode: ({ cfg, accountId, chatType }) => (0, plugin_sdk_1.resolveSlackReplyToMode)((0, plugin_sdk_1.resolveSlackAccount)({ cfg, accountId }), chatType),
        allowExplicitReplyTagsWhenOff: true,
        buildToolContext: (params) => (0, plugin_sdk_1.buildSlackThreadingToolContext)(params),
    },
    messaging: {
        normalizeTarget: plugin_sdk_1.normalizeSlackMessagingTarget,
        targetResolver: {
            looksLikeId: plugin_sdk_1.looksLikeSlackTargetId,
            hint: "<channelId|user:ID|channel:ID>",
        },
    },
    directory: {
        self: async () => null,
        listPeers: async (params) => (0, plugin_sdk_1.listSlackDirectoryPeersFromConfig)(params),
        listGroups: async (params) => (0, plugin_sdk_1.listSlackDirectoryGroupsFromConfig)(params),
        listPeersLive: async (params) => (0, runtime_js_1.getSlackRuntime)().channel.slack.listDirectoryPeersLive(params),
        listGroupsLive: async (params) => (0, runtime_js_1.getSlackRuntime)().channel.slack.listDirectoryGroupsLive(params),
    },
    resolver: {
        resolveTargets: async ({ cfg, accountId, inputs, kind }) => {
            const account = (0, plugin_sdk_1.resolveSlackAccount)({ cfg, accountId });
            const token = account.config.userToken?.trim() || account.botToken?.trim();
            if (!token) {
                return inputs.map((input) => ({
                    input,
                    resolved: false,
                    note: "missing Slack token",
                }));
            }
            if (kind === "group") {
                const resolved = await (0, runtime_js_1.getSlackRuntime)().channel.slack.resolveChannelAllowlist({
                    token,
                    entries: inputs,
                });
                return resolved.map((entry) => ({
                    input: entry.input,
                    resolved: entry.resolved,
                    id: entry.id,
                    name: entry.name,
                    note: entry.archived ? "archived" : undefined,
                }));
            }
            const resolved = await (0, runtime_js_1.getSlackRuntime)().channel.slack.resolveUserAllowlist({
                token,
                entries: inputs,
            });
            return resolved.map((entry) => ({
                input: entry.input,
                resolved: entry.resolved,
                id: entry.id,
                name: entry.name,
                note: entry.note,
            }));
        },
    },
    actions: {
        listActions: ({ cfg }) => (0, plugin_sdk_1.listSlackMessageActions)(cfg),
        extractToolSend: ({ args }) => (0, plugin_sdk_1.extractSlackToolSend)(args),
        handleAction: async ({ action, params, cfg, accountId, toolContext }) => {
            const resolveChannelId = () => (0, plugin_sdk_1.readStringParam)(params, "channelId") ?? (0, plugin_sdk_1.readStringParam)(params, "to", { required: true });
            if (action === "send") {
                const to = (0, plugin_sdk_1.readStringParam)(params, "to", { required: true });
                const content = (0, plugin_sdk_1.readStringParam)(params, "message", {
                    required: true,
                    allowEmpty: true,
                });
                const mediaUrl = (0, plugin_sdk_1.readStringParam)(params, "media", { trim: false });
                const threadId = (0, plugin_sdk_1.readStringParam)(params, "threadId");
                const replyTo = (0, plugin_sdk_1.readStringParam)(params, "replyTo");
                return await (0, runtime_js_1.getSlackRuntime)().channel.slack.handleSlackAction({
                    action: "sendMessage",
                    to,
                    content,
                    mediaUrl: mediaUrl ?? undefined,
                    accountId: accountId ?? undefined,
                    threadTs: threadId ?? replyTo ?? undefined,
                }, cfg, toolContext);
            }
            if (action === "react") {
                const messageId = (0, plugin_sdk_1.readStringParam)(params, "messageId", {
                    required: true,
                });
                const emoji = (0, plugin_sdk_1.readStringParam)(params, "emoji", { allowEmpty: true });
                const remove = typeof params.remove === "boolean" ? params.remove : undefined;
                return await (0, runtime_js_1.getSlackRuntime)().channel.slack.handleSlackAction({
                    action: "react",
                    channelId: resolveChannelId(),
                    messageId,
                    emoji,
                    remove,
                    accountId: accountId ?? undefined,
                }, cfg);
            }
            if (action === "reactions") {
                const messageId = (0, plugin_sdk_1.readStringParam)(params, "messageId", {
                    required: true,
                });
                const limit = (0, plugin_sdk_1.readNumberParam)(params, "limit", { integer: true });
                return await (0, runtime_js_1.getSlackRuntime)().channel.slack.handleSlackAction({
                    action: "reactions",
                    channelId: resolveChannelId(),
                    messageId,
                    limit,
                    accountId: accountId ?? undefined,
                }, cfg);
            }
            if (action === "read") {
                const limit = (0, plugin_sdk_1.readNumberParam)(params, "limit", { integer: true });
                return await (0, runtime_js_1.getSlackRuntime)().channel.slack.handleSlackAction({
                    action: "readMessages",
                    channelId: resolveChannelId(),
                    limit,
                    before: (0, plugin_sdk_1.readStringParam)(params, "before"),
                    after: (0, plugin_sdk_1.readStringParam)(params, "after"),
                    accountId: accountId ?? undefined,
                }, cfg);
            }
            if (action === "edit") {
                const messageId = (0, plugin_sdk_1.readStringParam)(params, "messageId", {
                    required: true,
                });
                const content = (0, plugin_sdk_1.readStringParam)(params, "message", { required: true });
                return await (0, runtime_js_1.getSlackRuntime)().channel.slack.handleSlackAction({
                    action: "editMessage",
                    channelId: resolveChannelId(),
                    messageId,
                    content,
                    accountId: accountId ?? undefined,
                }, cfg);
            }
            if (action === "delete") {
                const messageId = (0, plugin_sdk_1.readStringParam)(params, "messageId", {
                    required: true,
                });
                return await (0, runtime_js_1.getSlackRuntime)().channel.slack.handleSlackAction({
                    action: "deleteMessage",
                    channelId: resolveChannelId(),
                    messageId,
                    accountId: accountId ?? undefined,
                }, cfg);
            }
            if (action === "pin" || action === "unpin" || action === "list-pins") {
                const messageId = action === "list-pins"
                    ? undefined
                    : (0, plugin_sdk_1.readStringParam)(params, "messageId", { required: true });
                return await (0, runtime_js_1.getSlackRuntime)().channel.slack.handleSlackAction({
                    action: action === "pin" ? "pinMessage" : action === "unpin" ? "unpinMessage" : "listPins",
                    channelId: resolveChannelId(),
                    messageId,
                    accountId: accountId ?? undefined,
                }, cfg);
            }
            if (action === "member-info") {
                const userId = (0, plugin_sdk_1.readStringParam)(params, "userId", { required: true });
                return await (0, runtime_js_1.getSlackRuntime)().channel.slack.handleSlackAction({ action: "memberInfo", userId, accountId: accountId ?? undefined }, cfg);
            }
            if (action === "emoji-list") {
                const limit = (0, plugin_sdk_1.readNumberParam)(params, "limit", { integer: true });
                return await (0, runtime_js_1.getSlackRuntime)().channel.slack.handleSlackAction({ action: "emojiList", limit, accountId: accountId ?? undefined }, cfg);
            }
            throw new Error(`Action ${action} is not supported for provider ${meta.id}.`);
        },
    },
    setup: {
        resolveAccountId: ({ accountId }) => (0, plugin_sdk_1.normalizeAccountId)(accountId),
        applyAccountName: ({ cfg, accountId, name }) => (0, plugin_sdk_1.applyAccountNameToChannelSection)({
            cfg,
            channelKey: "slack",
            accountId,
            name,
        }),
        validateInput: ({ accountId, input }) => {
            if (input.useEnv && accountId !== plugin_sdk_1.DEFAULT_ACCOUNT_ID) {
                return "Slack env tokens can only be used for the default account.";
            }
            if (!input.useEnv && (!input.botToken || !input.appToken)) {
                return "Slack requires --bot-token and --app-token (or --use-env).";
            }
            return null;
        },
        applyAccountConfig: ({ cfg, accountId, input }) => {
            const namedConfig = (0, plugin_sdk_1.applyAccountNameToChannelSection)({
                cfg,
                channelKey: "slack",
                accountId,
                name: input.name,
            });
            const next = accountId !== plugin_sdk_1.DEFAULT_ACCOUNT_ID
                ? (0, plugin_sdk_1.migrateBaseNameToDefaultAccount)({
                    cfg: namedConfig,
                    channelKey: "slack",
                })
                : namedConfig;
            if (accountId === plugin_sdk_1.DEFAULT_ACCOUNT_ID) {
                return {
                    ...next,
                    channels: {
                        ...next.channels,
                        slack: {
                            ...next.channels?.slack,
                            enabled: true,
                            ...(input.useEnv
                                ? {}
                                : {
                                    ...(input.botToken ? { botToken: input.botToken } : {}),
                                    ...(input.appToken ? { appToken: input.appToken } : {}),
                                }),
                        },
                    },
                };
            }
            return {
                ...next,
                channels: {
                    ...next.channels,
                    slack: {
                        ...next.channels?.slack,
                        enabled: true,
                        accounts: {
                            ...next.channels?.slack?.accounts,
                            [accountId]: {
                                ...next.channels?.slack?.accounts?.[accountId],
                                enabled: true,
                                ...(input.botToken ? { botToken: input.botToken } : {}),
                                ...(input.appToken ? { appToken: input.appToken } : {}),
                            },
                        },
                    },
                },
            };
        },
    },
    outbound: {
        deliveryMode: "direct",
        chunker: null,
        textChunkLimit: 4000,
        sendText: async ({ to, text, accountId, deps, replyToId, cfg }) => {
            const send = deps?.sendSlack ?? (0, runtime_js_1.getSlackRuntime)().channel.slack.sendMessageSlack;
            const account = (0, plugin_sdk_1.resolveSlackAccount)({ cfg, accountId });
            const token = getTokenForOperation(account, "write");
            const botToken = account.botToken?.trim();
            const tokenOverride = token && token !== botToken ? token : undefined;
            const result = await send(to, text, {
                threadTs: replyToId ?? undefined,
                accountId: accountId ?? undefined,
                ...(tokenOverride ? { token: tokenOverride } : {}),
            });
            return { channel: "slack", ...result };
        },
        sendMedia: async ({ to, text, mediaUrl, accountId, deps, replyToId, cfg }) => {
            const send = deps?.sendSlack ?? (0, runtime_js_1.getSlackRuntime)().channel.slack.sendMessageSlack;
            const account = (0, plugin_sdk_1.resolveSlackAccount)({ cfg, accountId });
            const token = getTokenForOperation(account, "write");
            const botToken = account.botToken?.trim();
            const tokenOverride = token && token !== botToken ? token : undefined;
            const result = await send(to, text, {
                mediaUrl,
                threadTs: replyToId ?? undefined,
                accountId: accountId ?? undefined,
                ...(tokenOverride ? { token: tokenOverride } : {}),
            });
            return { channel: "slack", ...result };
        },
    },
    status: {
        defaultRuntime: {
            accountId: plugin_sdk_1.DEFAULT_ACCOUNT_ID,
            running: false,
            lastStartAt: null,
            lastStopAt: null,
            lastError: null,
        },
        buildChannelSummary: ({ snapshot }) => ({
            configured: snapshot.configured ?? false,
            botTokenSource: snapshot.botTokenSource ?? "none",
            appTokenSource: snapshot.appTokenSource ?? "none",
            running: snapshot.running ?? false,
            lastStartAt: snapshot.lastStartAt ?? null,
            lastStopAt: snapshot.lastStopAt ?? null,
            lastError: snapshot.lastError ?? null,
            probe: snapshot.probe,
            lastProbeAt: snapshot.lastProbeAt ?? null,
        }),
        probeAccount: async ({ account, timeoutMs }) => {
            const token = account.botToken?.trim();
            if (!token) {
                return { ok: false, error: "missing token" };
            }
            return await (0, runtime_js_1.getSlackRuntime)().channel.slack.probeSlack(token, timeoutMs);
        },
        buildAccountSnapshot: ({ account, runtime, probe }) => {
            const configured = Boolean(account.botToken && account.appToken);
            return {
                accountId: account.accountId,
                name: account.name,
                enabled: account.enabled,
                configured,
                botTokenSource: account.botTokenSource,
                appTokenSource: account.appTokenSource,
                running: runtime?.running ?? false,
                lastStartAt: runtime?.lastStartAt ?? null,
                lastStopAt: runtime?.lastStopAt ?? null,
                lastError: runtime?.lastError ?? null,
                probe,
                lastInboundAt: runtime?.lastInboundAt ?? null,
                lastOutboundAt: runtime?.lastOutboundAt ?? null,
            };
        },
    },
    gateway: {
        startAccount: async (ctx) => {
            const account = ctx.account;
            const botToken = account.botToken?.trim();
            const appToken = account.appToken?.trim();
            ctx.log?.info(`[${account.accountId}] starting provider`);
            return (0, runtime_js_1.getSlackRuntime)().channel.slack.monitorSlackProvider({
                botToken: botToken ?? "",
                appToken: appToken ?? "",
                accountId: account.accountId,
                config: ctx.cfg,
                runtime: ctx.runtime,
                abortSignal: ctx.abortSignal,
                mediaMaxMb: account.config.mediaMaxMb,
                slashCommand: account.config.slashCommand,
            });
        },
    },
};
