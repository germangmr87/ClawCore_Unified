"""
GESTOR DE OBJETIVOS SOBERANOS V1.0
Permite que el Kernel defina y persiga metas a largo plazo de forma proactiva.
"""
import json
import time
from pathlib import Path
from datetime import datetime

class ObjetivoSoberano:
    def __init__(self, id, descripcion, prioridad=1):
        self.id = id
        self.descripcion = descripcion
        self.prioridad = prioridad
        self.creado = datetime.now()
        self.estado = "PENDIENTE" # PENDIENTE, EJECUTANDO, COMPLETADO, FALLIDO
        self.progreso = 0
        self.logs = []

    def log(self, msj):
        self.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msj}")

class GestorObjetivos:
    def __init__(self):
        self.objetivos = {}
        self.archivo_persist = Path(__file__).parent / "objetivos_soberanos.json"
        self._cargar()

    def _cargar(self):
        if self.archivo_persist.exists():
            try:
                data = json.loads(self.archivo_persist.read_text())
                for oid, obj in data.items():
                    o = ObjetivoSoberano(oid, obj['descripcion'], obj['prioridad'])
                    o.estado = obj['estado']
                    o.progreso = obj['progreso']
                    o.logs = obj['logs']
                    self.objetivos[oid] = o
            except: pass

    def guardar(self):
        data = {oid: {
            "descripcion": o.descripcion,
            "prioridad": o.prioridad,
            "estado": o.estado,
            "progreso": o.progreso,
            "logs": o.logs
        } for oid, o in self.objetivos.items()}
        self.archivo_persist.write_text(json.dumps(data, indent=2))

    def crear_objetivo(self, id, descripcion, prioridad=1):
        if id not in self.objetivos:
            self.objetivos[id] = ObjetivoSoberano(id, descripcion, prioridad)
            self.guardar()
            return self.objetivos[id]
        return self.objetivos[id]

    def obtener_pendientes(self):
        return [o for o in self.objetivos.values() if o.estado in ["PENDIENTE", "FALLIDO"]]

if __name__ == "__main__":
    gestor = GestorObjetivos()
    o = gestor.crear_objetivo("MAINTENANCE_IDLE", "Refactorizar módulos lentos durante la noche", 2)
    o.log("Objetivo inicializado por el Kernel.")
    gestor.guardar()
    print(f"Objetivo proactivo creado: {o.descripcion}")
