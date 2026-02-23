#!/usr/bin/env python3
"""
SISTEMA AUTOMÁTICO DE GESTIÓN DE CONTEXTO
- Se ejecuta automáticamente al iniciar ClawCore
- Limpia contexto si es necesario
- Usa Gemini para mantener continuidad
- Previene límite de 131K tokens
"""

import os
import sys
import json
import requests
import shutil
from datetime import datetime
import subprocess
import time

class AutoContextSystem:
    """Sistema automático que ClawCore puede usar directamente"""
    
    def __init__(self):
        self.gemini_key = "AIzaSyBfgcBLZ0LmPi8MegonEchLjJn4JaAr4PE"
        self.context_file = "/home/ubuntu/.clawcore/workspace/auto_context.json"
        self.flag_file = "/home/ubuntu/.clawcore/context_needs_cleaning.flag"
        
        print("🤖 SISTEMA AUTOMÁTICO DE CONTEXTO")
        print("=" * 50)
    
    def check_and_clean(self):
        """Verificar y limpiar automáticamente si es necesario"""
        
        # 1. Verificar si hay flag de limpieza
        if os.path.exists(self.flag_file):
            print("🚩 Flag detectado: limpieza necesaria")
            return self.clean_context()
        
        # 2. Estimar contexto actual
        estimated = self.estimate_context()
        
        if estimated["tokens"] > 90000:  # 90K tokens
            print(f"⚠️  Contexto alto: {estimated['tokens']:,} tokens")
            
            # Crear flag para próxima ejecución
            with open(self.flag_file, 'w') as f:
                f.write(datetime.now().isoformat())
            
            print("🚩 Flag creado para limpieza en próximo inicio")
            return {
                "action": "flag_created",
                "message": "Contexto alto detectado. Se limpiará en próximo reinicio.",
                "estimated_tokens": estimated["tokens"]
            }
        
        print(f"✅ Contexto OK: {estimated['tokens']:,} tokens")
        return {"action": "none", "status": "ok"}
    
    def clean_context(self):
        """Limpieza automática de contexto"""
        print("🧹 INICIANDO LIMPIEZA AUTOMÁTICA")
        
        try:
            # 1. Estimar contexto actual
            estimated = self.estimate_context()
            
            # 2. Crear resumen con Gemini
            print("🤖 Creando resumen con Gemini...")
            summary = self.create_gemini_summary(estimated["tokens"])
            
            if not summary:
                print("❌ No se pudo crear resumen")
                return {"action": "failed", "error": "gemini_failed"}
            
            # 3. Guardar contexto limpio
            clean_data = {
                "timestamp": datetime.now().isoformat(),
                "original_tokens": estimated["tokens"],
                "summary": summary,
                "compression": estimated["tokens"] / (len(summary) / 4),
                "note": "Generado automáticamente por AutoContextSystem"
            }
            
            with open(self.context_file, 'w') as f:
                json.dump(clean_data, f, indent=2)
            
            # 4. Limpiar archivos de sesión (conservar solo últimos 2)
            self.clean_session_files()
            
            # 5. Eliminar flag
            if os.path.exists(self.flag_file):
                os.remove(self.flag_file)
            
            print(f"✅ LIMPIEZA COMPLETADA")
            print(f"   • Tokens: {estimated['tokens']:,} → ~{len(summary)/4:.0f}")
            print(f"   • Compresión: {clean_data['compression']:.1f}x")
            print(f"   • Resumen: {self.context_file}")
            
            return {
                "action": "cleaned",
                "original_tokens": estimated["tokens"],
                "summary_tokens": len(summary) / 4,
                "compression": clean_data["compression"],
                "summary_file": self.context_file
            }
            
        except Exception as e:
            print(f"❌ Error en limpieza: {e}")
            return {"action": "failed", "error": str(e)}
    
    def estimate_context(self):
        """Estimar tamaño del contexto"""
        try:
            # Buscar archivos de sesión
            session_files = []
            for root, dirs, files in os.walk("/home/ubuntu/.clawcore"):
                for file in files:
                    if file.endswith(".jsonl"):
                        session_files.append(os.path.join(root, file))
            
            total_size = 0
            for file in session_files[:20]:  # Limitar a 20 archivos
                if os.path.exists(file):
                    total_size += os.path.getsize(file)
            
            # Estimación: 1KB ≈ 250 tokens
            estimated_tokens = int((total_size / 1024) * 250)
            
            return {
                "tokens": estimated_tokens,
                "files": len(session_files),
                "size_kb": total_size / 1024
            }
            
        except Exception as e:
            print(f"❌ Error estimando: {e}")
            return {"tokens": 0, "files": 0, "size_kb": 0}
    
    def create_gemini_summary(self, token_count):
        """Crear resumen con Gemini"""
        try:
            prompt = f"""
            Crea un resumen ejecutivo MUY CONCISO (máximo 200 palabras) de la sesión de ClawCore.
            
            Contexto: La sesión tenía aproximadamente {token_count:,} tokens.
            
            El resumen debe capturar solo lo ESENCIAL:
            1. ¿Qué se estaba desarrollando/implementando?
            2. ¿Qué problemas se estaban resolviendo?
            3. ¿Qué decisiones importantes se tomaron?
            4. ¿Qué trabajo queda pendiente?
            
            Formato: Lista concisa de puntos clave.
            
            Resumen:
            """
            
            response = requests.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
                params={"key": self.gemini_key},
                json={
                    "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.1,
                        "maxOutputTokens": 300
                    }
                },
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                if "candidates" in data and len(data["candidates"]) > 0:
                    return data["candidates"][0]["content"]["parts"][0].get("text", "")
            
            return None
            
        except Exception as e:
            print(f"❌ Error Gemini: {e}")
            return None
    
    def clean_session_files(self):
        """Limpiar archivos de sesión antiguos"""
        try:
            # Buscar todos los archivos .jsonl
            all_files = []
            for root, dirs, files in os.walk("/home/ubuntu/.clawcore"):
                for file in files:
                    if file.endswith(".jsonl"):
                        full_path = os.path.join(root, file)
                        mtime = os.path.getmtime(full_path)
                        all_files.append((full_path, mtime))
            
            # Ordenar por fecha (más antiguos primero)
            all_files.sort(key=lambda x: x[1])
            
            # Conservar solo los 2 más recientes, archivar el resto
            if len(all_files) > 2:
                files_to_archive = all_files[:-2]  # Todos excepto los 2 más recientes
                
                for file_path, _ in files_to_archive:
                    if os.path.exists(file_path):
                        # Renombrar en lugar de eliminar
                        backup_name = f"{file_path}.backup_{int(time.time())}"
                        shutil.move(file_path, backup_name)
                
                print(f"   • Archivos conservados: 2")
                print(f"   • Archivos archivados: {len(files_to_archive)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error limpiando archivos: {e}")
            return False
    
    def get_status(self):
        """Obtener estado del sistema"""
        estimated = self.estimate_context()
        needs_cleaning = os.path.exists(self.flag_file)
        
        return {
            "context": estimated,
            "needs_cleaning": needs_cleaning,
            "flag_file": self.flag_file if needs_cleaning else None,
            "clean_context_file": self.context_file if os.path.exists(self.context_file) else None,
            "status": "needs_cleaning" if needs_cleaning else "ok"
        }

def main():
    """Función principal - para ejecución automática"""
    system = AutoContextSystem()
    
    # Verificar argumentos
    if len(sys.argv) > 1:
        if sys.argv[1] == "clean":
            result = system.clean_context()
            print(json.dumps(result, indent=2))
        elif sys.argv[1] == "status":
            status = system.get_status()
            print(json.dumps(status, indent=2))
        elif sys.argv[1] == "check":
            result = system.check_and_clean()
            print(json.dumps(result, indent=2))
        else:
            print("Uso: python3 auto_context_system.py [clean|status|check]")
    else:
        # Ejecución automática (sin argumentos)
        result = system.check_and_clean()
        
        # Mostrar resumen si hay uno
        if os.path.exists(system.context_file):
            with open(system.context_file, 'r') as f:
                data = json.load(f)
                if "summary" in data:
                    print("\n📋 RESUMEN DE CONTINUIDAD:")
                    print("=" * 50)
                    print(data["summary"])
                    print("=" * 50)
        
        return result

if __name__ == "__main__":
    main()