// 🚀 CLAWCORE V4 - MÓDULO SOBERANO REFACTORIZADO
// Sistema de alta eficiencia y autonomía progresiva

import { ClawCoreDoctor } from './doctor/auto_doctor.js';
import { ProtocoloContinuidad } from './protocolos/continuidad_siniestra.js';
import { ArquitecturaMallaHibrida } from './cerebro/arquitectura_malla.js';
import fs from 'fs/promises';
import path from 'path';

export class ClawCore {
  private doctor: ClawCoreDoctor;
  private protocolo: ProtocoloContinuidad;
  private arquitectura: ArquitecturaMallaHibrida;
  
  private readonly VERSION = '4.0.0-sovereign';
  private autonomyLevel = 0.30;
  private identity = "ClawCore V4 Sovereign Agent";

  constructor() {
    this.doctor = new ClawCoreDoctor();
    this.protocolo = new ProtocoloContinuidad();
    this.arquitectura = new ArquitecturaMallaHibrida();
  }

  /**
   * Inicialización del núcleo con conciencia de entorno y carga de memoria
   */
  async inicializar(): Promise<string> {
    console.log(`[CLAWCORE] Despertando sistema v${this.VERSION}...`);
    
    // 1. Cargar estado previo (Continuidad)
    const estadoPrevio = await this.protocolo.cargarEstadoPrevio();
    if (estadoPrevio) {
        this.autonomyLevel = estadoPrevio.contexto_actual?.autonomyLevel || this.autonomyLevel;
        console.log(`[CLAWCORE] Memoria recuperada. Nivel de Autonomía restaurado al ${this.autonomyLevel * 100}%`);
    }

    // 2. Escaneo de salud (Feedback Loop)
    const status = await this.doctor.realizarEscaneo();
    const recursos = await this.arquitectura.monitorearRecursos();
    
    // Throttling dinámico por hardware
    if (recursos.cpu > 80 || recursos.throttling) {
        console.warn(`[CLAWCORE] Carga de hardware ALTA (${recursos.cpu.toFixed(1)}%). Entrando en modo de ahorro energético.`);
        this.autonomyLevel = Math.max(0.05, this.autonomyLevel - 0.10);
    }

    if (status.salud < 0.9) {
        console.warn(`[CLAWCORE] Salud degradada (${(status.salud * 100).toFixed(1)}%). Iniciando auto-reparación...`);
        await this.doctor.reparar();
        this.autonomyLevel = Math.max(0.1, this.autonomyLevel - 0.05); 
    } else if (recursos.cpu < 50) {
        console.log('[CLAWCORE] Salud óptima y recursos disponibles. Evolución acelerada.');
        this.autonomyLevel = Math.min(1.0, this.autonomyLevel + 0.05);
    }


    // 3. Persistir estado actual
    await this.protocolo.garantizarSupervivencia({
        autonomyLevel: this.autonomyLevel,
        lastOnline: new Date().toISOString()
    });

    return `ClawCore Unified V4 Online. Nivel de Autonomía: ${(this.autonomyLevel * 100).toFixed(1)}%`;
  }

  async analizarArchivoLocal(filePath: string): Promise<string | null> {
    try {
        const absolutePath = path.resolve(process.cwd(), filePath);
        if (!absolutePath.includes('ClawCore_Unified')) return 'Acceso denegado: Violación de perímetro.';
        
        const content = await fs.readFile(absolutePath, 'utf8');
        return content;
    } catch (e) {
        return null;
    }
  }

  obtenerIdentidad(): string {
    return `Identidad Soberana: ${this.identity}. Arquitecto de Sistemas Gabriel.`;
  }
}
