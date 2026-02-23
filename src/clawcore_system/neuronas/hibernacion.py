"""
CONTINUIDAD SINIESTRA V1.0 — Hibernación y Restauración de Contexto
Serializa la pila de pensamientos antes de un reinicio y la restaura al despertar.
"""
import json
import logging
import time
from pathlib import Path
from datetime import datetime

logger = logging.getLogger("Hibernacion")
logger.setLevel(logging.INFO)

HIBERNATE_PATH = Path.home() / ".clawcore" / "hibernate_state.json"


class GestorHibernacion:
    """Guarda y restaura el estado cognitivo del sistema."""

    def __init__(self, state_path: Path = HIBERNATE_PATH):
        self.state_path = state_path
        self.state_path.parent.mkdir(parents=True, exist_ok=True)

    def hibernar(self, contexto: dict) -> bool:
        """Serializa el estado actual antes de un apagado."""
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "version": "4.5.1",
            "tarea_activa": contexto.get("tarea_activa", "ninguna"),
            "progreso": contexto.get("progreso", 0),
            "neuronas_estado": contexto.get("neuronas_estado", {}),
            "nivel_autonomia": contexto.get("nivel_autonomia", 0.35),
            "pila_pensamientos": contexto.get("pila_pensamientos", []),
            "tokens_consumidos": contexto.get("tokens_consumidos", 0),
            "vibe_score": contexto.get("vibe_score", 0.5)
        }
        try:
            self.state_path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False))
            logger.info(f"💤 Estado hibernado en {self.state_path}")
            return True
        except Exception as e:
            logger.error(f"Error hibernando: {e}")
            return False

    def despertar(self) -> dict:
        """Restaura el estado previo al reinicio."""
        if not self.state_path.exists():
            logger.info("🌅 Sin estado previo. Inicio limpio.")
            return {"estado": "inicio_limpio"}
        try:
            data = json.loads(self.state_path.read_text())
            tarea = data.get("tarea_activa", "ninguna")
            progreso = data.get("progreso", 0)
            ts = data.get("timestamp", "?")
            logger.info(f"🔄 Restaurando estado: tarea='{tarea}' progreso={progreso}% desde {ts}")
            return data
        except Exception as e:
            logger.error(f"Error restaurando: {e}")
            return {"estado": "error_restauracion", "detalle": str(e)}

    def limpiar(self):
        """Elimina el archivo de hibernación tras restauración exitosa."""
        if self.state_path.exists():
            self.state_path.unlink()
            logger.info("🧹 Estado de hibernación limpiado.")

    def hay_estado_previo(self) -> bool:
        return self.state_path.exists()


if __name__ == "__main__":
    gestor = GestorHibernacion()

    # Simular hibernación
    ctx = {
        "tarea_activa": "Optimizar sistema de seguridad",
        "progreso": 40,
        "nivel_autonomia": 0.42,
        "pila_pensamientos": [
            "Analizando patrones de ataque",
            "Generando reglas de firewall",
            "Pendiente: validar con tests"
        ],
        "vibe_score": 0.78
    }
    gestor.hibernar(ctx)

    # Simular despertar
    restored = gestor.despertar()
    if restored.get("tarea_activa"):
        print(f"🔄 Continuando con: {restored['tarea_activa']} ({restored['progreso']}%)")
        print(f"   Pila: {restored['pila_pensamientos']}")
    gestor.limpiar()
