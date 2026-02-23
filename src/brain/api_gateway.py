#!/home/ubuntu/.clawcore/venv-telegram/bin/python3
"""
API GATEWAY propio - Reemplaza ClawCore buggy
WebSocket + SSE para múltiples mensajes concurrentes
"""

import asyncio
import json
import logging
import time
from typing import Dict, List
import aiohttp
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
import uvicorn
from pathlib import Path
import sys

# Inyectar rutas para neuronas soberanas
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from src.clawcore_system.neuronas.vibe_dashboard import vibe
    from src.clawcore_system.neuronas.simulador_decisiones import simulador
    from src.clawcore_system.neuronas.kernel_soberano import kernel
    from src.clawcore_system.neuronas.sovereign_telemetry import telemetry
    from src.clawcore_system.neuronas.escucha_soberana import escucha
    from src.clawcore_system.neuronas.voz_edge import motor_voz
    from src.clawcore_system.neuronas.audio_local import audio_hardware
    from src.clawcore_system.neuronas.seguridad_soberana import seguridad
except ImportError as e:
    logger.error(f"Error importando neuronas soberanas: {e}")

# Garantizar certificados para HTTPS/WSS
seguridad.garantizar_cifrado_local()




logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Claw API Gateway", version="1.0")

# Configuración APIs disponibles
LLM_APIS = [
    {
        "name": "DeepSeek",
        "base_url": "https://api.deepseek.com",
        "api_key": None,  # Gratuita
        "model": "deepseek-chat",
        "cost_per_1k": 0.00014,
        "priority": 1
    },
    {
        "name": "LLMAPI",
        "base_url": "https://internal.llmapi.ai/v1",
        "api_key": "llmgtwy_jxlfeRWOWxTIKq8incbH7MKelBUxNhJtotLLFLBt",
        "model": "gpt-4o-mini",
        "cost_per_1k": 0.00015,
        "priority": 2
    },
    {
        "name": "Perplexity",
        "base_url": "https://api.perplexity.ai",
        "api_key": "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",
        "model": "llama-3.1-sonar-small-128k-online",
        "cost_per_1k": 0.00050,
        "priority": 3
    }
]

# Estadísticas
stats = {
    "total_requests": 0,
    "successful": 0,
    "failed": 0,
    "active_connections": 0,
    "avg_response_time": 0
}

# Conexiones WebSocket activas
active_connections: List[WebSocket] = []

