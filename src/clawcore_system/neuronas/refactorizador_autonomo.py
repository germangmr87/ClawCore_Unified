import ast
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RefactorizadorAutonomo")

class RefactorizadorAutonomo:
    """
    PUNTO 5: EVOLUCIÓN DEL CÓDIGO FUENTE (Self-Refactoring)
    Analiza el código propio en busca de ineficiencias y propone mejoras.
    """
    def __init__(self, root_path):
        self.root = Path(root_path)

    def analizar_eficiencia(self, file_path):
        """Analiza un archivo en busca de patrones refactorizables."""
        refactorizaciones = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                tree = ast.parse(content)
            
            for node in ast.walk(tree):
                # Pattern 1: Funciones demasiado largas
                if isinstance(node, ast.FunctionDef):
                    lines = node.end_lineno - node.lineno
                    if lines > 50:
                        refactorizaciones.append({
                            "linea": node.lineno,
                            "tipo": "COMPLEJIDAD",
                            "msj": f"Función '{node.name}' demasiado larga ({lines} líneas). Sugerencia: Modularizar."
                        })
                
                # Pattern 2: Falta de docstrings (Punto 1: Tool Discovery mejorado)
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if not ast.get_docstring(node):
                        refactorizaciones.append({
                            "linea": node.lineno,
                            "tipo": "DOCUMENTACION",
                            "msj": f"Elemento '{node.name}' sin docstring. Dificulta el Tool Discovery."
                        })
                        
            # Validar con pruebas automáticas antes de aceptar refactorizaciones
            from src.clawcore_system.neuronas.test_generator import TestGeneratorNeuron
            tester = TestGeneratorNeuron()
            if not tester.validar_cambio(Path(file_path)):
                logger.warning(f"⚠️ Cambios en {file_path} no pasan pruebas automáticas. Se descartan.")
                return []
            return refactorizaciones
        except:
            return []

    async def proponer_mejoras_globales(self):
        """Escanea el núcleo en busca de mejoras y usa el Kernel para refinar soluciones."""
        from src.clawcore_system.neuronas.gobernanza_soberana import gobernanza
        logger.info("🛠️ Iniciando ciclo de Auto-Refactorización interna (Capa de Músculo)...")
        hallazgos = {}
        
        for p in self.root.rglob("src/clawcore_system/neuronas/*.py"):
            principios = self.analizar_eficiencia(p)
            if principios:
                from src.clawcore_system.neuronas.kernel_soberano import kernel
                if kernel.evolucion_activa:
                    prompt = f"Actúa como Arquitecto. Refactoriza este archivo para máxima densidad técnica: {p.read_text()}"
                    propuesta = await kernel.pensar(prompt)
                    
                    # FILTRO DE GOBERNANZA: Validar antes de considerar
                    if gobernanza.validar_propuesta(str(p), propuesta):
                        hallazgos[str(p)] = {
                            "problemas": principios,
                            "solucion_propuesta": propuesta,
                            "manifiesto": gobernanza.generar_manifiesto(f"Refactorización de {p.name}")
                        }
        return hallazgos


if __name__ == "__main__":
    import asyncio
    async def run_test():
        ref = RefactorizadorAutonomo(".")
        mejoras = await ref.proponer_mejoras_globales()
        for f, m in mejoras.items():
            print(f"\nArchivo: {f}")
            print(f"  Propuesta: {m['solucion_propuesta'][:100]}...")
            
    asyncio.run(run_test())
