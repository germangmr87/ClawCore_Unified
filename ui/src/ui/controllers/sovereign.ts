import type { ClawCoreApp } from "../app.ts";

export type SovereignStatus = {
  sovereign: {
    timestamp: string;
    sovereignty_score: number;
    vibe_global: string;
    vibe_emoji: string;
    nodos_conocimiento: number;
    sinapsis_totales: number;
    hardware: {
      cpu: number;
      ram: number;
      alerta: boolean;
    };
    estado_red: string;
  };
  decisiones_pendientes: Record<string, {
    neurona: string;
    accion: string;
    riesgo: string;
    alerta: string;
    requiere_humano: boolean;
    timestamp: string;
  }>;
  kernel_running: boolean;
};


export async function loadSovereign(app: ClawCoreApp) {
  try {
    // Apuntamos al puerto 8788 del Claw API Gateway
    const resp = await fetch(`https://${window.location.hostname}:8788/v1/sovereign/status`);
    if (!resp.ok) return;
    const data = await resp.json() as SovereignStatus;
    (app as any).sovereignStatus = data;
  } catch (e) {
    console.warn("Error loading sovereign status:", e);
  }
}

export async function triggerHardwareListen(app: ClawCoreApp) {
  try {
    await fetch(`https://${window.location.hostname}:8788/v1/sovereign/hardware/listen`, { method: "POST" });
  } catch (e) {
    console.error("Error triggering hardware listen:", e);
  }
}

export async function triggerHardwareSay(app: ClawCoreApp, text: string) {
  try {
    await fetch(`https://${window.location.hostname}:8788/v1/sovereign/hardware/say`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });
  } catch (e) {
    console.error("Error triggering hardware say:", e);
  }
}

export async function resolveSovereignDecision(app: ClawCoreApp, d_id: string, action: 'approve' | 'reject') {

  try {
    const resp = await fetch(`https://${window.location.hostname}:8788/v1/sovereign/decision/${d_id}/${action}`, {
      method: "POST"
    });
    if (resp.ok) {
      await loadSovereign(app);
    }
  } catch (e) {
    console.error("Error resolving sovereign decision:", e);
  }
}
