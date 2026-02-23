#!/usr/bin/env python3
"""
EVOLUCIÓN AUTOMÁTICA PARA CRON
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def main():
    """Evolución automática"""
    estado_file = Path.home() / ".clawcore" / "clawcore" / "estado_evolucion.json"
    
    # Cargar estado
    if estado_file.exists():
        with open(estado_file, 'r') as f:
            estado = json.load(f)
        autonomia = estado.get("autonomia", 0.223)
        evoluciones = estado.get("evoluciones", 1)
    else:
        autonomia = 0.223
        evoluciones = 1
    
    # Evolucionar (+0.5%)
    nueva_autonomia = min(autonomia + 0.005, 1.0)
    evoluciones += 1
    
    # Guardar
    estado = {
        "autonomia": round(nueva_autonomia, 4),
        "evoluciones": evoluciones,
        "ultima_evolucion": datetime.now().isoformat() + "Z",
        "proximo_hito": 0.30 if nueva_autonomia < 0.30 else 0.50
    }
    
    with open(estado_file, 'w') as f:
        json.dump(estado, f, indent=2)
    
    # Log
    log_file = Path.home() / ".clawcore" / "clawcore" / "evolucion_cron.log"
    with open(log_file, 'a') as f:
        f.write(f"{datetime.now().isoformat()}Z - Autonomía: {nueva_autonomia:.2%} (+0.5%)\n")
    
    print(f"✅ Evolución: {nueva_autonomia:.2%} autonomía")
    return 0

if __name__ == "__main__":
    sys.exit(main())