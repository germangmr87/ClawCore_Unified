"""
ESCUCHA SOBERANA Ω.1 — Transcripción Local (STT)
Convierte audio en texto usando Whisper (offline).
"""

import os
import logging
from pathlib import Path
import subprocess

logger = logging.getLogger("EscuchaSoberana")
logger.setLevel(logging.INFO)

class EscuchaSoberana:
    """
    MOTOR DE ESCUCHA Ω.1
    Utiliza whisper-cpp o openai-whisper para procesar audio localmente.
    """
    def __init__(self):
        self.activo = False
        self.temp_dir = Path.home() / ".clawcore/audio_in"
        self.temp_dir.mkdir(exist_ok=True, parents=True)
        self._verificar_dependencias()

    def _verificar_dependencias(self):
        # Intentamos detectar whisper-cpp por velocidad en VPS/Mac
        try:
            res = subprocess.run(["whisper-cpp", "--version"], capture_output=True)
            if res.returncode == 0:
                self.activo = True
                logger.info("✅ Backend whisper-cpp detectado.")
        except:
            # Fallback a openai-whisper (python)
            try:
                import whisper
                self.model = whisper.load_model("tiny")
                self.activo = True
                logger.info("✅ Backend openai-whisper (tiny) cargado.")
            except ImportError:
                logger.warning("⚠️ No se detectó motor de transcripción. Instala: pip install openai-whisper")

    async def transcribir(self, audio_path: str) -> str:
        """Convierte audio a texto. Soporta formatos comunes vía ffmpeg."""
        if not self.activo:
            return "[Error: Motor de escucha no configurado]"

        logger.info(f"👂 Escuchando audio: {audio_path}")
        
        # Si es Telegram (.oga/.ogg), Whisper de Python lo maneja via ffmpeg, 
        # pero whisper-cpp requiere .wav 16khz. Uniformamos:
        wav_path = str(Path(audio_path).with_suffix(".wav"))
        try:
            # Convertir a WAV 16khz mono (requisito estándar de STT ligero)
            subprocess.run([
                "ffmpeg", "-y", "-i", audio_path, 
                "-ar", "16000", "-ac", "1", wav_path
            ], capture_output=True, check=True)
            
            # Transcripción (usando el modelo cargado en memoria)
            import whisper
            result = self.model.transcribe(wav_path, language="es")
            texto = result.get("text", "").strip()
            
            # Limpieza
            if os.path.exists(wav_path): os.remove(wav_path)
            
            logger.info(f"🗣️ Transcripción exitosa: {texto}")
            return texto
        except Exception as e:
            logger.error(f"❌ Fallo en transcripción: {e}")
            return f"[Error en procesamiento de audio: {e}]"

# Singleton
escucha = EscuchaSoberana()

if __name__ == "__main__":
    import asyncio
    # Test manual
    async def test():
        # Requiere un archivo de prueba
        res = await escucha.transcribir("test.raw")
        print(f"Resultado: {res}")
    # asyncio.run(test())
