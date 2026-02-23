# src/clawcore_system/neuronas/cerebro_config.py
"""Configuración del Cerebro Profundo.

Este módulo centraliza la lógica de selección entre:
1️⃣ **API externa** (por defecto, por ejemplo Gemini).
2️⃣ **Cerebro local** (Ollama / llama‑cpp) – opcional y activable por el usuario.

El portal (UI) podrá exponer esta configuración y, si el usuario lo desea,
activar la opción *"Usar cerebro local"* y descargar automáticamente el modelo.
"""

import json
from pathlib import Path
import os

# Ruta del archivo de configuración (se crea si no existe)
CONFIG_PATH = Path(__file__).resolve().parent / "cerebro_config.json"

# Valores por defecto
DEFAULT_CONFIG = {
    "use_local": False,                     # Por defecto se usa la API externa
    "local_endpoint": "http://localhost:11434/api/generate",
    "api_endpoint": "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
    "api_key_env": "GEMINI_API_KEY",      # Variable de entorno con la clave de la API
    "model_local": "llama3.2:3b",          # Modelo que Ollama debe cargar
    "model_api": "gemini-1.5-flash"
}


def _ensure_config_file() -> None:
    """Crea el archivo de configuración con los valores por defecto si no existe."""
    if not CONFIG_PATH.exists():
        CONFIG_PATH.write_text(json.dumps(DEFAULT_CONFIG, indent=4))


def load_config() -> dict:
    """Carga la configuración desde ``cerebro_config.json``.
    Si el archivo no está presente, se crea con los valores por defecto.
    """
    _ensure_config_file()
    try:
        return json.loads(CONFIG_PATH.read_text())
    except Exception as e:
        # En caso de corrupción, restauramos los defaults
        logger = __import__("logging").getLogger("CerebroConfig")
        logger.error(f"Error leyendo config, se restaura a defaults: {e}")
        CONFIG_PATH.write_text(json.dumps(DEFAULT_CONFIG, indent=4))
        return DEFAULT_CONFIG.copy()


def save_config(new_cfg: dict) -> None:
    """Sobrescribe la configuración completa.
    Se valida que sea un diccionario y se mantiene la estructura mínima.
    """
    if not isinstance(new_cfg, dict):
        raise ValueError("Config must be a dict")
    CONFIG_PATH.write_text(json.dumps(new_cfg, indent=4))

# Helper para que el portal pueda togglear la opción fácilmente
def set_use_local(enable: bool) -> None:
    cfg = load_config()
    cfg["use_local"] = enable
    save_config(cfg)

# Helper para actualizar el endpoint local (p.ej. cambiar puerto)
def set_local_endpoint(url: str) -> None:
    cfg = load_config()
    cfg["local_endpoint"] = url
    save_config(cfg)

# Helper para actualizar la clave de API (se guarda en env, no en disco)
def set_api_key(key: str) -> None:
    os.environ[DEFAULT_CONFIG["api_key_env"]] = key

# Exponer la configuración cargada al importar el módulo
CONFIG = load_config()
