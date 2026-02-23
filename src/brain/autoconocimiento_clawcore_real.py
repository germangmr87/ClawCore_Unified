#!/usr/bin/env python3
"""
AUTOCONOCIMIENTO CLAWCORE REAL - Verifica componentes REALES del sistema VPS 229
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime

def verificar_componente(nombre, rutas_posibles):
    """Verificar si un componente existe en múltiples rutas posibles"""
    for ruta in rutas_posibles:
        path = Path(ruta).expanduser()
        if path.exists():
            return {"componente": nombre, "estado": "✅ ENCONTRADO", "ruta": str(path)}
    
    return {"componente": nombre, "estado": "❌ NO ENCONTRADO", "ruta": rutas_posibles[0] if rutas_posibles else ""}

def verificar_servicio(nombre, servicio):
    """Verificar si un servicio systemd está activo"""
    try:
        result = subprocess.run(
            ["systemctl", "is-active", servicio],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.stdout.strip() == "active":
            return {"componente": nombre, "estado": "✅ ACTIVO", "detalle": servicio}
        else:
            return {"componente": nombre, "estado": "⚠️  INACTIVO", "detalle": servicio}
    except:
        return {"componente": nombre, "estado": "❌ NO VERIFICADO", "detalle": servicio}

def main():
    """Ejecutar autoconocimiento REAL"""
    print("🧠 REPORTE DE AUTOCONOCIMIENTO CLAWCORE REAL")
    print("=" * 60)
    print(f"Sistema: ClawCore Evolutivo (VPS 229)")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Componentes REALES a verificar (rutas múltiples)
    componentes = [
        ("ChromaDB", [
            "~/.clawcore/clawcore/venv/lib/python3.12/site-packages/chromadb",
            "/usr/local/lib/python3.12/dist-packages/chromadb"
        ]),
        ("Neuronas Locales", [
            "~/.clawcore/clawcore/neuronas_locales.py",
            "~/.clawcore/clawcore/__pycache__/neuronas_locales.cpython-312.pyc"
        ]),
        ("Cerebro en Malla", [
            "~/.clawcore/clawcore/cerebro_malla",
            "~/.clawcore/clawcore/cerebro_malla/axon/nucleo_axon.py"
        ]),
        ("Evolución Automática", [
            "~/.clawcore/clawcore/evolucion_cron_simple.py",
            "~/.clawcore/clawcore/estado_evolucion.json"
        ]),
        ("Perplexity API", [
            "~/.clawcore/clawcore/perplexity_investigator.py",
            "~/.clawcore/clawcore/investigacion"
        ]),
        ("Tareas Autónomas", [
            "~/.clawcore/clawcore/tareas_autonomas",
            "~/.clawcore/clawcore/sistema_tareas.py"
        ]),
        ("Documentación", [
            "~/.clawcore/clawcore/documentacion",
            "~/.clawcore/clawcore/documentacion/CLAWCORE_LocalHost.md"
        ]),
        ("Memoria Flash", [
            "~/.clawcore/clawcore/cerebro_malla/memoria_flash/memoria_flash.py"
        ]),
        ("Núcleo Axon", [
            "~/.clawcore/clawcore/cerebro_malla/axon/nucleo_axon.py"
        ]),
        ("Autonomía Silenciosa", [
            "~/.clawcore/clawcore/cerebro_malla/autonomia/autonomia_silenciosa.py"
        ]),
        ("Bot Telegram", [
            "~/.clawcore/clawcore/bot_autonomo.py",
            "~/.clawcore/clawcore/bot_clawcore_corregido.py"
        ]),
        ("Sistema Unificado", [
            "~/.clawcore/clawcore/sistema_unificado.py",
            "~/.clawcore/clawcore/sistema_bilingue.py"
        ])
    ]
    
    print("📊 COMPONENTES CLAWCORE IDENTIFICADOS:")
    resultados = []
    
    for nombre, rutas in componentes:
        resultado = verificar_componente(nombre, rutas)
        resultados.append(resultado)
        estado = resultado["estado"]
        if "✅" in estado:
            print(f"  • {nombre:25} ✅ {estado.replace('✅ ', '')}")
        elif "⚠️" in estado:
            print(f"  • {nombre:25} ⚠️  {estado.replace('⚠️  ', '')}")
        else:
            print(f"  • {nombre:25} ❌ {estado.replace('❌ ', '')}")
    
    # Verificar servicios
    print(f"\n🔧 SERVICIOS ACTIVOS:")
    servicios = [
        ("Gateway ClawCore", "clawcore-gateway.service"),
        ("Bot Telegram", "clawcore-telegram.service"),
        ("Fail2ban", "fail2ban.service")
    ]
    
    for nombre, servicio in servicios:
        resultado = verificar_servicio(nombre, servicio)
        resultados.append(resultado)
        estado = resultado["estado"]
        if "✅" in estado:
            print(f"  • {nombre:25} ✅ {estado.replace('✅ ', '')}")
        elif "⚠️" in estado:
            print(f"  • {nombre:25} ⚠️  {estado.replace('⚠️  ', '')}")
        else:
            print(f"  • {nombre:25} ❌ {estado.replace('❌ ', '')}")
    
    # Verificar autonomía REAL
    autonomia_path = Path("~/.clawcore/clawcore/estado_evolucion.json").expanduser()
    if autonomia_path.exists():
        try:
            with open(autonomia_path, 'r') as f:
                data = json.load(f)
            autonomia = data.get("autonomia", 0) * 100
            evoluciones = data.get("evoluciones", 0)
            print(f"\n🎯 AUTONOMÍA ACTUAL: {autonomia:.2f}%")
            print(f"📈 EVOLUCIONES: {evoluciones}")
            print(f"⏰ ÚLTIMA EVOLUCIÓN: {data.get('ultima_evolucion', 'N/A')}")
            print(f"🎯 PRÓXIMO HITO: {data.get('proximo_hito', 0.3)*100:.1f}%")
        except Exception as e:
            print(f"\n🎯 AUTONOMÍA: Error leyendo: {e}")
    else:
        print(f"\n🎯 AUTONOMÍA: Archivo no encontrado")
    
    # Verificar espacio disco
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        print(f"\n💾 ESPACIO DISCO VPS 229:")
        print(f"  • Total: {total // (2**30)}GB")
        print(f"  • Usado: {used // (2**30)}GB ({used/total*100:.1f}%)")
        print(f"  • Libre: {free // (2**30)}GB ({free/total*100:.1f}%)")
    except:
        pass
    
    # Verificar ataques de seguridad
    print(f"\n🛡️  ESTADO DE SEGURIDAD:")
    try:
        # Verificar si hay ataques recientes
        auth_log = "/var/log/auth.log"
        if os.path.exists(auth_log):
            result = subprocess.run(
                ["grep", "-c", "Failed password", auth_log],
                capture_output=True,
                text=True
            )
            failed_attempts = int(result.stdout.strip()) if result.stdout.strip() else 0
            print(f"  • Intentos fallidos SSH: {failed_attempts}")
            
            # Verificar fail2ban
            result = subprocess.run(
                ["systemctl", "is-active", "fail2ban"],
                capture_output=True,
                text=True
            )
            if result.stdout.strip() == "active":
                print(f"  • Fail2ban: ✅ ACTIVO")
            else:
                print(f"  • Fail2ban: ❌ INACTIVO")
    except:
        print(f"  • Seguridad: No se pudo verificar")
    
    print("\n🎯 RESUMEN CLAWCORE VPS 229:")
    print("=" * 60)
    
    componentes_encontrados = sum(1 for r in resultados if "✅" in r["estado"])
    componentes_totales = len(resultados)
    
    print(f"  • Componentes operativos: {componentes_encontrados}/{componentes_totales}")
    print(f"  • Sistema: {'✅ OPERATIVO' if componentes_encontrados > componentes_totales/2 else '⚠️  PARCIAL'}")
    print(f"  • Cerebro en Malla: {'✅ IMPLEMENTADO' if any('Cerebro en Malla' in r['componente'] and '✅' in r['estado'] for r in resultados) else '❌ NO IMPLEMENTADO'}")
    print(f"  • Autonomía: {'✅ CRECIENDO' if 'autonomia' in locals() and autonomia > 20 else '⚠️  BAJA'}")
    print(f"  • Seguridad: {'✅ REFORZADA' if any('Fail2ban' in r['componente'] and '✅' in r['estado'] for r in resultados) else '⚠️  BÁSICA'}")
    
    print("=" * 60)
    
    # Guardar reporte
    reporte = {
        "fecha": datetime.now().isoformat(),
        "sistema": "ClawCore Evolutivo VPS 229",
        "componentes": resultados,
        "autonomia": autonomia if 'autonomia' in locals() else None,
        "estado_general": "operativo" if componentes_encontrados > componentes_totales/2 else "parcial",
        "recomendaciones": [
            r["componente"] for r in resultados 
            if "❌" in r["estado"] and "NO ENCONTRADO" in r["estado"]
        ]
    }
    
    reporte_path = Path("~/.clawcore/workspace/ultimo_autoconocimiento_real.json").expanduser()
    with open(reporte_path, 'w') as f:
        json.dump(reporte, f, indent=2)
    
    print(f"📄 Reporte REAL guardado en: {reporte_path}")

if __name__ == "__main__":
    main()