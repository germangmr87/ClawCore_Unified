import os
import ast
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DescubridorHerramientas")

class DescubridorHerramientas:
    """
    PUNTO 1: DESCUBRIMIENTO AUTÓNOMO DE HERRAMIENTAS
    Escanea el proyecto en busca de scripts, funciones y capacidades
    para que las neuronas sepan 'qué pueden hacer'.
    """
    def __init__(self, root_path):
        self.root = Path(root_path).resolve()
        # Seguridad: El root debe existir y ser parte del workspace (Audit: Seguridad)
        if not self.root.exists():
            raise ValueError(f"Root path {root_path} no existe.")
        self.mapa_capacidades = {}

    def _es_ruta_segura(self, file_path):
        """Verifica que la ruta esté dentro del perímetro (Anti-Traversal)."""
        try:
            return Path(file_path).resolve().relative_to(self.root)
        except ValueError:
            return None


    def escanear_proyecto(self):
        """Escanea el proyecto buscando funciones anotadas o herramientas ejecutables."""
        logger.info("🔍 Iniciando descubrimiento autónomo de herramientas...")
        
        for p in self.root.rglob("*.py"):
            # Evitar bibliotecas externas y carpetas ocultas
            if "node_modules" in str(p) or p.name.startswith("."):
                continue
                
            self._analizar_archivo(p)
            
        logger.info(f"✅ Escaneo completado. {len(self.mapa_capacidades)} herramientas descubiertas.")
        return self.mapa_capacidades

    def _analizar_archivo(self, file_path):
        """Analiza un archivo Python para extraer funciones y clases."""
        rel_path = self._es_ruta_segura(file_path)
        if not rel_path:
            logger.warning(f"⚠️ Intento de acceso fuera de perímetro: {file_path}")
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())

                
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Guardamos la capacidad si tiene un docstring o nombre descriptivo
                    doc = ast.get_docstring(node)
                    if doc or node.name.startswith("tool_") or node.name.startswith("cmd_"):
                        rel_path = os.path.relpath(file_path, self.root)
                        self.mapa_capacidades[node.name] = {
                            "path": rel_path,
                            "tipo": "funcion",
                            "descripcion": doc or "Sin descripción (Heurística)",
                            "async": isinstance(node, ast.AsyncFunctionDef)
                        }
        except Exception as e:
            # Fallo silencioso para archivos corruptos o no-python
            pass

    def obtener_herramientas_para_tarea(self, tarea):
        """Busca herramientas en el mapa basándose en la intención de la tarea."""
        palabras_clave = tarea.lower().split()
        coincidencias = []
        
        for nombre, info in self.mapa_capacidades.items():
            score = 0
            for palabra in palabras_clave:
                if palabra in nombre.lower() or palabra in info["descripcion"].lower():
                    score += 1
            if score > 0:
                coincidencias.append({"herramienta": nombre, "score": score, **info})
                
        return sorted(coincidencias, key=lambda x: x["score"], reverse=True)

if __name__ == "__main__":
    descubridor = DescubridorHerramientas("/Users/german/Documents/GitHub/ClawCore_Unified")
    mapa = descubridor.escanear_proyecto()
    for k, v in list(mapa.items())[:5]:
        print(f"Capacidad: {k} -> {v['path']}")
