"""
PROTOCOLO SINIESTRO V1.0 — Gestión de Pánico y Rescate Soberano
Evita bloqueos totales (lockdowns) permitiendo una vía de rescate cifrada.
"""
import logging
import json
import hashlib
from pathlib import Path

logger = logging.getLogger("ProtocoloSiniestro")

class ProtocoloSiniestro:
    def __init__(self, admin_key_hash: str):
        # El hash de una clave maestra que solo tú conoces.
        self.admin_key_hash = admin_key_hash
        self.estado_panico = False
        self.archivo_estado = Path(__file__).parent / "panic_state.json"

    def activar_panico(self, razon: str):
        """Entra en modo de defensa pero mantiene el portal de rescate."""
        self.estado_panico = True
        logger.critical(f"🚨 MODO PÁNICO ACTIVADO: {razon}")
        self._persistir_estado({"estado": "PANIC", "razon": razon, "lockdown_p2p": True})
        # Aquí se daría la orden al firewall de cerrar todo EXCEPTO la IP del Admin.

    def intentar_rescate(self, key_plana: str) -> bool:
        """Permite al admin recuperar el control."""
        if hashlib.sha256(key_plana.encode()).hexdigest() == self.admin_key_hash:
            self.estado_panico = False
            self._persistir_estado({"estado": "RESCUED", "razon": "Intervención Humana"})
            logger.info("🔱 SISTEMA RESCATADO: Control devuelto al soberano.")
            return True
        return False

    def _persistir_estado(self, data: dict):
        self.archivo_estado.write_text(json.dumps(data, indent=2))

# Ejemplo de uso preventivo
# admin_hash = sha256("MiClaveMaestra")
rescue = ProtocoloSiniestro("8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918") 
