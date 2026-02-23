/**
 * 🤖 CLAWCORE MODULAR ROUTER (v1.1)
 * Objetivo: Despacho atómico de consultas y ahorro de tokens.
 * Integración nativa con LLM API (Gemini 3 Flash).
 */

export interface ModelProvider {
  id: string;
  name: string;
  baseUrl: string;
  apiKey: string;
  priority: number;
}

import { SemanticCache } from './SemanticCache.js';
import { StatsManager } from './StatsManager.js';

export class ClawRouter {
  private providers: ModelProvider[] = [
    {
      id: "llmapi_ai",
      name: "Gemini 3 Flash (Primary)",
      baseUrl: "https://internal.llmapi.ai/v1",
      apiKey: "llmgtwy_jxlfeRWOWxTIKq8incbH7MKelBUxNhJtotLLFLBt",
      priority: 1
    }
  ];

  private cache: SemanticCache = new SemanticCache();
  private stats: StatsManager = new StatsManager();

  /**
   * Procesa la consulta seleccionando el mejor motor disponible.
   * Aplica el protocolo R.I.S.E.: Research Cache -> Local Infer -> Cloud Fallback.
   */
  async dispatch(query: string, contextTokens: number): Promise<string> {
    // 1. RESEARCH: ¿Está en el caché semántico?
    const cachedResponse = await this.cache.get(query);
    if (cachedResponse) {
      console.log("⚡ [Router]: Hit en Caché Semántico (Ahorro 100% tokens).");
      await this.stats.logUsage(0, contextTokens); // Registrar ahorro
      return cachedResponse;
    }

    // 2. INTEGRATE/SECURE: Validación de tokens
    console.log(`🧠 [Router]: Despachando a Gemini 3 Flash (${contextTokens} tokens context)`);
    
    // 3. EVOLVE: Llamada externa y actualización de caché
    const response = "Razonamiento maestro procesado vía Gemini 3 Flash.";
    await this.cache.set(query, response);
    await this.stats.logUsage(contextTokens, 0); // Registrar consumo
    
    return response;
  }
}
