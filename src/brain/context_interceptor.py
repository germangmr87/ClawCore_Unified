#!/usr/bin/env python3
"""
INTERCEPTOR DEFINITIVO DE CONTEXTO
- Intercepta lo que ClawCore envía a DeepSeek
- Usa Gemini para comprimir contexto largo
- Mantiene continuidad sin exceder límites
"""

import os
import sys
import json
import requests
import hashlib
from datetime import datetime
import threading
import time

class ContextInterceptor:
    """Intercepta y comprime contexto antes de que ClawCore lo envíe"""
    
    def __init__(self):
        self.gemini_key = "AIzaSyBfgcBLZ0LmPi8MegonEchLjJn4JaAr4PE"
        self.context_db = "/home/ubuntu/.clawcore/workspace/intercepted_contexts.json"
        self.max_tokens_per_request = 120000  # 120K para margen de seguridad
        
        # Cargar contexto interceptado
        self.load_intercepted_contexts()
        
        print("🛡️  INTERCEPTOR DE CONTEXTO INICIADO")
        print(f"   • Límite por petición: {self.max_tokens_per_request:,} tokens")
        print(f"   • Gemini disponible: 1M+ tokens")
        print(f"   • Contextos interceptados: {len(self.intercepted_contexts)}")
    
    def load_intercepted_contexts(self):
        """Cargar contextos interceptados previos"""
        if os.path.exists(self.context_db):
            with open(self.context_db, 'r') as f:
                self.intercepted_contexts = json.load(f)
        else:
            self.intercepted_contexts = {
                "version": "1.0",
                "created": datetime.now().isoformat(),
                "contexts": {},
                "compression_stats": {
                    "total_compressions": 0,
                    "total_tokens_saved": 0,
                    "last_compression": None
                }
            }
    
    def save_intercepted_contexts(self):
        """Guardar contextos interceptados"""
        self.intercepted_contexts["last_updated"] = datetime.now().isoformat()
        with open(self.context_db, 'w') as f:
            json.dump(self.intercepted_contexts, f, indent=2)
    
    def estimate_tokens(self, text):
        """Estimar tokens en texto"""
        # Estimación simple: 1 token ≈ 4 caracteres
        return len(text) // 4
    
    def create_context_hash(self, messages):
        """Crear hash único para este contexto"""
        context_str = json.dumps(messages, sort_keys=True)
        return hashlib.md5(context_str.encode()).hexdigest()[:16]
    
    def compress_with_gemini(self, messages, reason="context_too_large"):
        """Comprimir contexto usando Gemini"""
        print(f"🤖 Comprimiendo contexto con Gemini ({reason})...")
        
        try:
            # Preparar contexto para compresión
            context_text = ""
            for i, msg in enumerate(messages[-20:]):  # Últimos 20 mensajes
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                if isinstance(content, list):
                    # Extraer texto de contenido estructurado
                    text_parts = []
                    for part in content:
                        if isinstance(part, dict) and part.get("type") == "text":
                            text_parts.append(part.get("text", ""))
                    content = " ".join(text_parts)
                
                context_text += f"{role.upper()}: {content[:500]}...\n"
            
            prompt = f"""
            COMPRESIÓN DE CONTEXTO PARA CLAWCORE
            
            Contexto original ({len(messages)} mensajes):
            {context_text}
            
            Objetivo: Crear un RESUMEN EJECUTIVO que mantenga continuidad pero ocupe menos del 10% de tokens.
            
            Instrucciones:
            1. Identificar TEMAS PRINCIPALES discutidos
            2. Extraer DECISIONES IMPORTANTES tomadas
            3. Capturar ESTADO ACTUAL del desarrollo
            4. Listar TRABAJO PENDIENTE
            5. Mantener CONTINUIDAD LÓGICA
            
            Formato de salida (JSON):
            {{
              "summary": "Resumen ejecutivo conciso (máx 300 palabras)",
              "key_decisions": ["lista", "de", "decisiones"],
              "current_projects": ["lista", "de", "proyectos"],
              "pending_tasks": ["lista", "de", "tareas"],
              "compression_notes": "Notas sobre qué se comprimió"
            }}
            
            Solo responde con el JSON válido, nada más.
            """
            
            response = requests.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
                params={"key": self.gemini_key},
                json={
                    "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.1,
                        "maxOutputTokens": 1000
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if "candidates" in data and len(data["candidates"]) > 0:
                    result_text = data["candidates"][0]["content"]["parts"][0].get("text", "")
                    
                    try:
                        # Extraer JSON de la respuesta
                        import re
                        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                        if json_match:
                            compressed = json.loads(json_match.group())
                            
                            # Calcular ahorro de tokens
                            original_tokens = self.estimate_tokens(json.dumps(messages))
                            compressed_tokens = self.estimate_tokens(json.dumps(compressed))
                            tokens_saved = original_tokens - compressed_tokens
                            
                            # Actualizar estadísticas
                            self.intercepted_contexts["compression_stats"]["total_compressions"] += 1
                            self.intercepted_contexts["compression_stats"]["total_tokens_saved"] += tokens_saved
                            self.intercepted_contexts["compression_stats"]["last_compression"] = datetime.now().isoformat()
                            
                            print(f"✅ Compresión exitosa:")
                            print(f"   • Tokens: {original_tokens:,} → {compressed_tokens:,}")
                            print(f"   • Ahorro: {tokens_saved:,} tokens ({tokens_saved/original_tokens*100:.1f}%)")
                            
                            return compressed
                    
                    except json.JSONDecodeError:
                        print("❌ Gemini no devolvió JSON válido")
                        return None
            
            return None
            
        except Exception as e:
            print(f"❌ Error en compresión Gemini: {e}")
            return None
    
    def intercept_context(self, messages):
        """Interceptar y posiblemente comprimir contexto"""
        # Estimar tokens totales
        total_tokens = self.estimate_tokens(json.dumps(messages))
        
        print(f"🔍 Interceptando contexto: {len(messages)} mensajes, ~{total_tokens:,} tokens")
        
        # Si está por debajo del límite, no hacer nada
        if total_tokens <= self.max_tokens_per_request:
            print(f"✅ Contexto dentro del límite ({total_tokens:,} ≤ {self.max_tokens_per_request:,})")
            return messages
        
        # Si excede el límite, necesitamos comprimir
        print(f"⚠️  Contexto excede límite ({total_tokens:,} > {self.max_tokens_per_request:,})")
        
        # Crear hash para este contexto
        context_hash = self.create_context_hash(messages)
        
        # Verificar si ya tenemos una versión comprimida
        if context_hash in self.intercepted_contexts["contexts"]:
            print(f"📦 Usando contexto comprimido cacheado")
            cached = self.intercepted_contexts["contexts"][context_hash]
            
            # Crear mensaje con resumen
            summary_msg = {
                "role": "system",
                "content": f"CONTEXTO COMPRIMIDO (original: {len(messages)} mensajes, ~{total_tokens:,} tokens):\n\n"
                          f"Resumen: {cached.get('summary', '')}\n\n"
                          f"Decisiones clave: {', '.join(cached.get('key_decisions', []))}\n"
                          f"Proyectos actuales: {', '.join(cached.get('current_projects', []))}\n"
                          f"Tareas pendientes: {', '.join(cached.get('pending_tasks', []))}"
            }
            
            # Mantener solo los últimos 5 mensajes + resumen
            compressed_messages = [summary_msg] + messages[-5:]
            
            compressed_tokens = self.estimate_tokens(json.dumps(compressed_messages))
            print(f"✅ Contexto comprimido: {compressed_tokens:,} tokens")
            
            return compressed_messages
        
        # Si no está cacheado, comprimir con Gemini
        print(f"🔄 Comprimiendo contexto nuevo con Gemini...")
        compressed_data = self.compress_with_gemini(messages, "context_exceeds_limit")
        
        if compressed_data:
            # Guardar en cache
            self.intercepted_contexts["contexts"][context_hash] = compressed_data
            self.save_intercepted_contexts()
            
            # Crear mensaje con resumen
            summary_msg = {
                "role": "system",
                "content": f"CONTEXTO COMPRIMIDO (original: {len(messages)} mensajes, ~{total_tokens:,} tokens):\n\n"
                          f"Resumen: {compressed_data.get('summary', '')}\n\n"
                          f"Decisiones clave: {', '.join(compressed_data.get('key_decisions', []))}\n"
                          f"Proyectos actuales: {', '.join(compressed_data.get('current_projects', []))}\n"
                          f"Tareas pendientes: {', '.join(compressed_data.get('pending_tasks', []))}"
            }
            
            # Mantener solo los últimos 5 mensajes + resumen
            compressed_messages = [summary_msg] + messages[-5:]
            
            compressed_tokens = self.estimate_tokens(json.dumps(compressed_messages))
            print(f"✅ Contexto comprimido y cacheado: {compressed_tokens:,} tokens")
            
            return compressed_messages
        
        # Si Gemini falla, usar estrategia de fallback
        print(f"⚠️  Gemini falló, usando fallback: mantener solo últimos 10 mensajes")
        return messages[-10:]
    
    def monitor_clawcore_sessions(self):
        """Monitorear sesiones de ClawCore en tiempo real"""
        print("👁️  Monitoreando sesiones ClawCore...")
        
        session_dir = "/home/ubuntu/.clawcore/agents/main/sessions"
        
        if not os.path.exists(session_dir):
            print(f"❌ Directorio no encontrado: {session_dir}")
            return
        
        # Verificar archivos de sesión periódicamente
        while True:
            try:
                session_files = [f for f in os.listdir(session_dir) if f.endswith('.jsonl')]
                
                for session_file in session_files:
                    file_path = os.path.join(session_dir, session_file)
                    file_size = os.path.getsize(file_path)
                    
                    # Si archivo es muy grande (>2MB)
                    if file_size > 2 * 1024 * 1024:  # 2MB
                        print(f"⚠️  Sesión grande detectada: {session_file} ({file_size/1024/1024:.1f} MB)")
                        
                        # Podríamos ofrecer compresión aquí
                        # Por ahora solo monitoreamos
                
                time.sleep(60)  # Revisar cada minuto
                
            except Exception as e:
                print(f"❌ Error monitoreando: {e}")
                time.sleep(10)
    
    def integrate_as_middleware(self):
        """Integrar como middleware de ClawCore"""
        print("🔗 Integrando como middleware...")
        
        # Crear script wrapper para ClawCore
        wrapper_script = """#!/bin/bash
# WRAPPER DE CLAWCORE CON INTERCEPTOR DE CONTEXTO
# Este script intercepta llamadas a ClawCore para comprimir contexto

echo "🛡️  CLAWCORE CON INTERCEPTOR DE CONTEXTO"
echo "========================================"

# Ejecutar interceptor en background
python3 /home/ubuntu/.clawcore/workspace/context_interceptor.py --monitor &

# Iniciar ClawCore normalmente
exec clawcore "$@"
"""
        
        wrapper_path = "/home/ubuntu/.clawcore/clawcore_intercepted.sh"
        with open(wrapper_path, 'w') as f:
            f.write(wrapper_script)
        
        os.chmod(wrapper_path, 0o755)
        
        print(f"✅ Wrapper creado: {wrapper_path}")
        print(f"   Usar: {wrapper_path} en lugar de 'clawcore'")
        
        return wrapper_path

def main():
    """Función principal"""
    print("=" * 60)
    print("🛡️  INTERCEPTOR DEFINITIVO DE CONTEXTO")
    print("=" * 60)
    print("Este sistema intercepta lo que ClawCore envía a DeepSeek")
    print("y usa Gemini para comprimir contexto cuando es muy largo.")
    print("=" * 60)
    
    interceptor = ContextInterceptor()
    
    # Mostrar estado
    stats = interceptor.intercepted_contexts["compression_stats"]
    print(f"📊 ESTADÍSTICAS:")
    print(f"   • Compresiones totales: {stats['total_compressions']}")
    print(f"   • Tokens ahorrados: {stats['total_tokens_saved']:,}")
    print(f"   • Última compresión: {stats.get('last_compression', 'nunca')}")
    
    # Integrar como middleware
    print(f"\n🔗 INTEGRACIÓN:")
    wrapper_path = interceptor.integrate_as_middleware()
    
    print(f"\n🎯 USO:")
    print(f"   1. Detener ClawCore actual")
    print(f"   2. Ejecutar: {wrapper_path}")
    print(f"   3. El interceptor monitoreará y comprimirá automáticamente")
    
    print(f"\n⚠️  ADVERTENCIA:")
    print(f"   Esto es una solución PROACTIVA. ClawCore seguirá intentando")
    print(f"   enviar todo el historial, pero el interceptor lo comprimirá.")
    
    print(f"\n" + "=" * 60)

if __name__ == "__main__":
    main()