/**
 * 🎼 CLAWCORE ORCHESTRATOR (v2.5) - Unified Edition
 * El director de orquesta soberano. 
 * Elimina dependencias externas y centraliza el flujo en el fuente local.
 * Protocolo R.I.S.E. 2026.
 */

import { ClawRouter } from './router.js';
import { Guardian } from './Guardian.js';
import { NanoInfer } from './NanoInfer.js';
import { MemoryCore } from './MemoryCore.js'; // Centralización de memoria
import { PowerOrchestrator } from './PowerOrchestrator.js'; // Gestión de Hardware

export class Orchestrator {
  private router: ClawRouter;
  private guardian: Guardian;
  private nano: NanoInfer;
  private memory: MemoryCore;
  private power: PowerOrchestrator;

  constructor() {
    this.router = new ClawRouter();
    this.guardian = new Guardian();
    this.nano = new NanoInfer();
    this.memory = new MemoryCore();
    this.power = new PowerOrchestrator();
    
    console.log("🎼 [Orchestrator v2.5]: Inicializado sobre ClawCore Unified.");
  }

  /**
   * Procesa tareas priorizando la soberanía local y el ahorro de tokens.
   */
  async processTask(task: string): Promise<string> {
    // 1. Evaluación de Hardware & SafetyGuard
    const tier = await this.power.autoEvaluateTier();
    console.log(`🎼 [Orchestrator]: Operando en modo ${tier}`);

    // 2. Consulta a Memoria Local (RAG Axiomático) - AHORRA TOKENS
    const context = await this.memory.recall(task);
    
    // 3. Intento de Inferencia Nano (0 Tokens)
    const localResult = await this.nano.infer(task);
    if (localResult !== "unknown") {
        console.log("🎼 [Orchestrator]: Resolución local exitosa (0 tokens used).");
        return localResult;
    }

    // 4. Resolución Cloud Protegida (Solo si es necesario)
    const response = await this.router.dispatch(task, 0);

    // 5. Reporte de Austeridad al Guardian
    this.guardian.updateTokens(task.length + response.length); // Estimación rápida
    
    return response;
  }
}
