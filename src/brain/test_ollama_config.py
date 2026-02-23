#!/usr/bin/env python3
"""
PRUEBA CONFIGURACIÓN OLLAMA COMO PRIMARIO
"""

import json
import subprocess
import time

print("🧪 PRUEBA CONFIGURACIÓN OLLAMA PRIMARIO")
print("=" * 50)

def test_config():
    """Prueba la configuración actual"""
    print("1. Verificando configuración ClawCore...")
    
    try:
        with open("/home/ubuntu/.clawcore/clawcore.json", "r") as f:
            config = json.load(f)
        
        primary = config["agents"]["defaults"]["model"]["primary"]
        fallbacks = config["agents"]["defaults"]["model"].get("fallbacks", [])
        
        print(f"   ✅ Configuración cargada")
        print(f"   🎯 Primario: {primary}")
        print(f"   🔄 Respaldo: {fallbacks}")
        
        if primary == "ollama/llama3.2:3b":
            print("   🎉 ¡Ollama configurado como primario!")
            return True
        else:
            print(f"   ⚠️  Primario es {primary}, no Ollama")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_ollama_service():
    """Prueba si Ollama está corriendo"""
    print("\n2. Verificando servicio Ollama...")
    
    try:
        # Verificar si ollama está instalado
        result = subprocess.run(["which", "ollama"], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"   ✅ Ollama instalado: {result.stdout.strip()}")
            
            # Verificar si el servicio está corriendo
            service_result = subprocess.run(["systemctl", "is-active", "ollama"], 
                                          capture_output=True, text=True)
            
            if service_result.stdout.strip() == "active":
                print("   ✅ Servicio Ollama activo")
                return True
            else:
                print(f"   ⚠️  Servicio Ollama: {service_result.stdout.strip()}")
                return False
        else:
            print("   ❌ Ollama no instalado")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_ollama_api():
    """Prueba la API de Ollama"""
    print("\n3. Probando API Ollama...")
    
    try:
        # Intentar conectar a la API
        curl_cmd = [
            "curl", "-s", "-X", "POST",
            "http://localhost:11434/api/generate",
            "-H", "Content-Type: application/json",
            "-d", '{"model":"llama3.2:3b","prompt":"OK","stream":false,"max_tokens":10}'
        ]
        
        result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("   ✅ API Ollama responde")
            
            try:
                response = json.loads(result.stdout)
                if "response" in response:
                    print(f"   📨 Respuesta: {response['response'][:50]}...")
                    return True
            except:
                print(f"   📨 Respuesta cruda: {result.stdout[:100]}...")
                return True
        else:
            print(f"   ❌ Error API: {result.stderr[:100]}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ⏱️  Timeout - Ollama puede estar iniciando")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_clawcore_gateway():
    """Prueba el gateway de ClawCore"""
    print("\n4. Probando ClawCore Gateway...")
    
    try:
        curl_cmd = [
            "curl", "-s", "http://127.0.0.1:18789/health"
        ]
        
        result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print("   ✅ Gateway ClawCore activo")
            return True
        else:
            print(f"   ❌ Gateway no responde: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Función principal"""
    print("\n🔍 EJECUTANDO PRUEBAS...\n")
    
    tests = [
        ("Configuración", test_config),
        ("Servicio Ollama", test_ollama_service),
        ("API Ollama", test_ollama_api),
        ("Gateway ClawCore", test_clawcore_gateway)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"   ❌ Error en {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📊 RESULTADOS DE PRUEBAS:")
    print("=" * 50)
    
    passed = 0
    for name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{status} - {name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Total: {passed}/{len(results)} pruebas exitosas")
    
    if passed == len(results):
        print("\n🚀 ¡CONFIGURACIÓN COMPLETA! Ollama es primario")
        print("=" * 50)
        print("\n🔧 Próximos pasos:")
        print("1. Reiniciar ClawCore gateway si es necesario")
        print("2. Probar con un mensaje real")
        print("3. Monitorear logs: tail -f ~/.clawcore/gateway.log")
    else:
        print("\n⚠️  Configuración necesita ajustes")
        print("=" * 50)
        print("\n🔧 Soluciones sugeridas:")
        print("1. Instalar Ollama: curl -fsSL https://ollama.com/install.sh | sh")
        print("2. Iniciar servicio: sudo systemctl start ollama")
        print("3. Descargar modelo: ollama pull llama3.2:3b")
        print("4. Reiniciar gateway: clawcore gateway restart")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)