import { AxiomEngine } from './AxiomEngine.js';

/**
 * ⚡ CLAWCORE NANO-INFERENCE (v2.0)
 * Cerebro local determinista. 0 Tokens Cloud.
 */
export class NanoInfer {
  private axiomEngine: AxiomEngine;

  constructor() {
    this.axiomEngine = new AxiomEngine();
  }

  async infer(prompt: string): Promise<string> {
    // 1. Resolver vía Axiomas (Rápido, 0 Tokens)
    const result = await this.axiomEngine.solve(prompt);
    if (result) return result;

    // 2. Lógica de Heurística de Seguridad
    if (prompt.toLowerCase().includes("peligro") || prompt.toLowerCase().includes("seguridad")) {
      return "⚠️ [NanoGuard]: Bloqueo preventivo activado. Tarea requiere supervisión humana.";
    }

    return "unknown";
  }
}
