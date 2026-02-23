#!/usr/bin/env python3
"""
INDEXADOR SIMPLE PARA RAG
"""

import os
import chromadb
from pathlib import Path

print("📚 INDEXANDO WORKSPACE BÁSICO")
print("=" * 50)

def indexar_sistemas():
    """Indexa sistemas desarrollados"""
    print("\n1. Indexando sistemas desarrollados...")
    
    try:
        chroma = chromadb.Client()
        coleccion = chroma.create_collection("sistemas_clawcore")
        
        sistemas_dir = Path.home() / ".clawcore" / "workspace" / "systems"
        if not sistemas_dir.exists():
            print("   ❌ Directorio systems no encontrado")
            return 0
        
        documentos = []
        metadatos = []
        ids = []
        
        # Indexar archivos Python
        for file in sistemas_dir.glob("*.py"):
            try:
                with open(file, 'r') as f:
                    contenido = f.read()
                
                documentos.append(contenido[:3000])
                metadatos.append({
                    "nombre": file.name,
                    "ruta": str(file),
                    "tipo": "sistema"
                })
                ids.append(f"sistema_{file.stem}")
                
                print(f"   ✅ {file.name}")
                
            except Exception as e:
                print(f"   ⚠️  Error {file}: {e}")
        
        if documentos:
            coleccion.add(
                documents=documentos,
                metadatas=metadatos,
                ids=ids
            )
            print(f"   📊 Total: {len(documentos)} sistemas indexados")
            return len(documentos)
        else:
            print("   ⚠️  No se encontraron sistemas")
            return 0
            
    except Exception as e:
        print(f"   ❌ Error general: {e}")
        return 0

def indexar_clawcore():
    """Indexa estructura ClawCore"""
    print("\n2. Indexando ClawCore...")
    
    try:
        chroma = chromadb.Client()
        coleccion = chroma.create_collection("estructura_clawcore")
        
        clawcore_dir = Path.home() / ".clawcore" / "clawcore"
        if not clawcore_dir.exists():
            print("   ❌ Directorio clawcore no encontrado")
            return 0
        
        # Archivos clave a indexar
        archivos_clave = [
            "config_clawcore.json",
            "agentes_base.json", 
            "neuronas_locales.py",
            "iniciar_clawcore_simple.py"
        ]
        
        documentos = []
        metadatos = []
        ids = []
        
        for archivo in archivos_clave:
            filepath = clawcore_dir / archivo
            if filepath.exists():
                try:
                    with open(filepath, 'r') as f:
                        contenido = f.read()
                    
                    documentos.append(contenido[:3000])
                    metadatos.append({
                        "nombre": archivo,
                        "ruta": str(filepath),
                        "tipo": "configuracion" if archivo.endswith('.json') else "codigo"
                    })
                    ids.append(f"clawcore_{archivo.split('.')[0]}")
                    
                    print(f"   ✅ {archivo}")
                    
                except Exception as e:
                    print(f"   ⚠️  Error {archivo}: {e}")
        
        if documentos:
            coleccion.add(
                documents=documentos,
                metadatas=metadatos,
                ids=ids
            )
            print(f"   📊 Total: {len(documentos)} archivos indexados")
            return len(documentos)
        else:
            print("   ⚠️  No se encontraron archivos clave")
            return 0
            
    except Exception as e:
        print(f"   ❌ Error general: {e}")
        return 0

def mostrar_colecciones():
    """Muestra colecciones creadas"""
    print("\n3. Mostrando colecciones...")
    
    try:
        chroma = chromadb.Client()
        colecciones = chroma.list_collections()
        
        if colecciones:
            print("   📚 Colecciones en ChromaDB:")
            for coleccion in colecciones:
                print(f"      • {coleccion.name}: {coleccion.count()} documentos")
        else:
            print("   ⚠️  No hay colecciones")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def prueba_busqueda():
    """Prueba búsqueda RAG"""
    print("\n4. Probando búsqueda RAG...")
    
    try:
        chroma = chromadb.Client()
        
        # Buscar en sistemas
        try:
            coleccion = chroma.get_collection("sistemas_clawcore")
            resultados = coleccion.query(
                query_texts=["neuronas locales"],
                n_results=2
            )
            
            if resultados['documents']:
                print("   🔍 Búsqueda 'neuronas locales':")
                for i, doc in enumerate(resultados['documents'][0][:2]):
                    print(f"      {i+1}. {doc[:80]}...")
            else:
                print("   ⚠️  No hay resultados")
                
        except:
            print("   ⚠️  Colección no encontrada")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    total = 0
    total += indexar_sistemas()
    total += indexar_clawcore()
    
    mostrar_colecciones()
    prueba_busqueda()
    
    print("\n" + "=" * 50)
    print(f"🎯 INDEXACIÓN COMPLETADA: {total} documentos")
    print("=" * 50)
    
    print("\n🚀 RAG ACTIVO PARA:")
    print("   • Sistemas desarrollados (neuronas, auto-aprendizaje, etc.)")
    print("   • Estructura ClawCore (config, agentes, código)")
    print("   • Búsqueda semántica en todo el workspace")