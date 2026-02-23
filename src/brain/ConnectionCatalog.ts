/**
 * 🔌 CLAWCORE CONNECTION CATALOG (v1.0)
 * Repositorio de configuraciones pre-validadas.
 * Evita errores de sintaxis al agregar nuevas APIs.
 */

export interface ConnectionTemplate {
  provider: string;
  baseUrl: string;
  requiredFields: string[];
  defaultModel: string;
}

export const ConnectionCatalog: ConnectionTemplate[] = [
  {
    provider: "openai",
    baseUrl: "https://api.openai.com/v1",
    requiredFields: ["apiKey"],
    defaultModel: "gpt-4o"
  },
  {
    provider: "anthropic",
    baseUrl: "https://api.anthropic.com/v1",
    requiredFields: ["apiKey"],
    defaultModel: "claude-3-5-sonnet"
  },
  {
    provider: "llmapi_ai",
    baseUrl: "https://internal.llmapi.ai/v1",
    requiredFields: ["apiKey"],
    defaultModel: "gemini-3-flash-preview"
  },
  {
    provider: "google",
    baseUrl: "https://generativelanguage.googleapis.com/v1beta",
    requiredFields: ["apiKey"],
    defaultModel: "gemini-1.5-pro"
  }
];

import { Guardian } from './Guardian.js';

export class ConnectionManager {
  private guardian: Guardian = new Guardian();

  /**
   * Actualiza una conexión existente con backup preventivo.
   */
  async updateConnection(providerId: string, values: Record<string, string>) {
    await this.guardian.createConfigBackup();
    console.log(`🔌 [ConnManager]: Actualizando valores para ${providerId}...`);
    // Lógica quirúrgica de actualización...
  }
}
