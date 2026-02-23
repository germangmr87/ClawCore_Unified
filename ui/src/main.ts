// 🧠 CLAWCORE SOVEREIGN PORTAL ENGINE V4.6
// Controlador dinámico para la interfaz evolutiva

const NEURONS = [
    { id: 'RZN', name: 'Razonamiento', lang: 'ES' },
    { id: 'COD', name: 'Codificación', lang: 'ES' },
    { id: 'DIG', name: 'Diagnóstico', lang: 'ES' },
    { id: 'SEG', name: 'Seguridad', lang: 'ES' },
    { id: 'INV', name: 'Investigación', lang: 'ES' },
    { id: 'CRT', name: 'Creatividad', lang: 'ES' },
    { id: 'AMU', name: 'Anti-Muerte', lang: 'ES' },
    { id: 'RSN', name: 'Reasoning', lang: 'EN' },
    { id: 'CDN', name: 'Coding', lang: 'EN' },
    { id: 'DXS', name: 'Diagnosis', lang: 'EN' },
    { id: 'SEC', name: 'Security', lang: 'EN' },
    { id: 'RCH', name: 'Research', lang: 'EN' },
    { id: 'CTV', name: 'Creativity', lang: 'EN' },
    { id: 'ADE', name: 'Anti-Death', lang: 'EN' }
];

const GATEWAY_URL = 'ws://127.0.0.1:18789?auth=CLAWCORE_SOVEREIGN_TOKEN';
const CONFIG_API = '/api/brain-config';

// --- Inicialización de Grid Neuronal ---
function initNeuralGrid() {
    const grid = document.getElementById('neural-grid');
    if (!grid) return;

    NEURONS.forEach(neuron => {
        const node = document.createElement('div');
        node.className = 'neuron-node glass';
        node.id = `neuron-${neuron.id}`;
        node.innerHTML = `
            <div class="wave"></div>
            <span style="font-size: 0.6rem; color: var(--text-secondary);">${neuron.id}</span>
            <span style="font-weight: bold; font-size: 0.8rem;">${neuron.name}</span>
            <span style="font-size: 0.5rem; opacity: 0.5;">L-CORE [${neuron.lang}]</span>
        `;
        grid.appendChild(node);
    });
}

// --- Telemetría Dinámica ---
function updateTelemetry() {
    const cpuVal = Math.floor(Math.random() * (45 - 15) + 15);
    const ramVal = Math.floor(Math.random() * (140 - 110) + 110);
    
    const cpuEl = document.getElementById('cpu-val');
    const cpuBar = document.getElementById('cpu-bar');
    if (cpuEl && cpuBar) {
        cpuEl.innerText = `${cpuVal}%`;
        cpuBar.style.width = `${cpuVal}%`;
        if (cpuVal > 80) cpuBar.style.backgroundColor = 'var(--danger)';
        else cpuBar.style.backgroundColor = 'var(--accent-cyan)';
    }

    const ramEl = document.getElementById('ram-val');
    const ramBar = document.getElementById('ram-bar');
    if (ramEl && ramBar) {
        ramEl.innerText = `${ramVal}MB`;
        ramBar.style.width = `${(ramVal/256)*100}%`;
    }
}

// --- Terminal & Logs ---
function addLog(msg: string, prefix: string = 'SYS') {
    const terminal = document.getElementById('terminal');
    if (!terminal) return;

    const entry = document.createElement('div');
    entry.className = 'log-entry';
    entry.innerHTML = `<span class="log-prefix">[${prefix}]:</span> ${msg}`;
    terminal.appendChild(entry);
    terminal.scrollTop = terminal.scrollHeight;
}

// --- Animación de Neuronas ---
function simulateNeuralActivity() {
    const activeIndex = Math.floor(Math.random() * NEURONS.length);
    const neuronId = `neuron-${NEURONS[activeIndex].id}`;
    const node = document.getElementById(neuronId);
    
    if (node) {
        node.classList.add('active');
        node.style.borderColor = 'var(--accent-cyan)';
        
        setTimeout(() => {
            node.classList.remove('active');
            node.style.borderColor = 'var(--glass-border)';
        }, 1500);
    }
}

// --- Reloj del Sistema ---
function updateClock() {
    const clock = document.getElementById('clock');
    if (clock) {
        clock.innerText = new Date().toLocaleTimeString();
    }
}

// --- Vibe Dashboard ---
function updateVibe(data: any) {
    const emoji = document.getElementById('vibe-emoji');
    const label = document.getElementById('vibe-label');
    const score = document.getElementById('vibe-score');
    const success = document.getElementById('vibe-success');
    const latency = document.getElementById('vibe-latency');
    const card = document.getElementById('vibe-card');

    if (emoji) emoji.innerText = data.emoji || '🙂';
    if (label) label.innerText = data.vibe || 'ESTABLE';
    if (score) score.innerText = data.score?.toFixed(3) || '0.000';
    if (success) success.innerText = `${((data.tasa_exito || 0) * 100).toFixed(0)}%`;
    if (latency) latency.innerText = `${(data.latencia_media_ms || 0).toFixed(2)}ms`;
    if (card) card.setAttribute('data-vibe', data.vibe || 'ESTABLE');
}

