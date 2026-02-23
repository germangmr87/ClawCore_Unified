#!/home/ubuntu/.clawcore/venv-telegram/bin/python3
"""
Bot ROUTER - Conexión intermedia entre Claws
"""

import os
import logging
import random
import subprocess
import json
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = "8501816149:AAEUSjYI0WbtMWnVdP58LnkM8R9dgHXc2yI"

# Configuración Claws
CLAWS = [
    {
        "name": "VPS132",
        "clawcore_path": "/home/ubuntu/.nvm/versions/node/v22.22.0/bin/clawcore",
        "cwd": "/home/ubuntu/.clawcore",
        "weight": 1  # Prioridad
    },
    {
        "name": "VpsClaw229bot",
        "ssh_cmd": "ssh -o StrictHostKeyChecking=no ubuntu@127.0.0.1",
        "clawcore_path": "/home/ubuntu/.nvm/versions/node/v22.22.0/bin/clawcore",
        "weight": 1
    }
]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClawRouter:
    """Router inteligente entre Claws"""
    
    def __init__(self):
        self.claw_stats = {claw["name"]: {"success": 0, "errors": 0, "last_response_time": None} for claw in CLAWS}
    
    def select_claw(self):
        """Selecciona el mejor Claw basado en estadísticas"""
        # Por ahora, round-robin simple
        available_claws = [c for c in CLAWS if self.claw_stats[c["name"]]["errors"] < 3]
        if not available_claws:
            available_claws = CLAWS  # Reset si todos tienen errores
        
        return random.choice(available_claws)
    
    def send_to_claw(self, claw, user_message):
        """Envía mensaje a un Claw específico"""
        start_time = time.time()
        
        try:
            if "ssh_cmd" in claw:
                # Claw remoto (VpsClaw229bot)
                cmd = f"{claw['ssh_cmd']} '{claw['clawcore_path']} agent turn --agent main --message \"{user_message}\" --model deepseek/deepseek-chat --json'"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            else:
                # Claw local (VPS132)
                cmd = [
                    claw["clawcore_path"],
                    "agent", "turn",
                    "--agent", "main",
                    "--message", user_message,
                    "--model", "deepseek/deepseek-chat",
                    "--json"
                ]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=25,
                    cwd=claw.get("cwd", "/home/ubuntu/.clawcore")
                )
            
            elapsed = time.time() - start_time
            
            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                    response = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    
                    if response:
                        self.claw_stats[claw["name"]]["success"] += 1
                        self.claw_stats[claw["name"]]["last_response_time"] = elapsed
                        return response
                    else:
                        self.claw_stats[claw["name"]]["errors"] += 1
                        return "❌ Claw respondió vacío"
                        
                except json.JSONDecodeError:
                    self.claw_stats[claw["name"]]["errors"] += 1
                    return f"❌ Error JSON Claw {claw['name']}"
            else:
                self.claw_stats[claw["name"]]["errors"] += 1
                return f"❌ Error Claw {claw['name']}: {result.stderr[:100]}"
                
        except subprocess.TimeoutExpired:
            self.claw_stats[claw["name"]]["errors"] += 1
            return f"⏳ Timeout Claw {claw['name']}"
        except Exception as e:
            self.claw_stats[claw["name"]]["errors"] += 1
            return f"❌ Error Claw {claw['name']}: {str(e)}"
    
    def get_stats(self):
        """Obtiene estadísticas de los Claws"""
        stats_text = "📊 Estadísticas Claws:\n"
        for name, stats in self.claw_stats.items():
            stats_text += f"• {name}: ✅{stats['success']} ❌{stats['errors']}"
            if stats['last_response_time']:
                stats_text += f" ⏱{stats['last_response_time']:.1f}s"
            stats_text += "\n"
        return stats_text

# Router global
router = ClawRouter()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja mensajes con routing entre Claws"""
    user_message = update.message.text
    user_id = update.effective_user.id
    
    logger.info(f"Mensaje ROUTER de {user_id}: {user_message[:50]}...")
    
    # Enviar typing indicator
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, 
        action="typing"
    )
    
    # Seleccionar Claw
    selected_claw = router.select_claw()
    logger.info(f"Routing a {selected_claw['name']}")
    
    # Enviar a Claw
    response = router.send_to_claw(selected_claw, user_message)
    
    # Agregar info de routing
    routed_response = (
        f"{response}\n\n"
        f"---\n"
        f"🔄 Routed via: {selected_claw['name']}\n"
        f"🤖 Bot: @VpsClaw132bot (Router)"
    )
    
    # Enviar respuesta
    if len(routed_response) > 4000:
        for i in range(0, len(routed_response), 4000):
            await update.message.reply_text(routed_response[i:i+4000])
    else:
        await update.message.reply_text(routed_response)
    
    logger.info(f"Respuesta ROUTER enviada desde {selected_claw['name']}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot ROUTER iniciado\n"
        "Conectado a múltiples Claws.\n"
        "Balanceo automático + failover.\n"
        "Envía cualquier mensaje."
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats_text = router.get_stats()
    await update.message.reply_text(stats_text)

async def claws(update: Update, context: ContextTypes.DEFAULT_TYPE):
    claws_info = "🔧 Claws disponibles:\n"
    for claw in CLAWS:
        claws_info += f"• {claw['name']}"
        if 'ssh_cmd' in claw:
            claws_info += " (remoto)"
        claws_info += f" - peso: {claw['weight']}\n"
    
    await update.message.reply_text(claws_info)

def main():
    logger.info("Iniciando bot ROUTER (conexión intermedia Claws)...")
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("claws", claws))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Bot ROUTER listo. Routing entre Claws activo.")
    app.run_polling()

if __name__ == '__main__':
    main()