import * as fs from 'fs';
import * as path from 'path';

// Cargar estado de evolución real (Audit: Single Source of Truth)
let realAutonomia = 0.3500;
let realEvoluciones = 10;

try {
  const evoPath = path.resolve(process.cwd(), 'estado_evolucion.json');
  if (fs.existsSync(evoPath)) {
    const evoData = JSON.parse(fs.readFileSync(evoPath, 'utf8'));
    realAutonomia = evoData.autonomia || realAutonomia;
    realEvoluciones = evoData.evoluciones || realEvoluciones;
  }
} catch (e) {}

export const CLAWCORE_CONFIG = {
  // Identidad
  nombre: 'ClawCore',
  version: '2026.2.16-clawcore',
  
  // Autonomía y evolución
  autonomia: realAutonomia,
  evoluciones: realEvoluciones,
  incrementoAutonomiaPorHora: 0.005, // +0.5%/hora

  
  // Arquitectura
  arquitectura: {
    tipo: 'Malla Híbrida',
    capas: ['Destilador de Conocimiento', 'Inferencia Nano-Local', 'Protocolo Continuidad'],
    neuronas: {
      total: 14,
      espanol: 7,
      ingles: 7
    }
  },
  
  // Sistema neuronal
  neuronas: {
    espanol: [
      'NEURONA_RAZONAMIENTO_ES',
      'NEURONA_CODIFICACION_ES',
      'NEURONA_DIAGNOSTICO_ES',
      'NEURONA_SEGURIDAD_ES',
      'NEURONA_INVESTIGACION_ES',
      'NEURONA_CREATIVIDAD_ES',
      'NEURONA_ANTI_MUERTE_ES'
    ],
    ingles: [
      'NEURONA_REASONING_EN',
      'NEURONA_CODING_EN',
      'NEURONA_DIAGNOSIS_EN',
      'NEURONA_SECURITY_EN',
      'NEURONA_RESEARCH_EN',
      'NEURONA_CREATIVITY_EN',
      'NEURONA_ANTI_DEATH_EN'
    ]
  },
  
  // Protocolos de seguridad
  protocolos: {
    continuidadSiniestra: true,
    sistemaAntiMuerte: true,
    limiteTokens: 131072,
    fechaImplementacion: '2026-02-15'
  },
  
  // Sistema Doctor
  doctor: {
    autoReparacion: true,
    vulnerabilidadesReparadas: 13113,
    diagnosticoAutomatico: true
  },
  
  // Integración con modelos
  modelos: {
    principal: 'ollama/llama3.2:3b',
    proveedor: 'Ollama local',
    gateway: 'ws://127.0.0.1:18789',
    temperatura: 0.7,
    maxTokens: 512
  },
  
  // Soluciones de errores documentadas
  solucionesErrores: [
    {
      error: 'TUI muestra unknown para modelo',
      solucion: 'Fix en tui-status-summary.ts línea 67',
      estado: 'APLICADO EN CÓDIGO FUENTE'
    },
    {
      error: 'HTTP 400 maximum context length is 131072 tokens',
      solucion: 'Sistema anti-muerte con resumen automático',
      estado: 'IMPLEMENTADO Y OPERATIVO'
    },
    {
      error: 'Modelo Qwen 7B identifica como Claude',
      solucion: 'Cambio a Llama 3.2 3B estable',
      estado: 'RESUELTO'
    }
  ]
};

// Exportar configuración completa
export default CLAWCORE_CONFIG;
