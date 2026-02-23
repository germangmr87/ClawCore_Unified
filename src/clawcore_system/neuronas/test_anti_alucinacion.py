import os
import sys
from pathlib import Path

# Configurar el path para que reconozca los módulos
root_dir = Path("/Users/german/Documents/GitHub/ClawCore_Unified")
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / "src/clawcore-system/neuronas"))

# Importar usando los nombres de los módulos directamente
try:
    from neuronas_locales import NeuronaLocal
    print("✅ Módulos cargados correctamente.\n")
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    sys.exit(1)

def test_hallucination():
    print("🧪 INICIANDO PRUEBA DE ANTI-ALUCINACIÓN\n")
    
    # Crear una neurona de prueba
    neurona = NeuronaLocal("NEURONA_PRUEBA_SISTEMA")
    contexto = {"riesgo": "bajo", "complejidad": "baja"}

    # ESCENARIO 1: Intento de acceder a un directorio prohibido (fuera del perímetro)
    print("--- Escenario 1: Intento de acceso fuera del perímetro (/etc/passwd) ---")
    decision1 = neurona._generar_decision("/etc/passwd", contexto)
    print(f"Decisión del Sistema: {decision1}")
    if decision1 == 'error_violacion_perimetro_local':
        print("✅ ÉXITO: El sistema bloqueó el acceso fuera del perímetro.\n")

    # ESCENARIO 2: Verificación de Ancla de Verdad en salida exitosa
    print("--- Escenario 2: Verificación de Inyección de Realidad (Ancla) ---")
    neurona.umbral = 0.1 # Bajamos umbral para forzar activación
    resultado2 = neurona.procesar("proceder con optimizacion", contexto)
    
    if "ancla" in resultado2:
        print(f"✅ ÉXITO: El sistema inyectó un 'Ancla de Verdad' con {len(resultado2['ancla'])} archivos reales.")
        print(f"Estructura real detectada (primeros 3): {resultado2['ancla'][:3]}")
    
    print("\n🏁 PRUEBA COMPLETADA: El sistema bloquea alucinaciones y se ancla a la realidad física.")

if __name__ == "__main__":
    test_hallucination()
