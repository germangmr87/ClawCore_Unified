import fs from 'node:fs';
import path from 'node:path';
import { Guardian } from './Guardian.js';

/**
 * 👨‍⚕️ CLAWCORE DOCTOR (v2.1)
 * Sistema de Diagnóstico y Restauración Quirúrgica.
 * Protocolo R.I.S.E. 2026: Verificación de Dependencias y Ciclos.
 */

export interface HealthReport {
  status: 'healthy' | 'warning' | 'critical';
  issues: string[];
  integrityScore: number;
}

export class Doctor {
  private guardian: Guardian;
  private projectRoot: string = process.cwd();

  constructor() {
    this.guardian = new Guardian();
    console.log("👨‍⚕️ [Doctor]: Iniciando consultorio técnico v2.1.");
  }

  /**
   * Chequeo General: Valida la salud de la arquitectura modular.
   */
  async fullCheckup(): Promise<HealthReport> {
    console.log("🔍 [Doctor]: Escaneando integridad semántica...");
    const issues: string[] = [];
    
    // 1. Verificar enlaces de módulos (Imports)
    const modules = ['src/brain/Orchestrator.js', 'src/brain/MindReader.js', 'src/ui/ConfigPortal.js'];
    for (const mod of modules) {
      if (!fs.existsSync(path.join(this.projectRoot, mod))) {
        issues.push(`Módulo ausente: ${mod}`);
      }
    }

    // 2. Detectar riesgos de recursión (Circular dependencies)
    // TODO: Inyectar analizador de grafo de dependencias estático

    const score = issues.length === 0 ? 100 : Math.max(0, 100 - (issues.length * 20));
    const status = score > 90 ? 'healthy' : (score > 50 ? 'warning' : 'critical');

    console.log(`📊 [Doctor]: Diagnóstico completado. Score: ${score}%`);
    return { status, issues, integrityScore: score };
  }

  async restoreSurgical(componentId: string) {
    console.warn(`🩹 [Doctor]: Aplicando parche quirúrgico a ${componentId}...`);
    await this.guardian.rollbackConfig();
  }
}
