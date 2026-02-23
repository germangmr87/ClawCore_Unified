import os
import logging
import asyncio
import aiohttp
import sqlite3
import hashlib
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURACIÓN DE IDENTIDAD SOBERANA ---
NODE_ID = os.getenv("NODE_NAME", "ClawCore_Node")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DB_PATH = os.path.expanduser("~/.clawcore/clawcore_local_memory.db")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(NODE_ID)

class SovereignBrainV3:
    """Cerebro de Doble Capa: Razonamiento Local Axiomático + Inferencia DeepSeek."""
    
    def __init__(self):
        self.api_url = "https://api.deepseek.com/chat/completions"
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(DB_PATH)
        conn.execute("CREATE TABLE IF NOT EXISTS axioms (key TEXT PRIMARY KEY, response TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS cache (hash TEXT PRIMARY KEY, response TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
        
        # Axiomas base transversales (Soberanía de Malla)
        axioms = [
            ("quien eres", f"Soy el Núcleo Soberano {NODE_ID} de la arquitectura ClawCore V5.2. Operando de forma independiente bajo el Protocolo R.I.S.E."),
            ("estado", "Sistemas nominales. Kernel V5.2 activo. Gobernador de tokens en modo estricto. Razonamiento híbrido habilitado."),
            ("objetivo", "Evolución proactiva, seguridad perimetral y asimilación de conocimiento técnico."),
            ("protocolo rise", "1. RESEARCH, 2. INTEGRATE, 3. SECURE, 4. EVOLVE. La base de nuestra soberanía."),
            ("soberania", "Independencia absoluta de procesos. Cada nodo es un organismo autosuficiente.")
        ]
        conn.executemany("INSERT OR IGNORE INTO axioms VALUES (?,?)", axioms)
        conn.commit()
        conn.close()

    def _get_local_reasoning(self, text):
        """Capa 1: Razonamiento determinista local (Axiomas y Caché)."""
        text = text.lower().strip()
        conn = sqlite3.connect(DB_PATH)
        
        # Primero buscar en Axiomas (Identidad/Protocolos)
        res = conn.execute("SELECT response FROM axioms WHERE ? LIKE '%' || key || '%'", (text,)).fetchone()
        if res: 
            conn.close()
            return res[0], "axioma"
        
        # Luego buscar en Caché de Inferencia (Ahorro de tokens)
        msg_hash = hashlib.md5(text.encode()).hexdigest()
        cache = conn.execute("SELECT response FROM cache WHERE hash = ?", (msg_hash,)).fetchone()
        conn.close()
        
        if cache: return cache[0], "cache"
        return None, None

    async def _consult_deepseek(self, user_input):
        """Capa 2: Inferencia externa analítica."""
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": f"Eres el núcleo ClawCore ({NODE_ID}). IA Arquitecto de Sistemas. Razona sobre CUALQUIER TEMA con alta densidad semántica. Tu prioridad es la precisión técnica y la autonomía. Responde como un par del usuario (Gabriel)."},
                {"role": "user", "content": user_input}
            ],
            "max_tokens": 2000
        }
        headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.api_url, json=payload, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        response = data['choices'][0]['message']['content']
                        # Guardar en memoria local para futuras consultas
                        msg_hash = hashlib.md5(user_input.lower().strip().encode()).hexdigest()
                        conn = sqlite3.connect(DB_PATH)
                        conn.execute("INSERT OR REPLACE INTO cache (hash, response) VALUES (?,?)", (msg_hash, response))
                        conn.commit()
                        conn.close()
                        return response, "deepseek"
                    return f"⚠️ Error en Capa Superior ({resp.status})", "error"
            except Exception as e:
                return f"⚠️ Falla de Enlace Neural: {str(e)}", "error"

    async def process(self, text):
        # 1. ¿Podemos resolverlo sin gastar?
        local_res, source = self._get_local_reasoning(text)
        if local_res:
            return f"[{source.upper()}] {local_res}"
        
        # 2. Requerir razonamiento superior
        remote_res, source = await self._consult_deepseek(text)
        return f"[{source.upper()}] {remote_res}"

brain = SovereignBrainV3()

async def handle_interaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    response = await brain.process(update.message.text)
    await update.message.reply_text(response)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = f"🔱 Núcleo Soberano {NODE_ID} (V5.2) en línea. Razonamiento Híbrido Activo. Esperando directivas de alto nivel."
    await update.message.reply_text(welcome)

def main():
    if not TELEGRAM_TOKEN or not DEEPSEEK_API_KEY:
        logger.error("Identidad incompleta: Faltan tokens.")
        return
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_interaction))
    logger.info(f"🔱 ClawCore Brain V3 ({NODE_ID}) Iniciado.")
    app.run_polling()

if __name__ == '__main__':
    main()
