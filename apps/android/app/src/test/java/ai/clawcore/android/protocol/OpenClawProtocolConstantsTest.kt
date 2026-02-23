package ai.clawcore.android.protocol

import org.junit.Assert.assertEquals
import org.junit.Test

class ClawCoreProtocolConstantsTest {
  @Test
  fun canvasCommandsUseStableStrings() {
    assertEquals("canvas.present", ClawCoreCanvasCommand.Present.rawValue)
    assertEquals("canvas.hide", ClawCoreCanvasCommand.Hide.rawValue)
    assertEquals("canvas.navigate", ClawCoreCanvasCommand.Navigate.rawValue)
    assertEquals("canvas.eval", ClawCoreCanvasCommand.Eval.rawValue)
    assertEquals("canvas.snapshot", ClawCoreCanvasCommand.Snapshot.rawValue)
  }

  @Test
  fun a2uiCommandsUseStableStrings() {
    assertEquals("canvas.a2ui.push", ClawCoreCanvasA2UICommand.Push.rawValue)
    assertEquals("canvas.a2ui.pushJSONL", ClawCoreCanvasA2UICommand.PushJSONL.rawValue)
    assertEquals("canvas.a2ui.reset", ClawCoreCanvasA2UICommand.Reset.rawValue)
  }

  @Test
  fun capabilitiesUseStableStrings() {
    assertEquals("canvas", ClawCoreCapability.Canvas.rawValue)
    assertEquals("camera", ClawCoreCapability.Camera.rawValue)
    assertEquals("screen", ClawCoreCapability.Screen.rawValue)
    assertEquals("voiceWake", ClawCoreCapability.VoiceWake.rawValue)
  }

  @Test
  fun screenCommandsUseStableStrings() {
    assertEquals("screen.record", ClawCoreScreenCommand.Record.rawValue)
  }
}
