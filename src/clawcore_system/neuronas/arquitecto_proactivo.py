"""
ARQUITECTO PROACTIVO Ω.1 (Capacidad Antigravity)
Diseña y construye mejoras estructurales de forma autónoma.
"""

import os
import logging
from pathlib import Path
import asyncio

# Conexiones internas
from src.clawcore_system.neuronas.kernel_soberano import kernel
from src.clawcore_system.neuronas.gobernanza_soberana import gobernanza
from src.clawcore_system.neuronas.test_generator import TestGeneratorNeuron
from src.clawcore_system.neuronas.hot_swap_manager import hotswap

logger = logging.getLogger("ArquitectoProactivo")
logger.setLevel(logging.INFO)

class ArquitectoProactivo:
    def __init__(self, root_path):
        self.root = Path(root_path)
        self.tester = TestGeneratorNeuron()
        self.active_tasks = []

    async def ciclo_evolucion(self):
        """Ciclo principal de desarrollo proactivo."""
        logger.info("👨‍💻 Arquitecto Proactivo iniciando guardia de desarrollo...")
        
        # 1. Escaneo de Oportunidades (Technical Debt & Feature Gaps)
        puntos_mejora = self._escanear_sistema()
        
        for punto in puntos_mejora:
            # 2. Planificación (Usando el Kernel como cerebro arquitecto)
            plan = await self._planificar_mejora(punto)
            
            # 3. Propuesta de Código
            if plan and "propuesta" in plan:
                if gobernanza.validar_propuesta(punto, plan["propuesta"]):
                    # 4. Verificación Rigurosa (Tests antes de aplicar)
                    temp_file = self.root / f"temp_{os.path.basename(punto)}"
                    temp_file.write_text(plan["propuesta"])
                    
                    if self.tester.validar_cambio(temp_file):
                        logger.info(f"✨ Mejora verificada para {punto}. Aplicando evolución...")
                        # 5. Aplicación y Hot-Swap
                        Path(punto).write_text(plan["propuesta"])
                        temp_file.unlink()
                        
                        # Notificar al Kernel para recargar el módulo
                        mod_name = punto.replace(".py", "").replace("/", ".")
                        hotswap.recargar_neurona(mod_name)
                    else:
                        logger.warning(f"⚠️ Propuesta falló tests en {punto}. Abortando evolución.")
                        if temp_file.exists(): temp_file.unlink()

    def _escanear_sistema(self):
        """Identifica archivos con baja densidad técnica o falta de modularidad."""
        objetivos = []
        for p in self.root.rglob("src/clawcore_system/neuronas/*.py"):
            with open(p, "r") as f:
                content = f.read()
                # El criterio: funciones largas o falta de tipos/docstrings
                if "def" in content and (len(content.split("\n")) > 100 or "typing" not in content):
                    objetivos.append(str(p))
        return objetivos[:2] # Máximo 2 por ciclo para evitar caos

    async def _planificar_mejora(self, file_path):
        """Usa el Kernel para generar un código que sea 'Arquitectura de Vanguardia'."""
        with open(file_path, "r") as f:
            source = f.read()
            
        prompt = f"""
        ACTÚA COMO UN DESARROLLADOR AGÉNTICO SENIOR (ANTIGRAVITY).
        Analiza este código y reescríbelo para:
        1. Máxima eficiencia (low latency).
        2. Escalabilidad modular.
        3. Seguridad nativa y tipado estático funcional.
        4. Autonomía proactiva.
        
        ARCHIVO: {file_path}
        CÓDIGO ACTUAL:
        {source}
        
        Responde SOLO con el código completo refactorizado.
        """
        
        logger.info(f"🧠 Consultando al Kernel para evolucionar {file_path}...")
        respuesta = await kernel.pensar(prompt)
        
        # Limpieza del formato Markdown si el Kernel lo incluye
        code = respuesta.replace("```python", "").replace("```", "").strip()
        if "[DEEPSEEK]" in code: code = code.split("[DEEPSEEK]")[1].strip()
        
        return {"propuesta": code}

# Singleton
arquitecto = ArquitectoProactivo(".")
