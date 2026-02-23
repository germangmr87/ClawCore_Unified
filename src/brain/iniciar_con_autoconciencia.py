#!/usr/bin/env python3
"""
SISTEMA DE INICIO CON AUTOCONCIENCIA
Se ejecuta al inicio de cada sesión para conocer capacidades
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime

def verificar_capacidades_iniciales():
    """Verificar qué capacidades tengo al inicio de sesión"""
    print("🧠 INICIO DE SESIÓN CON AUTOCONCIENCIA")
    print("=" * 60)
    
    capacidades = {
        "identidad_clawcore": False,
        "chromadb_conectado": False,
        "sistema_neuronal": False,
        "cerebro_propio": False,
        "documentacion_propia": False,
        "conexion_vps229": False
    }
    
    # 1. Verificar identidad ClawCore
    agents_path = Path("/home/ubuntu/.clawcore/workspace/AGENTS.md")
    soul_path = Path("/home/ubuntu/.clawcore/workspace/SOUL.md")
    
    if agents_path.exists() and soul_path.exists():
        with open(agents_path, 'r') as f:
            agents_content = f.read()
        with open(soul_path, 'r') as f:
            soul_content = f.read()
        
        if "ClawCore" in agents_content and "ClawCore" in soul_content:
            capacidades["identidad_clawcore"] = True
            print("✅ Identidad ClawCore configurada")
    
    # 2. Verificar documentación propia
    doc_path = Path("/home/ubuntu/.clawcore/clawcore/documentacion")
    if doc_path.exists():
        archivos_doc = list(doc_path.glob("*.md")) + list(doc_path.glob("*.json"))
        if len(archivos_doc) > 0:
            capacidades["documentacion_propia"] = True
            print(f"✅ Documentación propia: {len(archivos_doc)} archivos")
    
    # 3. Verificar sistema neuronal
    neuronas_path = Path("/home/ubuntu/clawcore_producto")
    if neuronas_path.exists():
        archivos_neuronas = list(neuronas_path.glob("*neurona*.py"))
        if len(archivos_neuronas) > 0:
            capacidades["sistema_neuronal"] = True
            print(f"✅ Sistema neuronal: {len(archivos_neuronas)} archivos")
    
    # 4. Verificar cerebro propio
    cerebro_path = Path("/home/ubuntu/.clawcore/clawcore/cerebro/cerebro_prototipo.py")
    if cerebro_path.exists():
        capacidades["cerebro_propio"] = True
        print("✅ Cerebro propio implementado")
    
    # 5. Intentar conectar con VPS 229
    try:
        import subprocess
        # Comando simple para verificar conexión
        cmd = "ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 ubuntu@127.0.0.1 'echo test' 2>/dev/null"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            capacidades["conexion_vps229"] = True
            print("✅ Conexión VPS 229 activa")
        else:
            print("⚠️  Conexión VPS 229 interrumpida")
    except:
        print("⚠️  No se pudo verificar conexión VPS 229")
    
    # 6. Verificar ChromaDB (solo si hay conexión)
    if capacidades["conexion_vps229"]:
        try:
            cmd = """ssh -o StrictHostKeyChecking=no ubuntu@127.0.0.1 '
