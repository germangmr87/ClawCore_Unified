#!/home/ubuntu/.clawcore/venv-telegram/bin/python3
"""
Bot SMART - Usa ClawCore CLI con caché para respuestas inteligentes
"""

import os
import logging
import subprocess
import json
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = "8501816149:AAEUSjYI0WbtMWnVdP58LnkM8R9dgHXc2yI"
CLAWCORE_PATH = "/home/ubuntu/.nvm/versions/node/v22.22.0/bin/clawcore"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache simple para no repetir
response_cache = {}

def get_clawcore_response(user_message, user_id):
    """Obtiene respuesta de ClawCore CLI (con caché simple)"""
    
    # Cache por mensaje similar
    cache_key = user_message.lower()[:50]
    if cache_key in response_cache:
        logger.info(f"Usando caché para: {cache_key}")
        return response_cache[cache_key]
    
    try:
        logger.info(f"Consultando ClawCore para: {user_message[:50]}...")
        
        # Comando ClawCore optimizado
        cmd = [
            CLAWCORE_PATH,
            "agent", "turn",
            "--agent", "main",
            "--message", user_message,
            "--model", "deepseek/deepseek-chat",
            "--max-tokens", "500",
            "--json"
        ]
        
        start_time = time.time()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=25,  # Timeout más corto
            cwd="/home/ubuntu/.clawcore"
        )
        
        elapsed = time.time() - start_time
        logger.info(f"ClawCore respondió en {elapsed:.1f}s")
        
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                response = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                if not response:
                    # Fallback a stdout
                    response = result.stdout.strip() or "No pude generar una respuesta."
                    
            except json.JSONDecodeError:
                response = result.stdout.strip() or "No pude generar una respuesta."
            
            # Guardar en caché
            response_cache[cache_key] = response
            return response
            
        else:
            error_msg = result.stderr[:100] if result.stderr else "Error ClawCore"
            logger.error(f"ClawCore error: {error_msg}")
            return f"⚠️ ClawCore error: {error_msg}"
            
    except subprocess.TimeoutExpired:
        logger.error("ClawCore timeout")
        return "⏳ ClawCore está tardando mucho. Intenta un mensaje más corto."
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {str(e)}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde usando ClawCore (inteligente)"""
    user_message = update.message.text
    user_id = update.effective_user.id
    
    logger.info(f"Mensaje SMART de {user_id}: {user_message[:50]}...")
    
    # Enviar typing indicator
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, 
        action="typing"
    )
    
    # Obtener respuesta de ClawCore
    response = get_clawcore_response(user_message, user_id)
    
    # Enviar respuesta (dividir si es muy larga)
    if len(response) > 4000:
        for i in range(0, len(response), 4000):
            await update.message.reply_text(response[i:i+4000])
    else:
        await update.message.reply_text(response)
    
    logger.info(f"Respuesta SMART enviada a {user_id}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot SMART iniciado\n"
        "Conectado a ClawCore para respuestas inteligentes.\n"
        "Modelo: DeepSeek V3\n"
        "Envía cualquier mensaje."
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 Bot SMART - Estado:\n"
        "• Conectado: ✅\n"
        "• ClawCore: Operativo\n"
        "• Modelo: DeepSeek V3\n"
        "• Cache: Activado\n"
        "• Respuestas: Inteligentes"
    )

def main():
    logger.info("Iniciando bot SMART (ClawCore + caché)...")
    
    if not os.path.exists(CLAWCORE_PATH):
        logger.error(f"ClawCore no encontrado: {CLAWCORE_PATH}")
        return
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Bot SMART listo. Respuestas inteligentes activas.")
    app.run_polling()

if __name__ == '__main__':
    main()