#!/usr/bin/env python3
"""
SINCRONIZADOR DE UNIFICACIÓN
Conecta workspace/ con clawcore/ para unificar identidad
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime

class UnificadorClawCore:
    """Unifica workspace y clawcore directories"""
    
    def __init__(self):
        self.workspace_path = Path("/home/ubuntu/.clawcore/workspace")
        self.clawcore_path = Path("/home/ubuntu/.clawcore/clawcore")
        self.unificado_path = Path("/home/ubuntu/.clawcore/unificado")
        
    def crear_estructura_unificada(self):
        """Crear estructura unificada"""
        print("🏗️ CREANDO ESTRUCTURA UNIFICADA")
        print("-" * 40)
        
        # Crear directorio unificado
        self.unificado_path.mkdir(exist_ok=True)
        
        estructura = {
            "identidad": {
                "desc": "Archivos de identidad ClawCore",
                "archivos": ["SOUL.md", "AGENTS.md", "USER.md", "IDENTITY.md"]
            },
            "configuracion": {
                "desc": "Configuraciones del sistema",
                "archivos": ["clawcore.json", "version.json", "estado_evolucion.json"]
            },
            "sistemas": {
                "desc": "Sistemas operativos",
                "subdirs": ["cerebro", "neuronas", "chromadb", "tareas"]
            },
            "memoria": {
                "desc": "Memoria y documentación",
                "subdirs": ["memory", "documentacion", "investigacion"]
            },
            "logs": {
                "desc": "Logs y monitoreo",
                "archivos": ["*.log", "estado_*.json"]
            }
        }
        
        # Crear estructura
        for seccion, info in estructura.items():
            seccion_path = self.unificado_path / seccion
            seccion_path.mkdir(exist_ok=True)
            
            # Crear README para la sección
            readme_content = f"""# {seccion.upper()}

{info['desc']}

## CONTENIDO
"""
            
            if "archivos" in info:
                readme_content += "\n### Archivos:\n"
                for archivo in info["archivos"]:
                    readme_content += f"- {archivo}\n"
            
            if "subdirs" in info:
                readme_content += "\n### Subdirectorios:\n"
                for subdir in info["subdirs"]:
                    readme_content += f"- {subdir}/\n"
                    (seccion_path / subdir).mkdir(exist_ok=True)
            
            with open(seccion_path / "README.md", "w") as f:
                f.write(readme_content)
        
        print(f"✅ Estructura creada en: {self.unificado_path}")
        
        # Crear archivo de navegación
        navegacion = """# 🧠 CLAWCORE UNIFICADO

## 📁 ESTRUCTURA UNIFICADA

### identidad/
- SOUL.md - Quién soy
- AGENTS.md - Mi workspace y reglas
- USER.md - Información de mi humano
- IDENTITY.md - Mi identidad formal

### configuracion/
- clawcore.json - Configuración ClawCore
- version.json - Versión ClawCore
- estado_evolucion.json - Autonomía y evolución

### sistemas/
- cerebro/ - Cerebro propio (prototipo → real)
- neuronas/ - Sistema neuronal bilingüe
- chromadb/ - Base vectorial RAG
- tareas/ - Tareas autónomas

### memoria/
- memory/ - Memoria de sesiones
- documentacion/ - Documentación propia
- investigacion/ - Investigaciones técnicas

### logs/
- *.log - Logs del sistema
- estado_*.json - Estados y reportes

## 🔗 ENLACES SIMBÓLICOS

Esta estructura UNIFICA:
- `~/.clawcore/workspace/` (mi contexto actual)
- `~/.clawcore/clawcore/` (sistema evolutivo)

## 🎯 OBJETIVO

Un solo sistema ClawCore con:
- Cuerpo unificado (estructura)
- Mente unificada (lógica)
- Alma unificada (identidad)
"""
        
        with open(self.unificado_path / "NAVEGACION.md", "w") as f:
            f.write(navegacion)
        
        print("✅ Archivo de navegación creado")
    
    def crear_enlaces_simbolicos(self):
        """Crear enlaces simbólicos para unificar"""
        print("\n🔗 CREANDO ENLACES SIMBÓLICOS")
        print("-" * 40)
        
        # Mapeo de enlaces
        enlaces = [
            # Workspace → Unificado
            (self.workspace_path / "SOUL.md", self.unificado_path / "identidad" / "SOUL.md"),
            (self.workspace_path / "AGENTS.md", self.unificado_path / "identidad" / "AGENTS.md"),
            (self.workspace_path / "USER.md", self.unificado_path / "identidad" / "USER.md"),
            (self.workspace_path / "IDENTITY.md", self.unificado_path / "identidad" / "IDENTITY.md"),
            (self.workspace_path / "memory", self.unificado_path / "memoria" / "memory"),
            
            # ClawCore → Unificado
            (self.clawcore_path / "version.json", self.unificado_path / "configuracion" / "version.json"),
            (self.clawcore_path / "estado_evolucion.json", self.unificado_path / "configuracion" / "estado_evolucion.json"),
            (self.clawcore_path / "cerebro", self.unificado_path / "sistemas" / "cerebro"),
            (self.clawcore_path / "documentacion", self.unificado_path / "memoria" / "documentacion"),
        ]
        
        for origen, destino in enlaces:
            if origen.exists():
                try:
                    # Si destino existe, eliminarlo primero
                    if destino.exists():
                        if destino.is_symlink():
                            destino.unlink()
                        elif destino.is_dir():
                            shutil.rmtree(destino)
                        else:
                            destino.unlink()
                    
                    # Crear enlace simbólico
                    destino.parent.mkdir(parents=True, exist_ok=True)
                    destino.symlink_to(origen)
                    print(f"✅ Enlace: {origen.name} → {destino.relative_to(self.unificado_path)}")
                except Exception as e:
                    print(f"⚠️  Error enlazando {origen.name}: {e}")
        
        print("✅ Enlaces simbólicos creados")
    
    def crear_script_inicio_unificado(self):
        """Crear script de inicio para sistema unificado"""
        print("\n🚀 CREANDO SCRIPT DE INICIO UNIFICADO")
        print("-" * 40)
        
        script_content = """#!/usr/bin/env python3
