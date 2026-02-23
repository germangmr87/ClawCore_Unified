import type { ReplyPayload } from "../../auto-reply/types.js";
import type { ClawCoreConfig } from "../../config/config.js";
import type { GroupToolPolicyConfig } from "../../config/types.tools.js";
import type { OutboundDeliveryResult, OutboundSendDeps } from "../../infra/outbound/deliver.js";
import type { OutboundIdentity } from "../../infra/outbound/identity.js";
import type { RuntimeEnv } from "../../runtime.js";
import type {
  ChannelAccountSnapshot,
  ChannelAccountState,
  ChannelDirectoryEntry,
  ChannelGroupContext,
  ChannelHeartbeatDeps,
  ChannelLogSink,
  ChannelOutboundTargetMode,
  ChannelPollContext,
  ChannelPollResult,
  ChannelSecurityContext,
  ChannelSecurityDmPolicy,
  ChannelSetupInput,
  ChannelStatusIssue,
} from "./types.core.js";

export type ChannelSetupAdapter = {
  resolveAccountId?: (params: { cfg: ClawCoreConfig; accountId?: string }) => string;
  applyAccountName?: (params: {
    cfg: ClawCoreConfig;
    accountId: string;
    name?: string;
  }) => ClawCoreConfig;
  applyAccountConfig: (params: {
    cfg: ClawCoreConfig;
    accountId: string;
    input: ChannelSetupInput;
  }) => ClawCoreConfig;
  validateInput?: (params: {
    cfg: ClawCoreConfig;
    accountId: string;
    input: ChannelSetupInput;
  }) => string | null;
};

export type ChannelConfigAdapter<ResolvedAccount> = {
  listAccountIds: (cfg: ClawCoreConfig) => string[];
  resolveAccount: (cfg: ClawCoreConfig, accountId?: string | null) => ResolvedAccount;
  defaultAccountId?: (cfg: ClawCoreConfig) => string;
  setAccountEnabled?: (params: {
    cfg: ClawCoreConfig;
    accountId: string;
    enabled: boolean;
  }) => ClawCoreConfig;
  deleteAccount?: (params: { cfg: ClawCoreConfig; accountId: string }) => ClawCoreConfig;
  isEnabled?: (account: ResolvedAccount, cfg: ClawCoreConfig) => boolean;
  disabledReason?: (account: ResolvedAccount, cfg: ClawCoreConfig) => string;
  isConfigured?: (account: ResolvedAccount, cfg: ClawCoreConfig) => boolean | Promise<boolean>;
  unconfiguredReason?: (account: ResolvedAccount, cfg: ClawCoreConfig) => string;
  describeAccount?: (account: ResolvedAccount, cfg: ClawCoreConfig) => ChannelAccountSnapshot;
  resolveAllowFrom?: (params: {
    cfg: ClawCoreConfig;
    accountId?: string | null;
  }) => string[] | undefined;
  formatAllowFrom?: (params: {
    cfg: ClawCoreConfig;
    accountId?: string | null;
    allowFrom: Array<string | number>;
  }) => string[];
};

export type ChannelGroupAdapter = {
  resolveRequireMention?: (params: ChannelGroupContext) => boolean | undefined;
  resolveGroupIntroHint?: (params: ChannelGroupContext) => string | undefined;
  resolveToolPolicy?: (params: ChannelGroupContext) => GroupToolPolicyConfig | undefined;
};

export type ChannelOutboundContext = {
  cfg: ClawCoreConfig;
  to: string;
  text: string;
  mediaUrl?: string;
  mediaLocalRoots?: readonly string[];
  gifPlayback?: boolean;
  replyToId?: string | null;
  threadId?: string | number | null;
  accountId?: string | null;
  identity?: OutboundIdentity;
  deps?: OutboundSendDeps;
  silent?: boolean;
};

export type ChannelOutboundPayloadContext = ChannelOutboundContext & {
  payload: ReplyPayload;
};

