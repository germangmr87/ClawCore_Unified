/**
 * 🌉 CLAWCORE BRAIN BRIDGE (v2.0)
 * Decoupler: Transport (WebSocket) <-> Intelligence (Orchestrator).
 * Permite evolucionar el cerebro sin reiniciar el Gateway.
 */

import { Orchestrator } from '../brain/Orchestrator.js';

export class BrainBridge {
  private orchestrator: Orchestrator;

  constructor() {
    this.orchestrator = new Orchestrator();
  }

  /**
   * Canaliza mensajes a través del Orchestrator y gestiona el flujo de señales.
   */
  async handleRequest(raw: string): Promise<any> {
    try {
      const payload = JSON.parse(raw);
      console.log(`🌉 [Bridge]: Mensaje procesado -> ${payload.type}`);
      
      const result = await this.orchestrator.processTask(payload.content);
      
      return {
        status: "success",
        response: result,
        timestamp: Date.now()
      };
    } catch (e) {
      return { status: "error", message: "Malformed Brain Signal" };
    }
  }
}
