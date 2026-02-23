"""
INTEGRIDAD V1.0 — Auditoría de archivos en tiempo real (Anti-Drift)
Calcula SHA-256 de cada .py bajo src/ y detecta cambios no autorizados.
"""
import hashlib
import json
import logging
import threading
import time
from pathlib import Path

logger = logging.getLogger("Integridad")
logger.setLevel(logging.INFO)


class MonitorIntegridad:
    """Huellas digitales de archivos con detección de drift."""

    def __init__(self, root: Path, interval: int = 60):
        self.root = root
        self.interval = interval
        self.hashes: dict[str, str] = {}
        self.alertas: list[dict] = []
        self._running = False
        self._thread = None

    def _hash_file(self, fp: Path) -> str:
        h = hashlib.sha256()
        h.update(fp.read_bytes())
        return h.hexdigest()

    def snapshot(self) -> dict[str, str]:
        result = {}
        for py in self.root.rglob("*.py"):
            try:
                rel = str(py.relative_to(self.root))
                result[rel] = self._hash_file(py)
            except Exception:
                pass
        return result

    def verificar(self) -> list[dict]:
        current = self.snapshot()
        cambios = []
        for path_str, old_hash in self.hashes.items():
            new_hash = current.get(path_str)
            if new_hash is None:
                cambios.append({"archivo": path_str, "tipo": "ELIMINADO"})
            elif new_hash != old_hash:
                cambios.append({"archivo": path_str, "tipo": "MODIFICADO", "hash_prev": old_hash[:12], "hash_new": new_hash[:12]})
        for path_str in current:
            if path_str not in self.hashes:
                cambios.append({"archivo": path_str, "tipo": "NUEVO"})
        self.hashes = current
        return cambios

    def iniciar(self):
        self.hashes = self.snapshot()
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        logger.info(f"🔐 Monitor de integridad activo ({len(self.hashes)} archivos)")

    def detener(self):
        self._running = False

    def _loop(self):
        while self._running:
            time.sleep(self.interval)
            cambios = self.verificar()
            if cambios:
                self.alertas.extend(cambios)
                for c in cambios:
                    logger.warning(f"⚠️ DRIFT: {c['tipo']} → {c['archivo']}")

    def reporte(self):
        return {"archivos_monitoreados": len(self.hashes), "alertas_pendientes": len(self.alertas),
                "ultimas_alertas": self.alertas[-5:]}


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent.parent
    mon = MonitorIntegridad(root)
    snap = mon.snapshot()
    print(f"🔐 {len(snap)} archivos hasheados")
    print(json.dumps(list(snap.items())[:5], indent=2))
