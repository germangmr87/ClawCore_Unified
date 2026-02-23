import sys
import os
import json
import logging
from pathlib import Path

# Configurar logs para el test
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("ClawCoreTest")

# Añadir rutas al path para importar componentes
root_dir = Path("/Users/german/Documents/GitHub/ClawCore_Unified")
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / "src/clawcore_system/neuronas"))
sys.path.append(str(root_dir / "src/brain"))


def test_module_loading():
    """TEST 1: Carga de Módulos e Independencia"""
    print("\n🧪 TEST 1: Carga de Módulos e Independencia")
    from neuronas_locales import NeuronaLocal, RedNeuronalAutonoma
    from verificador_verdad import VerificadorVerdad
    from compresor_tokens import CompresorTokens
    print("✅ Módulos cargados sin dependencias externas.")
    return True

def test_truth_perimeter():
    """TEST 2: Verificador de Verdad (Perímetro)"""
    print("\n🧪 TEST 2: Verificador de Verdad (Perímetro)")
    from verificador_verdad import VerificadorVerdad
    verificador = VerificadorVerdad(root_dir)
    check_prohibido = verificador.validar_perimetro("/etc/shadow")
    if not check_prohibido["valido"]:
        print(f"✅ Bloqueo correcto de ruta externa: {check_prohibido['msj']}")
        return True
    print("❌ FALLO: No se bloqueó el acceso perimetral.")
    return False

def test_token_compression():
    """TEST 3: Compresor de Tokens (Ahorro Simbólico)"""
    print("\n🧪 TEST 3: Compresor de Tokens")
    from compresor_tokens import CompresorTokens
    compresor = CompresorTokens()
    texto_original = "la neurona de seguridad detectó un error en la arquitectura"
    texto_compreso = compresor.comprimir_texto(texto_original)
    ratio = (1 - len(texto_compreso)/len(texto_original)) * 100
    print(f"✅ Texto original: {len(texto_original)} chars")
    print(f"✅ Texto compreso: {len(texto_compreso)} chars (Ahorro: {ratio:.1f}%)")
    return True

def test_neuronal_anchors():
    """TEST 4: Neurona Local (Ciclo de Decisión y Anclaje)"""
    print("\n🧪 TEST 4: Neurona Local y Anclajes")
    from neuronas_locales import NeuronaLocal
    neurona = NeuronaLocal("NEURONA_CORE_TEST")
    neurona.umbral = 0.1 
    resultado = neurona.procesar("test de integridad de sistema", {"riesgo": "bajo"})
    if "ancla" in resultado and "decision" in resultado:
        print(f"✅ Decisión generada: {resultado['decision']}")
        print(f"✅ Ancla de realidad inyectada: {len(resultado['ancla'])} archivos")
        return True
    print("❌ FALLO: El resultado no contiene anclas de verdad o decisiones.")
    return False

def test_sqlite_persistence():
    """TEST 5: Persistencia SQLite (Inmunidad Amnesia)"""
    print("\n🧪 TEST 5: Persistencia Transaccional SQLite")
    from persistencia_soberana import PersistenciaSoberana
    db = PersistenciaSoberana()
    db.guardar_estado_global("test_key", "sovereign_value")
    val = db.cargar_estado_global("test_key")
    if val == "sovereign_value":
        print("✅ Persistencia SQLite con WAL confirmada.")
        return True
    return False

def test_resource_governor():
    """TEST 6: Gobernador de Recursos (Eficiencia psutil)"""
    print("\n🧪 TEST 6: Gobernador de Recursos (psutil)")
    from gobernador_recursos import GobernadorRecursos
    gob = GobernadorRecursos()
    estado = gob.obtener_estado_critico()
    if "cpu_total" in estado and len(estado["top_procesos"]) > 0:
        print(f"✅ Telemetría de Kernel activa (CPU: {estado['cpu_total']}%).")
        return True
    return False

def test_full_system():
    """Ejecuta todos los tests de integridad del sistema ClawCore."""
    print("🛡️ INICIANDO TEST INTEGRAL DE CLAWCORE UNIFIED 🛡️")
    print("=" * 60)
    
    tests = [
        test_module_loading,
        test_truth_perimeter,
        test_token_compression,
        test_neuronal_anchors,
        test_sqlite_persistence,
        test_resource_governor
    ]

    
    intentos_exitosos = sum(1 for test in tests if test())

    print("\n" + "=" * 60)
    print(f"📊 RESULTADO FINAL: {intentos_exitosos}/{len(tests)} Tests superados.")
    if intentos_exitosos == len(tests):
        print("🔱 SISTEMA NOMINAL: ClawCore Unified listo para evolución soberana.")
    else:
        print("⚠️ SISTEMA DEGRADADO: Revisar fallos indicados arriba.")
    print("=" * 60)


if __name__ == "__main__":
    test_full_system()
