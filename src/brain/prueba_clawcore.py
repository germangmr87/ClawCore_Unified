#!/usr/bin/env python3
"""
PRUEBA COMPLETA CLAWCORE EVOLUTIVO
"""

import chromadb
import sys
import os

print("🚀 PRUEBA COMPLETA CLAWCORE EVOLUTIVO")
print("=" * 50)

# 1. Probar ChromaDB (RAG)
print("1. Probando ChromaDB (RAG)...")
try:
    client = chromadb.Client()
    collection = client.create_collection("test_clawcore")
    
    # Agregar documentos
    collection.add(
        documents=["ClawCore es un sistema evolutivo con IA local", 
                  "Usa Ollama para IA gratis y ChromaDB para RAG"],
        metadatas=[{"tipo": "descripcion"}, {"tipo": "tecnologia"}],
        ids=["doc1", "doc2"]
    )
    
    # Buscar
    results = collection.query(
        query_texts=["Qué es ClawCore?"],
        n_results=1
    )
    
    print(f"   ✅ RAG funcionando: {results['documents'][0][0][:50]}...")
except Exception as e:
    print(f"   ❌ Error RAG: {e}")

# 2. Probar Ollama (IA local)
print("\n2. Probando Ollama (IA local)...")
try:
    import subprocess
    
    # Usar subprocess para ollama
    result = subprocess.run(
        ["ollama", "run", "llama3.2:3b", "Responde OK si funcionas."],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode == 0:
        print(f"   ✅ Ollama funcionando: {result.stdout[:50]}...")
    else:
        print(f"   ❌ Error Ollama: {result.stderr}")
except Exception as e:
    print(f"   ❌ Error Ollama: {e}")

# 3. Probar sistema neuronal
print("\n3. Probando sistema neuronal...")
try:
    sys.path.append(".")
    from neuronas_locales import decidir_autonomamente, aprender_de_experiencia
    
    decision = decidir_autonomamente(
        "Probar integración ClawCore",
        {"contexto": "prueba", "riesgo": "bajo"}
    )
    print(f"   ✅ Sistema neuronal: {decision[:50]}...")
except Exception as e:
    print(f"   ❌ Error neuronas: {e}")

print("\n" + "=" * 50)
print("🎯 CLAWCORE EVOLUTIVO - PRUEBA COMPLETADA")
print("=" * 50)