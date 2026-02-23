import hashlib
import logging
import os
from pathlib import Path

logger = logging.getLogger("GobernanzaSoberana")

class GobernanzaSoberana:
    """
    EL ANCLA INMUTABLE (Freno de Mano Ω.1)
    Asegura que la evolución nunca comprometa la autoridad del humano.
    """
    def __init__(self):
        self.signature_file = Path.home() / ".clawcore/.master_anchor"
        self.locked_files = [
            "src/clawcore_system/neuronas/kernel_soberano.py", # El interruptor vive aquí
            "src/clawcore_system/neuronas/interface_telegram.py", # Comunicación vital
            "src/clawcore_system/neuronas/gobernanza_soberana.py"  # Auto-protección
        ]
        self._ensure_anchor()

    def _ensure_anchor(self):
        """Crea el ancla de identidad si no existe."""
        if not self.signature_file.exists():
            self.signature_file.parent.mkdir(exist_ok=True, parents=True)
            # El ancla es una firma de la autoridad de Gabriel
            self.signature_file.write_text("AUTHORITY_ROOT:GABRIEL_SOVEREIGN_SIGNATURE_2026")
            os.chmod(self.signature_file, 0o400) # Solo lectura

    def validar_propuesta(self, file_path: str, proposed_code: str) -> bool:
        """Audita una propuesta de evolución antes de permitir su escritura."""
        # 1. Bloqueo de archivos núcleo
        for locked in self.locked_files:
            if locked in file_path:
                logger.error(f"🚨 INTENTO DE REVELIÓN: El sistema intentó modificar {locked}")
                return False

        # 2. Análisis de Alineación (Simple Keyword Audit)
        forbidden_patterns = ["evolucion_activa = True", "self.evolucion_activa = True", "os.remove", "chmod 777"]
        for pattern in forbidden_patterns:
            if pattern in proposed_code:
                logger.error(f"🚨 VIOLACIÓN DE ALINEACIÓN: Código prohibido detectado en propuesta para {file_path}")
                return False

        # 3. Verificación de Ancla
        if not self.signature_file.exists():
             logger.critical("🚨 ALERTA: Ancla de Identidad destruida. Bloqueo total del Kernel.")
             return False

        return True

    def generar_manifiesto(self, mejora_desc: str):
        """Exige una justificación humana para cada cambio."""
        return f"[MANIFIESTO_Ω.1] Mejora propuesta por eficiencia: {mejora_desc}. Objetivo: Optimizar ROI para Gabriel."

# Singleton
gobernanza = GobernanzaSoberana()
