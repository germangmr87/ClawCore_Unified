#!/home/ubuntu/.clawcore/venv-telegram/bin/python3
"""
API Gateway SOBERANO V5.4 — Edición Misión Control
Unificado con el Portal Visual de ClawCore.
"""
import asyncio
import os
import json
import logging
import time
import uuid
import sys
from typing import Dict, List
from pathlib import Path

import aiohttp
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

# Cargar variables de entorno (.env) con ruta absoluta
ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Configurar Logger INMEDIATAMENTE
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GatewaySoberano")

# Inyectar rutas
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))

import aiohttp
from starlette.websockets import WebSocketState

# --- SOVEREIGN FALLBACK (macOS TCC Fix) ---
if not os.getenv("TELEGRAM_BOT_TOKEN"):
    os.environ["TELEGRAM_BOT_TOKEN"] = "8236923260:AAF0y9N6Jy8hJuy-RKSZfpmE9puBDwguzDk"
    logger.warning("🛡️ GATEWAY: Usando TELEGRAM_BOT_TOKEN de Respaldo Soberano.")
if not os.getenv("GEMINI_API_KEY"):
    os.environ["GEMINI_API_KEY"] = "AIzaSyBC22up54NB1cGsumk5QiTcsG2RciW6aSw"
    logger.warning("🛡️ GATEWAY: Usando GEMINI_API_KEY de Respaldo Soberano.")

try:
    from src.clawcore_system.neuronas.vibe_dashboard import vibe
    from src.clawcore_system.neuronas.simulador_decisiones import simulador
    from src.clawcore_system.neuronas.kernel_soberano import kernel
    from src.clawcore_system.neuronas.sovereign_telemetry import telemetry
    from src.clawcore_system.neuronas.audio_local import audio_hardware
    from src.clawcore_system.neuronas.seguridad_soberana import seguridad
    from src.clawcore_system.neuronas.interface_telegram import run_bot_task
except ImportError as e:
    # Si falla el logger, usamos print como fallback extremo
    msg = f"⚠️ Error crítico importando neuronas: {e}"
    try: logger.error(msg)
    except: print(msg)

# --- PERSISTENCIA DE MEMORIA ---
HISTORY_FILE = os.path.expanduser("~/.clawcore/sofia_history_v5.json")

