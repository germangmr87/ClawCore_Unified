#!/home/ubuntu/.clawcore/venv-telegram/bin/python3
"""
Bot DEBUG - Muestra exactamente qué se envía
"""

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = "8501816149:AAEUSjYI0WbtMWnVdP58LnkM8R9dgHXc2yI"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Envía respuesta DEBUG"""
    user_message = update.message.text
    user_id = update.effective_user.id
    
    logger.info(f"Mensaje de {user_id}: {user_message}")
    
    # Respuesta DEBUG clara
    debug_response = (
        f"🔍 DEBUG BOT FUNCIONANDO\n"
        f"----------------------\n"
        f"✅ Bot: @VpsClaw132bot\n"
        f"✅ Usuario: {user_id}\n"
        f"✅ Mensaje: {user_message}\n"
        f"✅ Hora: 07:26 UTC\n"
        f"✅ Estado: Bot independiente FAST\n"
        f"✅ ClawCore: Interactivo\n"
        f"\n"
        f"Si ves esto → Bot SÍ funciona\n"
        f"Si no ves → Problema Telegram/bloqueo"
    )
    
    await update.message.reply_text(debug_response)
    logger.info(f"DEBUG enviado a {user_id}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot DEBUG iniciado. Envía cualquier mensaje.")

def main():
    logger.info("Iniciando bot DEBUG...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()