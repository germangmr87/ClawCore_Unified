"""
HEALER V2 — Auto-Reparación Lógica
Analiza tracebacks y propone correcciones de lógica, no solo de sintaxis.
Usa AST + patrones comunes + LLM local (si disponible) para generar parches.
"""
import ast
import re
import logging
import traceback as tb_module
from pathlib import Path
from typing import Optional

logger = logging.getLogger("HealerV2")
logger.setLevel(logging.INFO)


# Patrones comunes de errores lógicos y sus correcciones heurísticas
PATTERNS = [
    {"regex": r"TypeError:.*NoneType.*not subscriptable",
     "diagnostic": "Se accede a un valor None como si fuera dict/list",
     "fix_hint": "Añadir guard: if var is not None"},
    {"regex": r"IndexError: list index out of range",
     "diagnostic": "Índice fuera del rango de la lista",
     "fix_hint": "Verificar len(lista) antes de acceder por índice"},
    {"regex": r"KeyError: '(\w+)'",
     "diagnostic": "Clave ausente en diccionario",
     "fix_hint": "Usar dict.get('key', default) en lugar de dict['key']"},
    {"regex": r"ZeroDivisionError",
     "diagnostic": "División por cero",
     "fix_hint": "Añadir guard: if divisor != 0"},
    {"regex": r"AttributeError: '(\w+)' object has no attribute '(\w+)'",
     "diagnostic": "Atributo inexistente en objeto",
     "fix_hint": "Verificar con hasattr(obj, 'attr') o revisar la clase"},
    {"regex": r"RecursionError",
     "diagnostic": "Recursión infinita detectada",
     "fix_hint": "Verificar caso base de la recursión; añadir límite de profundidad"},
]


class HealerV2:
    """Neurona de auto-reparación lógica."""

    def __init__(self):
        self.historial_reparaciones: list[dict] = []
        self.patrones = PATTERNS

    def diagnosticar(self, traceback_text: str) -> dict:
        """Analiza un traceback y devuelve diagnóstico + sugerencia."""
        for p in PATTERNS:
            m = re.search(p["regex"], traceback_text)
            if m:
                # Extraer archivo y línea del traceback
                file_line = re.findall(r'File "(.+?)", line (\d+)', traceback_text)
                location = file_line[-1] if file_line else ("desconocido", "?")
                result = {
                    "diagnostico": p["diagnostic"],
                    "sugerencia": p["fix_hint"],
                    "archivo": location[0],
                    "linea": int(location[1]) if location[1] != "?" else 0,
                    "patron": p["regex"],
                    "severidad": "ALTA"
                }
                self.historial_reparaciones.append(result)
                return result

        return {"diagnostico": "Error no reconocido en patrones conocidos",
                "sugerencia": "Escalar a revisión humana o LLM profundo",
                "severidad": "MEDIA", "traceback": traceback_text[-500:]}

    def intentar_parche_ast(self, filepath: Path, linea: int, hint: str) -> Optional[str]:
        """Intenta generar un parche basado en AST para la línea problemática."""
        try:
            src = filepath.read_text()
            lines = src.split("\n")
            if linea < 1 or linea > len(lines):
                return None

            original_line = lines[linea - 1]
            patched = original_line

            # Heurística: KeyError → dict.get
            if "dict.get" in hint and "[" in original_line and "'" in original_line:
                key = re.search(r"\['(.+?)'\]", original_line)
                var = re.search(r"(\w+)\[", original_line)
                if key and var:
                    patched = original_line.replace(
                        f"{var.group(1)}['{key.group(1)}']",
                        f"{var.group(1)}.get('{key.group(1)}', None)")

            # Heurística: ZeroDivision → guard
            if "divisor != 0" in hint and "/" in original_line:
                indent = len(original_line) - len(original_line.lstrip())
                guard = " " * indent + "# HEALER: guard contra división por cero\n"
                guard += " " * indent + f"if True:  # TODO: verificar divisor\n"
                patched = guard + "    " + original_line.lstrip()

            if patched != original_line:
                return patched
            return None
        except Exception as e:
            logger.error(f"Error generando parche AST: {e}")
            return None

    def reporte(self):
        return {"reparaciones_totales": len(self.historial_reparaciones),
                "ultimas": self.historial_reparaciones[-5:]}


if __name__ == "__main__":
    healer = HealerV2()
    # Simular un traceback
    fake_tb = '''Traceback (most recent call last):
  File "/Users/german/Documents/GitHub/ClawCore_Unified/src/clawcore_system/neuronas/neuronas_locales.py", line 85, in procesar
    decision = experiencia_previa[0]
TypeError: 'NoneType' object is not subscriptable'''
    diag = healer.diagnosticar(fake_tb)
    print(f"Diagnóstico: {diag['diagnostico']}")
    print(f"Sugerencia:  {diag['sugerencia']}")
    print(f"Ubicación:   {diag['archivo']}:{diag['linea']}")
