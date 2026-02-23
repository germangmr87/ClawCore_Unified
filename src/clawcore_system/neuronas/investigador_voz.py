import os
import sys
import logging
import asyncio
import subprocess
from pathlib import Path

# --- CONFIGURACIÓN SOBERANA ---
VENV_PATH = Path.home() / "clawcore_voice_env"
MODEL_DIR = Path.home() / ".clawcore/voice_models"
MODEL_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/alvaro/medium/es_ES-alvaro-medium.onnx"
CONFIG_URL = MODEL_URL + ".json"

logger = logging.getLogger("VozInvestigador")

class VozInvestigador:
    """
    INVESTIGADOR DE VOZ LOCAL Ω.1
    Busca, instala y testea motores TTS de alta fidelidad sin APIs externas.
    """
    def __init__(self):
        MODEL_DIR.mkdir(exist_ok=True, parents=True)

    async def preparar_entorno(self):
        """Crea un entorno aislado para evitar ensuciar el sistema base."""
        if not VENV_PATH.exists():
            logger.info("🛠️ Creando entorno neural para voz local...")
            subprocess.run([sys.executable, "-m", "venv", str(VENV_PATH)], check=True)
            # Instalar dependencias necesarias
            pip = str(VENV_PATH / "bin/pip")
            subprocess.run([pip, "install", "piper-tts", "onnxruntime"], check=True)
        return True

    async def descargar_modelo_fidelidad(self):
        """Descarga modelos de alta densidad técnica (VITS/Piper)."""
        onnx_path = MODEL_DIR / "es_ES-alvaro-medium.onnx"
        json_path = MODEL_DIR / "es_ES-alvaro-medium.onnx.json"
        
        if not onnx_path.exists():
            logger.info("📡 Descargando modelo de voz neuronal (VITS)...")
            subprocess.run(["curl", "-L", MODEL_URL, "-o", str(onnx_path)], check=True)
            subprocess.run(["curl", "-L", CONFIG_URL, "-o", str(json_path)], check=True)
        return str(onnx_path)

    async def test_seguridad_codigo(self, script_content: str):
        """Audita scripts de terceros antes de ejecutarlos."""
        forbidden = ["eval(", "os.system(", "subprocess.Popen(", "requests.get("]
        for f in forbidden:
            if f in script_content:
                return False, f"Patrón inseguro detectado: {f}"
        return True, "Seguro"

# Singleton
investigador_voz = VozInvestigador()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    async def run():
        await investigador_voz.preparar_entorno()
        path = await investigador_voz.descargar_modelo_fidelidad()
        print(f"✅ Motor de voz local listo en: {path}")
    asyncio.run(run())