// --- Brain Config ---
function initBrainConfig() {
    const toggle = document.getElementById('toggle-local-brain') as HTMLInputElement;
    const downloadBtn = document.getElementById('btn-download-model');
    const backendLabel = document.getElementById('brain-backend');
    const statusEl = document.getElementById('brain-status');

    if (!toggle) return;

    toggle.addEventListener('change', async () => {
        const useLocal = toggle.checked;
        if (downloadBtn) downloadBtn.style.display = useLocal ? 'block' : 'none';
        if (backendLabel) backendLabel.innerText = useLocal ? 'Ollama Local' : 'Gemini API';
        if (statusEl) statusEl.innerText = useLocal ? 'Activando cerebro local...' : 'API externa activa';
        addLog(useLocal ? 'Cerebro Local activado por el usuario' : 'Volviendo a API externa', 'BRAIN');

        try {
            await fetch(CONFIG_API, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ use_local: useLocal })
            });
            if (statusEl) statusEl.innerText = useLocal ? 'Cerebro local configurado ✅' : 'API activa ✅';
        } catch {
            if (statusEl) statusEl.innerText = 'Error conectando con gateway';
        }
    });

    if (downloadBtn) {
        downloadBtn.addEventListener('click', async () => {
            addLog('Descargando modelo local...', 'BRAIN');
            if (statusEl) statusEl.innerText = '📥 Descargando modelo... (puede tardar)';
            try {
                const res = await fetch(CONFIG_API, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ use_local: true, download: true })
                });
                const data = await res.json();
                if (statusEl) statusEl.innerText = `Modelo listo: ${data.config?.model_local || 'llama3.2:3b'}`;
                addLog('Modelo descargado correctamente ✅', 'BRAIN');
            } catch {
                if (statusEl) statusEl.innerText = 'Error descargando modelo';
                addLog('Error descargando modelo ❌', 'BRAIN');
            }
        });
    }

    // Cargar estado inicial
    fetch(CONFIG_API).then(r => r.json()).then(cfg => {
        if (cfg.use_local) {
            toggle.checked = true;
            if (downloadBtn) downloadBtn.style.display = 'block';
            if (backendLabel) backendLabel.innerText = 'Ollama Local';
        }
    }).catch(() => {});
}

// --- P2P Mesh Update ---
function updateP2P(data: any) {
    const id = document.getElementById('p2p-id');
    const peers = document.getElementById('p2p-peers');
    const alive = document.getElementById('p2p-alive');
    if (id) id.innerText = data.my_id || 'imac-primary';
    if (peers) peers.innerText = data.peers_total || '0';
    if (alive) alive.innerText = data.peers_alive || '0';
}

// --- Healer Update ---
function updateHealer(data: any) {
    const el = document.getElementById('healer-status');
    if (!el) return;
    if (data.reparaciones_totales > 0) {
        const last = data.ultimas?.[data.ultimas.length - 1];
        el.innerHTML = `⚠️ ${data.reparaciones_totales} reparaciones<br><small>${last?.diagnostico || ''}</small>`;
        el.style.borderLeftColor = 'var(--danger)';
    } else {
        el.innerText = 'Sin alertas activas ✅';
        el.style.borderLeftColor = 'var(--success)';
    }
}

// --- Hibernate Update ---
function updateHibernate(data: any) {
    const el = document.getElementById('hibernate-status');
    if (!el) return;
    if (data.tarea_activa && data.tarea_activa !== 'ninguna') {
        el.innerHTML = `🔄 Continuando: ${data.tarea_activa}<br><small>Progreso: ${data.progreso || 0}%</small>`;
    } else {
        el.innerText = 'Estado: Activo (sin tareas pendientes)';
    }
}

// --- Conexión WebSocket ---
function connectToGateway() {
    const ws = new WebSocket(GATEWAY_URL);

    ws.onopen = () => {
        addLog('Conexión con el Gateway establecida.', 'NETWORK');
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'welcome') {
            addLog(data.message, 'GATEWAY');
        } else if (data.type === 'vibe') {
            updateVibe(data.payload);
        } else if (data.type === 'p2p') {
            updateP2P(data.payload);
        } else if (data.type === 'healer') {
            updateHealer(data.payload);
        } else if (data.type === 'hibernate') {
            updateHibernate(data.payload);
        } else {
            if (data.autonomia) {
                const autVal = document.getElementById('autonomy-val');
                if (autVal) autVal.innerText = `${(data.autonomia * 100).toFixed(1)}%`;
            }
        }
    };

    ws.onerror = () => {
        addLog('Fallo de conexión con el Gateway local.', 'ERROR');
    };

    ws.onclose = () => {
        addLog('Conexión cerrada. Reintentando en 5s...', 'NETWORK');
        setTimeout(connectToGateway, 5000);
    };
}

// --- Kickoff ---
window.onload = () => {
    initNeuralGrid();
    initBrainConfig();
    setInterval(updateTelemetry, 3000);
    setInterval(simulateNeuralActivity, 2000);
    setInterval(updateClock, 1000);
    connectToGateway();
    
    addLog('Portal Soberano ClawCore V4.6 cargado.', 'CORE');
    addLog('Módulos: Vibe, P2P, Healer, Hibernación, Brain Config activos.', 'SYSTEM');
};
