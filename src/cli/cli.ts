#!/usr/bin/env node
// 🚀 CLAWCORE CLI - Interfaz de línea de comandos

import { iniciarClawCore, obtenerIdentidadClawCore } from '../clawcore_system/cli-adapter.js';

const command = process.argv[2];

switch(command) {
  case 'start':
    console.log(iniciarClawCore());
    break;
    
  case 'identidad':
    console.log(obtenerIdentidadClawCore());
    break;
    
  case 'version':
  case '--version':
  case '-v':
    console.log('ClawCore 2026.2.16-clawcore');
    console.log('• Instalación: Local / Independiente');

    console.log('• Autonomía: 25.85%');
    console.log('• Evoluciones: 8');
    break;
    
  default:
    console.log('📖 CLAWCORE CLI - Ayuda');
    console.log('=======================');
    console.log('Uso: clawcore <comando>');
    console.log('');
    console.log('Comandos:');
    console.log('  start     - Iniciar sistema ClawCore');
    console.log('  identidad - Mostrar identidad completa');
    console.log('  version   - Mostrar versión');
    console.log('');
    console.log('🎯 Sistema evolutivo operativo');

}
