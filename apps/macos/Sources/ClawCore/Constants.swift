import Foundation

// Stable identifier used for both the macOS LaunchAgent label and Nix-managed defaults suite.
// nix-clawcore writes app defaults into this suite to survive app bundle identifier churn.
let launchdLabel = "ai.clawcore.mac"
let gatewayLaunchdLabel = "ai.clawcore.gateway"
let onboardingVersionKey = "clawcore.onboardingVersion"
let onboardingSeenKey = "clawcore.onboardingSeen"
let currentOnboardingVersion = 7
let pauseDefaultsKey = "clawcore.pauseEnabled"
let iconAnimationsEnabledKey = "clawcore.iconAnimationsEnabled"
let swabbleEnabledKey = "clawcore.swabbleEnabled"
let swabbleTriggersKey = "clawcore.swabbleTriggers"
let voiceWakeTriggerChimeKey = "clawcore.voiceWakeTriggerChime"
let voiceWakeSendChimeKey = "clawcore.voiceWakeSendChime"
let showDockIconKey = "clawcore.showDockIcon"
let defaultVoiceWakeTriggers = ["clawcore"]
let voiceWakeMaxWords = 32
let voiceWakeMaxWordLength = 64
let voiceWakeMicKey = "clawcore.voiceWakeMicID"
let voiceWakeMicNameKey = "clawcore.voiceWakeMicName"
let voiceWakeLocaleKey = "clawcore.voiceWakeLocaleID"
let voiceWakeAdditionalLocalesKey = "clawcore.voiceWakeAdditionalLocaleIDs"
let voicePushToTalkEnabledKey = "clawcore.voicePushToTalkEnabled"
let talkEnabledKey = "clawcore.talkEnabled"
let iconOverrideKey = "clawcore.iconOverride"
let connectionModeKey = "clawcore.connectionMode"
let remoteTargetKey = "clawcore.remoteTarget"
let remoteIdentityKey = "clawcore.remoteIdentity"
let remoteProjectRootKey = "clawcore.remoteProjectRoot"
let remoteCliPathKey = "clawcore.remoteCliPath"
let canvasEnabledKey = "clawcore.canvasEnabled"
let cameraEnabledKey = "clawcore.cameraEnabled"
let systemRunPolicyKey = "clawcore.systemRunPolicy"
let systemRunAllowlistKey = "clawcore.systemRunAllowlist"
let systemRunEnabledKey = "clawcore.systemRunEnabled"
let locationModeKey = "clawcore.locationMode"
let locationPreciseKey = "clawcore.locationPreciseEnabled"
let peekabooBridgeEnabledKey = "clawcore.peekabooBridgeEnabled"
let deepLinkKeyKey = "clawcore.deepLinkKey"
let modelCatalogPathKey = "clawcore.modelCatalogPath"
let modelCatalogReloadKey = "clawcore.modelCatalogReload"
let cliInstallPromptedVersionKey = "clawcore.cliInstallPromptedVersion"
let heartbeatsEnabledKey = "clawcore.heartbeatsEnabled"
let debugPaneEnabledKey = "clawcore.debugPaneEnabled"
let debugFileLogEnabledKey = "clawcore.debug.fileLogEnabled"
let appLogLevelKey = "clawcore.debug.appLogLevel"
let voiceWakeSupported: Bool = ProcessInfo.processInfo.operatingSystemVersion.majorVersion >= 26
