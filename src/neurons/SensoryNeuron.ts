/**
 * 👂 CLAWCORE SENSORY CORTEX (v1.0)
 * Unifica la percepción del sistema: Oídos (STT) y Ojos (Vision).
 * Basado en Faster-Whisper (Sovereign Ears) y VisionMaster.
 */

export interface SensoryInput {
  type: 'audio' | 'image' | 'video';
  filePath: string;
}

export class SensoryNeuron {
  /**
   * Procesa la entrada sensorial y la convierte en axiomas técnicos.
   */
  async perceive(input: SensoryInput): Promise<string> {
    console.log(`👁️👂 [Sensory]: Percibiendo entrada de tipo "${input.type}"...`);
    
    if (input.type === 'audio') {
      return await this.transcribeSovereign(input.filePath);
    }
    
    return "unknown";
  }

  private async transcribeSovereign(path: string): Promise<string> {
    // Inyección de Faster-Whisper local vía script de Python
    console.log("👂 [Sensory]: Transcribiendo vía Faster-Whisper local...");
    const { execSync } = require('child_process');
    try {
      const result = execSync(`python3.10 /Users/german/.clawcore/workspace/neurons/sovereign_ears.py ${path}`).toString();
      return result.trim();
    } catch (e) {
      return "Error en transcripción soberana.";
    }
  }
}
