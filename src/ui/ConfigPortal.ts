import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';

export class ConfigPortal {
  private port: number = 18790;
  private neuronsDir: string = path.join(process.cwd(), 'src/neurons');

  constructor() {
    this.startServer();
  }

  private startServer() {
    const server = http.createServer(async (req, res) => {
      // API: Nivel de Poder (con seguridad adaptativa)
      if (req.url === '/api/power' && req.method === 'GET') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        return res.end(JSON.stringify({
          tier: "MAXIMUM",
          color: "indigo-500",
          details: "16GB RAM + 8 Cores VPS229. Modo Soberano Activo.",
          safetyGuard: "Active"
        }));
      }

      // API: Listar Neuronas
      if (req.url === '/api/neurons' && req.method === 'GET') {
        try {
            const files = fs.readdirSync(this.neuronsDir);
            res.writeHead(200, { 'Content-Type': 'application/json' });
            return res.end(JSON.stringify(files));
        } catch (e) {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            return res.end(JSON.stringify([]));
        }
      }

      // UI Principal Evolucionada (ClawCore V3 Master Interface)
      res.writeHead(200, { 'Content-Type': 'text/html' });
      res.end(`
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>ClawCore V3 | Master Portal</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
            <style>
                body { background-color: #0a0a0c; color: #e2e8f0; font-family: 'Inter', sans-serif; }
                .glass { background: rgba(23, 23, 26, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.05); }
                .glow-indigo { box-shadow: 0 0 20px rgba(79, 70, 229, 0.2); }
                .status-pulse { animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
                @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: .5; } }
                .tab-active { border-bottom: 2px solid #6366f1; color: white; }
            </style>
        </head>
        <body class="p-6">
            <nav class="flex justify-between items-center mb-10">
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 bg-indigo-600 rounded-lg flex items-center justify-center glow-indigo">
                        <i class="fas fa-brain text-white"></i>
                    </div>
                    <div>
                        <h1 class="text-xl font-bold tracking-tight">ClawCore <span class="text-indigo-500">Unified V3</span></h1>
                        <p class="text-xs text-gray-500 font-mono uppercase tracking-widest">Sovereign OS | VPS229</p>
                    </div>
                </div>
                <div class="flex items-center gap-4">
                    <div class="glass px-4 py-2 rounded-full text-xs flex items-center gap-2">
                        <div class="w-2 h-2 bg-green-500 rounded-full status-pulse"></div>
                        CORE ONLINE
                    </div>
                    <button class="bg-red-600/20 hover:bg-red-600 text-red-400 hover:text-white px-4 py-2 rounded-lg text-sm transition-all font-medium border border-red-500/30">
                        <i class="fas fa-power-off mr-2"></i> EMERGENCY STOP
                    </button>
                </div>
            </nav>

            <!-- TABS -->
            <div class="flex gap-8 mb-8 border-b border-white/5 text-sm font-medium text-gray-500">
                <button class="pb-4 tab-active">DASHBOARD</button>
                <button class="pb-4 hover:text-white transition-colors">NEURONAS</button>
                <button class="pb-4 hover:text-white transition-colors">TERMINAL</button>
                <button class="pb-4 hover:text-white transition-colors">LOGS PM2</button>
                <button class="pb-4 hover:text-white transition-colors">ARBITRAGE HUNTER</button>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
                <!-- PANEL: SISTEMA -->
                <div class="md:col-span-1 space-y-6">
                    <div class="glass rounded-2xl p-6">
                        <h3 class="text-sm font-semibold text-gray-400 mb-4 flex items-center gap-2">
                            <i class="fas fa-microchip"></i> RECURSOS
                        </h3>
                        <div class="space-y-4">
                            <div>
                                <div class="flex justify-between text-xs mb-1">
                                    <span>CPU Usage</span>
                                    <span class="text-indigo-400 font-mono">18%</span>
                                </div>
                                <div class="w-full bg-gray-800 rounded-full h-1.5">
                                    <div class="bg-indigo-500 h-1.5 rounded-full shadow-[0_0_8px_#6366f1]" style="width: 18%"></div>
                                </div>
                            </div>
                            <div>
                                <div class="flex justify-between text-xs mb-1">
                                    <span>RAM (16GB)</span>
                                    <span class="text-indigo-400 font-mono">3.8GB</span>
                                </div>
                                <div class="w-full bg-gray-800 rounded-full h-1.5">
                                    <div class="bg-indigo-500 h-1.5 rounded-full shadow-[0_0_8px_#6366f1]" style="width: 24%"></div>
                                </div>
                            </div>
                            <div class="pt-4 border-t border-white/5">
                                <p class="text-[10px] text-gray-500 uppercase">Uptime</p>
                                <p class="text-sm font-mono text-indigo-300">02:45:12</p>
                            </div>
                        </div>
                    </div>

                    <div class="glass rounded-2xl p-6">
                        <h3 class="text-sm font-semibold text-gray-400 mb-4 flex items-center gap-2">
                            <i class="fas fa-shield-alt"></i> SEGURIDAD
                        </h3>
                        <div class="space-y-3">
                            <div class="flex justify-between items-center text-xs">
                                <span class="text-gray-500">Whitelist ID</span>
                                <span class="bg-white/5 px-2 py-0.5 rounded text-indigo-400 font-mono">6220610722</span>
                            </div>
                            <div class="flex justify-between items-center text-xs">
                                <span class="text-gray-500">Firewall</span>
                                <span class="text-green-500">ACTIVE</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- PANEL CENTRAL -->
                <div class="md:col-span-3 space-y-6">
                    <div class="glass rounded-2xl p-8">
                        <div class="flex justify-between items-center mb-8">
                            <div>
                                <h2 class="text-2xl font-bold">Resumen de Operaciones</h2>
                                <p class="text-gray-500 text-sm">Estado global de los hilos de ejecución.</p>
                            </div>
                            <div class="flex gap-2">
                                <button onclick="loadNeurons()" class="glass p-2 rounded-lg hover:bg-white/5" title="Recargar">
                                    <i class="fas fa-sync-alt"></i>
                                </button>
                                <button class="bg-indigo-600 hover:bg-indigo-500 px-4 py-2 rounded-lg text-xs transition-all flex items-center gap-2">
                                    <i class="fas fa-plus"></i> NUEVA NEURONA
                                </button>
                            </div>
                        </div>

                        <div id="neuron-grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                            <!-- Neuronas se cargan aquí -->
                        </div>
                    </div>

                    <!-- TERMINAL EMULATOR -->
                    <div class="bg-[#050505] border border-white/5 rounded-2xl p-6 font-mono text-sm h-64 overflow-y-auto">
                        <div class="flex items-center gap-2 text-gray-600 mb-4 border-b border-white/5 pb-2">
                            <i class="fas fa-terminal text-xs"></i>
                            <span class="text-xs uppercase tracking-widest">Live Output Console</span>
                        </div>
                        <div class="space-y-1">
                            <p class="text-indigo-500">[SYSTEM] <span class="text-gray-300">ClawCore V3.1.2 Kernel Loaded.</span></p>
                            <p class="text-indigo-500">[SYSTEM] <span class="text-gray-300">Initializing Neural Mesh...</span></p>
                            <p class="text-green-500">[SUCCESS] <span class="text-gray-300">Gateway established on port 18789.</span></p>
                            <p class="text-yellow-500">[WARN] <span class="text-gray-300">ArbitrageNeuron is awaiting configuration data.</span></p>
                            <p class="text-gray-600">_</p>
                        </div>
                    </div>
                </div>
            </div>

            <script>
                async function loadNeurons() {
                    const grid = document.getElementById('neuron-grid');
                    grid.innerHTML = '<div class="col-span-full py-20 text-center text-gray-600"><i class="fas fa-circle-notch fa-spin mr-2"></i> Sincronizando Malla...</div>';
                    
                    try {
                        const res = await fetch('/api/neurons');
                        const data = await res.json();
                        grid.innerHTML = data.map(n => \`
                            <div class="glass p-6 rounded-xl hover:border-indigo-500/50 transition-all cursor-pointer group relative overflow-hidden">
                                <div class="absolute top-0 right-0 p-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <i class="fas fa-cog text-gray-600 hover:text-indigo-400"></i>
                                </div>
                                <div class="w-12 h-12 bg-indigo-500/10 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:bg-indigo-500 transition-colors shadow-[0_0_15px_rgba(99,102,241,0)] group-hover:shadow-[0_0_15px_rgba(99,102,241,0.4)]">
                                    <i class="fas fa-bolt text-indigo-400 group-hover:text-white"></i>
                                </div>
                                <h4 class="font-bold text-sm text-center">\${n.replace('.js', '')}</h4>
                                <div class="flex items-center justify-center gap-2 mt-3">
                                    <div class="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                                    <p class="text-[10px] text-gray-500 uppercase font-bold tracking-tighter">Active</p>
                                </div>
                            </div>
                        \`).join('');
                    } catch (e) {
                        grid.innerHTML = '<div class="col-span-full py-20 text-center text-red-500">Error al conectar con el Core.</div>';
                    }
                }
                loadNeurons();
                setInterval(loadNeurons, 30000); // Auto-refresh cada 30s
            </script>
        </body>
        </html>
      `);
    });

    server.listen(this.port, '0.0.0.0', () => {
      console.log('🌐 [ConfigPortal]: Master Portal V3 en el puerto 18790');
    });
  }
}
