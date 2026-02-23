import os
import sys
import ast
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def audit_python_files():
    print("🔍 Iniciando Auditoría de Fuente Python...")
    error_count = 0
    
    python_files = list(ROOT.rglob("*.py"))
    print(f"📂 Encontrados {len(python_files)} archivos Python.")
    
    for pf in python_files:
        if "venv" in str(pf) or "node_modules" in str(pf):
            continue
            
        # 1. Syntax Check
        try:
            with open(pf, "r", encoding="utf-8") as f:
                ast.parse(f.read())
        except SyntaxError as e:
            print(f"❌ ERROR SINTAXIS en {pf.relative_to(ROOT)}: {e}")
            error_count += 1
            continue
        except Exception as e:
            print(f"⚠️ Error leyendo {pf.relative_to(ROOT)}: {e}")
            continue

    print(f"\n✅ Auditoría completada con {error_count} errores críticos de sintaxis.")

if __name__ == "__main__":
    audit_python_files()
