#!/usr/bin/env python3
"""
BOT TELEGRAM SIMPLE PARA CLAWCORE
"""

import logging
import asyncio
import json
import subprocess
from pathlib import Path
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token del bot
TOKEN = "8105513236:AAHnAiCZ82urAqyA6x3U3PcVKGSy8KBCWjk"

class SimpleClawCoreBot:
    def __init__(self):
        self.base_dir = Path.home() / ".clawcore" / "clawcore"
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start"""
        await update.message.reply_text(
            "🤖 *ClawCore Bot Activado*\n\n"
            "Comandos:\n"
            "/start - Este mensaje\n"
            "/status - Estado ClawCore\n" 
            "/ollama <texto> - Pregunta a IA local\n"
            "/help - Ayuda\n\n"
            "VPS: 127.0.0.1\n"
            "IA: Ollama llama3.2:3b (gratis)",
            parse_mode='Markdown'
        )
    
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /status"""
        try:
            # Verificar estado
            estado_file = self.base_dir / "estado_evolucion.json"
            if estado_file.exists():
                with open(estado_file, 'r') as f:
                    estado = json.load(f)
                autonomia = estado.get("autonomia", 0.228)
                
                status_msg = f"📊 *Estado ClawCore*\n\n"
                status_msg += f"🧠 Autonomía: {autonomia:.2%}\n"
                status_msg += f"🔄 Evoluciones: {estado.get('evoluciones', 2)}\n"
                status_msg += f"⏱️ Última: {estado.get('ultima_evolucion', 'N/A')[11:19]} UTC\n\n"
                
                # Barra de progreso
                progreso = autonomia * 100
                barra = "█" * int(progreso / 5) + "░" * (20 - int(progreso / 5))
                status_msg += f"📈 Progreso: [{barra}] {progreso:.1f}%\n\n"
                
                status_msg += "✅ Componentes activos:\n"
                status_msg += "• Ollama (IA local gratis)\n"
                status_msg += "• Sistema neuronal\n"
                status_msg += "• Cron job (+0.5%/hora)\n"
                status_msg += "• ClawCore gateway\n"
                
                await update.message.reply_text(status_msg, parse_mode='Markdown')
            else:
                await update.message.reply_text("⚠️ Estado no disponible")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def ollama(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /ollama"""
        if not context.args:
            await update.message.reply_text("Uso: /ollama <tu pregunta>")
            return
        
        pregunta = " ".join(context.args)
        await update.message.reply_text(f"🤖 Consultando Ollama...")
        
        try:
            # Ejecutar Ollama
            cmd = ["ollama", "run", "llama3.2:3b", pregunta[:500]]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                respuesta = result.stdout.strip()
                if len(respuesta) > 4000:
                    respuesta = respuesta[:4000] + "\n\n... (truncado)"
                
                await update.message.reply_text(f"*Respuesta:*\n\n{respuesta}", parse_mode='Markdown')
            else:
                await update.message.reply_text(f"❌ Error: {result.stderr[:200]}")
                
        except subprocess.TimeoutExpired:
            await update.message.reply_text("⏱️ Timeout: Intenta pregunta más corta")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /help"""
        help_msg = (
            "🆘 *Ayuda ClawCore Bot*\n\n"
            "*Comandos:*\n"
            "/start - Mensaje inicio\n"
            "/status - Estado sistema\n"
            "/ollama <texto> - Pregunta IA local\n"
            "/help - Esta ayuda\n\n"
            "*Ejemplos:*\n"
            "/ollama escribe código Python\n"
            "/status (ver autonomía)\n\n"
            "*VPS:* 127.0.0.1\n"
            "*Token:* 8105513236:AAHnAiCZ82urAqyA6x3U3PcVKGSy8KBCWjk"
        )
        await update.message.reply_text(help_msg, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja mensajes normales"""
        if not update.message.text.startswith('/'):
            await update.message.reply_text(
                "Escribe /help para ver comandos disponibles",
                parse_mode='Markdown'
            )

async def main():
    """Función principal"""
    print("🤖 Iniciando Bot Telegram ClawCore...")
    print(f"Token: {TOKEN}")
    
    bot = SimpleClawCoreBot()
    
    # Crear aplicación
    application = Application.builder().token(TOKEN).build()
    
    # Configurar handlers
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("status", bot.status))
    application.add_handler(CommandHandler("ollama", bot.ollama))
    application.add_handler(CommandHandler("help", bot.help))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    
    print("✅ Bot configurado. Iniciando...")
    print("📱 Telegram: @VpsClaw229bot")
    
    # Iniciar bot
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    print("🚀 Bot activo. Manteniendo ejecución...")
    
    # Mantener corriendo
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot detenido")
    except Exception as e:
        print(f"❌ Error: {e}")