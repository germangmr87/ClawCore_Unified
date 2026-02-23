import ast
import logging
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Dict

logger = logging.getLogger("TestGeneratorNeuron")
logger.setLevel(logging.INFO)


class TestGeneratorNeuron:
    """Neurona que genera y ejecuta tests unitarios antes de aplicar cambios.
    Utiliza `pytest` en un entorno temporal para validar la corrección del código.
    """

    def __init__(self, test_dir: Path = Path("/tmp/clawcore_tests")):
        self.test_dir = test_dir
        self.test_dir.mkdir(parents=True, exist_ok=True)

    def _extraer_funciones(self, source: str) -> List[str]:
        """Devuelve los nombres de las funciones definidas en `source`."""
        try:
            tree = ast.parse(source)
            return [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        except Exception as e:
            logger.error(f"Error parseando código para test: {e}")
            return []

    def generar_test(self, module_path: Path) -> Path:
        """Crea un archivo de test básico para todas las funciones del módulo.
        El test simplemente verifica que la función se pueda importar sin errores.
        """
        src = module_path.read_text()
        funciones = self._extraer_funciones(src)
        test_name = f"test_{module_path.stem}.py"
        test_path = self.test_dir / test_name
        with test_path.open("w") as f:
            f.write("import pytest\n")
            f.write(f"import {module_path.stem}\n\n")
            for fn in funciones:
                f.write(f"def test_{fn}_importable():\n    assert hasattr({module_path.stem}, '{fn}')\n\n")
        logger.info(f"Test generado: {test_path}")
        return test_path

    def ejecutar_test(self, test_path: Path) -> bool:
        """Ejecuta pytest sobre el archivo de test y devuelve True si pasa.
        Se ejecuta en un proceso aislado para evitar contaminación del entorno.
        """
        cmd = [sys.executable, "-m", "pytest", str(test_path), "-q"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                logger.info(f"Test {test_path.name} PASADO")
                return True
            else:
                logger.warning(f"Test {test_path.name} FALLÓ: {result.stdout}\n{result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error ejecutando test: {e}")
            return False

    def validar_cambio(self, module_path: Path) -> bool:
        """Genera y ejecuta el test; devuelve True si el módulo pasa la validación.
        Este método será llamado por la neurona de refactorización antes de aplicar cambios.
        """
        test_file = self.generar_test(module_path)
        return self.ejecutar_test(test_file)
