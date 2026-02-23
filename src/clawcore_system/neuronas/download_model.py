"""Script auxiliar: descarga el modelo configurado vía Ollama."""
import subprocess
import json
from pathlib import Path

CFG = Path(__file__).parent / "cerebro_config.json"

def descargar():
    cfg = json.loads(CFG.read_text()) if CFG.exists() else {}
    modelo = cfg.get("model_local", "llama3.2:3b")
    print(f"📥 Descargando modelo: {modelo}")
    try:
        subprocess.run(["ollama", "pull", modelo], check=True)
        print(f"✅ Modelo {modelo} listo.")
    except FileNotFoundError:
        print("❌ Ollama no está instalado. Instálalo desde https://ollama.ai")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error descargando {modelo}: {e}")

if __name__ == "__main__":
    descargar()
