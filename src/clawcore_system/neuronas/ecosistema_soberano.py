#!/usr/bin/env python3
"""
LANZADOR SOBERANO V5.2
Inicia el Gateway API y la Interfaz Telegram de forma coordinada.
"""
import subprocess
import time
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))

def launch():
    print("🔱 INICIANDO ECOSISTEMA SOBERANO V5.2")
    print("-" * 40)

    processes = []
    
    # 1. API Gateway (Puerto 8788)
    print("🚀 Lanzando API Gateway...")
    p_gateway = subprocess.Popen(
        [sys.executable, "src/brain/api_gateway.py"],
        cwd=ROOT,
        env=os.environ.copy()
    )
    processes.append(p_gateway)
    time.sleep(2) # Esperar a que el Gateway levante

    # 2. Telegram Interface
    print("📱 Lanzando Interfaz Telegram...")
    p_telegram = subprocess.Popen(
        [sys.executable, "src/clawcore_system/neuronas/interface_telegram.py"],
        cwd=ROOT,
        env=os.environ.copy()
    )
    processes.append(p_telegram)

    print("-" * 40)
    print("✅ Sistema en línea. Presiona Ctrl+C para detener.")
    
    try:
        while True:
            time.sleep(1)
            # Check if processes are alive
            if p_gateway.poll() is not None:
                print("⚠️ Gateway se detuvo. Reiniciando...")
                break
            if p_telegram.poll() is not None:
                print("⚠️ Telegram se detuvo. Reiniciando...")
                break
    except KeyboardInterrupt:
        print("\n🛑 Apagando sistema...")
        p_gateway.terminate()
        p_telegram.terminate()
        print("Done.")

if __name__ == "__main__":
    launch()
