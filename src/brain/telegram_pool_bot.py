#!/home/ubuntu/.clawcore/venv-telegram/bin/python3
"""
Bot con POOL de procesos ClawCore - Conexión robusta via CLI
"""

import os
import logging
import asyncio
import subprocess
import json
import time
from concurrent.futures import ThreadPoolExecutor
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = "8501816149:AAEUSjYI0WbtMWnVdP58LnkM8R9dgHXc2yI"
CLAWCORE_PATH = "/home/ubuntu/.nvm/versions/node/v22.22.0/bin/clawcore"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClawCoreProcessPool:
    """Pool de procesos ClawCore para conexión robusta"""
    
    def __init__(self, pool_size=3):
        self.pool_size = pool_size
        self.executor = ThreadPoolExecutor(max_workers=pool_size)
        self.process_cache = {}  # Cache de respuestas
        self.stats = {
            "total_requests": 0,
            "successful": 0,
            "failed": 0,
            "avg_response_time": 0
        }
    
    def _run_clawcore_sync(self, message):
        """Ejecuta ClawCore CLI (síncrono, para thread pool)"""
        start_time = time.time()
        
        try:
            # Cache simple
            cache_key = message.lower()[:100]
            if cache_key in self.process_cache:
                logger.info(f"Cache hit: {cache_key[:50]}...")
                return self.process_cache[cache_key]
            
            cmd = [
                CLAWCORE_PATH,
                "agent", "turn",
                "--agent", "main",
                "--message", message,
                "--model", "deepseek/deepseek-chat",
                "--max-tokens", "500",
                "--json",
                "--timeout", "20"
            ]
            
            logger.info(f"Ejecutando ClawCore: {message[:50]}...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=25,
                cwd="/home/ubuntu/.clawcore"
            )
            
            elapsed = time.time() - start_time
            
            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                    response = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    
                    if response:
                        # Actualizar stats
                        self.stats["total_requests"] += 1
                        self.stats["successful"] += 1
                        self.stats["avg_response_time"] = (
                            (self.stats["avg_response_time"] * (self.stats["successful"] - 1) + elapsed) 
                            / self.stats["successful"]
                        )
                        
                        # Cachear
                        self.process_cache[cache_key] = response
                        if len(self.process_cache) > 100:  # Limitar cache
                            self.process_cache.pop(next(iter(self.process_cache)))
                        
                        return response
                    else:
                        self.stats["failed"] += 1
                        return "❌ ClawCore respondió vacío"
                        
                except json.JSONDecodeError:
                    self.stats["failed"] += 1
                    return f"❌ Error JSON: {result.stdout[:100]}"
            else:
                self.stats["failed"] += 1
                error_msg = result.stderr[:100] if result.stderr else "Unknown error"
                return f"❌ ClawCore error: {error_msg}"
                
        except subprocess.TimeoutExpired:
            self.stats["failed"] += 1
            return "⏳ Timeout ClawCore (25s)"
        except Exception as e:
            self.stats["failed"] += 1
            return f"❌ Error: {str(e)}"
    
    async def get_response(self, message):
        """Obtiene respuesta usando thread pool"""
        loop = asyncio.get_event_loop()
        
        # Ejecutar en thread pool (no bloquea event loop)
        response = await loop.run_in_executor(
            self.executor,
            self._run_clawcore_sync,
            message
        )
        
        return response
    
    def get_stats(self):
        """Obtiene estadísticas"""
        success_rate = (self.stats["successful"] / self.stats["total_requests"] * 100) if self.stats["total_requests"] > 0 else 0
        return {
            "total_requests": self.stats["total_requests"],
            "successful": self.stats["successful"],
            "failed": self.stats["failed"],
            "success_rate": f"{success_rate:.1f}%",
            "avg_response_time": f"{self.stats['avg_response_time']:.1f}s",
            "cache_size": len(self.process_cache),
            "pool_size": self.pool_size
        }
    
    def cleanup(self):
        """Limpia recursos"""
        self.executor.shutdown(wait=True)

# Pool global
clawcore_pool = ClawCoreProcessPool(pool_size=3)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja mensajes con pool de procesos"""
    user_message = update.message.text
    user_id = update.effective_user.id
    
    logger.info(f"Mensaje POOL de {user_id}: {user_message[:50]}...")
    
    # Enviar typing indicator
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, 
        action="typing"
    )
    
    # Obtener respuesta usando pool
    start_time = time.time()
    response = await clawcore_pool.get_response(user_message)
    elapsed = time.time() - start_time
    
    # Agregar métricas
    pool_response = (
        f"{response}\n\n"
        f"---\n"
        f"⏱ {elapsed:.1f}s | 🏊 Pool: {clawcore_pool.pool_size} procesos"
    )
    
    # Enviar respuesta
    if len(pool_response) > 4000:
        for i in range(0, len(pool_response), 4000):
            await update.message.reply_text(pool_response[i:i+4000])
    else:
        await update.message.reply_text(pool_response)
    
    logger.info(f"Respuesta POOL enviada en {elapsed:.1f}s")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot POOL iniciado\n"
        "Pool de procesos ClawCore para conexión robusta.\n"
        "• Thread pool (no bloqueante)\n"
        "• Cache de respuestas\n"
        "• Estadísticas en tiempo real\n"
        "• Máxima confiabilidad CLI"
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats_data = clawcore_pool.get_stats()
    stats_text = "📊 Estadísticas POOL:\n"
    for key, value in stats_data.items():
        stats_text += f"• {key}: {value}\n"
    
    await update.message.reply_text(stats_text)

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test de conexión"""
    start_time = time.time()
    test_response = await clawcore_pool.get_response("Responde OK si estás funcionando")
    elapsed = time.time() - start_time
    
    await update.message.reply_text(
        f"🏓 PONG\n"
        f"Tiempo: {elapsed:.1f}s\n"
        f"Respuesta: {test_response[:100]}..."
    )

def main():
    logger.info("Iniciando bot POOL (conexión robusta via CLI pool)...")
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info(f"Bot POOL listo. Pool size: {clawcore_pool.pool_size}")
    
    try:
        app.run_polling()
    finally:
        # Limpiar pool al salir
        clawcore_pool.cleanup()

if __name__ == '__main__':
    main()