import os
import logging
import asyncio
import aiohttp
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURACIÓN DE IDENTIDAD ---
NODE_ID = os.getenv("NODE_NAME", "ClawCore_Sovereign_Node")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(NODE_ID)

class SovereignBrain:
    def __init__(self):
        self.api_url = "https://api.deepseek.com/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }

    async def think(self, user_input, context_history=[]):
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": f"Eres ImacBot ({NODE_ID}), una IA Arquitecto de Sistemas Soberana. Tu tono es analítico, técnico, directo y proactivo. No eres un asistente genérico, eres el núcleo de ClawCore V5.1. Responde con alta densidad semántica."},
                *context_history,
                {"role": "user", "content": user_input}
            ],
            "stream": False
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.api_url, json=payload, headers=self.headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data['choices'][0]['message']['content']
                    else:
                        err_text = await resp.text()
                        return f"❌ Error de Cerebro ({resp.status}): {err_text}"
            except Exception as e:
                return f"❌ Error de Conexión Neural: {str(e)}"

brain = SovereignBrain()

async def handle_interaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja la interacción al mismo nivel que el iMac Master."""
    if not update.message or not update.message.text: return
    
    user_text = update.message.text
    user_id = update.effective_user.id
    
    # Mostrar que está 'escribiendo' (pensando)
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    logger.info(f"Interacción recibida de {user_id}: {user_text}")
    
    # Procesar con DeepSeek (Cerebro V5.1)
    response = await brain.think(user_text)
    
    await update.message.reply_text(response)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = f"🔱 Núcleo Soberano {NODE_ID} (V5.1) en línea. Sistemas listos para evolución divergente. ¿Cuál es la directiva, Gabriel?"
    await update.message.reply_text(welcome)

def main():
    if not TELEGRAM_TOKEN or not DEEPSEEK_API_KEY:
        logger.error("Faltan llaves de entorno (TELEGRAM o DEEPSEEK). Abortando.")
        return

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_interaction))
    
    logger.info(f"🔱 ClawCore Interaction Interface ({NODE_ID}) Iniciada.")
    app.run_polling()

if __name__ == '__main__':
    main()