def save_history():
    """Guarda el historial de Sofia del portal UI."""
    try:
        data = kernel.histories.get('gateway', [])
        with open(HISTORY_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        pass

def load_history():
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
    except: pass
    return []

# Inicializar Kernel con historia persistente
if 'gateway' not in kernel.histories:
    kernel.histories['gateway'] = load_history()
start_time_global = time.time()

# ─── REGISTRO DE MODELOS DISPONIBLES ─────────────────────────────────────────
LLM_APIS = [
    {
        "name": "VPS-229-Ollama",
        "base_url": os.getenv("OLLAMA_REMOTE_URL", "http://15.204.231.229:11434"),
        "api_key": "ollama",
        "model": "llama3.1:8b",
        "provider": "ollama",
        "cost_per_1k": 0.0,
        "priority": 1,
        "enabled": True,
    },
    {
        "name": "Ollama-Local",
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
        "model": "llama3.1:8b",
        "provider": "ollama",
        "cost_per_1k": 0.0,
        "priority": 2,
        "enabled": True,
    },
    {
        "name": "Gemini-Directo",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "api_key": os.getenv("GEMINI_API_KEY"),
        "model": "gemini-1.5-flash",
        "provider": "google",
        "cost_per_1k": 0.00010,
        "priority": 3,
        "enabled": bool(os.getenv("GEMINI_API_KEY")),
    },
    {
        "name": "DeepSeek-Chat",
        "base_url": "https://api.deepseek.com",
        "api_key": os.getenv("DEEPSEEK_API_KEY"),
        "model": "deepseek-chat",
        "provider": "deepseek",
        "cost_per_1k": 0.00014,
        "priority": 4,
        "enabled": bool(os.getenv("DEEPSEEK_API_KEY")),
    },
]

# Modelo activo actual (índice en LLM_APIS o "kernel" para usar el Kernel Soberano)
active_model_name: str = "kernel"  # Por defecto: usar el Kernel Sofia

stats = {"total_requests": 0, "successful": 0, "failed": 0}

app = FastAPI(title="Claw API Gateway", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class ConnectionManager:
    def __init__(self): 
        self.active_connections = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active_connections.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active_connections:
            self.active_connections.remove(ws)

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    """Inicia el kernel y el bot unificado cuando arranca el gateway."""
    kernel.iniciar()
    logger.info("🧠 Kernel Sofia iniciado exitosamente desde el Gateway.")
    asyncio.create_task(run_bot_task())
    logger.info("📱 Interfaz Telegram sincronizada con el núcleo principal.")

async def get_llm_response(messages: List[Dict]) -> str:
    """Usa el modelo activo o el Kernel Soberano si está en modo 'kernel'."""
    global active_model_name
    stats["total_requests"] += 1

    # Modo Kernel (Sofia nativa — incluye memoria y sistema de personalidad)
    if active_model_name == "kernel":
        try:
                response = await kernel.pensar(messages[-1].get("content", ""), context_id="gateway")
                if response:
                    stats["successful"] += 1
                    save_history()
                    return response
        except Exception as e:
            logger.warning(f"Kernel falló, intentando fallback: {e}")

    # Modo LLM externo
    api_cfg = next((a for a in LLM_APIS if a["name"] == active_model_name and a.get("enabled")), None)
    if api_cfg:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{api_cfg['base_url']}/chat/completions",
                    json={"model": api_cfg["model"], "messages": messages, "max_tokens": 1000},
                    headers={"Authorization": f"Bearer {api_cfg['api_key']}", "Content-Type": "application/json"},
                    timeout=30
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        ans = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                        if ans:
                            stats["successful"] += 1
                            if 'gateway' not in kernel.histories: kernel.histories['gateway'] = []
                            history = kernel.histories['gateway']
                            history.append({"role": "assistant", "content": ans})
                            if len(history) > 30: kernel.histories['gateway'] = history[-30:]
                            save_history()
                        return ans
        except Exception as e:
            logger.error(f"Error llamando a {active_model_name}: {e}")

    stats["failed"] += 1
    return "Sofia está procesando tu solicitud (sin conexión con el modelo activo)."

@app.websocket("/")
async def websocket_unificador(websocket: WebSocket):
    """WebSocket Inteligente: Decide si responde Sofia o el Sistema (Node)."""
    ws_id = str(uuid.uuid4())
    await manager.connect(websocket)
    
    # Abrir conexión espejo con Node (Esclavo)
    async with aiohttp.ClientSession() as session:
        try:
            async with session.ws_connect("ws://localhost:18790/") as node_ws:
                # Tarea para escuchar a Node y retransmitir al Cliente
                async def node_listener():
                    try:
                        async for msg in node_ws:
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                if websocket.client_state == WebSocketState.CONNECTED:
                                    await websocket.send_text(msg.data)
                            elif msg.type == aiohttp.WSMsgType.BINARY:
                                if websocket.client_state == WebSocketState.CONNECTED:
                                    await websocket.send_bytes(msg.data)
                    except Exception as e:
                        logger.debug(f"Node WS client loop closed: {e}")

                listener_task = asyncio.create_task(node_listener())

                # Loop Principal: Escuchar al Cliente
                while True:
                    data = await websocket.receive_text()
                    msg = json.loads(data)
                    
                    if msg.get("type") == "req":
                        m_id = msg.get("id")
                        method = msg.get("method", "")
                        params = msg.get("params", {})
                        
                        # 1. ¿Es para Sofia? (Cerebro)
                        if method in ["chat", "turn"]:
                            messages = params.get("messages", []) or [{"role": "user", "content": params.get("message", "")}]
                            resp = await get_llm_response(messages)
                            await websocket.send_json({
                                "type": "res", "id": m_id, "ok": True, 
                                "payload": {"response": resp}
                            })
                        
                        # 2. ¿Es para el Sistema? (Node)
                        else:
                            await node_ws.send_str(data)
                    
                    else:
                        # Eventos o respuestas a desafíos del cliente, reenviar a Node
                        await node_ws.send_str(data)

        except Exception as e:
            logger.error(f"⚠️ Puente Unificador WS error: {e}")
        finally:
            manager.disconnect(websocket)
            if 'listener_task' in locals():
                listener_task.cancel()

@app.get("/health")
async def health(): return {"status": "healthy", "stats": stats, "active_model": active_model_name}

# ─── GESTIÓN DE MODELOS ────────────────────────────────────────────────────────

@app.get("/v1/models")
async def list_models():
    """Lista todos los modelos disponibles y cuál está activo."""
    return {
        "active": active_model_name,
        "models": [
            {
                "name": "kernel",
                "display": "Sofia Ω (Kernel Soberano)",
                "provider": "local",
                "model": "sovereign",
                "enabled": True,
                "cost_per_1k": 0.0,
                "is_active": active_model_name == "kernel",
            }
        ] + [
            {
                "name": a["name"],
                "display": a["name"],
                "provider": a.get("provider", "api"),
                "model": a["model"],
                "enabled": a.get("enabled", bool(a.get("api_key"))),
                "cost_per_1k": a.get("cost_per_1k", 0),
                "is_active": active_model_name == a["name"],
            }
            for a in LLM_APIS
        ]
    }

@app.post("/v1/models/active")
async def set_active_model(request: Request):
    """Cambia el modelo activo de Sofia."""
    global active_model_name
    body = await request.json()
    name = body.get("name", "").strip()
    valid_names = ["kernel"] + [a["name"] for a in LLM_APIS]
    if name not in valid_names:
        return {"ok": False, "error": f"Modelo '{name}' no encontrado. Opciones: {valid_names}"}
    active_model_name = name
    logger.info(f"🔄 Modelo activo cambiado a: {name}")
    return {"ok": True, "active": active_model_name}

@app.post("/v1/models/test")
async def test_model(request: Request):
    """Prueba un modelo específico con un mensaje de validación."""
    body = await request.json()
    model_name = body.get("name", active_model_name)
    test_prompt = body.get("prompt", "Responde con una sola frase: ¿cuál es tu nombre y cuál es tu modelo?")
    
    start = time.time()
    try:
        if model_name == "kernel":
            response = await kernel.pensar(test_prompt)
            elapsed = time.time() - start
            return {
                "ok": True, "model": model_name, "provider": "local",
                "response": response, "latency_ms": int(elapsed * 1000),
                "test_passed": bool(response and len(response) > 0)
            }
        
        api_cfg = next((a for a in LLM_APIS if a["name"] == model_name), None)
        if not api_cfg:
            return {"ok": False, "error": f"Modelo '{model_name}' no configurado."}
        if not api_cfg.get("api_key"):
            return {"ok": False, "error": f"Sin API key para '{model_name}'. Configura la variable de entorno."}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{api_cfg['base_url']}/chat/completions",
                json={
                    "model": api_cfg["model"],
                    "messages": [{"role": "user", "content": test_prompt}],
                    "max_tokens": 200
                },
                headers={"Authorization": f"Bearer {api_cfg['api_key']}", "Content-Type": "application/json"},
                timeout=15
            ) as resp:
                elapsed = time.time() - start
                if resp.status == 200:
                    data = await resp.json()
                    answer = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    return {
                        "ok": True, "model": model_name, "provider": api_cfg.get("provider"),
                        "response": answer, "latency_ms": int(elapsed * 1000),
                        "test_passed": bool(answer and len(answer) > 5)
                    }
                else:
                    err_text = await resp.text()
                    return {
                        "ok": False, "model": model_name,
                        "error": f"HTTP {resp.status}: {err_text[:200]}",
                        "latency_ms": int(elapsed * 1000)
                    }
    except Exception as e:
        elapsed = time.time() - start
        return {"ok": False, "model": model_name, "error": str(e), "latency_ms": int(elapsed * 1000)}

@app.get("/v1/sovereign/status")
async def get_sovereign_status():
    state = telemetry.obtener_estado_holistico()
    state["hardware"]["listening"] = getattr(audio_hardware, "listening", False)
    return {"sovereign": state, "decisiones_pendientes": simulador.decisiones_pendientes, "kernel_running": True}

@app.post("/v1/sovereign/decision/{d_id}/{action}")
async def resolve_decision(d_id: str, action: str):
    res = simulador.resolver_decision(d_id, action == "approve")
    return {"ok": res}

@app.post("/v1/sovereign/hardware/listen")
async def hardware_listen():
    active = audio_hardware.toggle_centinela()
    return {"status": "active" if active else "inactive"}

@app.post("/v1/sovereign/hardware/say")
async def hardware_say(request: Request):
    body = await request.json()
    text = body.get("text", "")
    await audio_hardware.hablar_fisicamente(text)
    return {"ok": True}

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    resp = await get_llm_response(body.get("messages", []))
    return {"choices": [{"message": {"role": "assistant", "content": resp}}]}

UI_DIST_PATH = "/Users/german/Documents/GitHub/ClawCore_Unified/dist/control-ui"

# --- ENDPOINTS REQUERIDOS POR EL CONTROL UI ---
@app.get("/__clawcore/control-ui-config.json")
async def control_ui_config():
    """Config que el Control UI busca al iniciar."""
    return {
        "basePath": "",
        "assistantName": "Sofia",
        "assistantAvatar": "⚡",
        "assistantAgentId": "sofia"
    }

@app.get("/avatar/{agent_id}")
@app.get("/avatar/{agent_id}/")
async def agent_avatar(agent_id: str, meta: str = None):
    if meta:
        return {"id": agent_id, "name": "Sofia", "avatar": "⚡"}
    # Devolver favicon como avatar por defecto
    favicon = os.path.join(UI_DIST_PATH, "favicon.svg")
    if os.path.exists(favicon): return FileResponse(favicon)
    return HTMLResponse("⚡", media_type="image/svg+xml")

# --- UNIFICACIÓN UI: RUTAS PRINCIPALES ---
UI_DIST_PATH = os.path.expanduser("~/.clawcore/dist/control-ui")

@app.get("/sofia")
@app.get("/sofia/")
async def sofia_portal():
    index = os.path.join(UI_DIST_PATH, "index.html")
    if os.path.exists(index): return FileResponse(index)
    return HTMLResponse("<h1>UI no encontrada en dist/control-ui</h1>")

# PROXY HTTP: Lo que no maneja Sofia, va a Node
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_node_http(request: Request, path: str):
    # Si el cliente pide un asset o API que no definimos arriba, puenteamos a Node
    async with aiohttp.ClientSession() as session:
        url = f"http://localhost:18790/{path}"
        try:
            # Enviar mismo método, body y headers (filtrados)
            headers = {k: v for k, v in request.headers.items() if k.lower() not in ["host", "content-length", "connection", "upgrade"]}
            body = await request.body()
            
            async with session.request(request.method, url, headers=headers, data=body) as resp:
                content = await resp.read()
                # Excluir headers de transferencia que aiohttp maneja solo
                resp_headers = {k: v for k, v in resp.headers.items() if k.lower() not in ["content-encoding", "transfer-encoding", "content-length"]}
                return StreamingResponse(
                    content=iter([content]),
                    status_code=resp.status,
                    headers=resp_headers
                )
        except Exception as e:
            # Si Node no responde, devolver 404 para assets o error para APIs
            if "." in path: return HTMLResponse("Asset not found", status_code=404)
            return HTMLResponse(f"Sistema no disponible (Esclavo @ 18790): {e}", status_code=502)

if os.path.exists(UI_DIST_PATH):
    app.mount("/", StaticFiles(directory=UI_DIST_PATH, html=True), name="ui")


if __name__ == "__main__":
    port = int(os.getenv("SOFIA_GATEWAY_PORT", "18791"))
    logger.info(f"🧠 Sofia AI Gateway (Modo Misión Control) en puerto {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info", workers=1)