export type ChannelOutboundAdapter = {
  deliveryMode: "direct" | "gateway" | "hybrid";
  chunker?: ((text: string, limit: number) => string[]) | null;
  chunkerMode?: "text" | "markdown";
  textChunkLimit?: number;
  pollMaxOptions?: number;
  resolveTarget?: (params: {
    cfg?: ClawCoreConfig;
    to?: string;
    allowFrom?: string[];
    accountId?: string | null;
    mode?: ChannelOutboundTargetMode;
  }) => { ok: true; to: string } | { ok: false; error: Error };
  sendPayload?: (ctx: ChannelOutboundPayloadContext) => Promise<OutboundDeliveryResult>;
  sendText?: (ctx: ChannelOutboundContext) => Promise<OutboundDeliveryResult>;
  sendMedia?: (ctx: ChannelOutboundContext) => Promise<OutboundDeliveryResult>;
  sendPoll?: (ctx: ChannelPollContext) => Promise<ChannelPollResult>;
};

export type ChannelStatusAdapter<ResolvedAccount, Probe = unknown, Audit = unknown> = {
  defaultRuntime?: ChannelAccountSnapshot;
  buildChannelSummary?: (params: {
    account: ResolvedAccount;
    cfg: ClawCoreConfig;
    defaultAccountId: string;
    snapshot: ChannelAccountSnapshot;
  }) => Record<string, unknown> | Promise<Record<string, unknown>>;
  probeAccount?: (params: {
    account: ResolvedAccount;
    timeoutMs: number;
    cfg: ClawCoreConfig;
  }) => Promise<Probe>;
  auditAccount?: (params: {
    account: ResolvedAccount;
    timeoutMs: number;
    cfg: ClawCoreConfig;
    probe?: Probe;
  }) => Promise<Audit>;
  buildAccountSnapshot?: (params: {
    account: ResolvedAccount;
    cfg: ClawCoreConfig;
    runtime?: ChannelAccountSnapshot;
    probe?: Probe;
    audit?: Audit;
  }) => ChannelAccountSnapshot | Promise<ChannelAccountSnapshot>;
  logSelfId?: (params: {
    account: ResolvedAccount;
    cfg: ClawCoreConfig;
    runtime: RuntimeEnv;
    includeChannelPrefix?: boolean;
  }) => void;
  resolveAccountState?: (params: {
    account: ResolvedAccount;
    cfg: ClawCoreConfig;
    configured: boolean;
    enabled: boolean;
  }) => ChannelAccountState;
  collectStatusIssues?: (accounts: ChannelAccountSnapshot[]) => ChannelStatusIssue[];
};

export type ChannelGatewayContext<ResolvedAccount = unknown> = {
  cfg: ClawCoreConfig;
  accountId: string;
  account: ResolvedAccount;
  runtime: RuntimeEnv;
  abortSignal: AbortSignal;
  log?: ChannelLogSink;
  getStatus: () => ChannelAccountSnapshot;
  setStatus: (next: ChannelAccountSnapshot) => void;
};

export type ChannelLogoutResult = {
  cleared: boolean;
  loggedOut?: boolean;
  [key: string]: unknown;
};

export type ChannelLoginWithQrStartResult = {
  qrDataUrl?: string;
  message: string;
};

export type ChannelLoginWithQrWaitResult = {
  connected: boolean;
  message: string;
};

export type ChannelLogoutContext<ResolvedAccount = unknown> = {
  cfg: ClawCoreConfig;
  accountId: string;
  account: ResolvedAccount;
  runtime: RuntimeEnv;
  log?: ChannelLogSink;
};

export type ChannelPairingAdapter = {
  idLabel: string;
  normalizeAllowEntry?: (entry: string) => string;
  notifyApproval?: (params: {
    cfg: ClawCoreConfig;
    id: string;
    runtime?: RuntimeEnv;
  }) => Promise<void>;
};

