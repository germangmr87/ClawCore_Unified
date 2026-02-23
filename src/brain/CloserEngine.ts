/**
 * 💰 CLAWCORE CLOSER ENGINE (v1.0)
 * Lógica autónoma de cierre de ventas "Lead-to-Cash".
 * Orquesta WebOperator y VoiceSales para conversiones.
 */

import { WebOperator } from '../neurons/WebOperator.js';
import { VoiceSales } from '../neurons/VoiceSales.js';

export interface SalesLead {
  id: string;
  source: string; // ej: 'facebook', 'ebay'
  contactInfo: string;
  itemOfInterest: string;
  status: 'new' | 'qualifying' | 'contacted' | 'closed';
}

export class CloserEngine {
  private web: WebOperator;
  private voice: VoiceSales;

  constructor() {
    this.web = new WebOperator();
    this.voice = new VoiceSales();
  }

  /**
   * Ciclo de cierre autónomo:
   * 1. Detecta interés en RRSS (via WebOperator).
   * 2. Extrae contacto.
   * 3. Inicia llamada de cualificación (via VoiceSales).
   */
  async autoCloseCycle(lead: SalesLead) {
    console.log(`💰 [Closer]: Iniciando ciclo para lead ${lead.id} (${lead.source})...`);
    
    // Paso 1: Interactuar en la web para obtener más datos
    const context = await this.web.executeMission(`Cualifica interés de ${lead.contactInfo} sobre ${lead.itemOfInterest}`);
    
    // Paso 2: Si el contexto es positivo, llamar
    if (context.includes("interesado")) {
      await this.voice.startCall(lead.contactInfo, `Hola, llamo por el artículo ${lead.itemOfInterest}...`);
    }
    
    console.log("✅ [Closer]: Ciclo de venta completado.");
  }
}
