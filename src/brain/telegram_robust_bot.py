#!/home/ubuntu/.clawcore/venv-telegram/bin/python3
"""
Bot ROBUSTO - Conexión WebSocket persistente a ClawCore
"""

import os
import logging
import asyncio
import aiohttp
import json
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = "8501816149:AAEUSjYI0WbtMWnVdP58LnkM8R9dgHXc2yI"
CLAWCORE_WS_URL = "ws://localhost:18789/ws"  # WebSocket ClawCore
CLAWCORE_API_URL = "http://localhost:18789/v1/chat/completions"  # REST fallback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClawCoreConnection:
    """Conexión robusta a ClawCore (WebSocket + REST fallback)"""
    
    def __init__(self):
        self.ws = None
        self.session = None
        self.connected = False
        self.last_ping = time.time()
        self.reconnect_attempts = 0
        self.max_reconnect = 5
    
    async def connect_websocket(self):
        """Conecta WebSocket a ClawCore"""
        try:
            logger.info("Conectando WebSocket a ClawCore...")
            self.session = aiohttp.ClientSession()
            self.ws = await self.session.ws_connect(
                CLAWCORE_WS_URL,
                heartbeat=30,
                timeout=10
            )
            self.connected = True
            self.reconnect_attempts = 0
            logger.info("✅ WebSocket conectado")
            return True
        except Exception as e:
            logger.error(f"❌ WebSocket error: {e}")
            self.connected = False
            return False
    
    async def ensure_connection(self):
        """Asegura conexión activa"""
        if not self.connected or self.ws.closed:
            if self.reconnect_attempts < self.max_reconnect:
                self.reconnect_attempts += 1
                logger.info(f"Reconectando... intento {self.reconnect_attempts}")
                return await self.connect_websocket()
            else:
                logger.error("Máximo de reconexiones alcanzado")
                return False
        return True
    
    async def send_via_websocket(self, message):
        """Envía mensaje via WebSocket"""
        try:
            if not await self.ensure_connection():
                return None
            
            # Enviar mensaje
            payload = {
                "type": "agent_turn",
                "agent": "main",
                "messages": [{"role": "user", "content": message}],
                "model": "deepseek/deepseek-chat"
            }
            
            await self.ws.send_str(json.dumps(payload))
            
            # Recibir respuesta (timeout 20s)
            async with asyncio.timeout(20):
                response = await self.ws.receive()
                
                if response.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(response.data)
                    return data.get("content", "No response")
                elif response.type == aiohttp.WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {response}")
                    self.connected = False
                    return None
                else:
                    logger.warning(f"WebSocket message type: {response.type}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.error("WebSocket timeout")
            return None
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            self.connected = False
            return None
    
    async def send_via_rest(self, message):
        """Envía mensaje via REST (fallback)"""
        try:
            payload = {
                "model": "deepseek/deepseek-chat",
                "messages": [{"role": "user", "content": message}],
                "max_tokens": 500
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    CLAWCORE_API_URL,
                    json=payload,
                    timeout=15
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    else:
                        logger.error(f"REST error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"REST error: {e}")
            return None
    
    async def get_response(self, message):
        """Obtiene respuesta usando mejor método disponible"""
        # Primero intentar WebSocket
        response = await self.send_via_websocket(message)
        
        # Si WebSocket falla, usar REST
        if response is None:
            logger.info("Fallando a REST...")
            response = await self.send_via_rest(message)
        
        # Si REST falla, usar CLI como último recurso
        if response is None:
            logger.info("Fallando a CLI...")
            response = await self.send_via_cli(message)
        
        return response or "❌ No se pudo conectar a ClawCore"
    
    async def send_via_cli(self, message):
        """Último recurso: CLI"""
        import subprocess
        try:
            cmd = [
                "/home/ubuntu/.nvm/versions/node/v22.22.0/bin/clawcore",
                "agent", "turn",
                "--agent", "main",
                "--message", message,
                "--model", "deepseek/deepseek-chat",
                "--json"
            ]
            
            result = await asyncio.wait_for(
                asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd="/home/ubuntu/.clawcore"
                ),
                timeout=20
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                data = json.loads(stdout.decode())
                return data.get("choices", [{}])[0].get("message", {}).get("content", "")
            else:
                logger.error(f"CLI error: {stderr.decode()[:100]}")
                return None
                
        except asyncio.TimeoutError:
            logger.error("CLI timeout")
            return None
        except Exception as e:
            logger.error(f"CLI error: {e}")
            return None
    
    async def close(self):
        """Cierra conexiones"""
        if self.ws and not self.ws.closed:
            await self.ws.close()
        if self.session and not self.session.closed:
            await self.session.close()
        self.connected = False

# Conexión global
clawcore_conn = ClawCoreConnection()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja mensajes con conexión robusta"""
    user_message = update.message.text
    user_id = update.effective_user.id
    
    logger.info(f"Mensaje ROBUST de {user_id}: {user_message[:50]}...")
    
    # Enviar typing indicator
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, 
        action="typing"
    )
    
    # Obtener respuesta con conexión robusta
    start_time = time.time()
    response = await clawcore_conn.get_response(user_message)
    elapsed = time.time() - start_time
    
    # Agregar métricas
    robust_response = (
        f"{response}\n\n"
        f"---\n"
        f"⏱ {elapsed:.1f}s | 🔗 Conexión robusta"
    )
    
    # Enviar respuesta
    if len(robust_response) > 4000:
        for i in range(0, len(robust_response), 4000):
            await update.message.reply_text(robust_response[i:i+4000])
    else:
        await update.message.reply_text(robust_response)
    
    logger.info(f"Respuesta ROBUST enviada en {elapsed:.1f}s")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot ROBUSTO iniciado\n"
        "Conexión WebSocket persistente a ClawCore.\n"
        "Fallback automático: WebSocket → REST → CLI\n"
        "Máxima confiabilidad."
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_text = (
        "📊 Estado conexión ROBUSTA:\n"
        f"• WebSocket: {'✅' if clawcore_conn.connected else '❌'}\n"
        f"• Reconexiones: {clawcore_conn.reconnect_attempts}\n"
        f"• Método preferido: WebSocket\n"
        f"• Fallbacks: REST, CLI\n"
    )
    await update.message.reply_text(status_text)

async def connect_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando para forzar reconexión"""
    await update.message.reply_text("🔄 Forzando reconexión WebSocket...")
    success = await clawcore_conn.connect_websocket()
    if success:
        await update.message.reply_text("✅ Reconectado")
    else:
        await update.message.reply_text("❌ Error reconectando")

async def startup(app):
    """Inicialización al arrancar"""
    logger.info("Inicializando conexión ClawCore...")
    await clawcore_conn.connect_websocket()

async def shutdown(app):
    """Limpieza al detener"""
    logger.info("Cerrando conexiones...")
    await clawcore_conn.close()

def main():
    logger.info("Iniciando bot ROBUSTO (conexión WebSocket persistente)...")
    
    # Crear aplicación con handlers de inicio/cierre
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Registrar handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("connect", connect_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Handlers de inicio/cierre
    app.post_init = startup
    app.post_shutdown = shutdown
    
    logger.info("Bot ROBUSTO listo. Conexión persistente activa.")
    app.run_polling()

if __name__ == '__main__':
    main()