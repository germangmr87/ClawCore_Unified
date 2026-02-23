import { html } from "lit";
import { resolveSovereignDecision, triggerHardwareListen, triggerHardwareSay } from "../controllers/sovereign.ts";

export function renderSovereign(app: any) {

  const status = app.sovereignStatus || {
    sovereign: { 
      sovereignty_score: 0.5, 
      vibe_global: "INICIALIZANDO", 
      vibe_emoji: "⏳", 
      nodos_conocimiento: 0, 
      sinapsis_totales: 0,
      hardware: { cpu: 0, ram: 0, alerta: false },
      estado_red: "DESCONECTADO"
    },
    decisiones_pendientes: {},
    kernel_running: false
  };

  const sov = status.sovereign;
  const decisiones = Object.entries(status.decisiones_pendientes || {});
  
  return html`
    <style>
      .sovereign-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 20px;
        padding: 20px;
        animation: fadeIn var(--duration-normal) var(--ease-out);
      }

      .moderation-overlay {
        grid-column: 1 / -1;
        background: rgba(255, 62, 62, 0.05);
        border: 1px solid rgba(255, 62, 62, 0.3);
        border-radius: var(--radius-lg, 12px);
        padding: 20px;
        margin-bottom: 20px;
        display: ${decisiones.length > 0 ? 'block' : 'none'};
      }

      .decision-card {
        background: var(--bg-elevated);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 15px;
        margin-top: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
      }

      .decision-info h4 { margin: 0; color: #ff3e3e; }
      .decision-info p { margin: 5px 0 0; font-size: 0.9em; opacity: 0.8; }

      .decision-actions { display: flex; gap: 10px; }
      .btn-approve { background: var(--ok); color: black; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer; font-weight: bold; }
      .btn-reject { background: transparent; color: white; border: 1px solid var(--border); padding: 8px 15px; border-radius: 4px; cursor: pointer; }

      .sovereign-panel {
        border: 1px solid var(--border);
        border-radius: var(--radius-lg, 12px);
        background: var(--panel);
        overflow: hidden;
        transition: border-color var(--duration-normal) var(--ease-out), box-shadow var(--duration-normal) var(--ease-out);
        display: flex;
        flex-direction: column;
      }

      .sovereign-panel:hover {
        border-color: var(--accent);
        box-shadow: var(--shadow-md);
      }

      .sovereign-panel__header {
        padding: 12px 16px;
        background: rgba(255, 255, 255, 0.03);
        border-bottom: 1px solid var(--border);
        display: flex;
        justify-content: space-between;
        align-items: center;
      }

      .sovereign-panel__title {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        font-size: 0.9em;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        color: var(--text-strong);
      }

      .sovereign-panel__body {
        padding: 16px;
        flex: 1;
      }

      .sovereign-bar-container {
        margin-top: 8px;
      }

      .sovereign-bar-label {
        font-size: 0.75em;
        margin-bottom: 6px;
        opacity: 0.6;
        text-transform: uppercase;
      }

      .sovereign-bar {
        height: 6px;
        background: var(--input);
        border-radius: var(--radius-full);
      }

      .sovereign-bar__fill {
        height: 100%;
        background: var(--accent);
        border-radius: var(--radius-full);
        box-shadow: 0 0 8px var(--accent-alpha);
      }

      .sovereign-health-ok {
        color: var(--ok);
        font-size: 0.75em;
        font-weight: bold;
      }

      .sovereign-toggle {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
      }

      .sovereign-toggle__slider {
        width: 32px;
        height: 18px;
        background: var(--input);
        border-radius: var(--radius-full);
        position: relative;
        transition: background-color var(--duration-fast) var(--ease-out);
        border: 1px solid var(--border);
      }

      .sovereign-toggle__slider::after {
        content: '';
        position: absolute;
        top: 2px;
        left: 2px;
        width: 12px;
        height: 12px;
        background: white;
        border-radius: 50%;
        transition: transform var(--duration-fast) var(--ease-out);
      }

      .sovereign-toggle__slider--active {
        background: var(--accent);
      }

      .sovereign-toggle__slider--active::after {
        transform: translateX(14px);
      }

      .sovereign-stat {
        display: flex;
        justify-content: space-between;
        margin-bottom: 12px;
        font-size: 0.9em;
      }

      .sovereign-stat__label {
        color: var(--text);
        opacity: 0.8;
      }

      .sovereign-stat__value {
        color: var(--text-strong);
        font-weight: 500;
      }

      @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
      }
      .hardware-alerta { color: #ff3e3e; animation: pulse 2s infinite; }
      @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
    </style>

    <div class="sovereign-container">
      
      <!-- SECCIÓN DE MODERACIÓN PROACTIVA -->
      <div class="moderation-overlay">
        <h3 style="color: #ff3e3e; margin-top: 0;">🛡️ Moderación de Decisiones Críticas</h3>
        <p>Sovereign ha pausado las siguientes acciones por alto riesgo de bloqueo:</p>
        ${decisiones.map(([id, d]: [string, any]) => html`
          <div class="decision-card">
            <div class="decision-info">
              <h4>${d.neurona}: ${d.riesgo}</h4>
              <p><strong>Acción:</strong> ${d.accion}</p>
              <p><strong>Razón:</strong> ${d.alerta}</p>
            </div>
            <div class="decision-actions">
              <button class="btn-reject" @click=${() => resolveSovereignDecision(app, id, 'reject')}>Rechazar</button>
              <button class="btn-approve" @click=${() => resolveSovereignDecision(app, id, 'approve')}>Aprobar</button>
            </div>
          </div>
        `)}
      </div>

      <!-- PANEL PRINCIPAL DE SOBERANÍA -->
      <div class="sovereign-panel">
        <div class="sovereign-panel__header">
          <span class="sovereign-panel__title">Puntaje de Soberanía</span>
          <span class="sovereign-health-ok">RED: ${sov.estado_red} ${sov.vibe_emoji}</span>
        </div>
        <div class="sovereign-panel__body">
          <div style="font-size: 2.5em; font-weight: bold; margin-bottom: 10px; color: var(--accent);">
            ${(sov.sovereignty_score * 100).toFixed(1)}%
          </div>
          <div class="sovereign-bar-container">
            <div class="sovereign-bar-label">Índice de Autonomía Holística</div>
            <div class="sovereign-bar">
              <div class="sovereign-bar__fill" style="width: ${sov.sovereignty_score * 100}%"></div>
            </div>
          </div>
          <div style="margin-top: 15px; font-size: 0.85em; opacity: 0.7; display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
            <div>Conocimiento: ${sov.nodos_conocimiento} nodos</div>
            <div>Sinapsis: ${sov.sinapsis_totales}</div>
            <div class="${sov.hardware.alerta ? 'hardware-alerta' : ''}">CPU: ${sov.hardware.cpu}%</div>
            <div>RAM: ${sov.hardware.ram}%</div>
            <div>Kernel: ${status.kernel_running ? 'ACTIVO' : 'IDLE'}</div>
            <div>Vibe: ${sov.vibe_global}</div>
          </div>
        </div>
      </div>


      <!-- Physical Presence (iMac Hardware) -->
      <div class="sovereign-panel">
        <div class="sovereign-panel__header">
          <span class="sovereign-panel__title">Presencia Física (iMac)</span>
          <span style="color: var(--accent);">ALTAVOZ DISPONIBLE</span>
        </div>
        <div class="sovereign-panel__body">
          <div class="sovereign-toggle">
            <span>Escucha Ambiental (Ambient Mic)</span>
            <div class="sovereign-toggle__slider" @click=${() => triggerHardwareListen(app)}></div>
          </div>
          <button class="btn-approve" style="width: 100%; margin-top: 10px;" @click=${() => triggerHardwareSay(app, "Iniciando llamada de voz con el host.")}>
            📞 LLAMADA DIRECTA (iMac)
          </button>
        </div>
      </div>


      <!-- WebRTC Voice (Browser) -->
      <div class="sovereign-panel">
        <div class="sovereign-panel__header">
          <span class="sovereign-panel__title">Voz del Navegador (WebRTC)</span>
        </div>
        <div class="sovereign-panel__body">
          <div style="text-align: center; padding: 10px;">
            <div style="font-size: 3em; margin-bottom: 10px;">🎙️</div>
            <button class="btn-approve" 
              @mousedown=${() => console.log('Recording...')}
              @mouseup=${() => console.log('Processing...')}
              style="border-radius: 50px; padding: 15px 30px;">
              MANTENER PARA HABLAR
            </button>
          </div>
        </div>
      </div>

      <!-- Brain Config -->

      <div class="sovereign-panel">
        <div class="sovereign-panel__header">
          <span class="sovereign-panel__title">Cerebro Profundo</span>
          <span style="color: var(--accent);">V4.6</span>
        </div>
        <div class="sovereign-panel__body">
          <div class="sovereign-toggle">
            <span>Inferencia Local (Ollama)</span>
            <div class="sovereign-toggle__slider sovereign-toggle__slider--active"></div>
          </div>
          <div class="sovereign-toggle">
            <span>Auto-Gen Unit Tests</span>
            <div class="sovereign-toggle__slider sovereign-toggle__slider--active"></div>
          </div>
          <div class="sovereign-bar-container" style="margin-top: 15px;">
            <div class="sovereign-bar-label">Compresión de Tokens (Ratio)</div>
            <div class="sovereign-bar">
              <div class="sovereign-bar__fill" style="width: 82%"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- P2P Mesh -->
      <div class="sovereign-panel">
        <div class="sovereign-panel__header">
          <span class="sovereign-panel__title">Malla P2P</span>
          <span style="color: var(--ok);">3 Nodos</span>
        </div>
        <div class="sovereign-panel__body">
          <div class="sovereign-stat">
            <span class="sovereign-stat__label">Estado de Red</span>
            <span class="sovereign-stat__value">Sincronizado</span>
          </div>
          <div class="sovereign-stat">
            <span class="sovereign-stat__label">Latencia de Red</span>
            <span class="sovereign-stat__value">42ms</span>
          </div>
        </div>
      </div>

      <!-- Healer V2 -->
      <div class="sovereign-panel">
        <div class="sovereign-panel__header">
          <span class="sovereign-panel__title">Healer V2</span>
          <span class="sovereign-health-ok">Salud 100%</span>
        </div>
        <div class="sovereign-panel__body">
          <div class="sovereign-stat">
            <span class="sovereign-stat__label">Auto-Parches Aplicados</span>
            <span class="sovereign-stat__value">14</span>
          </div>
          <div class="sovereign-bar-container">
            <div class="sovereign-bar-label">Efectividad de Diagnóstico</div>
            <div class="sovereign-bar">
              <div class="sovereign-bar__fill" style="width: 95%"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Integrity -->
      <div class="sovereign-panel">
        <div class="sovereign-panel__header">
          <span class="sovereign-panel__title">Monitoreo de Integridad</span>
          <span class="sovereign-health-ok">Sin Drift</span>
        </div>
        <div class="sovereign-panel__body">
          <div class="sovereign-toggle">
            <span>Anti-Hacking (Inmutable)</span>
            <div class="sovereign-toggle__slider sovereign-toggle__slider--active"></div>
          </div>
          <div style="font-size: 0.8em; opacity: 0.6; margin-top: 10px;">
            Auditando 30 archivos core vía SHA-256.
          </div>
        </div>
      </div>

    </div>
  `;
}
