#!/usr/bin/env python3
"""
SISTEMA DE AUTOCONOCIMIENTO CLAWCORE
Verifica automáticamente qué componentes existen al inicio de cada sesión
"""

import os
import json
import sys
from pathlib import Path

def verificar_sistema_clawcore():
    """Verificar qué componentes de ClawCore existen"""
    base_path = Path(os.path.expanduser("~/.clawcore/clawcore"))
    
    componentes = {
        "chromadb": False,
        "neuronas": False,
        "cerebro_propio": False,
        "evolucion_automatica": False,
        "perplexity_api": False,
        "tareas_autonomas": False,
        "documentacion": False
    }
    
    rutas = {
        "chromadb": base_path / "venv" / "lib" / "python3.12" / "site-packages" / "chromadb",
        "neuronas_es": Path("~/clawcore_producto/neuronas_claude.py").expanduser(),
        "neuronas_en": Path("~/clawcore_producto/neuronas_english.py").expanduser(),
        "cerebro_propio": base_path / "cerebro" / "cerebro_prototipo.py",
        "evolucion": base_path / "estado_evolucion.json",
        "perplexity": base_path / "perplexity_investigator.py",
        "tareas": base_path / "sistema_tareas.py",
        "documentacion": base_path / "documentacion" / "CLAWCORE_LocalHost.md"
    }
    
    # Verificar cada componente
    for nombre, ruta in rutas.items():
        if ruta.exists():
            if "chromadb" in nombre:
                componentes["chromadb"] = True
            elif "neuronas" in nombre:
                componentes["neuronas"] = True
            elif "cerebro" in nombre:
                componentes["cerebro_propio"] = True
            elif "evolucion" in nombre:
                componentes["evolucion_automatica"] = True
            elif "perplexity" in nombre:
                componentes["perplexity_api"] = True
            elif "tareas" in nombre:
                componentes["tareas_autonomas"] = True
            elif "documentacion" in nombre:
                componentes["documentacion"] = True
    
    return componentes

def generar_reporte_autoconocimiento():
    """Generar reporte de autoconocimiento"""
    componentes = verificar_sistema_clawcore()
    
    print("🧠 REPORTE DE AUTOCONOCIMIENTO CLAWCORE")
    print("=" * 60)
    print(f"Sistema: ClawCore Evolutivo (VPS 229)")
    print(f"Fecha: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("📊 COMPONENTES IDENTIFICADOS:")
    for nombre, existe in componentes.items():
        estado = "✅ ACTIVO" if existe else "❌ NO ENCONTRADO"
        print(f"  • {nombre.replace('_', ' ').title():20} {estado}")
    
    print()
    
    # Leer autonomía si existe
    evolucion_path = Path(os.path.expanduser("~/.clawcore/clawcore/estado_evolucion.json"))
    if evolucion_path.exists():
        try:
            with open(evolucion_path, 'r') as f:
                data = json.load(f)
                autonomia = data.get('autonomia', 0.241)
                evoluciones = data.get('evoluciones', 4)
                print(f"🎯 AUTONOMÍA: {autonomia:.1%} (Evolución {evoluciones})")
                print(f"📈 INCREMENTO: +0.5% cada hora automáticamente")
        except:
            print("🎯 AUTONOMÍA: ~24.1% (estimada)")
    else:
        print("🎯 AUTONOMÍA: ~24.1% (estimada - archivo no encontrado)")
    
    print()
    print("💾 ESPACIO DISCO:")
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        print(f"  • Total: {total // (2**30)}GB")
        print(f"  • Usado: {used // (2**30)}GB ({used/total*100:.1f}%)")
        print(f"  • Libre: {free // (2**30)}GB ({free/total*100:.1f}%)")
    except:
        print("  • No disponible")
    
    print()
    print("🎯 RECOMENDACIONES:")
    
    if not componentes["chromadb"]:
        print("  • Instalar/activar ChromaDB para RAG")
    if not componentes["neuronas"]:
        print("  • Integrar sistema neuronal bilingüe")
    if componentes["cerebro_propio"]:
        print("  • Usar cerebro propio en lugar de APIs externas")
    if componentes["perplexity_api"]:
        print("  • Usar Perplexity API para investigación automática")
    
    print("=" * 60)
    
    # Guardar reporte
    reporte_path = Path(os.path.expanduser("~/.clawcore/workspace/ultimo_autoconocimiento.json"))
    with open(reporte_path, 'w') as f:
        json.dump({
            "timestamp": __import__('datetime').datetime.now().isoformat(),
            "componentes": componentes,
            "autonomia": 0.241,  # Valor por defecto
            "vps": "127.0.0.1"
        }, f, indent=2)
    
    print(f"📄 Reporte guardado en: {reporte_path}")

if __name__ == "__main__":
    generar_reporte_autoconocimiento()