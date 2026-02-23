"""
MEMORIA FEDERADA V5 — Capa de Abstracción de Grafo (Muscle & Connectivity)
Implementa un grafo semántico sobre SQLite para conectar experiencias entre neuronas.
Permite que el conocimiento de 'Trading' sea visible para 'Seguridad' vía Tags.
"""

import sqlite3
import json
import logging
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger("MemoriaFederada")

class MemoriaFederadaGrafo:
    def __init__(self, db_path=None):
        self.db_path = db_path or os.path.expanduser("~/.clawcore/federated_graph.db")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Esquema de Grafo: Nodos y Relaciones (Edges)."""
        conn = sqlite3.connect(self.db_path)
        # Nodos: Pueden ser neuronas, experiencias, conceptos o archivos.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS nodes (
                id TEXT PRIMARY KEY,
                label TEXT,
                type TEXT,
                data TEXT,
                timestamp TEXT
            )
        """)
        # Edges: Relaciones pesadas entre nodos (Tags, dependencia, causalidad).
        conn.execute("""
            CREATE TABLE IF NOT EXISTS edges (
                source TEXT,
                target TEXT,
                weight REAL DEFAULT 1.0,
                relation_type TEXT,
                PRIMARY KEY (source, target, relation_type)
            )
        """)
        conn.commit()
        conn.close()

    def registrar_experiencia(self, neurona_id: str, situacion: str, etiquetas: List[str], metadatos: Dict[str, Any]):
        """Crea un nodo de experiencia y lo conecta con la neurona y sus conceptos (Tags)."""
        conn = sqlite3.connect(self.db_path)
        exp_id = f"exp_{hash(situacion + str(datetime.now())) % 1000000}"
        
        # 1. Registrar Nodo de Experiencia
        conn.execute("INSERT OR REPLACE INTO nodes VALUES (?,?,?,?,?)", 
                     (exp_id, situacion[:50], "EXPERIENCIA", json.dumps(metadatos), datetime.now().isoformat()))
        
        # 2. Conectar con la Neurona de Origen
        conn.execute("INSERT OR REPLACE INTO edges VALUES (?,?,?,?)", 
                     (neurona_id, exp_id, 1.0, "GENERO"))

        # 3. Conectar con Etiquetas (Conceptos Transversales)
        for tag in etiquetas:
            tag_id = f"tag_{tag.lower().strip()}"
            # Asegurar que el nodo de tag existe
            conn.execute("INSERT OR IGNORE INTO nodes VALUES (?,?,?,?,?)",
                         (tag_id, tag, "CONCEPT", "{}", datetime.now().isoformat()))
            # Crear relación semántica
            conn.execute("INSERT OR REPLACE INTO edges VALUES (?,?,?,?)",
                         (exp_id, tag_id, 0.8, "ETIQUETADO_CON"))
        
        conn.commit()
        conn.close()
        logger.info(f"🧬 Nodo de experiencia {exp_id} federado con tags: {etiquetas}")

    def buscar_conocimiento_transversal(self, tag: str) -> List[Dict]:
        """Busca experiencias compartidas por un tag, sin importar qué neurona las generó."""
        conn = sqlite3.connect(self.db_path)
        tag_id = f"tag_{tag.lower().strip()}"
        
        query = """
            SELECT n.id, n.label, n.data, n.type
            FROM nodes n
            JOIN edges e ON n.id = e.source
            WHERE e.target = ? AND e.relation_type = 'ETIQUETADO_CON'
        """
        res = conn.execute(query, (tag_id,)).fetchall()
        conn.close()
        
        return [{"id": r[0], "descripcion": r[1], "metadatos": json.loads(r[2])} for r in res]

    def exportar_vps(self) -> str:
        """Serializa el grafo para sincronización entre VPS132 y VPS229."""
        # En una fase real, esto se enviaría vía P2P o SSH
        conn = sqlite3.connect(self.db_path)
        nodos = conn.execute("SELECT * FROM nodes").fetchall()
        edges = conn.execute("SELECT * FROM edges").fetchall()
        conn.close()
        
        packet = {"nodos": nodos, "edges": edges, "origin": "VPS132"}
        return json.dumps(packet)

# Singleton
memoria_grafo = MemoriaFederadaGrafo()

if __name__ == "__main__":
    # Test de interconexión
    print("🧠 Test de Memoria Federada (Grafo)...")
    memoria_grafo.registrar_experiencia(
        "neurona_trading", 
        "Detección de alta volatilidad en par BTC/USDT", 
        ["RiesgoAlto", "Inestabilidad", "IA_Decision"],
        {"profit_estimado": 0.05}
    )
    
    # Ahora la neurona de Seguridad consulta por 'RiesgoAlto'
    hallazgos = memoria_grafo.buscar_conocimiento_transversal("RiesgoAlto")
    print(f"🔍 Seguridad encontró conocimiento de Trading: {json.dumps(hallazgos, indent=2)}")
