import { ClawCoreGateway } from './gateway/index.js';

// Lanzador Soberano del Gateway V4.5
const port = 18789;
const gateway = new ClawCoreGateway(port);
gateway.start();

console.log(`🔱 Nodo de Comunicaciones ClawCore activo en puerto ${port}`);
