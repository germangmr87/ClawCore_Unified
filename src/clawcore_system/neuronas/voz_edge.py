import asyncio
import os
import edge_tts
import logging
from pathlib import Path

logger = logging.getLogger("VozSoberana")

class VozSoberana:
    """
    MOTOR DE VOZ Ω.1 (Edge-TTS Integration)
    Proporciona salida de audio fluida para la malla.
    """
    def __init__(self):
        self.voice = "es-ES-AlvaroNeural" # Voz masculina, técnica y clara
        self.output_dir = Path.home() / ".clawcore/audio_out"
        self.output_dir.mkdir(exist_ok=True, parents=True)

    async def sintetizar(self, texto: str, filename: str = "vocal_output.mp3"):
        """Convierte texto a audio con baja latencia."""
        path = self.output_dir / filename
        communicate = edge_tts.Communicate(texto, self.voice)
        await communicate.save(str(path))
        logger.info(f"🔊 Audio sintetizado con éxito: {path}")
        return str(path)

# Singleton
motor_voz = VozSoberana()

if __name__ == "__main__":
    # Test rápido
    async def test():
        path = await motor_voz.sintetizar("🔱 Sistemas de voz ClawCore Ω.1 activos. ¿Cuál es la directiva, Gabriel?")
        print(f"Test completado: {path}")
    asyncio.run(test())
