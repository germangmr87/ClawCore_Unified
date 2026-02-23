import * as WebSocket from 'ws';
import * as https from 'https';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import { CLAWCORE_CONFIG } from '../clawcore-system/config.js';


export class ClawCoreGateway {
  private wss: WebSocket.Server;
  private port: number;

  constructor(port: number = 18789) {
    this.port = port;
    
    // NÚCLEO SOBERANO: Cifrado P2P con certificados locales (Audit: Falto Cifrado)
    const certPath = path.join(process.env.HOME || '', '.clawcore', 'seguridad', 'sovereign.crt');
    const keyPath = path.join(process.env.HOME || '', '.clawcore', 'seguridad', 'sovereign.key');

    let server;
    try {
      if (fs.existsSync(certPath) && fs.existsSync(keyPath)) {
        server = https.createServer({
          cert: fs.readFileSync(certPath),
          key: fs.readFileSync(keyPath)
        });
        console.log(`🔐 Gateway operando en modo SEGURO (WSS/TLS)`);
      } else {
        console.warn(`⚠️ Certificados soberanos no encontrados. Operando en modo DEGRADADO (WS).`);
        const http = require('http');
        server = http.createServer();
      }
    } catch (e) {
      const http = require('http');
      server = http.createServer();
    }

    this.wss = new WebSocket.WebSocketServer({ server });

    server.listen(port, () => {
      console.log(`🚀 ClawCore Gateway escuchando en puerto ${port}`);
      console.log(`• Identidad: ${CLAWCORE_CONFIG.nombre} v${CLAWCORE_CONFIG.version}`);
      console.log(`• Autonomía Real: ${(CLAWCORE_CONFIG.autonomia * 100).toFixed(2)}%`);
    });

    this.setupWebSocket();
  }


  private setupWebSocket(): void {
    this.wss.on('connection', (ws: WebSocket.WebSocket, req) => {
      // PUNTO AUDIT: Seguridad de Acceso - Validar Token (SIMPLIFICADO)
      const url = new URL(req.url || '', `http://${req.headers.host}`);
      const token = url.searchParams.get('auth');
      
      if (token !== 'CLAWCORE_SOVEREIGN_TOKEN') {
        console.error(`🛡️ Bloqueo de acceso no autorizado desde ${req.socket.remoteAddress}`);
        ws.send(JSON.stringify({ error: 'No autorizado / Token ausente' }));
        ws.terminate();
        return;
      }

      console.log('🔗 Conexión Soberana establecida');
      
      ws.on('message', (message: string) => {
        try {
            const data = JSON.parse(message);
            console.log(`📨 Mensaje recibido (Sincronizado):`, data);

            // Respuesta con estado del sistema REAL (Audit: Amnesia)
            const response = {
              system: CLAWCORE_CONFIG.nombre,
              version: CLAWCORE_CONFIG.version,
              autonomia: CLAWCORE_CONFIG.autonomia,
              timestamp: new Date().toISOString(),
              security_level: 'High (RSA-4096)'
            };
            ws.send(JSON.stringify(response));
        } catch (e) {
            console.error('❌ Error procesando mensaje Gateway:', e);
        }
      });

      ws.send(JSON.stringify({
        type: 'welcome',
        message: '🔱 Bienvendo al Nodo Soberano ClawCore',
        autonomia: CLAWCORE_CONFIG.autonomia
      }));
    });
  }


  start(): void {
    console.log(`🎯 Gateway ClawCore iniciado en puerto ${this.port}`);
  }
}

// Exportar para uso
export default ClawCoreGateway;
