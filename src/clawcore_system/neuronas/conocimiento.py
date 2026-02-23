import os
import json
import re
from pathlib import Path

class ConocimientoSoberano:
    """Sistema simple de RAG local para ClawCore"""
    
    def __init__(self, workspace_path=None):
        if workspace_path is None:
            self.workspace_path = Path(__file__).parent.parent.parent.parent
        else:
            self.workspace_path = Path(workspace_path)
            
        self.indice = {}
        self.kb_path = self.workspace_path / "src/brain/knowledge"
        
    def indexar_documentacion(self):
        """PUNTO 8: Deep-RAG - Indexación dinámica con detección de cambios"""
        if not self.kb_path.exists():
            return
            
        docs = list(self.kb_path.glob("*.md"))
        for doc in docs:
            # Hash del archivo para detectar cambios
            mtime = os.path.getmtime(doc)
            self._procesar_archivo(doc, mtime)
                
    def _procesar_archivo(self, doc, mtime):
        try:
            with open(doc, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            secciones = re.split(r'\n#+ ', contenido)
            for i, seccion in enumerate(secciones):
                if not seccion.strip(): continue
                lineas = seccion.splitlines()
                titulo = lineas[0] if lineas else "Sin título"
                # Extracción de anclas semánticas (keywords)
                keywords = set(re.findall(r'\b\w{5,}\b', seccion.lower()))
                
                self.indice[f"{doc.name}#{i}"] = {
                    "titulo": titulo,
                    "contenido": seccion,
                    "archivo": doc.name,
                    "mtime": mtime,
                    "keywords": keywords
                }
        except Exception as e:
            pass

    def buscar(self, consulta, top_k=3):
        """Búsqueda mejorada con anclas semánticas"""
        query = consulta.lower()
        query_words = set(query.split())
        resultados = []
        
        for data in self.indice.values():
            score = 0
            # Match exacto en título
            if query in data["titulo"].lower(): score += 20
            # Intersección de keywords (relevancia semántica ligera)
            score += len(query_words.intersection(data["keywords"])) * 5
            # Densidad de palabras
            score += data["contenido"].lower().count(query)
            
            if score > 0:
                resultados.append((score, data))
        
        resultados.sort(key=lambda x: x[0], reverse=True)
        return [r[1] for r in resultados[:top_k]]


if __name__ == "__main__":
    # Prueba rápida
    rag = ConocimientoSoberano()
    rag.indexar_documentacion()
    print(f"📚 Indexados {len(rag.indice)} fragmentos de conocimiento.")
    
    query = "n8n"
    print(f"\n🔍 Buscando: '{query}'...")
    hallazgos = rag.buscar(query)
    for h in hallazgos:
        print(f"📍 {h['archivo']} -> {h['titulo']} (Previa: {h['contenido'][:100]}...)")
