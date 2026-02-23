"""
SIMULADOR DE DECISIONES SOBERANAS V1.0
Evalúa el impacto de las decisiones agénticas antes de su ejecución.
Previene el 'pánico' bloqueando acciones que dejen fuera al administrador.
"""
import logging
import json
from enum import Enum
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("SimuladorDecisiones")

class NivelRiesgo(Enum):
    BAJO = 1
    MEDIO = 2
    ALTO = 3
    CRITICO = 4  # Acciones que pueden bloquear el acceso al servidor

class DecisionPropuesta:
    def __init__(self, id, accion, razon, riesgo: NivelRiesgo):
        self.id = id
        self.accion = accion
        self.razon = razon
        self.riesgo = riesgo
        self.timestamp = datetime.now()
        self.estado = "PENDIENTE" # PENDIENTE, APROBADA, RECHAZADA, EJECUTADA

class SimuladorDecisiones:
    def __init__(self):
        self.historial_simulaciones = []
        self.decisiones_pendientes = {}
        self.archivo_pendientes = Path(__file__).parent / "decisiones_pendientes.json"
        self._cargar_pendientes()

    def _cargar_pendientes(self):
        if self.archivo_pendientes.exists():
            try:
                data = json.loads(self.archivo_pendientes.read_text())
                for d_id, d in data.items():
                    self.decisiones_pendientes[d_id] = d
            except: pass

    def evaluar_accion(self, neurona: str, accion: str, contexto: dict) -> dict:
        """
        Analiza una acción propuesta y determina si es segura para ejecución autónoma.
        """
        riesgo = NivelRiesgo.BAJO
        mensaje_alerta = ""
        requiere_aprobacion = False

        # Heurísticas de riesgo crítico (Evitar Pánico de Servidor)
        palabras_criticas = ["iptables", "ufw", "block", "shutdown", "restrict", "close port 22", "lockdown"]
        
        if any(p in accion.lower() for p in palabras_criticas):
            riesgo = NivelRiesgo.CRITICO
            mensaje_alerta = "⚠️ ACCIÓN CRÍTICA: Esta decisión puede bloquear tu acceso al servidor."
            requiere_aprobacion = True

        elif "delete" in accion.lower() or "rm " in accion.lower():
            riesgo = NivelRiesgo.ALTO
            mensaje_alerta = "Destrucción de datos detectada."
            requiere_aprobacion = True

        res = {
            "neurona": neurona,
            "accion": accion,
            "riesgo": riesgo.name,
            "alerta": mensaje_alerta,
            "requiere_humano": requiere_aprobacion,
            "timestamp": datetime.now().isoformat()
        }

        if requiere_aprobacion:
            d_id = f"DEC-{int(datetime.now().timestamp())}"
            self.decisiones_pendientes[d_id] = res
            self._guardar_pendientes()
            return {**res, "decision_id": d_id}

        return res

    def _guardar_pendientes(self):
        self.archivo_pendientes.write_text(json.dumps(self.decisiones_pendientes, indent=2))

    def resolver_decision(self, d_id, aprobada: bool):
        if d_id in self.decisiones_pendientes:
            decision = self.decisiones_pendientes.pop(d_id)
            self._guardar_pendientes()
            logger.info(f"🔱 Decisión {d_id} {'APROBADA' if aprobada else 'RECHAZADA'} por el Soberano.")
            return True
        return False

# Singleton
simulador = SimuladorDecisiones()

if __name__ == "__main__":
    # Test de simulación de pánico
    pánico = simulador.evaluar_accion("SEGURIDAD_ES", "Aplicar iptables -P INPUT DROP para detener ataque", {"ip": "unknown"})
    print(json.dumps(pánico, indent=4))
