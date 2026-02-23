import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from src.clawcore_system.neuronas.kernel_soberano import kernel
from src.clawcore_system.neuronas.voz_edge import motor_voz
from src.clawcore_system.neuronas.escucha_soberana import escucha

# --- Configuración ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
NODE_NAME = os.getenv("NODE_NAME", "Unknown_Node")
DS_KEY = os.getenv("DEEPSEEK_API_KEY")

logging.basicConfig(level=logging.INFO)

if not DS_KEY:
    logging.error("❌ CRÍTICO: DEEPSEEK_API_KEY no detectada en el entorno.")

async def procesar_voz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja notas de voz entrantes (El oído de ClawCore)."""
    if not update.message.voice: return
    
    chat_id = update.effective_chat.id
    await context.bot.send_chat_action(chat_id=chat_id, action="record_voice")
    
    # 1. Descargar archivo
    file = await context.bot.get_file(update.message.voice.file_id)
    temp_path = f"/tmp/voice_{file.file_id}.ogg"
    await file.download_to_drive(temp_path)
    
    # 2. Transcribir (STT)
    texto_usuario = await escucha.transcribir(temp_path)
    if not texto_usuario or "[Error" in texto_usuario:
        await update.message.reply_text("❌ No pude entender tu voz.")
        return

    # 3. Pensar (Kernel)
    respuesta = await kernel.pensar(f"[VOZ] {texto_usuario}")
    
    # 4. Responder con Voz (TTS)
    try:
        audio_path = await motor_voz.sintetizar(respuesta.replace("[DEEPSEEK]", "").replace("[LOCAL]", "").strip())
        with open(audio_path, 'rb') as voice_file:
            await context.bot.send_voice(chat_id=chat_id, voice=voice_file, caption=f"🗣️ Entendido: \"{texto_usuario}\"")
        
        # Limpieza
        if os.path.exists(temp_path): os.remove(temp_path)
    except Exception as e:
        await update.message.reply_text(f"📝 Respuesta: {respuesta}\n(Error en voz: {e})")

async def listener(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """El 'Teléfono': Solo recibe y entrega."""
    if not update.message or not update.message.text: return
    
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # El Kernel decide cómo procesar
    respuesta = await kernel.pensar(user_text)
    
    # MODO VOZ: Si el mensaje empieza por /voz o /habla
    if user_text.lower().startswith(("/voz", "/habla")):
        texto_limpio = user_text.lower().replace("/voz", "").replace("/habla", "").strip()
        audio_text = texto_limpio if texto_limpio else respuesta.replace("[DEEPSEEK]", "").replace("[LOCAL]", "").strip()
        
        try:
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="record_voice")
            audio_path = await motor_voz.sintetizar(audio_text)
            with open(audio_path, 'rb') as voice_file:
                await context.bot.send_voice(chat_id=update.effective_chat.id, voice=voice_file, caption="🎙️ Salida Vocal Ω.1")
        except Exception as e:
            await update.message.reply_text(f"❌ Error en motor de voz: {e}")
    else:
        await update.message.reply_text(respuesta)

def main():
    print(f"📱 Interfaz Telegram Ω.1 activa para {NODE_NAME}. Voz Bidireccional habilitada.")
    if not TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN no configurado.")
        return
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, listener))
    app.add_handler(MessageHandler(filters.VOICE, procesar_voz)) # Nuevo Oído
    app.run_polling()

if __name__ == "__main__":
    main()
