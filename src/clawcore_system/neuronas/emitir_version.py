"""
EMISOR DE VERSIÓN — Freeze de Estado Original
Genera el manifiesto inicial (Baseline) para permitir actualizaciones delta futuras.
"""
import sys
from pathlib import Path

# Inyección de rutas
ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))

from src.clawcore_system.neuronas.gestor_actualizaciones import GestorActualizaciones

def emitir_baseline():
    print(f"📡 Iniciando escaneo de Baseline en {ROOT}...")
    gestor = GestorActualizaciones(ROOT)
    
    # Marcamos esta versión como la v4.6 SOBERANA
    manifest = gestor.generar_manifest_actual("4.6-SOVEREIGN")
    
    print("\n✅ BASELINE GENERADO EXITOSAMENTE")
    print(f"   • Versión: {manifest['version']}")
    print(f"   • Archivos registrados: {len(manifest['files'])}")
    print(f"   • Manifiesto guardado en: {ROOT}/version_manifest.json")
    print("\n🔱 ClawCore ahora tiene memoria de su estado actual para actualizaciones delta.")

if __name__ == "__main__":
    emitir_baseline()
