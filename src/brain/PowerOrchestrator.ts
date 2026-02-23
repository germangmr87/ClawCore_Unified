import * as os from 'os';
// import psutil

/**
 * ⚡ CLAWCORE POWER ORCHESTRATOR (v2.0)
 * Detecta el hardware y decide el Nivel de Despliegue.
 * Incluye SafetyGuard para prevenir colapsos por mala gestión del usuario.
 */

export enum PowerTier {
  MINIMUM = "MINIMUM",
  MEDIUM = "MEDIUM",
  MAXIMUM = "MAXIMUM"
}

export class PowerOrchestrator {
  private safetyLimit: number = 0.90; // No permitir usar más del 90% de los recursos totales

  /**
   * Evalúa los recursos y aplica el SafetyGuard.
   */
  async autoEvaluateTier(): Promise<PowerTier> {
    const totalMemory = os.totalmem() / (1024 ** 3);
    const cpuCores = os.cpus().length;
    
    // SafetyGuard: Si la memoria libre es < 10%, forzar modo inferior
    const freeMemoryPercent = os.freemem() / os.totalmem();
    
    if (freeMemoryPercent < (1 - this.safetyLimit)) {
      console.warn("🚨 [PowerOrch]: Recursos críticos detectados. Activando SafetyGuard.");
      return PowerTier.MINIMUM; 
    }

    if (totalMemory >= 16 && cpuCores >= 4) {
      return PowerTier.MAXIMUM;
    } else if (totalMemory >= 8) {
      return PowerTier.MEDIUM;
    }
    return PowerTier.MINIMUM;
  }

  /**
   * Procesa la solicitud de aumento de poder del usuario (Overdrive).
   */
  async requestOverdrive() {
    const freeMem = os.freemem() / (1024 ** 3);
    if (freeMem < 1.5) { // Si queda menos de 1.5GB libres, denegar aumento
      return { status: "denied", message: "Recursos insuficientes para Overdrive seguro." };
    }
    return { status: "granted", message: "Overdrive activado bajo vigilancia del Guardian." };
  }
}