export type ChannelGatewayAdapter<ResolvedAccount = unknown> = {
  startAccount?: (ctx: ChannelGatewayContext<ResolvedAccount>) => Promise<unknown>;
  stopAccount?: (ctx: ChannelGatewayContext<ResolvedAccount>) => Promise<void>;
  loginWithQrStart?: (params: {
    accountId?: string;
    force?: boolean;
    timeoutMs?: number;
    verbose?: boolean;
  }) => Promise<ChannelLoginWithQrStartResult>;
  loginWithQrWait?: (params: {
    accountId?: string;
    timeoutMs?: number;
  }) => Promise<ChannelLoginWithQrWaitResult>;
  logoutAccount?: (ctx: ChannelLogoutContext<ResolvedAccount>) => Promise<ChannelLogoutResult>;
};

export type ChannelAuthAdapter = {
  login?: (params: {
    cfg: ClawCoreConfig;
    accountId?: string | null;
    runtime: RuntimeEnv;
    verbose?: boolean;
    channelInput?: string | null;
  }) => Promise<void>;
};

export type ChannelHeartbeatAdapter = {
  checkReady?: (params: {
    cfg: ClawCoreConfig;
    accountId?: string | null;
    deps?: ChannelHeartbeatDeps;
  }) => Promise<{ ok: boolean; reason: string }>;
  resolveRecipients?: (params: { cfg: ClawCoreConfig; opts?: { to?: string; all?: boolean } }) => {
    recipients: string[];
    source: string;
  };
};

export type ChannelDirectoryAdapter = {
  self?: (params: {
    cfg: ClawCoreConfig;
    accountId?: string | null;
    runtime: RuntimeEnv;
  }) => Promise<ChannelDirectoryEntry | null>;
  listPeers?: (params: {
    cfg: ClawCoreConfig;
    accountId?: string | null;
    query?: string | null;
    limit?: number | null;
    runtime: RuntimeEnv;
  }) => Promise<ChannelDirectoryEntry[]>;
  listPeersLive?: (params: {
    cfg: ClawCoreConfig;
    accountId?: string | null;
    query?: string | null;
    limit?: number | null;
    runtime: RuntimeEnv;
  }) => Promise<ChannelDirectoryEntry[]>;
  listGroups?: (params: {
    cfg: ClawCoreConfig;
    accountId?: string | null;
    query?: string | null;
    limit?: number | null;
    runtime: RuntimeEnv;
  }) => Promise<ChannelDirectoryEntry[]>;
  listGroupsLive?: (params: {
    cfg: ClawCoreConfig;
    accountId?: string | null;
    query?: string | null;
    limit?: number | null;
    runtime: RuntimeEnv;
  }) => Promise<ChannelDirectoryEntry[]>;
  listGroupMembers?: (params: {
    cfg: ClawCoreConfig;
    accountId?: string | null;
    groupId: string;
    limit?: number | null;
    runtime: RuntimeEnv;
  }) => Promise<ChannelDirectoryEntry[]>;
};

export type ChannelResolveKind = "user" | "group";

export type ChannelResolveResult = {
  input: string;
  resolved: boolean;
  id?: string;
  name?: string;
  note?: string;
};

export type ChannelResolverAdapter = {
  resolveTargets: (params: {
    cfg: ClawCoreConfig;
    accountId?: string | null;
    inputs: string[];
    kind: ChannelResolveKind;
    runtime: RuntimeEnv;
  }) => Promise<ChannelResolveResult[]>;
};

export type ChannelElevatedAdapter = {
  allowFromFallback?: (params: {
    cfg: ClawCoreConfig;
    accountId?: string | null;
  }) => Array<string | number> | undefined;
};

export type ChannelCommandAdapter = {
  enforceOwnerForCommands?: boolean;
  skipWhenConfigEmpty?: boolean;
};

export type ChannelSecurityAdapter<ResolvedAccount = unknown> = {
  resolveDmPolicy?: (
    ctx: ChannelSecurityContext<ResolvedAccount>,
  ) => ChannelSecurityDmPolicy | null;
  collectWarnings?: (ctx: ChannelSecurityContext<ResolvedAccount>) => Promise<string[]> | string[];
};
