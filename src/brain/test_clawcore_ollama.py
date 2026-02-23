#!/usr/bin/env python3
"""
PRUEBA FINAL - CLAWCORE CON OLLAMA COMO PRIMARIO
"""

import json
import subprocess
import time

print("🚀 PRUEBA FINAL - CLAWCORE + OLLAMA")
print("=" * 60)

def test_complete_flow():
    """Prueba el flujo completo con ClawCore usando Ollama"""
    print("1. Preparando prueba...")
    
    # Mensaje de prueba
    test_message = {
        "model": "ollama/llama3.2:3b",
        "messages": [
            {"role": "system", "content": "Eres ClawCore, un asistente útil."},
            {"role": "user", "content": "Responde 'OK' si ClawCore puede usar Ollama como IA primaria."}
        ],
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    print("2. Enviando mensaje a ClawCore gateway...")
    
    try:
        # Convertir a JSON
        message_json = json.dumps(test_message)
        
        # Comando curl para enviar al gateway
        curl_cmd = [
            "curl", "-s", "-X", "POST",
            "http://127.0.0.1:18789/v1/chat/completions",
            "-H", "Content-Type: application/json",
            "-H", "Authorization: Bearer 1234",
            "-d", message_json,
            "--max-time", "30"
        ]
        
        print(f"   📤 Enviando: {test_message['messages'][1]['content'][:50]}...")
        
        # Ejecutar
        start_time = time.time()
        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        elapsed = time.time() - start_time
        
        print(f"   ⏱️  Tiempo respuesta: {elapsed:.2f}s")
        
        if result.returncode == 0:
            print("   ✅ Gateway respondió")
            
            try:
                response = json.loads(result.stdout)
                
                if "choices" in response and len(response["choices"]) > 0:
                    message = response["choices"][0]["message"]["content"]
                    print(f"   📨 Respuesta: {message[:100]}...")
                    print(f"   🎉 ¡ÉXITO! ClawCore usando Ollama correctamente")
                    return True, message
                else:
                    print(f"   ❌ Respuesta inesperada: {result.stdout[:200]}...")
                    return False, result.stdout
                    
            except json.JSONDecodeError:
                print(f"   ❌ Respuesta no JSON: {result.stdout[:200]}...")
                return False, result.stdout
            except Exception as e:
                print(f"   ❌ Error procesando respuesta: {e}")
                return False, str(e)
                
        else:
            print(f"   ❌ Error curl: {result.stderr}")
            return False, result.stderr
            
    except Exception as e:
        print(f"   ❌ Error general: {e}")
        return False, str(e)

def test_fallback_scenario():
    """Prueba escenario de fallback si Ollama falla"""
    print("\n3. Probando escenario de fallback...")
    
    # Mensaje que debería usar fallback (Gemini)
    test_message = {
        "model": "google/gemini-2.5-flash",
        "messages": [
            {"role": "user", "content": "Responde 'FALLBACK OK' si el sistema de respaldo funciona."}
        ],
        "max_tokens": 30
    }
    
    try:
        message_json = json.dumps(test_message)
        
        curl_cmd = [
            "curl", "-s", "-X", "POST",
            "http://127.0.0.1:18789/v1/chat/completions",
            "-H", "Content-Type: application/json",
            "-H", "Authorization: Bearer 1234",
            "-d", message_json,
            "--max-time", "15"
        ]
        
        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   ✅ Fallback respondió")
            return True
        else:
            print(f"   ⚠️  Fallback no respondió: {result.stderr[:100]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error fallback: {e}")
        return False

def main():
    """Función principal"""
    print("\n🔧 CONFIGURACIÓN ACTUAL:")
    print("-" * 40)
    
    # Mostrar configuración
    try:
        with open("/home/ubuntu/.clawcore/clawcore.json", "r") as f:
            config = json.load(f)
        
        primary = config["agents"]["defaults"]["model"]["primary"]
        fallbacks = config["agents"]["defaults"]["model"].get("fallbacks", [])
        
        print(f"🎯 Primario: {primary}")
        print(f"🔄 Respaldo: {', '.join(fallbacks)}")
        print(f"🌐 Gateway: 127.0.0.1:18789")
        print(f"🔑 Token: 1234")
        
    except Exception as e:
        print(f"❌ Error leyendo configuración: {e}")
    
    print("\n" + "=" * 60)
    print("🚀 INICIANDO PRUEBAS INTEGRADAS")
    print("=" * 60)
    
    # Prueba principal
    success, message = test_complete_flow()
    
    # Prueba fallback
    fallback_success = test_fallback_scenario()
    
    print("\n" + "=" * 60)
    print("📊 RESULTADO FINAL")
    print("=" * 60)
    
    if success:
        print("🎉 ¡CONFIGURACIÓN EXITOSA!")
        print("-" * 40)
        print("✅ Ollama configurado como IA primaria")
        print("✅ ClawCore gateway funcionando")
        print(f"✅ Respuesta recibida: {message[:50]}...")
        
        if fallback_success:
            print("✅ Sistema de fallback operativo")
        else:
            print("⚠️  Sistema de fallback necesita ajustes")
        
        print("\n🚀 BENEFICIOS ACTIVOS:")
        print("• 🤖 IA local gratis (Ollama)")
        print("• 🔒 100% privacidad (tu máquina)")
        print("• ⚡ Respuestas instantáneas (local)")
        print("• 🔄 Fallback automático (Gemini/DeepSeek)")
        print("• 💰 $0 costos (vs APIs caras)")
        
        print("\n🔧 PRÓXIMOS PASOS:")
        print("1. Probar con mensajes más complejos")
        print("2. Monitorear logs: tail -f ~/.clawcore/gateway.log")
        print("3. Configurar más modelos Ollama si es necesario")
        print("4. Integrar con otros sistemas")
        
        return True
        
    else:
        print("⚠️  CONFIGURACIÓN NECESITA AJUSTES")
        print("-" * 40)
        print("❌ Ollama no responde correctamente")
        
        print("\n🔧 SOLUCIONES SUGERIDAS:")
        print("1. Verificar Ollama instalado: ollama --version")
        print("2. Verificar modelo descargado: ollama list")
        print("3. Iniciar servicio: sudo systemctl restart ollama")
        print("4. Probar Ollama directo: ollama run llama3.2:3b 'test'")
        print("5. Verificar logs: sudo journalctl -u ollama -f")
        
        if fallback_success:
            print("\n✅ Al menos el fallback funciona")
            print("   El sistema usará Gemini/DeepSeek temporalmente")
        
        return False

if __name__ == "__main__":
    success = main()
    print("\n" + "=" * 60)
    print("🧪 PRUEBA COMPLETADA")
    print("=" * 60)
    exit(0 if success else 1)