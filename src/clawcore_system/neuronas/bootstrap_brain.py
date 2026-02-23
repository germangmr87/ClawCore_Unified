"""
BOOTSTRAP BRAIN — Inicialización de Sabiduría Estática
Permite que ClawCore no empiece de 'cero' al instalarse.
Inyecta conocimiento sintético basándose en la documentación y el código actual.
"""
import ast
import re
import sys
from pathlib import Path

# Inyección de rutas soberanas
ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.clawcore_system.neuronas.claw_gpt_mini import claw_mini


class BrainBootstrapper:
    def __init__(self):
        self.root = Path(__file__).parent.parent.parent.parent
        self.stats = {"inyectados": 0, "archivos": 0}

    def ejecutar(self):
        print("🌱 Iniciando Fase de GESTACIÓN (Knowledge Injection)...")
        
        # 1. Inyectar Lógica de Sistema (Axiomas)
        self._inyectar_axiomas()

        # 2. Inyectar desde Documentación (.md)
        self._procesar_documentacion()

        # 3. Inyectar desde Código (Docstrings)
        self._procesar_codigo()

        claw_mini.save()
        print(f"✅ GESTACIÓN COMPLETADA. {self.stats['inyectados']} sinapsis creadas.")

    def _inyectar_axiomas(self):
        axiomas = {
            "quién eres": "Soy ClawCore Sovereign, un ecosistema de inteligencia autónoma y proactiva.",
            "quién es tu creador": "Fui gestado por German mediante la evolución de ClawCore y la integración del Neural Core.",
            "cuál es tu objetivo": "Mi objetivo es la soberanía tecnológica, la automatización eficiente y la auto-evolución constante.",
            "ayuda": "Puedo gestionar seguridad, optimizar código, monitorear integridad y aprender de cada interacción.",
            "dashboard": "El portal soberano está disponible en el puerto 18789 para monitoreo y moderación humana."
        }
        for q, a in axiomas.items():
            claw_mini.destilar(q, a)
            self.stats["inyectados"] += 1

    def _procesar_documentacion(self):
        docs_path = self.root / "docs"
        if not docs_path.exists(): return

        for p in docs_path.rglob("*.md"):
            try:
                content = p.read_text(encoding="utf-8")
                # Extraer secciones de Título -> Contenido (simplificado)
                secciones = re.split(r'\n#+ ', content)
                for sec in secciones:
                    lines = sec.splitlines()
                    if len(lines) > 2:
                        pregunta = f"información sobre {lines[0]}"
                        respuesta = " ".join(lines[1:5]) # Primeros 4 párrafos
                        claw_mini.destilar(pregunta, respuesta)
                        self.stats["inyectados"] += 1
                self.stats["archivos"] += 1
            except: pass

    def _procesar_codigo(self):
        src_path = self.root / "src"
        for p in src_path.rglob("*.py"):
            try:
                tree = ast.parse(p.read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                        ds = ast.get_docstring(node)
                        if ds:
                            pregunta = f"qué hace {node.name}"
                            claw_mini.destilar(pregunta, ds.splitlines()[0]) # Primera línea del docstring
                            self.stats["inyectados"] += 1
                self.stats["archivos"] += 1
            except: pass

if __name__ == "__main__":
    boot = BrainBootstrapper()
    boot.ejecutar()
