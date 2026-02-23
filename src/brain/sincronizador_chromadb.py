#!/usr/bin/env python3
"""
🧠 SINCRONIZADOR CHROMADB (SOBERANO & LOCAL)
Guarda interacciones importantes en una instancia local de ChromaDB.
Eliminadas todas las referencias a VPS externos para garantizar independencia total.
"""

import os
import json
import hashlib
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("ChromaLocal")

class SincronizadorChromaDB:
    """Sincroniza conversaciones importantes de forma local y soberana"""
    
    def __init__(self, db_path=None):
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if db_path is None:
            self.db_path = Path.home() / ".clawcore" / "chroma_data"
        else:
            self.db_path = Path(db_path)
        
        self.db_path.mkdir(exist_ok=True, parents=True)
        
        self.important_topics = [
            "configuración", "decisión", "aprendizaje", "error", "solución",
            "arquitectura", "neurona", "cerebro", "chromadb", "autonomía",
            "versión", "documentación", "problema", "mejora", "plan"
        ]
        
    def es_interaccion_importante(self, texto):
        """Determinar si una interacción debe guardarse en la memoria local"""
        texto_lower = texto.lower()
        return any(topic in texto_lower for topic in self.important_topics) or \
               any(word in texto_lower for word in ["cómo", "por qué", "qué es", "funciona"])

    def generar_id_unico(self, texto, timestamp):
        """Generar ID único para documento"""
        content_hash = hashlib.md5(texto.encode()).hexdigest()[:8]
        return f"{self.session_id}_{content_hash}"

    def guardar_en_chromadb_local(self, texto, metadata=None):
        """Guardar texto en la instancia local de ChromaDB"""
        try:
            import chromadb
            
            # Conectar a ChromaDB local (Soberanía de datos)
            client = chromadb.PersistentClient(path=str(self.db_path))
            collection = client.get_or_create_collection(
                name="clawcore_local_memory",
                metadata={"description": "Memoria soberana de ClawCore"}
            )
            
            doc_id = self.generar_id_unico(texto, datetime.now().isoformat())
            metadata = metadata or {}
            metadata.update({
                "session_id": self.session_id,
                "timestamp": datetime.now().isoformat(),
                "sovereign": "true"
            })
            
            collection.add(
                documents=[texto],
                metadatas=[metadata],
                ids=[doc_id]
            )
            
            logger.info(f"💾 Guardado en memoria local: {doc_id}")
            return True
            
        except ImportError:
            logger.warning("⚠️  ChromaDB no está instalado localmente. Memoria persistente desactivada.")
            return False
        except Exception as e:
            logger.error(f"❌ Error guardando en memoria: {e}")
            return False

    def buscar_en_memoria(self, consulta, n_resultados=3):
        """Buscar en la base de conocimientos local"""
        try:
            import chromadb
            client = chromadb.PersistentClient(path=str(self.db_path))
            collection = client.get_collection(name="clawcore_local_memory")
            
            results = collection.query(
                query_texts=[consulta],
                n_results=n_resultados
            )
            return results
        except:
            return None

    def sincronizar_interaccion(self, pregunta, respuesta, contexto=""):
        """Sincronizar una interacción completa en el almacén local"""
        if not self.es_interaccion_importante(pregunta + " " + respuesta):
            return False
            
        texto_completo = f"P: {pregunta}\nR: {respuesta}"
        if contexto:
            texto_completo = f"C: {contexto}\n{texto_completo}"
            
        return self.guardar_en_chromadb_local(texto_completo)

if __name__ == "__main__":
    sync = SincronizadorChromaDB()
    print("🎯 Sincronizador Local Inicializado (Perímetro Soberano)")
    sync.sincronizar_interaccion("Prueba de independencia", "ClawCore ahora es 100% local.")
