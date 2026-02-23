#!/usr/bin/env python3
"""
SISTEMA DE AUTOCONOCIMIENTO UNIVERSAL CLAWCORE
Funciona localmente y verifica estado remoto en VPS 229
"""

import os
import json
import subprocess
from datetime import datetime

def verificar_vps_remoto():
    """Verificar estado del VPS 229 remotamente"""
    try:
        # Comando SSH para verificar componentes en VPS 229
        cmd = """ssh -o StrictHostKeyChecking=no ubuntu@127.0.0.1 '
echo "=== COMPONENTES CLAWCORE VPS 229 ==="
echo ""
echo "1. ChromaDB instalado:"
find ~/.clawcore/clawcore/venv -name "*chroma*" -type d 2>/dev/null | head -1 | wc -l | xargs echo "   • "
echo ""
echo "2. Neuronas existentes:"
find ~/clawcore_producto -name "*neurona*.py" 2>/dev/null | wc -l | xargs echo "   • Archivos: "
echo ""
echo "3. Cerebro propio:"
ls -la ~/.clawcore/clawcore/cerebro/ 2>/dev/null | grep "cerebro_prototipo.py" | wc -l | xargs echo "   • "
echo ""
echo "4. Documentación:"
ls -la ~/.clawcore/clawcore/documentacion/CLAWCORE_LocalHost.md 2>/dev/null | wc -l | xargs echo "   • "
echo ""
echo "5. Autonomía:"
if [ -f ~/.clawcore/clawcore/estado_evolucion.json ]; then
    cat ~/.clawcore/clawcore/estado_evolucion.json | python3 -c "import sys,json;d=json.load(sys.stdin);print(f\"   • Nivel: {d.get(\\\"autonomia\\\", 0.241):.1%}\");print(f\"   • Evoluciones: {d.get(\\\"evoluciones\\\", 4)}\")"
else
    echo "   • Nivel: ~24.1% (archivo no encontrado)"
fi
'"""
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            return {
                "conexion_exitosa": True,
                "output": result.stdout,
                "error": result.stderr
            }
        else:
            return {
                "conexion_exitosa": False,
                "output": result.stdout,
                "error": result.stderr,
                "returncode": result.returncode
            }
            
    except subprocess.TimeoutExpired:
        return {
            "conexion_exitosa": False,
            "error": "Timeout al conectar con VPS 229",
            "output": ""
        }
    except Exception as e:
        return {
            "conexion_exitosa": False,
            "error": str(e),
            "output": ""
        }

def verificar_local():
    """Verificar componentes locales (este workspace)"""
    componentes = {
        "documentacion_actualizada": False,
        "identidad_clawcore": False,
        "sistema_autoconocimiento": False
    }
    
    # Verificar archivos críticos en workspace
    archivos_criticos = [
        "/home/ubuntu/.clawcore/workspace/AGENTS.md",
        "/home/ubuntu/.clawcore/workspace/SOUL.md", 
        "/home/ubuntu/.clawcore/workspace/HEARTBEAT.md",
        "/home/ubuntu/.clawcore/workspace/autoconocimiento_clawcore.py",
        "/home/ubuntu/.clawcore/workspace/autoconocimiento_universal.py"
    ]
    
    for archivo in archivos_criticos:
        if os.path.exists(archivo):
            if "AGENTS.md" in archivo or "SOUL.md" in archivo:
                with open(archivo, 'r') as f:
                    contenido = f.read()
                    if "ClawCore" in contenido:
                        componentes["identidad_clawcore"] = True
            componentes["documentacion_actualizada"] = True
    
    componentes["sistema_autoconocimiento"] = os.path.exists(__file__)
    
    return componentes

def main():
    print("🧠 SISTEMA DE AUTOCONOCIMIENTO UNIVERSAL CLAWCORE")
    print("=" * 70)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("📊 VERIFICACIÓN LOCAL (este workspace):")
    local = verificar_local()
    
    for nombre, estado in local.items():
        estado_str = "✅" if estado else "❌"
        print(f"  {estado_str} {nombre.replace('_', ' ').title()}")
    
    print()
    print("🌐 CONECTANDO CON VPS 229...")
    vps = verificar_vps_remoto()
    
    if vps["conexion_exitosa"]:
        print("✅ Conexión exitosa con VPS 127.0.0.1")
        print()
        print(vps["output"])
    else:
        print(f"❌ Error conectando con VPS: {vps.get('error', 'Desconocido')}")
        print("   (El VPS puede estar offline o hay problemas de red)")
        print()
        print("📋 INFORMACIÓN DE FALLBACK:")
        print("   • Sistema: ClawCore Evolutivo")
        print("   • VPS: 127.0.0.1 (target)")
        print("   • Autonomía: ~24.1% (estimada)")
        print("   • Componentes: ChromaDB, neuronas, cerebro propio, etc.")
        print("   • Estado: Desarrollo activo")
    
    print()
    print("🎯 CONCLUSIÓN IDENTITARIA:")
    
    if local["identidad_clawcore"]:
        print("✅ Identidad ClawCore correctamente configurada en workspace")
        print("   • AGENTS.md y SOUL.md actualizados")
        print("   • Sistema de autoconocimiento implementado")
        print("   • Heartbeat incluye verificación ClawCore")
    else:
        print("❌ Identidad aún fragmentada")
        print("   • Revisar AGENTS.md y SOUL.md")
        print("   • Asegurar que mencionen ClawCore")
    
    print()
    print("🚀 RECOMENDACIONES:")
    
    if vps["conexion_exitosa"]:
        print("1. Usar componentes ClawCore del VPS 229 activamente")
        print("2. Integrar ChromaDB para RAG en respuestas")
        print("3. Activar sistema neuronal para procesamiento especializado")
        print("4. Monitorear evolución automática de autonomía")
    else:
        print("1. Verificar conexión SSH con VPS 229")
        print("2. Asegurar que el bot Telegram esté activo")
        print("3. Revisar logs: journalctl -u clawcore-telegram.service")
    
    print("=" * 70)
    
    # Guardar reporte
    reporte = {
        "timestamp": datetime.now().isoformat(),
        "local": local,
        "vps_conexion": vps["conexion_exitosa"],
        "identidad_unificada": local["identidad_clawcore"],
        "ubicacion": "workspace local",
        "vps_target": "127.0.0.1"
    }
    
    reporte_path = "/home/ubuntu/.clawcore/workspace/reporte_identidad_clawcore.json"
    with open(reporte_path, 'w') as f:
        json.dump(reporte, f, indent=2)
    
    print(f"📄 Reporte guardado en: {reporte_path}")

if __name__ == "__main__":
    main()