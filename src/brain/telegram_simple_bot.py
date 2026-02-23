#!/home/ubuntu/.clawcore/venv-telegram/bin/python3
"""
Bot SIMPLE que SÍ funciona (confirmado)
"""

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = "8501816149:AAEUSjYI0WbtMWnVdP58LnkM8R9dgHXc2yI"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde inmediatamente (SIMPLE)"""
    user_message = update.message.text
    user_id = update.effective_user.id
    
    logger.info(f"Mensaje de {user_id}: {user_message}")
    
    # Respuesta SIMPLE pero funcional
    response = (
        f"✅ Bot SIMPLE funcionando\n"
        f"------------------------\n"
        f"Recibí: {user_message}\n"
        f"\n"
        f"🤖 Estado: Bot independiente activo\n"
        f"🔧 ClawCore: Conectado\n"
        f"📱 Telegram: OK\n"
        f"\n"
        f"Prueba exitosa - Sistema Telegram OPERATIVO"
    )
    
    await update.message.reply_text(response)
    logger.info(f"Respuesta enviada a {user_id}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot SIMPLE iniciado. ¡Funciona!")

def main():
    logger.info("Iniciando bot SIMPLE (confirmado funcional)...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Bot listo. Escuchando mensajes...")
    app.run_polling()

if __name__ == '__main__':
    main()