class ConnectionManager:
    """Gestiona conexiones WebSocket"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        stats["active_connections"] = len(self.active_connections)
        logger.info(f"WebSocket conectado. Total: {stats['active_connections']}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        stats["active_connections"] = len(self.active_connections)
        logger.info(f"WebSocket desconectado. Total: {stats['active_connections']}")
    
    async def broadcast(self, message: str):
        """Envía mensaje a todas las conexiones"""
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                self.disconnect(connection)

manager = ConnectionManager()

async def call_llm_api(api_config: Dict, messages: List[Dict]) -> str:
    """Llama a una API LLM (async)"""
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_config['api_key']}" if api_config['api_key'] else ""
        }
        
        payload = {
            "model": api_config["model"],
            "messages": messages,
            "max_tokens": 1000,
            "stream": False
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{api_config['base_url']}/chat/completions",
                json=payload,
                headers=headers,
                timeout=30
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    return data.get("choices", [{}])[0].get("message", {}).get("content", "")
                else:
                    logger.error(f"API {api_config['name']} error: {response.status}")
                    return None
                    
    except Exception as e:
        logger.error(f"API {api_config['name']} exception: {e}")
        return None

async def get_llm_response(messages: List[Dict]) -> str:
    """Obtiene respuesta de la mejor API disponible"""
    stats["total_requests"] += 1
    start_time = time.time()
    
    # Ordenar APIs por prioridad (más barata primero)
    apis_sorted = sorted(LLM_APIS, key=lambda x: x["priority"])
    
    for api in apis_sorted:
        logger.info(f"Intentando API: {api['name']}")
        response = await call_llm_api(api, messages)
        
        if response:
            elapsed = time.time() - start_time
            stats["successful"] += 1
            stats["avg_response_time"] = (
                (stats["avg_response_time"] * (stats["successful"] - 1) + elapsed) 
                / stats["successful"]
            )
            logger.info(f"✅ {api['name']} respondió en {elapsed:.1f}s")
            return response
    
    # Si todas fallan, fallback a ClawCore CLI
    stats["failed"] += 1
    logger.warning("Todas las APIs fallaron, usando fallback CLI")
    return await fallback_cli(messages)

async def fallback_cli(messages: List[Dict]) -> str:
    """Fallback a ClawCore CLI (último recurso)"""
    try:
        last_message = messages[-1]["content"]
        
        cmd = [
            "/home/ubuntu/.nvm/versions/node/v22.22.0/bin/clawcore",
            "agent", "turn",
            "--agent", "main",
            "--message", last_message,
            "--model", "deepseek/deepseek-chat",
            "--json"
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd="/home/ubuntu/.clawcore"
        )
        
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=25)
        
        if process.returncode == 0:
            data = json.loads(stdout.decode())
            return data.get("choices", [{}])[0].get("message", {}).get("content", "")
        else:
            return f"❌ Fallback CLI error: {stderr.decode()[:100]}"
            
    except asyncio.TimeoutError:
        return "⏳ Timeout fallback CLI"
    except Exception as e:
        return f"❌ Fallback error: {str(e)}"

@app.get("/")
async def root():
    return {
        "service": "Claw API Gateway",
        "version": "1.0",
        "status": "operational",
        "apis_configured": len(LLM_APIS),
        "stats": stats
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/stats")
async def get_stats():
    return stats

@app.get("/v1/sovereign/status")
async def get_sovereign_status():
    """Estado de telemetría vibe y decisiones pendientes."""
    return {
        "sovereign": telemetry.obtener_estado_holistico(),
        "decisiones_pendientes": simulador.decisiones_pendientes,
        "kernel_running": getattr(kernel, "running", False)
    }


@app.post("/v1/sovereign/hardware/listen")
async def hardware_listen():
    """Activa el micrófono del iMac localmente."""
    asyncio.create_task(audio_hardware.escuchar_ambiente(duracion=5))
    return {"status": "listening", "hardware": "iMac Mic"}

@app.post("/v1/sovereign/hardware/say")
async def hardware_say(request: dict):
    """Hace que el iMac hable por sus altavoces."""
    texto = request.get("text", "Sistemas activos.")
    audio_hardware.hablar_fisicamente(texto)
    return {"status": "speaking", "text": texto}

@app.post("/v1/chat/completions")

async def chat_completions(request: dict):
    """Endpoint compatible OpenAI API"""
    messages = request.get("messages", [])
    model = request.get("model", "deepseek-chat")
    
    logger.info(f"Chat completions request: {len(messages)} messages")
    
    # Obtener respuesta
    response_content = await get_llm_response(messages)
    
    return {
        "choices": [{
            "message": {
                "role": "assistant",
                "content": response_content
            }
        }]
    }

@app.websocket("/v1/sovereign/voice")
async def sovereign_voice_endpoint(websocket: WebSocket):
    """WebSocket para streaming de voz bidireccional"""
    await websocket.accept()
    temp_audio = f"/tmp/web_voice_{time.time()}.webm"
    
    try:
        while True:
            data = await websocket.receive_bytes()
            # Guardamos los bytes recibidos (en un sistema real usaríamos un buffer)
            with open(temp_audio, "ab") as f:
                f.write(data)
                
            # Si recibimos un mensaje de texto "FIN", procesamos
            # (El frontend enviará esto al soltar el botón de hablar)
    except WebSocketDisconnect:
        # Procesar al desconectar
        if Path(temp_audio).exists():
            texto = await escucha.transcribir(temp_audio)
            if texto:
                respuesta = await kernel.pensar(f"[WEB-VOZ] {texto}")
                audio_path = await motor_voz.sintetizar(respuesta.replace("[DEEPSEEK]", "").replace("[LOCAL]", "").strip())
                # Como no podemos enviar a un WS cerrado, el frontend deberá 
                # pedir el audio resultante o usaremos un canal de broadcast
                logger.info(f"Voz procesada: {texto} -> {respuesta}")
            os.remove(temp_audio)

# Servir archivos de audio para la UI
from fastapi.staticfiles import StaticFiles
audio_dir = Path.home() / ".clawcore/audio_out"
audio_dir.mkdir(exist_ok=True, parents=True)
app.mount("/audio", StaticFiles(directory=str(audio_dir)), name="audio")

@app.websocket("/ws")

async def websocket_endpoint(websocket: WebSocket):
    """WebSocket para mensajes en tiempo real"""
    await manager.connect(websocket)
    
    try:
        while True:
            # Recibir mensaje del cliente
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Procesar
            messages = message_data.get("messages", [])
            response = await get_llm_response(messages)
            
            # Enviar respuesta
            await websocket.send_json({
                "response": response,
                "timestamp": time.time()
            })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@app.get("/stream")
async def stream_response(prompt: str):
    """Server-Sent Events (SSE) para streaming"""
    async def event_stream():
        # Simular streaming
        messages = [{"role": "user", "content": prompt}]
        response = await get_llm_response(messages)
        
        # Enviar en chunks (simulado)
        chunks = [response[i:i+100] for i in range(0, len(response), 100)]
        
        for chunk in chunks:
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            await asyncio.sleep(0.1)
        
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")

if __name__ == "__main__":
    logger.info("🚀 Iniciando Claw API Gateway...")
    logger.info(f"📡 APIs configuradas: {len(LLM_APIS)}")
    logger.info("🌐 Endpoints:")
    logger.info("  • GET  /          - Status")
    logger.info("  • GET  /health    - Health check")
    logger.info("  • GET  /stats     - Estadísticas")
    logger.info("  • POST /v1/chat/completions - OpenAI-compatible")
    logger.info("  • WS   /ws        - WebSocket real-time")
    logger.info("  • GET  /stream    - SSE streaming")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8788,
        ssl_keyfile=str(seguridad.key_path),
        ssl_certfile=str(seguridad.cert_path),
        log_level="info"
    )
