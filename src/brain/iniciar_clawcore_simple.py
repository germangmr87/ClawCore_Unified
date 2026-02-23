#!/usr/bin/env python3
"""
INICIALIZADOR CLAWCORE SIMPLE
"""

import os
import sys
import json
from pathlib import Path

print("🚀 INICIANDO CLAWCORE EVOLUTIVO")
print("=" * 50)

class InicializadorClawCore:
    def __init__(self):
        self.base_dir = Path.home() / ".clawcore" / "clawcore"
        
    def verificar_componentes(self):
        """Verifica que todo esté instalado"""
        print("1. Verificando componentes...")
        
        componentes = {
            "Ollama": self._verificar_ollama(),
            "ChromaDB": self._verificar_chromadb(),
            "Sistema neuronal": self._verificar_neuronas(),
            "ClawCore": self._verificar_clawcore()
        }
        
        for nombre, estado in componentes.items():
            print(f"   {nombre}: {'✅' if estado else '❌'}")
        
        return all(componentes.values())
    
    def _verificar_ollama(self):
        """Verifica Ollama"""
        try:
            import subprocess
            result = subprocess.run(["ollama", "list"], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _verificar_chromadb(self):
        """Verifica ChromaDB"""
        try:
            import chromadb
            return True
        except:
            return False
    
    def _verificar_neuronas(self):
        """Verifica sistema neuronal"""
        neurona_file = self.base_dir / "neuronas_locales.py"
        return neurona_file.exists()
    
    def _verificar_clawcore(self):
        """Verifica ClawCore"""
        try:
            import subprocess
            result = subprocess.run(["clawcore", "--version"],
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def crear_configuracion(self):
        """Crea configuración básica"""
        print("\n2. Creando configuración...")
        
        config = {
            "version": "ClawCore Evolutivo 1.0",
            "timestamp": "2026-02-15T20:15:00Z",
            "vps": "127.0.0.1",
            "modelo_primario": "ollama/llama3.2:3b",
            "autonomia_inicial": 0.10,
            "componentes": {
                "ollama": True,
                "chromadb": True,
                "neuronas": True,
                "agentes_modulares": True,
                "rag": True
            },
            "agentes_base": ["frontend", "database", "documentacion"]
        }
        
        config_file = self.base_dir / "config_clawcore.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"   ✅ Configuración: {config_file}")
        return True
    
    def crear_agentes_base(self):
        """Crea definición de agentes base"""
        print("\n3. Creando agentes base...")
        
        agentes = {
            "frontend": {
                "especialidad": "HTML/CSS/JavaScript",
                "archivos": ["*.html", "*.css", "*.js", "*.vue", "*.react"],
                "descripcion": "Especialista en interfaces web"
            },
            "database": {
                "especialidad": "Bases de datos",
                "archivos": ["*.sql", "*.json", "*.yaml", "*.yml"],
                "descripcion": "Especialista en datos y esquemas"
            },
            "documentacion": {
                "especialidad": "Documentación",
                "archivos": ["*.md", "*.txt", "*.rst"],
                "descripcion": "Especialista en documentación"
            }
        }
        
        agentes_file = self.base_dir / "agentes_base.json"
        with open(agentes_file, 'w') as f:
            json.dump(agentes, f, indent=2)
        
        print(f"   ✅ Agentes: {len(agentes)} agentes creados")
        return True
    
    def ejecutar(self):
        """Ejecuta inicialización"""
        print("\n" + "=" * 50)
        
        # Verificar componentes
        if not self.verificar_componentes():
            print("❌ Faltan componentes, revisar instalación")
            return False
        
        # Crear configuración
        self.crear_configuracion()
        
        # Crear agentes
        self.crear_agentes_base()
        
        print("\n" + "=" * 50)
        print("🎯 CLAWCORE EVOLUTIVO INICIALIZADO")
        print("=" * 50)
        
        print(f"\n📍 VPS: 127.0.0.1")
        print(f"🧠 Autonomía: 10%")
        print(f"🤖 IA: Ollama (gratis)")
        print(f"📚 RAG: ChromaDB activo")
        print(f"🔧 Agentes: 3 modulares base")
        
        print("\n🚀 ClawCore listo para la revolución")
        return True

if __name__ == "__main__":
    inicializador = InicializadorClawCore()
    if inicializador.ejecutar():
        sys.exit(0)
    else:
        sys.exit(1)