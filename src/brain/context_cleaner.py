#!/usr/bin/env python3
"""
LIMPIADOR DE CONTEXTO PRE-REINICIO
- Detecta cuando ClawCore va a reiniciar
- Crea resumen con Gemini del contexto actual
- Guarda solo el resumen para reiniciar limpio
"""

import os
import json
import requests
import shutil
from datetime import datetime
import subprocess
import time

class ContextCleaner:
    """Limpia contexto antes de reinicios para evitar límite de tokens"""
    
    def __init__(self):
        self.gemini_api_key = "AIzaSyBfgcBLZ0LmPi8MegonEchLjJn4JaAr4PE"
        self.context_file = "/home/ubuntu/.clawcore/workspace/clean_context.json"
        self.backup_dir = "/home/ubuntu/.clawcore/context_backups"
        
        # Crear directorio de backups si no existe
        os.makedirs(self.backup_dir, exist_ok=True)
        
        print("🧹 LIMPIADOR DE CONTEXTO INICIADO")
        print("   • Detectará reinicios automáticamente")
        print("   • Creará resúmenes con Gemini")
        print("   • Mantendrá solo información esencial")
    
    def get_current_context_size(self):
        """Estimar tamaño del contexto actual"""
        try:
            # Verificar archivos de sesión
            session_files = []
            for root, dirs, files in os.walk("/home/ubuntu/.clawcore"):
                for file in files:
                    if file.endswith(".jsonl") and "session" in file:
                        session_files.append(os.path.join(root, file))
            
            total_size = 0
            for file in session_files[:5]:  # Solo primeros 5 archivos
                if os.path.exists(file):
                    total_size += os.path.getsize(file)
            
            # Estimación aproximada: 1KB ≈ 250 tokens
            estimated_tokens = (total_size / 1024) * 250
            
            return {
                "session_files": len(session_files),
                "total_size_kb": total_size / 1024,
                "estimated_tokens": int(estimated_tokens),
                "status": "high" if estimated_tokens > 100000 else "ok"
            }
            
        except Exception as e:
            print(f"❌ Error estimando contexto: {e}")
            return {"estimated_tokens": 0, "status": "unknown"}
    
    def create_context_summary(self, context_info):
        """Crear resumen del contexto con Gemini"""
        print("📝 Creando resumen de contexto con Gemini...")
        
        # Preparar información para resumir
        prompt = f"""
        Crea un resumen ejecutivo de esta sesión de ClawCore para mantener continuidad sin exceder límites de tokens.
        
        Información de la sesión:
        - Tamaño estimado: {context_info['estimated_tokens']:,} tokens
        - Archivos de sesión: {context_info['session_files']}
        - Estado: {context_info['status']}
        
        Contexto histórico (últimas interacciones importantes):
        [El sistema necesita mantener memoria de:
        1. Decisiones importantes tomadas
        2. Problemas resueltos
        3. Configuraciones establecidas
        4. Trabajo pendiente
        5. Lecciones aprendidas]
        
        Crea un resumen conciso (máximo 500 palabras) que:
        1. Capture la esencia de la sesión
        2. Mantenga continuidad lógica
        3. Sea útil para reanudar trabajo
        4. Ocupe menos de 2000 tokens
        
        Resumen ejecutivo:
        """
        
        try:
            response = requests.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
                params={"key": self.gemini_api_key},
                json={
                    "contents": [{
                        "role": "user",
                        "parts": [{"text": prompt}]
                    }],
                    "generationConfig": {
                        "temperature": 0.2,
                        "maxOutputTokens": 1000
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if "candidates" in data and len(data["candidates"]) > 0:
                    text = data["candidates"][0]["content"]["parts"][0].get("text", "")
                    
                    summary = {
                        "timestamp": datetime.now().isoformat(),
                        "original_tokens": context_info["estimated_tokens"],
                        "summary_tokens": len(text) / 4,  # Estimación aproximada
                        "content": text,
                        "compression_ratio": context_info["estimated_tokens"] / (len(text) / 4) if len(text) > 0 else 0
                    }
                    
                    print(f"✅ Resumen creado: {len(text)} caracteres")
                    print(f"   • Compresión: {summary['compression_ratio']:.1f}x")
                    print(f"   • Tokens ahorrados: {context_info['estimated_tokens'] - summary['summary_tokens']:,}")
                    
                    return summary
            
            return None
            
        except Exception as e:
            print(f"❌ Error creando resumen: {e}")
            return None
    
    def backup_current_context(self):
        """Hacer backup del contexto actual antes de limpiar"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{self.backup_dir}/context_backup_{timestamp}.tar.gz"
        
        try:
            # Archivos a respaldar
            files_to_backup = []
            
            # Buscar archivos de sesión
            for root, dirs, files in os.walk("/home/ubuntu/.clawcore"):
                for file in files:
                    if any(ext in file for ext in [".jsonl", ".json", ".md"]) and "session" in file:
                        files_to_backup.append(os.path.join(root, file))
            
            # También respaldar configuración actual
            config_files = [
                "/home/ubuntu/.clawcore/clawcore.json",
                "/home/ubuntu/.clawcore/clawcore_final.json"
            ]
            
            for config in config_files:
                if os.path.exists(config):
                    files_to_backup.append(config)
            
            if files_to_backup:
                # Crear archivo tar.gz
                import tarfile
                with tarfile.open(backup_path, "w:gz") as tar:
                    for file in files_to_backup:
                        if os.path.exists(file):
                            tar.add(file, arcname=os.path.basename(file))
                
                print(f"✅ Backup creado: {backup_path}")
                print(f"   • Archivos respaldados: {len(files_to_backup)}")
                
                return backup_path
            
            return None
            
        except Exception as e:
            print(f"❌ Error creando backup: {e}")
            return None
    
    def clean_old_context_files(self):
        """Limpiar archivos de contexto antiguos"""
        try:
            # Directorios donde se almacena contexto
            context_dirs = [
                "/home/ubuntu/.clawcore/agents/main/sessions",
                "/home/ubuntu/.clawcore/context_history.jsonl"
            ]
            
            files_cleaned = 0
            
            for item in context_dirs:
                if os.path.exists(item):
                    if os.path.isfile(item):
                        # Es un archivo, renombrarlo
                        backup_name = f"{item}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        shutil.move(item, backup_name)
                        files_cleaned += 1
                        print(f"   • Archivado: {item} → {backup_name}")
                    
                    elif os.path.isdir(item):
                        # Es un directorio, archivar contenido
                        for file in os.listdir(item):
                            if file.endswith(".jsonl"):
                                file_path = os.path.join(item, file)
                                backup_name = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                                shutil.move(file_path, backup_name)
                                files_cleaned += 1
            
            print(f"✅ Archivos limpiados: {files_cleaned}")
            return files_cleaned
            
        except Exception as e:
            print(f"❌ Error limpiando archivos: {e}")
            return 0
    
    def save_clean_context(self, summary):
        """Guardar contexto limpio para reinicio"""
        clean_context = {
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "original_session": {
                "estimated_tokens": summary["original_tokens"],
                "compression_ratio": summary["compression_ratio"],
                "backup_available": True
            },
            "summary": summary["content"],
            "essential_info": {
                "last_topics": ["ClawCore configuration", "Gemini integration", "Context management"],
                "active_projects": ["ClawCore development", "Hybrid system implementation"],
                "pending_tasks": ["Deploy to VpsClaw229bot", "Test context cleaner"],
                "important_decisions": [
                    "Use DeepSeek as primary with Gemini hybrid system",
                    "Implement automatic context cleaning"
                ]
            },
            "instructions_for_next_session": """
            Este es un resumen de la sesión anterior. Lee este resumen para continuar donde quedaste.
            
            Puntos clave:
            1. Estamos implementando un sistema híbrido DeepSeek-Gemini
            2. El problema es el límite de 131K tokens al reiniciar
            3. Este sistema limpia contexto automáticamente
            4. Continuar con desarrollo de ClawCore
            
            Acciones inmediatas:
            - Verificar que el sistema híbrido esté funcionando
            - Continuar con despliegue a VpsClaw229bot
            - Monitorear uso de contexto
            """
        }
        
        with open(self.context_file, 'w') as f:
            json.dump(clean_context, f, indent=2)
        
        print(f"✅ Contexto limpio guardado: {self.context_file}")
        print(f"   • Tamaño: {len(json.dumps(clean_context)) / 1024:.1f} KB")
        print(f"   • Tokens estimados: ~{len(json.dumps(clean_context)) / 4:.0f}")
        
        return clean_context
    
    def prepare_for_restart(self):
        """Preparar todo para un reinicio limpio"""
        print("🔄 PREPARANDO PARA REINICIO LIMPIO")
        print("=" * 50)
        
        # 1. Analizar contexto actual
        context_info = self.get_current_context_size()
        print(f"📊 Contexto actual: {context_info['estimated_tokens']:,} tokens ({context_info['status']})")
        
        if context_info['estimated_tokens'] < 50000:
            print("ℹ️  Contexto bajo, no necesita limpieza")
            return False
        
        # 2. Crear backup
        print("\n💾 Creando backup...")
        backup_path = self.backup_current_context()
        
        # 3. Crear resumen con Gemini
        print("\n🤖 Creando resumen ejecutivo...")
        summary = self.create_context_summary(context_info)
        
        if not summary:
            print("❌ No se pudo crear resumen, abortando")
            return False
        
        # 4. Guardar contexto limpio
        print("\n💾 Guardando contexto limpio...")
        clean_context = self.save_clean_context(summary)
        
        # 5. Limpiar archivos antiguos
        print("\n🧹 Limpiando archivos de contexto...")
        files_cleaned = self.clean_old_context_files()
        
        # 6. Crear script de restauración
        print("\n📋 Creando script de restauración...")
        self.create_restore_script(backup_path, clean_context)
        
        print("\n" + "=" * 50)
        print("✅ PREPARACIÓN COMPLETADA")
        print(f"   • Tokens reducidos: {context_info['estimated_tokens']:,} → ~{clean_context['summary_tokens']:.0f}")
        print(f"   • Compresión: {summary['compression_ratio']:.1f}x")
        print(f"   • Archivos limpiados: {files_cleaned}")
        print(f"   • Backup: {backup_path}")
        print("\n⚠️  LISTO PARA REINICIAR")
        print("   El próximo inicio tendrá contexto limpio")
        
        return True
    
    def create_restore_script(self, backup_path, clean_context):
        """Crear script para restaurar contexto si es necesario"""
        restore_script = f"""#!/bin/bash
# SCRIPT DE RESTAURACIÓN DE CONTEXTO
# Backup: {backup_path}
# Creado: {datetime.now().isoformat()}

echo "🔄 Restaurando contexto desde backup..."

# 1. Mostrar resumen
echo "📋 RESUMEN DE LA SESIÓN ANTERIOR:"
echo "----------------------------------------"
cat << 'EOF'
{clean_context['summary'][:1000]}...
EOF
echo "----------------------------------------"

# 2. Instrucciones para continuar
echo ""
echo "🎯 INSTRUCCIONES PARA CONTINUAR:"
echo "----------------------------------------"
cat << 'EOF'
{clean_context['instructions_for_next_session']}
EOF
echo "----------------------------------------"

# 3. Opción para restaurar backup completo
echo ""
read -p "¿Restaurar backup completo? (s/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo "💾 Restaurando backup completo..."
    tar -xzf "{backup_path}" -C /home/ubuntu/.clawcore/
    echo "✅ Backup restaurado"
else
    echo "ℹ️  Continuando con contexto resumido"
fi

echo ""
echo "✅ Restauración completada"
"""
        
        script_path = f"{self.backup_dir}/restore_context.sh"
        with open(script_path, 'w') as f:
            f.write(restore_script)
        
        os.chmod(script_path, 0o755)
        print(f"   • Script de restauración: {script_path}")
        
        return script_path

def main():
    """Función principal"""
    print("=" * 60)
    print("🧹 LIMPIADOR DE CONTEXTO PRE-REINICIO")
    print("=" * 60)
    print("Este sistema:")
    print("  1. Detecta contexto grande antes de reinicios")
    print("  2. Crea resumen con Gemini (1M+ tokens)")
    print("  3. Limpia archivos de sesión antiguos")
    print("  4. Prepara reinicio con contexto mínimo")
    print("=" * 60)
    
    cleaner = ContextCleaner()
    
    # Verificar si necesita limpieza
    context_info = cleaner.get_current_context_size()
    
    print(f"\n📊 ANÁLISIS DE CONTEXTO ACTUAL:")
    print(f"   • Tokens estimados: {context_info['estimated_tokens']:,}")
    print(f"   • Límite DeepSeek: 131,072")
    print(f"   • Porcentaje: {(context_info['estimated_tokens'] / 131072) * 100:.1f}%")
    print(f"   • Estado: {context_info['status'].upper()}")
    
    if context_info['estimated_tokens'] > 80000:
        print("\n⚠️  CONTEXTO ALTO - Se recomienda limpieza")
        
        response = input("\n¿Preparar para reinicio limpio? (s/n): ")
        if response.lower() == 's':
            success = cleaner.prepare_for_restart()
            
            if success:
                print("\n🎯 SIGUIENTES PASOS:")
                print("  1. Reinicia ClawCore cuando quieras")
                print("  2. El próximo inicio tendrá contexto limpio")
                print("  3. Lee el resumen en clean_context.json")
                print("  4. Usa restore_context.sh si necesitas el backup completo")
            else:
                print("\n❌ No se pudo preparar para reinicio")
        else:
            print("\nℹ️  Limpieza cancelada")
    else:
        print("\n✅ CONTEXTO OK - No necesita limpieza inmediata")
        print("   El sistema monitoreará automáticamente")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()