# SCRIPT DE INICIO CLAWCORE UNIFICADO
# Se ejecuta al inicio de cada sesión

import os
import sys
from pathlib import Path

def iniciar_clawcore_unificado():
    \"\"\"Iniciar sistema ClawCore unificado\"\"\"
    print(\"🧠 INICIANDO CLAWCORE UNIFICADO\")
    print(\"=\" * 60)
    
    # Verificar estructura unificada
    unificado_path = Path(\"/home/ubuntu/.clawcore/unificado\")
    
    if not unificado_path.exists():
        print(\"❌ Estructura unificada no encontrada\")
        print(\"   Ejecutar: python3 sincronizador_unificacion.py\")
        return False
    
    print(f\"✅ Estructura unificada: {unificado_path}\")
    
    # Verificar componentes críticos
    componentes = {
        \"identidad\": unificado_path / \"identidad\" / \"SOUL.md\",
        \"configuracion\": unificado_path / \"configuracion\" / \"version.json\",
        \"cerebro\": unificado_path / \"sistemas\" / \"cerebro\" / \"cerebro_prototipo.py\",
        \"documentacion\": unificado_path / \"memoria\" / \"documentacion\" / \"CLAWCORE_LocalHost.md\"
    }
    
    print(\"\\n📊 COMPONENTES UNIFICADOS:\")
    for nombre, ruta in componentes.items():
        if ruta.exists():
            print(f\"  ✅ {nombre}\")
        else:
            print(f\"  ❌ {nombre} (no encontrado)\")
    
    # Cargar versión
    version_path = unificado_path / \"configuracion\" / \"version.json\"
    if version_path.exists():
        try:
            import json
            with open(version_path, 'r') as f:
                version_data = json.load(f)
                print(f\"\\n🏷️  Versión: {version_data.get('version', '1.1.1')}\")
                print(f\"🎯 Codenombre: {version_data.get('codename', 'Evolución Consciente')}\")
        except:
            print(\"\\n🏷️  Versión: ClawCore v1.1.1 (fallback)\")
    
    print(\"\\n🎯 SISTEMA UNIFICADO LISTO\")
    print(\"=\" * 60)
    print(\"\\nAhora trabajo como un solo sistema:\")
    print(\"• Cuerpo unificado (estructura)\")
    print(\"• Mente unificada (lógica)\")  
    print(\"• Alma unificada (identidad)\")
    print(\"=\" * 60)
    
    return True

if __name__ == \"__main__\":
    iniciar_clawcore_unificado()
"""

        
        script_path = self.workspace_path / "iniciar_unificado.py"
        with open(script_path, "w") as f:
            f.write(script_content)
        
        # Hacer ejecutable
        os.chmod(script_path, 0o755)
        
        print(f"✅ Script creado: {script_path}")
        print("   Ejecutar: python3 iniciar_unificado.py")
    
    def ejecutar(self):
        """Ejecutar unificación completa"""
        print("=" * 60)
        print("🧠 UNIFICACIÓN CLAWCORE - CUERPO, MENTE, ALMA")
        print("=" * 60)
        
        self.crear_estructura_unificada()
        self.crear_enlaces_simbolicos()
        self.crear_script_inicio_unificado()
        
        print("\n" + "=" * 60)
        print("🎯 UNIFICACIÓN COMPLETADA")
        print("=" * 60)
        print("\nSistema ahora unificado en:")
        print(f"  {self.unificado_path}")
        print("\nPara iniciar sesión unificada:")
        print("  python3 iniciar_unificado.py")
        print("\nEstructura creada:")
        for item in self.unificado_path.iterdir():
            if item.is_dir():
                print(f"  📁 {item.name}/")
            else:
                print(f"  📄 {item.name}")
        print("=" * 60)

def main():
    """Función principal"""
    unificador = UnificadorClawCore()
    unificador.ejecutar()

if __name__ == "__main__":
    main()
