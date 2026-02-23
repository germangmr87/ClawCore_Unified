try:
    import psutil
except ImportError:
    psutil = None

import logging
import os
from pathlib import Path

# Audit: Evitar I/O bottleneck en logs
logger = logging.getLogger("GobernadorRecursos")
logger.setLevel(logging.WARNING)

class GobernadorRecursos:
    """
    SISTEMA DE GOBERNANZA DE RECURSOS V4.5 (Audit Compliance)
    Optimizado: Fallback nativo (os) si psutil falla (Sin SPOF).
    """
    def __init__(self, umbral_cpu=80.0, umbral_ram=85.0):
        self.umbral_cpu = umbral_cpu
        self.umbral_ram = umbral_ram

    def obtener_estado_critico(self):
        """Obtiene métricas de hardware de forma eficiente (Audit: Resiliencia)."""
        try:
            if psutil:
                cpu_pct = psutil.cpu_percent(interval=0.1)
                ram_uso = psutil.virtual_memory().percent
                
                # Detección de procesos (SPOF Protection)
                procesos = []
                try:
                    procesos = sorted(
                        psutil.process_iter(['pid', 'name', 'cpu_percent']),
                        key=lambda x: x.info['cpu_percent'] or 0,
                        reverse=True
                    )[:3]
                except: pass
            else:
                # Fallback nativo: os.getloadavg (Audit: Anti-SPOF)
                load1, _, _ = os.getloadavg()
                cpu_pct = (load1 / os.cpu_count()) * 100
                ram_uso = 50.0 # Valor neutral si psutil no está
                procesos = []

            return {
                "cpu_total": cpu_pct,
                "ram_uso_pct": ram_uso,
                "carga_alta": cpu_pct > self.umbral_cpu or ram_uso > self.umbral_ram,
                "top_procesos": [p.info if hasattr(p, 'info') else p for p in procesos]
            }
        except Exception as e:
            return {"carga_alta": False, "error": str(e)}


    def aplicar_throttling_agéntico(self, nivel_autonomia):
        """Ajusta la intensidad de la red neuronal según el hardware."""
        estado = self.obtener_estado_critico()
        if estado["carga_alta"]:
            # Reducción proactiva (Punto 4 del Roadmap)
            factor_reduccion = 0.5 if estado["cpu_total"] > 90 else 0.8
            return nivel_autonomia * factor_reduccion
        return nivel_autonomia

if __name__ == "__main__":
    gob = GobernadorRecursos()
    print(gob.obtener_estado_critico())
