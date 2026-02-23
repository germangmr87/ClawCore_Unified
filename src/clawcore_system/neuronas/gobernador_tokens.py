"""
GOBERNADOR DE TOKENS V1.0 — Tokenomics Soberana
Asigna cuotas de tokens por neurona y fuerza el uso de compresión/caché local
antes de gastar recursos en APIs externas.
"""
import json
import logging
import threading
from pathlib import Path

logger = logging.getLogger("GobernadorTokens")
logger.setLevel(logging.INFO)


class GobernadorTokens:
    """Gestiona presupuesto de tokens por neurona."""

    def __init__(self, quota_global: int = 50000, config_path: Path = None):
        self.quota_global = quota_global
        self.uso_global = 0
        self._lock = threading.Lock()
        self.cuotas: dict[str, dict] = {}  # neurona_id -> {quota, usado}
        self.config_path = config_path or Path(__file__).parent / "token_quotas.json"
        self._cargar()

    def _cargar(self):
        if self.config_path.exists():
            try:
                data = json.loads(self.config_path.read_text())
                self.cuotas = data.get("cuotas", {})
                self.uso_global = data.get("uso_global", 0)
                return
            except Exception:
                pass
        self.cuotas = {}
        self.uso_global = 0

    def _guardar(self):
        self.config_path.write_text(json.dumps(
            {"cuotas": self.cuotas, "uso_global": self.uso_global, "quota_global": self.quota_global},
            indent=2))

    def asignar_cuota(self, neurona_id: str, tokens: int = 5000):
        with self._lock:
            self.cuotas[neurona_id] = {"quota": tokens, "usado": self.cuotas.get(neurona_id, {}).get("usado", 0)}
            self._guardar()

    def consumir(self, neurona_id: str, tokens: int) -> bool:
        """Intenta consumir tokens. Devuelve False si se excede la cuota."""
        with self._lock:
            info = self.cuotas.get(neurona_id)
            if not info:
                self.asignar_cuota(neurona_id)
                info = self.cuotas[neurona_id]
            restante = info["quota"] - info["usado"]
            if tokens > restante:
                logger.warning(f"🚫 {neurona_id}: cuota excedida ({info['usado']}/{info['quota']})")
                return False
            info["usado"] += tokens
            self.uso_global += tokens
            self._guardar()
            return True

    def resetear_ciclo(self):
        """Reinicia los contadores de uso (llamar diariamente o por ciclo)."""
        with self._lock:
            for nid in self.cuotas:
                self.cuotas[nid]["usado"] = 0
            self.uso_global = 0
            self._guardar()
            logger.info("♻️ Cuotas de tokens reiniciadas")

    def reporte(self):
        return {"quota_global": self.quota_global, "uso_global": self.uso_global,
                "neuronas": {k: v.copy() for k, v in self.cuotas.items()}}


if __name__ == "__main__":
    gov = GobernadorTokens(quota_global=10000)
    gov.asignar_cuota("NEURONA_RAZONAMIENTO_ES", 3000)
    gov.asignar_cuota("NEURONA_CODIFICACION_ES", 3000)
    print("Consumir 500:", gov.consumir("NEURONA_RAZONAMIENTO_ES", 500))
    print("Consumir 4000:", gov.consumir("NEURONA_RAZONAMIENTO_ES", 4000))
    print(json.dumps(gov.reporte(), indent=2))
