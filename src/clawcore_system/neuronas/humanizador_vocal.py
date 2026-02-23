import os
import logging
import random
from pathlib import Path

# Intentar importar pydub para procesamiento de audio (requiere ffmpeg)
try:
    from pydub import AudioSegment
    from pydub.generators import WhiteNoise
except ImportError:
    AudioSegment = None

logger = logging.getLogger("HumanizadorVocal")

class HumanizadorVocal:
    """
    NEURONA DE HUMANIZACIÓN Ω.1
    Añade imperfecciones orgánicas, pausas y ruido de confort al audio sintético.
    """
    def __init__(self):
        self.output_dir = Path.home() / ".clawcore/vocal_mastered"
        self.output_dir.mkdir(exist_ok=True, parents=True)

    def procesar(self, input_path: str):
        if not AudioSegment:
            logger.warning("⚠️ pydub no instalado. Devolviendo audio original.")
            return input_path

        try:
            audio = AudioSegment.from_file(input_path)
            
            # 1. Añadir Ruido de Confort (Casi inaudible)
            noise = WhiteNoise().to_audio_segment(duration=len(audio), volume=-50) # Muy suave
            audio = audio.overlay(noise)
            
            # 2. Ecualización de Calor (Potenciar medios-bajos)
            audio = audio.low_pass_filter(4000) # Suavizar agudos quirúrgicos
            
            # 3. Micro-pausa inicial orgánica
            silence = AudioSegment.silent(duration=random.randint(100, 300))
            audio = silence + audio
            
            output_path = self.output_dir / f"master_{os.path.basename(input_path)}"
            audio.export(str(output_path), format="wav")
            
            logger.info(f"✨ Audio humanizado y masterizado: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"❌ Error en humanización: {e}")
            return input_path

# Singleton
humanizador = HumanizadorVocal()
