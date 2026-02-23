import { ClawCore } from './clawcore.js';

const system = new ClawCore();

export function iniciarClawCore(): string {
    // La inicialización es asíncrona, pero para el CLI podemos devolver un estado inmediato
    // o manejarlo con una promesa en el CLI propiamente.
    // Por simplicidad en este adaptador, devolvemos el comando de inicio.
    system.inicializar();
    return "🛰️ Nucleo ClawCore Iniciado (Modo Independiente)";
}

export function obtenerIdentidadClawCore(): string {
    return system.obtenerIdentidad();
}