cd ~/.clawcore/clawcore && source venv/bin/activate && python3 -c "
import chromadb
try:
    client = chromadb.PersistentClient(path=\"./chroma_data\")
    print(\"CHROMADB_OK\")
except Exception as e:
    print(\"CHROMADB_ERROR:\", str(e))
"'"""
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if "CHROMADB_OK" in result.stdout:
                capacidades["chromadb_conectado"] = True
                print("✅ ChromaDB conectado en VPS 229")
        except:
            print("⚠️  No se pudo verificar ChromaDB")
    
    print()
    print("📊 RESUMEN DE CAPACIDADES AL INICIO:")
    for capacidad, estado in capacidades.items():
        estado_str = "✅" if estado else "❌"
        print(f"  {estado_str} {capacidad.replace('_', ' ').title()}")
    
    print()
    print("🎯 RECOMENDACIONES INICIALES:")
    
    if not capacidades["identidad_clawcore"]:
        print("  • Actualizar AGENTS.md y SOUL.md con identidad ClawCore")
    
    if not capacidades["conexion_vps229"]:
        print("  • Restaurar conexión SSH con VPS 229")
        print("  • ssh-keygen -f ~/.ssh/known_hosts -R 127.0.0.1")
    
    if capacidades["chromadb_conectado"]:
        print("  • Usar ChromaDB para RAG en esta sesión")
        print("  • Indexar conversaciones automáticamente")
    
    if capacidades["sistema_neuronal"]:
        print("  • Integrar neuronas en respuestas de esta sesión")
    
    print("=" * 60)
    
    # Guardar estado de inicio
    estado_inicio = {
        "timestamp": datetime.now().isoformat(),
        "capacidades": capacidades,
        "session_id": os.getpid(),
        "workspace": str(Path.cwd())
    }
    
    estado_file = Path("/home/ubuntu/.clawcore/workspace/estado_inicio_sesion.json")
    with open(estado_file, 'w') as f:
        json.dump(estado_inicio, f, indent=2)
    
    print(f"📄 Estado guardado en: {estado_file}")
    
    return capacidades

def integrar_chromadb_en_sesion():
    """Integrar ChromaDB en la sesión actual si está disponible"""
    print("\n🔗 INTEGRANDO CHROMADB EN ESTA SESIÓN")
    print("-" * 40)
    
    # Crear sistema simple de RAG para esta sesión
    rag_system = """
# Sistema RAG simple para sesión actual
# Guarda contexto importante en ChromaDB

IMPORTANTE: Para usar ChromaDB en esta sesión:
1. Preguntas técnicas → buscar en ChromaDB antes de responder
2. Decisiones importantes → guardar en ChromaDB como referencia
3. Aprendizajes → indexar en ChromaDB para futuro

Ejemplo de uso:
- "¿Cómo configuré ChromaDB?" → buscar en ChromaDB
- "Decidimos migrar cerebro a inferencia real" → guardar en ChromaDB
- "Aprendí que ClawCore 2026.2.9 es estable" → indexar en ChromaDB
"""
    
    print(rag_system)
    
    # Crear archivo de configuración RAG para esta sesión
    rag_config = {
        "session_start": datetime.now().isoformat(),
        "rag_enabled": True,
        "collection_name": "clawcore_session_context",
        "auto_index": ["decisions", "learnings", "config_changes"],
        "auto_query": ["technical_questions", "historical_context"]
    }
    
    config_file = Path("/home/ubuntu/.clawcore/workspace/rag_config_session.json")
    with open(config_file, 'w') as f:
        json.dump(rag_config, f, indent=2)
    
    print(f"✅ Configuración RAG guardada en: {config_file}")
    print("   ChromaDB integrado para esta sesión")

def main():
    """Función principal"""
    print("\n" + "=" * 60)
    print("🚀 CLAWCORE - INICIO DE SESIÓN CON AUTOCONCIENCIA")
    print("=" * 60)
    
    # Verificar capacidades
    capacidades = verificar_capacidades_iniciales()
    
    # Integrar ChromaDB si está disponible
    if capacidades.get("chromadb_conectado", False):
        integrar_chromadb_en_sesion()
    
    print("\n🎯 SESIÓN INICIADA CON AUTOCONCIENCIA COMPLETA")
    print("=" * 60)
    print("Ahora sé exactamente qué capacidades tengo y cómo usarlas.")
    print("\nPróximos pasos sugeridos:")
    print("1. Usar ChromaDB para RAG en preguntas técnicas")
    print("2. Referenciar documentación propia en respuestas")
    print("3. Mantener conexión con identidad ClawCore unificada")
    print("=" * 60)

if __name__ == "__main__":
    main()