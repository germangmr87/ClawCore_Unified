#!/home/ubuntu/.clawcore/venv-telegram/bin/python3
"""
Bot Telegram independiente que usa CLI ClawCore
(solución práctica mientras resolvemos API REST)
"""

import os
import logging
import subprocess
import json
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejador del comando /start"""
    user = update.effective_user
    await update.message.reply_text(
        f"¡Hola {user.first_name}! 🤖\n"
        f"Soy VPS132 (bot independiente).\n"
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
        # Verificar ClawCore CLI
        result = subprocess.run([CLAWCORE_PATH, "--version"], 
                              capture_output=True, text=True, timeout=5)
        clawcore_version = result.stdout.strip() if result.returncode == 0 else "❌ No disponible"
    except:
        clawcore_version = "❌ Error"
    
    await update.message.reply_text(
        f"📊 Estado del sistema:\n"
        f"• Bot Telegram: ✅ Operativo\n"
        f"• ClawCore CLI: {clawcore_version}\n"
        f"• Conexión: CLI independiente\n"
        f"• Modelo: DeepSeek V3"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejador de mensajes de texto (usa CLI ClawCore)"""
    user_message = update.message.text
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    logger.info(f"Mensaje de {user_id}: {user_message[:50]}...")
    
    # Enviar typing indicator
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    
    try:
        # Usar ClawCore CLI para procesar mensaje
        cmd = [
            CLAWCORE_PATH,
            "agent", "turn",
            "--agent", "main",
            "--message", user_message,
            "--model", "deepseek/deepseek-chat",
            "--json"
        ]
        
        logger.info(f"Ejecutando: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/home/ubuntu/.clawcore"
        )
        
        if result.returncode == 0:
            try:
                # Parsear respuesta JSON
                response_data = json.loads(result.stdout)
                bot_reply = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                if not bot_reply:
                    # Si no hay JSON, usar stdout directo
                    bot_reply = result.stdout.strip() or "No pude generar una respuesta."
            except json.JSONDecodeError:
                # Si no es JSON, usar stdout
                bot_reply = result.stdout.strip() or "No pude generar una respuesta."
            
            # Enviar respuesta (dividir si es muy larga)
            if len(bot_reply) > 4000:
                for i in range(0, len(bot_reply), 4000):
                    await update.message.reply_text(bot_reply[i:i+4000])
            else:
                await update.message.reply_text(bot_reply)
                
            logger.info(f"Respuesta enviada a {user_id}")
        else:
            error_msg = result.stderr[:100] if result.stderr else "Error desconocido"
            await update.message.reply_text(
                f"❌ Error ClawCore CLI (code {result.returncode}):\n"
                f"{error_msg}"
            )
            logger.error(f"Error ClawCore CLI: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        await update.message.reply_text("⏳ ClawCore está tardando mucho en responder. Intenta de nuevo.")
        logger.error("Timeout ClawCore CLI")
    except Exception as e:
        await update.message.reply_text(f"❌ Error interno: {str(e)}")
        logger.error(f"Error procesando mensaje: {e}")

def main():
    """Función principal"""
    logger.info("Iniciando bot Telegram independiente (CLI version)...")
    
    # Verificar que ClawCore CLI existe
    if not os.path.exists(CLAWCORE_PATH):
        logger.error(f"ClawCore no encontrado en: {CLAWCORE_PATH}")
        print(f"❌ ERROR: ClawCore no encontrado en {CLAWCORE_PATH}")
        print("   Ejecuta: which clawcore")
        return
    
    # Crear aplicación
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Registrar manejadores
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Iniciar bot
    logger.info("Bot CLI iniciado. Presiona Ctrl+C para detener.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()