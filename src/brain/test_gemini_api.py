#!/usr/bin/env python3
"""
Prueba de API Gemini usando requests directo
"""

import requests
import json
import sys

API_KEY = "AIzaSyBfgcBLZ0LmPi8MegonEchLjJn4JaAr4PE"
URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

def test_gemini():
    """Probar API Gemini"""
    print("🧪 Probando API Gemini...")
    
    headers = {
        "Content-Type": "application/json"
    }
    
    params = {
        "key": API_KEY
    }
    
    data = {
        "contents": [{
            "parts": [{
                "text": "Responde con 'API FUNCIONAL' si recibes este mensaje."
            }]
        }]
    }
    
    try:
        response = requests.post(
            URL,
            headers=headers,
            params=params,
            json=data,
            timeout=10
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API GEMINI FUNCIONAL")
            
            # Extraer respuesta
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    text = candidate["content"]["parts"][0].get("text", "")
                    print(f"📝 Respuesta: {text}")
            
            # Mostrar metadatos de tokens
            if "usageMetadata" in result:
                usage = result["usageMetadata"]
                print(f"🧮 Tokens: {usage.get('totalTokenCount', 'N/A')}")
                print(f"   • Prompt: {usage.get('promptTokenCount', 'N/A')}")
                print(f"   • Respuesta: {usage.get('candidatesTokenCount', 'N/A')}")
            
            return True
            
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"📄 Respuesta: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Error JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def check_context_capabilities():
    """Verificar capacidades de contexto"""
    print("\n🔍 Verificando capacidades de contexto...")
    
    # Gemini 1.5 Flash tiene 1,000,000 tokens de contexto
    # vs DeepSeek que tiene 131,072 tokens
    
    capabilities = {
        "model": "gemini-1.5-flash",
        "max_context_tokens": 1000000,  # 1M tokens
        "input_tokens": 1048576,
        "output_tokens": 8192,
        "comparison": {
            "deepseek": 131072,
            "gemini_ratio": "7.6x más contexto",
            "gemini_absolute": "868,928 tokens más"
        },
        "features": [
            "Contexto largo (1M tokens)",
            "Multimodal (texto, imágenes)",
            "Razonamiento mejorado",
            "Bajo costo"
        ]
    }
    
    print(f"📊 Modelo: {capabilities['model']}")
    print(f"🧠 Contexto máximo: {capabilities['max_context_tokens']:,} tokens")
    print(f"📈 Comparación con DeepSeek: {capabilities['comparison']['gemini_ratio']}")
    print(f"   • DeepSeek: {capabilities['comparison']['deepseek']:,} tokens")
    print(f"   • Gemini: {capabilities['max_context_tokens']:,} tokens")
    print(f"   • Diferencia: {capabilities['comparison']['gemini_absolute']}")
    print(f"✨ Características:")
    for feature in capabilities["features"]:
        print(f"   • {feature}")
    
    return capabilities

if __name__ == "__main__":
    print("=" * 60)
    print("🔬 PRUEBA DE API GEMINI 1.5 FLASH")
    print("=" * 60)
    
    # Probar API
    api_works = test_gemini()
    
    if api_works:
        print("\n" + "=" * 60)
        print("🎯 IMPLICACIONES PARA NUESTRO PROBLEMA:")
        print("=" * 60)
        
        caps = check_context_capabilities()
        
        print("\n💡 SOLUCIÓN AL LÍMITE DE CONTEXTO:")
        print("1. Gemini 1.5 Flash tiene 1M tokens vs 131K de DeepSeek")
        print("2. 7.6x más capacidad de contexto")
        print("3. Resolvería el problema de reinicios por límite")
        print("4. Podríamos mantener conversaciones MUCHO más largas")
        
        print("\n🚀 RECOMENDACIÓN:")
        print("Implementar Gemini como modelo primario en ClawCore")
        print("Configurar en ~/.clawcore/clawcore.json")
        
        print("\n📋 EJEMPLO DE CONFIGURACIÓN:")
        print('''
{
  "models": {
    "providers": {
      "google": {
        "api": "google-genai",
        "apiKey": "AIzaSyBfgcBLZ0LmPi8MegonEchLjJn4JaAr4PE",
        "models": [
          { "id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash" }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": { "primary": "google/gemini-1.5-flash" }
    }
  }
}
        ''')
    else:
        print("\n❌ API no funcional. Revisar clave o conexión.")
    
    print("\n" + "=" * 60)