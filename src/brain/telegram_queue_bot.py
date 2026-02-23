#!/home/ubuntu/.clawcore/venv-telegram/bin/python3
"""
Bot con QUEUE asíncrona - Múltiples mensajes concurrentes
"""

import asyncio
import logging
import json
import time
from typing import Dict
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = "8501816149:AAEUSjYI0WbtMWnVdP58LnkM8R9dgHXc2yI"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cola de mensajes
message_queue = asyncio.Queue()
processing_tasks = {}

# Worker pools
MAX_CONCURRENT = 3  # Máximo mensajes procesando simultáneamente
active_workers = 0

async def clawcore_worker(message_id: int, user_message: str, user_id: int):
    """Worker que procesa un mensaje con ClawCore"""
    global active_workers
    
    try:
        logger.info(f"Worker {message_id} procesando: {user_message[:50]}...")
        
        # Simular procesamiento (en realidad sería ClawCore CLI)
        await asyncio.sleep(2)  # Simular procesamiento rápido
        
        # Respuesta simulada (en realidad de ClawCore)
        response = (
            f"✅ Mensaje procesado concurrentemente\n"
            f"ID: {message_id}\n"
            f"Usuario: {user_id}\n"
            f"Mensaje: {user_message[:100]}...\n"
            f"\n"
            f"🔧 Procesado en worker pool\n"
            f"🎯 Respuesta rápida (2s simulado)"
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Worker {message_id} error: {e}")
        return f"❌ Error procesando mensaje {message_id}"
    finally:
        active_workers -= 1
        logger.info(f"Worker {message_id} terminado. Activos: {active_workers}")

async def queue_manager():
    """Manager que procesa la cola de mensajes"""
    while True:
        try:
            # Esperar mensaje en cola
            message_data = await message_queue.get()
            message_id = message_data["message_id"]
            user_message = message_data["user_message"]
            user_id = message_data["user_id"]
            update = message_data["update"]
            context = message_data["context"]
            
            # Si hay workers disponibles, procesar
            if active_workers < MAX_CONCURRENT:
                active_workers += 1
                logger.info(f"Iniciando worker {message_id}. Activos: {active_workers}")
                
                # Procesar en background
                task = asyncio.create_task(
                    clawcore_worker(message_id, user_message, user_id)
                )
                processing_tasks[message_id] = task
                
                # Cuando termine, enviar respuesta
                response = await task
                
                # Enviar a Telegram
                try:
                    await update.message.reply_text(response)
                    logger.info(f"Respuesta enviada para mensaje {message_id}")
                except Exception as e:
                    logger.error(f"Error enviando respuesta {message_id}: {e}")
                
                # Limpiar
                del processing_tasks[message_id]
                message_queue.task_done()
                
            else:
                # Re-encolar si no hay workers disponibles
                logger.info(f"Cola llena, re-encolando mensaje {message_id}")
                await asyncio.sleep(0.5)
                await message_queue.put(message_data)
                
        except Exception as e:
            logger.error(f"Queue manager error: {e}")
            await asyncio.sleep(1)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe mensaje y lo pone en cola"""
    user_message = update.message.text
    user_id = update.effective_user.id
    message_id = update.message.message_id
    
    logger.info(f"Mensaje recibido {message_id} de {user_id}: {user_message[:50]}...")
    
    # Enviar typing indicator inmediatamente
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, 
        action="typing"
    )
    
    # Poner en cola
    message_data = {
        "message_id": message_id,
        "user_message": user_message,
        "user_id": user_id,
        "update": update,
        "context": context
    }
    
    await message_queue.put(message_data)
    logger.info(f"Mensaje {message_id} encolado. Tamaño cola: {message_queue.qsize()}")
    
    # Confirmación inmediata
    await update.message.reply_text(
        f"📥 Mensaje recibido (ID: {message_id})\n"
        f"Posición en cola: {message_queue.qsize()}\n"
        f"Workers activos: {active_workers}/{MAX_CONCURRENT}\n"
        f"⏳ Procesando..."
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot QUEUE iniciado\n"
        "• Cola asíncrona de mensajes\n"
        f"• {MAX_CONCURRENT} workers concurrentes\n"
        "• Múltiples mensajes simultáneos\n"
        "• Sin bloqueos\n"
        "Envía varios mensajes seguidos para probar."
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_text = (
        "📊 Estado QUEUE:\n"
        f"• Mensajes en cola: {message_queue.qsize()}\n"
        f"• Workers activos: {active_workers}/{MAX_CONCURRENT}\n"
        f"• Tareas procesando: {len(processing_tasks)}\n"
        f"• Máximo concurrente: {MAX_CONCURRENT}"
    )
    await update.message.reply_text(status_text)

async def flood_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test de envío múltiple"""
    for i in range(5):
        test_msg = f"Mensaje test {i+1} - {time.time()}"
        await update.message.reply_text(f"📤 Enviando: {test_msg}")
        
        message_data = {
            "message_id": f"test_{i}_{time.time()}",
            "user_message": test_msg,
            "user_id": update.effective_user.id,
            "update": update,
            "context": context
        }
        
        await message_queue.put(message_data)
        await asyncio.sleep(0.5)
    
    await update.message.reply_text("✅ 5 mensajes encolados para test concurrente")

def main():
    logger.info(f"Iniciando bot QUEUE (máximo {MAX_CONCURRENT} concurrentes)...")
    
    # Iniciar queue manager en background
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    queue_task = loop.create_task(queue_manager())
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("flood", flood_test))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Bot QUEUE listo. Cola asíncrona activa.")
    
    try:
        app.run_polling()
    finally:
        # Cancelar queue task al salir
        queue_task.cancel()

if __name__ == '__main__':
    main()