package ai.clawcore.android.node

import android.os.Build
import ai.clawcore.android.BuildConfig
import ai.clawcore.android.SecurePrefs
import ai.clawcore.android.gateway.GatewayClientInfo
import ai.clawcore.android.gateway.GatewayConnectOptions
import ai.clawcore.android.gateway.GatewayEndpoint
import ai.clawcore.android.gateway.GatewayTlsParams
import ai.clawcore.android.protocol.ClawCoreCanvasA2UICommand
import ai.clawcore.android.protocol.ClawCoreCanvasCommand
import ai.clawcore.android.protocol.ClawCoreCameraCommand
import ai.clawcore.android.protocol.ClawCoreLocationCommand
import ai.clawcore.android.protocol.ClawCoreScreenCommand
import ai.clawcore.android.protocol.ClawCoreSmsCommand
import ai.clawcore.android.protocol.ClawCoreCapability
import ai.clawcore.android.LocationMode
import ai.clawcore.android.VoiceWakeMode

class ConnectionManager(
  private val prefs: SecurePrefs,
  private val cameraEnabled: () -> Boolean,
  private val locationMode: () -> LocationMode,
  private val voiceWakeMode: () -> VoiceWakeMode,
  private val smsAvailable: () -> Boolean,
  private val hasRecordAudioPermission: () -> Boolean,
  private val manualTls: () -> Boolean,
) {
  companion object {
    internal fun resolveTlsParamsForEndpoint(
      endpoint: GatewayEndpoint,
      storedFingerprint: String?,
      manualTlsEnabled: Boolean,
    ): GatewayTlsParams? {
      val stableId = endpoint.stableId
      val stored = storedFingerprint?.trim().takeIf { !it.isNullOrEmpty() }
      val isManual = stableId.startsWith("manual|")

      if (isManual) {
        if (!manualTlsEnabled) return null
        if (!stored.isNullOrBlank()) {
          return GatewayTlsParams(
            required = true,
            expectedFingerprint = stored,
            allowTOFU = false,
            stableId = stableId,
          )
        }
        return GatewayTlsParams(
          required = true,
          expectedFingerprint = null,
          allowTOFU = false,
          stableId = stableId,
        )
      }

      // Prefer stored pins. Never let discovery-provided TXT override a stored fingerprint.
      if (!stored.isNullOrBlank()) {
        return GatewayTlsParams(
          required = true,
          expectedFingerprint = stored,
          allowTOFU = false,
          stableId = stableId,
        )
      }

      val hinted = endpoint.tlsEnabled || !endpoint.tlsFingerprintSha256.isNullOrBlank()
      if (hinted) {
        // TXT is unauthenticated. Do not treat the advertised fingerprint as authoritative.
        return GatewayTlsParams(
          required = true,
          expectedFingerprint = null,
          allowTOFU = false,
          stableId = stableId,
        )
      }

      return null
    }
  }

  fun buildInvokeCommands(): List<String> =
    buildList {
      add(ClawCoreCanvasCommand.Present.rawValue)
      add(ClawCoreCanvasCommand.Hide.rawValue)
      add(ClawCoreCanvasCommand.Navigate.rawValue)
      add(ClawCoreCanvasCommand.Eval.rawValue)
      add(ClawCoreCanvasCommand.Snapshot.rawValue)
      add(ClawCoreCanvasA2UICommand.Push.rawValue)
      add(ClawCoreCanvasA2UICommand.PushJSONL.rawValue)
      add(ClawCoreCanvasA2UICommand.Reset.rawValue)
      add(ClawCoreScreenCommand.Record.rawValue)
      if (cameraEnabled()) {
        add(ClawCoreCameraCommand.Snap.rawValue)
        add(ClawCoreCameraCommand.Clip.rawValue)
      }
      if (locationMode() != LocationMode.Off) {
        add(ClawCoreLocationCommand.Get.rawValue)
      }
      if (smsAvailable()) {
        add(ClawCoreSmsCommand.Send.rawValue)
      }
      if (BuildConfig.DEBUG) {
        add("debug.logs")
        add("debug.ed25519")
      }
      add("app.update")
    }

  fun buildCapabilities(): List<String> =
    buildList {
      add(ClawCoreCapability.Canvas.rawValue)
      add(ClawCoreCapability.Screen.rawValue)
      if (cameraEnabled()) add(ClawCoreCapability.Camera.rawValue)
      if (smsAvailable()) add(ClawCoreCapability.Sms.rawValue)
      if (voiceWakeMode() != VoiceWakeMode.Off && hasRecordAudioPermission()) {
        add(ClawCoreCapability.VoiceWake.rawValue)
      }
      if (locationMode() != LocationMode.Off) {
        add(ClawCoreCapability.Location.rawValue)
      }
    }

  fun resolvedVersionName(): String {
    val versionName = BuildConfig.VERSION_NAME.trim().ifEmpty { "dev" }
    return if (BuildConfig.DEBUG && !versionName.contains("dev", ignoreCase = true)) {
      "$versionName-dev"
    } else {
      versionName
    }
  }

  fun resolveModelIdentifier(): String? {
    return listOfNotNull(Build.MANUFACTURER, Build.MODEL)
      .joinToString(" ")
      .trim()
      .ifEmpty { null }
  }

  fun buildUserAgent(): String {
    val version = resolvedVersionName()
    val release = Build.VERSION.RELEASE?.trim().orEmpty()
    val releaseLabel = if (release.isEmpty()) "unknown" else release
    return "ClawCoreAndroid/$version (Android $releaseLabel; SDK ${Build.VERSION.SDK_INT})"
  }

  fun buildClientInfo(clientId: String, clientMode: String): GatewayClientInfo {
    return GatewayClientInfo(
      id = clientId,
      displayName = prefs.displayName.value,
      version = resolvedVersionName(),
      platform = "android",
      mode = clientMode,
      instanceId = prefs.instanceId.value,
      deviceFamily = "Android",
      modelIdentifier = resolveModelIdentifier(),
    )
  }

  fun buildNodeConnectOptions(): GatewayConnectOptions {
    return GatewayConnectOptions(
      role = "node",
      scopes = emptyList(),
      caps = buildCapabilities(),
      commands = buildInvokeCommands(),
      permissions = emptyMap(),
      client = buildClientInfo(clientId = "clawcore-android", clientMode = "node"),
      userAgent = buildUserAgent(),
    )
  }

  fun buildOperatorConnectOptions(): GatewayConnectOptions {
    return GatewayConnectOptions(
      role = "operator",
      scopes = listOf("operator.read", "operator.write", "operator.talk.secrets"),
      caps = emptyList(),
      commands = emptyList(),
      permissions = emptyMap(),
      client = buildClientInfo(clientId = "clawcore-control-ui", clientMode = "ui"),
      userAgent = buildUserAgent(),
    )
  }

  fun resolveTlsParams(endpoint: GatewayEndpoint): GatewayTlsParams? {
    val stored = prefs.loadGatewayTlsFingerprint(endpoint.stableId)
    return resolveTlsParamsForEndpoint(endpoint, storedFingerprint = stored, manualTlsEnabled = manualTls())
  }
}
