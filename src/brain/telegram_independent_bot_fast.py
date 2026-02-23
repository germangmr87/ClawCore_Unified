#!/home/ubuntu/.clawcore/venv-telegram/bin/python3
"""
Bot Telegram FAST - Usa ClawCore en modo persistente
"""

import os
import logging
import subprocess
import json
import threading
import queue
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configuración
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8501816149:AAEUSjYI0WbtMWnVdP58LnkM8R9dgHXc2yI")
CLAWCORE_PATH = "/home/ubuntu/.nvm/versions/node/v22.22.0/bin/clawcore"

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Cola para procesamiento en batch
message_queue = queue.Queue()
results = {}

class ClawCoreProcessor:
    """Procesador que mantiene ClawCore corriendo para respuestas rápidas"""
    
    def __init__(self):
        self.process = None
        self.start_clawcore_session()
    
    def start_clawcore_session(self):
        """Inicia ClawCore en modo interactivo"""
        try:
            logger.info("Iniciando ClawCore en modo interactivo...")
            self.process = subprocess.Popen(
                [CLAWCORE_PATH, "agent", "console", "--agent", "main"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                cwd="/home/ubuntu/.clawcore"
            )
            # Esperar inicio
            import time
            time.sleep(3)
            logger.info("ClawCore interactivo iniciado")
        except Exception as e:
            logger.error(f"Error iniciando ClawCore: {e}")
            self.process = None
    
    def send_message(self, message_id, user_message):
        """Envía mensaje a ClawCore interactivo"""
        if not self.process or self.process.poll() is not None:
            self.start_clawcore_session()
            if not self.process:
                return "❌ ClawCore no disponible"
        
        try:
            # Enviar mensaje
            self.process.stdin.write(user_message + "\n")
            self.process.stdin.flush()
            
            # Leer respuesta (timeout 15 segundos)
            import time
            start_time = time.time()
            response_lines = []
            
            while time.time() - start_time < 15:
                line = self.process.stdout.readline()
                if line:
                    response_lines.append(line.strip())
                    # Heurística: si línea parece fin de respuesta
                    if any(marker in line for marker in ["```", "---", ">>>"]):
                        break
                    if len(response_lines) > 10:  # Límite líneas
                        break
            
            response = " ".join(response_lines[-5:]) if response_lines else "No response"
            return response[:4000]  # Límite Telegram
            
        except Exception as e:
            logger.error(f"Error comunicando con ClawCore: {e}")
            return f"❌ Error: {str(e)}"

# Procesador global
processor = ClawCoreProcessor()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejador del comando /start"""
    user = update.effective_user
    await update.message.reply_text(
        f"¡Hola {user.first_name}! 🤖\n"
        f"Soy VPS132 (bot FAST).\n"
        f"Procesando con ClawCore interactivo (más rápido)."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejador de mensajes de texto (FAST)"""
    user_message = update.message.text
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    logger.info(f"Mensaje FAST de {user_id}: {user_message[:50]}...")
    
    # Enviar typing indicator inmediatamente
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    
    try:
        # Usar procesador interactivo (más rápido)
        response = processor.send_message(update.message.message_id, user_message)
        
        if response:
            await update.message.reply_text(response[:4000])
            logger.info(f"Respuesta FAST enviada a {user_id}")
        else:
            await update.message.reply_text("⏳ Procesando... (timeout)")
            
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")
        logger.error(f"Error procesando mensaje FAST: {e}")

def main():
    """Función principal"""
    logger.info("Iniciando bot Telegram FAST (interactive mode)...")
    
    # Verificar ClawCore
    if not os.path.exists(CLAWCORE_PATH):
        logger.error(f"ClawCore no encontrado: {CLAWCORE_PATH}")
        return
    
    # Crear aplicación
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Registrar manejadores
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Iniciar bot
    logger.info("Bot FAST iniciado. Presiona Ctrl+C para detener.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()