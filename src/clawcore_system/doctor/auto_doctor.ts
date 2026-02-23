import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs/promises';
import path from 'path';

const execAsync = promisify(exec);

export class ClawCoreDoctor {
  private autonomia: number = 0.30;
  private neuronasPath: string;

  constructor() {
    this.neuronasPath = path.resolve(__dirname, '../../neuronas');
  }

  /**
   * Realiza un escaneo profundo de salud invocando al reparador Python
   */
  async realizarEscaneo(): Promise<{ salud: number; vulnerabilidades: number }> {
    console.log('🩺 ClawDoctor: Iniciando escaneo de salud neuronal...');
    try {
      // Invocamos al script de Python
      const scriptPath = path.join(this.neuronasPath, 'auto_reparacion_neuronas.py');
      await execAsync(`python3 ${scriptPath}`);
      
      // Leemos el reporte generado
      const reportePath = path.join(this.neuronasPath, 'salud_neuronal.json');
      const data = await fs.readFile(reportePath, 'utf8');
      const reporte = JSON.parse(data);
      
      const v = reporte.vulnerabilidades_detectadas || 0;
      const salud = v === 0 ? 1.0 : Math.max(0.1, 1.0 - (v * 0.05));
      
      return { salud, vulnerabilidades: v };
    } catch (error) {
      console.error('❌ Error en escaneo de doctor:', error);
      return { salud: 0.5, vulnerabilidades: -1 };
    }
  }

  /**
   * Ejecuta reparaciones automáticas
   */
  async reparar(): Promise<void> {
    console.log('🔧 ClawDoctor: Ejecutando protocolos de auto-reparación...');
    try {
      const scriptPath = path.join(this.neuronasPath, 'auto_reparacion_neuronas.py');
      const { stdout } = await execAsync(`python3 ${scriptPath}`);
      console.log(stdout);
      
      // Incrementar autonomía simbólicamente tras reparación exitosa
      this.autonomia = Math.min(1.0, this.autonomia + 0.01);
    } catch (error) {
      console.error('❌ Fallo en reparación:', error);
    }
  }
}
