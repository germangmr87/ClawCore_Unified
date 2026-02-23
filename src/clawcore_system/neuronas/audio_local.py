"""
AUDIO LOCAL Ω.1 — Interfaz de Presencia Física (iMac)
Maneja los altavoces y el micrófono del host local.
"""

import os
import logging
import subprocess
import time
import asyncio
from pathlib import Path

# Importaciones soberanas
from src.clawcore_system.neuronas.voz_edge import motor_voz
from src.clawcore_system.neuronas.escucha_soberana import escucha
from src.clawcore_system.neuronas.kernel_soberano import kernel

logger = logging.getLogger("AudioLocal")
logger.setLevel(logging.INFO)

class AudioLocal:
    def __init__(self):
        self.output_dir = Path.home() / ".clawcore/audio_local"
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.listening = False

    def hablar_fisicamente(self, texto: str):
        """Sintetiza y reproduce audio por los altavoces del iMac."""
        async def _hablar():
            try:
                # 1. Generar MP3
                path = await motor_voz.sintetizar(texto, "ambient_out.mp3")
                
                # 2. Reproducir usando 'afplay' (nativo de macOS)
                logger.info(f"🔊 Reproduciendo en altavoces: {texto}")
                subprocess.run(["afplay", path], check=True)
            except Exception as e:
                logger.error(f"❌ Error en reproducción física: {e}")
        
        asyncio.run_coroutine_threadsafe(_hablar(), asyncio.get_event_loop())

    async def escuchar_ambiente(self, duracion=5):
        """Graba del micrófono y procesa la intención."""
        temp_rec = self.output_dir / "ambient_rec.wav"
        try:
            logger.info(f"🎤 Escuchando ambiente ({duracion}s)...")
            
            # Usamos ffmpeg para grabar del micro nativo de macOS (avfoundation)
            # 'default' es usualmente el micro integrado.
            cmd = [
                "ffmpeg", "-y", "-f", "avfoundation", "-i", ":0", 
                "-t", str(duracion), "-ar", "16000", "-ac", "1", str(temp_rec)
            ]
            
            process = await asyncio.create_subprocess_exec(*cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            await process.wait()
            
            if temp_rec.exists():
                texto = await escucha.transcribir(str(temp_rec))
                if texto and len(texto) > 2:
                    logger.info(f"👤 Usuario dijo: {texto}")
                    respuesta = await kernel.pensar(f"[AMBIENTE] {texto}")
                    self.hablar_fisicamente(respuesta.replace("[DEEPSEEK]", "").replace("[LOCAL]", ""))
                else:
                    logger.info("🔇 No se detectó voz clara.")
        except Exception as e:
            logger.error(f"❌ Error capturando ambiente: {e}")

    def modo_centinela(self):
        """Activa la escucha continua (Wake Word simplificado por ahora)."""
        logger.info("🛡️ Modo Centinela Vocal activado en iMac.")
        self.listening = True
        # En un sistema real, esto iría en un hilo loop
        # Por ahora lo exponemos para ser llamado por el Kernel o ecosistema

# Singleton
audio_hardware = AudioLocal()

if __name__ == "__main__":
    # Test: Hacer que el iMac diga hola
    # audio_hardware.hablar_fisicamente("Sistemas de audio físico inicializados. Hola Gabriel.")
    pass
