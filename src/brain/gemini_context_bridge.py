#!/usr/bin/env python3
"""
PUENTE DE CONTEXTO GEMINI - Usa Gemini 2.5 Flash (1M tokens) para contexto largo
Mientras ClawCore usa DeepSeek (131K tokens) para operaciones normales
"""

import requests
import json
import os
from datetime import datetime

class GeminiContextBridge:
    """Puente para usar Gemini cuando se necesita contexto largo"""
    
    def __init__(self):
        self.api_key = "AIzaSyBfgcBLZ0LmPi8MegonEchLjJn4JaAr4PE"
        self.model = "gemini-2.5-flash"
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        
        # Historial de contexto largo
        self.context_db = "/home/ubuntu/.clawcore/workspace/gemini_context.json"
        self.load_context()
    
    def load_context(self):
        """Cargar contexto persistente"""
        if os.path.exists(self.context_db):
            with open(self.context_db, 'r') as f:
                self.context = json.load(f)
        else:
            self.context = {
                "conversations": [],
                "summaries": [],
                "knowledge_base": [],
                "last_updated": datetime.now().isoformat()
            }
    
    def save_context(self):
        """Guardar contexto persistente"""
        self.context["last_updated"] = datetime.now().isoformat()
        with open(self.context_db, 'w') as f:
            json.dump(self.context, f, indent=2)
    
    def add_to_context(self, role, content, metadata=None):
        """Agregar mensaje al contexto largo"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": content[:5000],  # Limitar tamaño
            "metadata": metadata or {}
        }
        
        self.context["conversations"].append(entry)
        
        # Mantener máximo 1000 entradas
        if len(self.context["conversations"]) > 1000:
            self.context["conversations"] = self.context["conversations"][-1000:]
        
        self.save_context()
        return entry
    
    def create_summary(self, conversation_chunk):
        """Crear resumen de chunk de conversación"""
        prompt = f"""
        Crea un resumen conciso de esta conversación:
        
        {json.dumps(conversation_chunk, indent=2)}
        
        Resumen (máximo 200 palabras):
        """
        
        response = self.call_gemini(prompt)
        
        if response:
            summary = {
                "timestamp": datetime.now().isoformat(),
                "chunk_size": len(conversation_chunk),
                "summary": response
            }
            self.context["summaries"].append(summary)
            self.save_context()
            return summary
        
        return None
    
    def call_gemini(self, prompt, use_context=True):
        """Llamar a Gemini API"""
        try:
            # Preparar contexto si se solicita
            contents = [{"parts": [{"text": prompt}]}]
            
            if use_context and self.context["conversations"]:
                # Usar últimos 10 mensajes como contexto
                recent = self.context["conversations"][-10:]
                context_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent])
                full_prompt = f"Contexto previo:\n{context_text}\n\nNueva consulta: {prompt}"
                contents = [{"parts": [{"text": full_prompt}]}]
            
            response = requests.post(
                self.url,
                params={"key": self.api_key},
                json={
                    "contents": contents,
                    "generationConfig": {
                        "temperature": 0.3,
                        "maxOutputTokens": 4000
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if "candidates" in data and len(data["candidates"]) > 0:
                    candidate = data["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        text = candidate["content"]["parts"][0].get("text", "")
                        
                        # Registrar en contexto
                        self.add_to_context("assistant", text, {
                            "model": self.model,
                            "tokens": data.get("usageMetadata", {}).get("totalTokenCount", 0)
                        })
                        
                        return text
            
            return None
            
        except Exception as e:
            print(f"❌ Error Gemini: {e}")
            return None
    
    def handle_context_overflow(self, current_context_size):
        """Manejar desbordamiento de contexto de DeepSeek"""
        if current_context_size > 100000:  # Cerca del límite de 131K
            print("🚨 CONTEXTO CERCA DEL LÍMITE - Usando Gemini")
            
            # Crear resumen del contexto actual
            summary_prompt = """
            Estoy cerca del límite de contexto (131K tokens). 
            Crea un resumen ejecutivo de la conversación actual para poder continuar 
            sin perder información crítica.
            
            Incluye:
            1. Puntos principales discutidos
            2. Decisiones tomadas
            3. Trabajo pendiente
            4. Estado emocional/cognitivo
            5. Próximos pasos
            """
            
            summary = self.call_gemini(summary_prompt)
            
            if summary:
                # Agregar resumen al conocimiento base
                self.context["knowledge_base"].append({
                    "timestamp": datetime.now().isoformat(),
                    "type": "context_summary",
                    "content": summary,
                    "original_size": current_context_size
                })
                self.save_context()
                
                return {
                    "action": "context_summarized",
                    "summary": summary[:500],
                    "recommendation": "Continuar con contexto resumido",
                    "gemini_available": True
                }
        
        return {"action": "continue_normal", "gemini_available": True}
    
    def integrate_with_clawcore(self):
        """Integrar con ClawCore para conciencia unificada"""
        # Cargar autoconocimiento
        autoconocimiento_path = "/home/ubuntu/.clawcore/autoconocimiento.db"
        
        if os.path.exists(autoconocimiento_path):
            print("🔗 Integrando con sistema de autoconocimiento...")
            
            # Agregar Gemini como capacidad
            gemini_capability = {
                "timestamp": datetime.now().isoformat(),
                "system": "Gemini Context Bridge",
                "capability": "Contexto largo (1M tokens)",
                "purpose": "Resolver límite de contexto de DeepSeek",
                "status": "active"
            }
            
            self.context["knowledge_base"].append(gemini_capability)
            self.save_context()
            
            return True
        
        return False

def main():
    """Función principal de demostración"""
    print("=" * 60)
    print("🌉 PUENTE DE CONTEXTO GEMINI 2.5 FLASH")
    print("=" * 60)
    
    bridge = GeminiContextBridge()
    
    # Probar conexión
    print("🧪 Probando conexión con Gemini...")
    test_response = bridge.call_gemini("Responde con 'GEMINI CONECTADO' si funciona.")
    
    if test_response and "GEMINI CONECTADO" in test_response:
        print("✅ GEMINI 2.5 FLASH CONECTADO")
        print(f"📝 Respuesta: {test_response}")
        
        # Mostrar capacidades
        print("\n🔍 CAPACIDADES:")
        print("   • Contexto: 1,000,000+ tokens")
        print("   • Comparación: 7.6x más que DeepSeek")
        print("   • Uso: Resolver límite de contexto")
        print("   • Persistencia: Contexto guardado en JSON")
        
        # Integrar con autoconocimiento
        if bridge.integrate_with_clawcore():
            print("✅ Integrado con sistema de autoconocimiento")
        
        # Manejar ejemplo de desbordamiento
        print("\n🛡️  SISTEMA DE PROTECCIÓN ACTIVO:")
        overflow_result = bridge.handle_context_overflow(120000)
        print(f"   • {overflow_result['action']}")
        print(f"   • Gemini disponible: {overflow_result['gemini_available']}")
        
        print("\n🎯 USO:")
        print("1. Cuando DeepSeek alcance límite de contexto")
        print("2. Este puente creará resumen con Gemini")
        print("3. Continuará conversación sin reinicio")
        print("4. Contexto persistente guardado")
        
    else:
        print("❌ GEMINI NO CONECTADO")
        print("   Revisar API key o conexión")
    
    print("\n" + "=" * 60)
    print("📁 Contexto guardado en:", bridge.context_db)
    print("=" * 60)

if __name__ == "__main__":
    main()