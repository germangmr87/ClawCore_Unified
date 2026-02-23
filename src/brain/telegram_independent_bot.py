#!/home/ubuntu/.clawcore/venv-telegram/bin/python3
"""
Bot Telegram independiente que usa ClawCore API
Evita bug del plugin Telegram oficial de ClawCore
"""

import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configuración
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8501816149:AAEUSjYI0WbtMWnVdP58LnkM8R9dgHXc2yI")
CLAWCORE_API_URL = "http://localhost:18789/v1/chat/completions"
CLAWCORE_API_KEY = os.getenv("CLAWCORE_API_KEY", "")

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejador del comando /start"""
    user = update.effective_user
    await update.message.reply_text(
        f"¡Hola {user.first_name}! 🤖\n"
        f"Soy VPS132 conectado via API independiente.\n"
        f"Envíame cualquier mensaje y lo procesaré con ClawCore."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejador del comando /help"""
    await update.message.reply_text(
        "Comandos disponibles:\n"
        "/start - Iniciar conversación\n"
        "/help - Mostrar esta ayuda\n"
        "/status - Ver estado del sistema\n"
        "\nEnvía cualquier mensaje para procesarlo con IA."
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejador del comando /status"""
    try:
        # Verificar conexión a ClawCore
        response = requests.get("http://localhost:18789", timeout=5)
        clawcore_status = "✅ Conectado" if response.status_code == 200 else "❌ Desconectado"
    except:
        clawcore_status = "❌ Desconectado"
    
    await update.message.reply_text(
        f"📊 Estado del sistema:\n"
        f"• Bot Telegram: ✅ Operativo\n"
        f"• ClawCore API: {clawcore_status}\n"
        f"• Conexión: API independiente\n"
        f"• Modelo: DeepSeek V3 (via ClawCore)"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejador de mensajes de texto"""
    user_message = update.message.text
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    logger.info(f"Mensaje de {user_id}: {user_message[:50]}...")
    
    # Enviar typing indicator
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    
    try:
        # Enviar a ClawCore API
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            "model": "deepseek/deepseek-chat"
        }
        
        headers = {}
        if CLAWCORE_API_KEY:
            headers["Authorization"] = f"Bearer {CLAWCORE_API_KEY}"
        
        response = requests.post(
            CLAWCORE_API_URL,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            bot_reply = data.get("choices", [{}])[0].get("message", {}).get("content", "No pude generar una respuesta.")
            
            # Enviar respuesta (dividir si es muy larga)
            if len(bot_reply) > 4000:
                for i in range(0, len(bot_reply), 4000):
                    await update.message.reply_text(bot_reply[i:i+4000])
            else:
                await update.message.reply_text(bot_reply)
                
            logger.info(f"Respuesta enviada a {user_id}")
        else:
            await update.message.reply_text(
                f"❌ Error al conectar con ClawCore (HTTP {response.status_code})\n"
                f"Intenta de nuevo en unos momentos."
            )
            logger.error(f"Error ClawCore API: {response.status_code} - {response.text}")
            
    except requests.exceptions.Timeout:
        await update.message.reply_text("⏳ ClawCore está tardando mucho en responder. Intenta de nuevo.")
        logger.error("Timeout ClawCore API")
    except Exception as e:
        await update.message.reply_text(f"❌ Error interno: {str(e)}")
        logger.error(f"Error procesando mensaje: {e}")

def main():
    """Función principal"""
    logger.info("Iniciando bot Telegram independiente...")
    
    # Crear aplicación
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Registrar manejadores
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Iniciar bot
    logger.info("Bot iniciado. Presiona Ctrl+C para detener.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()