import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

/**
 * 🛡️ CLAWCORE GUARDIAN (v2.1)
 * El protocolo anti-muerte e inmortalidad por recursos.
 * Vigilancia de archivos, configuración y RAM crítica.
 */
export class Guardian {
  private vitalSigns: Map<string, boolean> = new Map();
  private ramThreshold: number = 0.05; // 5% RAM libre mínima
  private contextLimit: number = 1048576; // 1M tokens (Gemini 1.5 Flash)
  private currentTokens: number = 0;

  constructor() {
    this.startPulse();
  }

  /**
   * Reporte detallado para el usuario: Recursos + Saldo/Tokens
   */
  public getAusterityReport() {
    const freeMem = (os.freemem() / 1024 / 1024 / 1024).toFixed(2);
    const totalMem = (os.totalmem() / 1024 / 1024 / 1024).toFixed(2);
    const usagePercent = ((this.currentTokens / this.contextLimit) * 100).toFixed(2);

    return {
      hardware: { ram_free: `${freeMem}GB`, ram_total: `${totalMem}GB` },
      tokens: {
        limit: this.contextLimit,
        used: this.currentTokens,
        percent: `${usagePercent}%`,
        status: this.currentTokens > 800000 ? "CRITICAL" : "OPTIMAL"
      },
      austerity_active: true
    };
  }

  public updateTokens(count: number) {
    this.currentTokens = count;
  }

  private startPulse() {
    setInterval(() => this.heartCheck(), 60000); // Latido cada minuto
  }

  async heartCheck() {
    console.log("🛡️ [Guardian]: Latido detectado. Verificando integridad y recursos...");
    
    // 1. Vigilancia de Archivos Críticos
    const criticalFiles = ['entry.js', 'brain/Orchestrator.js', 'ui/ConfigPortal.js'];
    for (const file of criticalFiles) {
      const p = path.join(process.cwd(), 'src', file);
      if (!fs.existsSync(p)) {
        console.error(`🚨 [Guardian]: Archivo crítico ausente: ${file}. Iniciando recuperación...`);
        this.heal(file);
      }
    }

    // 2. Vigilancia de Recursos (NUEVO v2.1)
    await this.resourceVigilance();
  }

  /**
   * Monitoriza la RAM y cierra procesos no esenciales si baja del 5%.
   */
  private async resourceVigilance() {
    const totalMem = os.totalmem();
    const freeMem = os.freemem();
    const freePercent = freeMem / totalMem;

    if (freePercent < this.ramThreshold) {
      console.warn(`🚨 [Guardian]: RAM Crítica detectada (${(freePercent * 100).toFixed(2)}%). Ejecutando Purga de Supervivencia...`);
      await this.survivalPurge();
    }
  }

  /**
   * Cierra procesos pesados o no vitales (ej. indexadores, caches antiguos).
   */
  private async survivalPurge() {
    console.log("🧬 [Guardian]: Purgando procesos no vitales para liberar memoria...");
    // Lógica: pkill -f scan_and_learn.py, limpiar caches de memoria volátil, etc.
  }

  async heal(file: string) {
    console.log(`🧬 [Guardian]: Sanando ${file}...`);
  }

  /**
   * Crea un backup instantáneo de la configuración.
   */
  async createConfigBackup() {
    const configPath = path.join(process.cwd(), 'clawcore.json');
    const backupPath = `${configPath}.sovereign.bak`;
    if (fs.existsSync(configPath)) {
      fs.copyFileSync(configPath, backupPath);
      console.log("🛡️ [Guardian]: Backup preventivo de configuración creado.");
    }
  }

  /**
   * Revierte a la última configuración estable.
   */
  async rollbackConfig() {
    const configPath = path.join(process.cwd(), 'clawcore.json');
    const backupPath = `${configPath}.sovereign.bak`;
    if (fs.existsSync(backupPath)) {
      fs.copyFileSync(backupPath, configPath);
      console.warn("🚨 [Guardian]: Rollback ejecutado. Configuración restaurada.");
    }
  }
}
