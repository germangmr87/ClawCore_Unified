import importlib
import sys
import os
import logging
from pathlib import Path

logger = logging.getLogger("HotSwapManager")

class HotSwapManager:
    """
    SISTEMA DE MIGRACIÓN INVISIBLE (Ω.Shadow)
    Permite recargar neuronas en caliente sin detener el Kernel.
    """
    def __init__(self, root_path):
        self.root = Path(root_path)
        self.registry = {} # Módulos cargados

    def recargar_neurona(self, module_name: str):
        """Re-inyecta una neurona en el espacio de nombres de ejecución."""
        try:
            if module_name in sys.modules:
                # 1. Detectar el módulo en el sistema
                module = sys.modules[module_name]
                # 2. Recargar físicamente el archivo del disco
                importlib.reload(module)
                logger.info(f"♻️ NEURONA RECARGADA: {module_name} ha migrado a la nueva versión en caliente.")
                return True
            else:
                # 3. Si no existe, lo carga por primera vez
                self.registry[module_name] = importlib.import_module(module_name)
                logger.info(f"🧬 NEURONA CARGADA: {module_name} integrada al sistema.")
                return True
        except Exception as e:
            logger.error(f"❌ FALLO EN MIGRACIÓN CALIENTE ({module_name}): {e}")
            return False

    def monitorizar_cambios(self, monitor_integridad):
        """Analiza el drift de integridad y dispara recargas automáticas."""
        cambios = monitor_integridad.verificar()
        for cambio in cambios:
            if cambio["tipo"] == "MODIFICADO" and cambio["archivo"].endswith(".py"):
                # Convertir ruta a formato de módulo python
                rel_path = os.path.relpath(cambio["archivo"], os.getcwd())
                mod_path = rel_path.replace(".py", "").replace("/", ".")
                logger.warning(f"⚠️ Detectado cambio en {cambio['archivo']}. Iniciando Hot-Swap de {mod_path}...")
                self.recargar_neurona(mod_path)

# Instancia global para el Kernel
hotswap = HotSwapManager(os.getcwd())
