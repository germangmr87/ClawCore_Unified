import os
import json
import logging
from flask import Flask, render_template_string, jsonify
from src.clawcore_system.neuronas.sovereign_telemetry import telemetry
from src.clawcore_system.neuronas.orquestador_p2p import mesh

app = Flask(__name__)
logger = logging.getLogger("SovereignPortal")

# --- INTERFAZ UI SOBERANA (HTML/JS) ---
UI_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>ClawCore V5 | Portal de Soberanía</title>
    <style>
        body { background: #0a0a0c; color: #00ffcc; font-family: 'JetBrains Mono', monospace; margin: 0; overflow: hidden; }
        #header { padding: 20px; border-bottom: 1px solid #00ffcc; display: flex; justify-content: space-between; align-items: center; }
        #mesh-map { width: 100vw; height: 60vh; background: radial-gradient(circle, #1a1a2e 0%, #0a0a0c 100%); position: relative; }
        .node { position: absolute; width: 20px; height: 20px; background: #00ffcc; border-radius: 50%; box-shadow: 0 0 15px #00ffcc; transition: all 0.5s; }
        .node-label { position: absolute; margin-top: 25px; font-size: 12px; white-space: nowrap; text-align: center; transform: translateX(-40%); }
        #stats-panel { height: 30vh; padding: 20px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; background: rgba(0, 255, 204, 0.05); }
        .stat-card { border: 1px solid #00ffcc; padding: 15px; border-radius: 5px; }
        .pulse { animation: pulse-animation 2s infinite; }
        @keyframes pulse-animation { 0% { box-shadow: 0 0 0 0px rgba(0, 255, 204, 0.4); } 100% { box-shadow: 0 0 0 20px rgba(0, 255, 204, 0); } }
    </style>
</head>
<body>
    <div id="header">
        <div style="font-size: 24px;">🔱 CLAWCORE <span style="font-weight:100">V5.3 Ω</span></div>
        <div id="sovereignty-score">SOVEREIGNTY: 0%</div>
    </div>
    
    <div id="mesh-map">
        <!-- Nodos inyectados por JS -->
    </div>

    <div id="stats-panel">
        <div class="stat-card">
            <h3>🧠 COGNICIÓN</h3>
            <div id="cog-stats">Cargando sinapsis...</div>
        </div>
        <div class="stat-card">
            <h3>🛡️ SEGURIDAD</h3>
            <div id="sec-stats">Integridad nominal.</div>
        </div>
        <div class="stat-card">
            <h3>⚡ HARDWARE</h3>
            <div id="hw-stats">CPU: 0% | RAM: 0%</div>
        </div>
    </div>

    <script>
        async function updateData() {
            const res = await fetch('/api/status');
            const data = await res.json();
            
            document.getElementById('sovereignty-score').innerText = `SOVEREIGNTY: ${data.sovereignty_score * 100}%`;
            document.getElementById('cog-stats').innerHTML = `Nodos: ${data.nodos_conocimiento}<br>Sinapsis: ${data.sinapsis_totales}`;
            document.getElementById('hw-stats').innerHTML = `CPU: ${data.hardware.cpu}%<br>RAM: ${data.hardware.ram}%`;
            
            const map = document.getElementById('mesh-map');
            map.innerHTML = ''; // Limpiar
            
            // Dibujar Nodo Master
            drawNode(400, 200, 'iMac Master', true);
            
            // Dibujar Peers
            if(data.peers) {
                let angle = 0;
                for(const peerId in data.peers) {
                    const x = 400 + Math.cos(angle) * 200;
                    const y = 200 + Math.sin(angle) * 150;
                    drawNode(x, y, peerId, data.peers[peerId].alive);
                    angle += Math.PI;
                }
            }
        }

        function drawNode(x, y, label, alive) {
            const map = document.getElementById('mesh-map');
            const div = document.createElement('div');
            div.className = 'node' + (alive ? ' pulse' : '');
            div.style.left = x + 'px';
            div.style.top = y + 'px';
            div.style.background = alive ? '#00ffcc' : '#ff3366';
            div.style.boxShadow = alive ? '0 0 15px #00ffcc' : '0 0 15px #ff3366';
            
            const name = document.createElement('div');
            name.className = 'node-label';
            name.innerText = label;
            div.appendChild(name);
            map.appendChild(div);
        }

        setInterval(updateData, 5000);
        updateData();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(UI_TEMPLATE)

@app.route('/api/status')
def status():
    # Unir telemetría local con datos de la malla P2P
    base = telemetry.obtener_estado_holistico()
    malla = mesh.reporte()
    base['peers'] = malla['peers']
    return jsonify(base)

def start_portal(port=18790):
    logger.info(f"🌐 Iniciando Portal de Soberanía en puerto {port}...")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    # Registro de la malla real para el portal
    mesh.registrar_peer("SENTINEL-229", "15.204.231.229", 19000)
    mesh.registrar_peer("EVOLUTION-132", "15.204.248.132", 19000)
    mesh.iniciar()
    start_portal()
