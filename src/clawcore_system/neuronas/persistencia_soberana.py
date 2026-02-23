import sqlite3
import json
import logging
import threading
import os
from pathlib import Path
from datetime import datetime

# Audit: Logging de Alta Carga - Filtrar telemetría redundante
logger = logging.getLogger("PersistenciaSoberana")
logger.setLevel(logging.WARNING) 

class PersistenciaSoberana:
    """
    SISTEMA DE PERSISTENCIA CRÍTICA V4.5 (Audit Compliance)
    Standard Industrial: Conexión persistente, Thread-Safe, Gating de permisos.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(PersistenciaSoberana, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, db_path=None):
        if self._initialized: return
        
        if db_path is None:
            self.db_path = Path.home() / ".clawcore" / "clawcore_memory.db"
        else:
            self.db_path = Path(db_path)
            
        self.db_path.parent.mkdir(exist_ok=True, parents=True)
        
        # Audit: Conexión persistente con Thread Safety
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._inicializar_db()
        self._ensure_permissions()
        self._initialized = True

    def _ensure_permissions(self):
        """Asegura permisos 0600 (Audit: Seguridad)"""
        try:
            os.chmod(self.db_path, 0o600)
        except:
            pass

    def _inicializar_db(self):
        """Crea las tablas y configura performance (Audit: Concurrencia)"""
        with self._lock:
            # Audit: Busy timeout para evitar 'Database is locked' en swarms
            self.conn.execute("PRAGMA busy_timeout = 5000")
            self.conn.execute("PRAGMA journal_mode = WAL")
            self.conn.execute("PRAGMA synchronous = NORMAL")
            
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS neuronas (
                    id TEXT PRIMARY KEY,
                    datos_json TEXT NOT NULL
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS experiencias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    neurona_id TEXT,
                    situacion TEXT,
                    decision TEXT,
                    exito INTEGER,
                    timestamp TEXT,
                    entrada_hash TEXT
                )
            """)
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_hash ON experiencias(entrada_hash)")
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS estado_sistema (
                    clave TEXT PRIMARY KEY,
                    valor TEXT
                )
            """)
            self.conn.commit()

    def guardar_neurona(self, neurona_id, datos):
        """Persiste el estado de una neurona."""
        with self._lock:
            try:
                self.conn.execute(
                    "INSERT OR REPLACE INTO neuronas (id, datos_json) VALUES (?, ?)",
                    (neurona_id, json.dumps(datos))
                )
                self.conn.commit()
            except Exception as e:
                logger.error(f"Error guardando neurona {neurona_id}: {e}")

    def guardar_experiencia(self, neurona_id, situacion, decision, exito, entrada_hash):
        """Registra una experiencia de forma transaccional."""
        with self._lock:
            try:
                self.conn.execute(
                    "INSERT INTO experiencias (neurona_id, situacion, decision, exito, timestamp, entrada_hash) VALUES (?, ?, ?, ?, ?, ?)",
                    (neurona_id, situacion, decision, 1 if exito else 0, datetime.now().isoformat(), entrada_hash)
                )
                self.conn.commit()
            except Exception as e:
                logger.error(f"Error guardando experiencia: {e}")

    def buscar_experiencia(self, entrada_hash):
        """Búsqueda eficiente indexada."""
        with self._lock:
            cursor = self.conn.execute(
                "SELECT decision, exito FROM experiencias WHERE entrada_hash = ? ORDER BY id DESC LIMIT 1",
                (entrada_hash,)
            )
            res = cursor.fetchone()
            return (res['decision'], res['exito']) if res else None

    def guardar_estado_global(self, clave, valor):
        with self._lock:
            self.conn.execute(
                "INSERT OR REPLACE INTO estado_sistema (clave, valor) VALUES (?, ?)",
                (clave, str(valor))
            )
            self.conn.commit()

    def cargar_estado_global(self, clave, default=None):
        with self._lock:
            cursor = self.conn.execute("SELECT valor FROM estado_sistema WHERE clave = ?", (clave,))
            res = cursor.fetchone()
            return res['valor'] if res else default

    def cargar_todas_neuronas(self):
        """Recupera el mapa con validación de esquema (Audit: Integridad)"""
        with self._lock:
            cursor = self.conn.execute("SELECT id, datos_json FROM neuronas")
            mapa = {}
            for row in cursor.fetchall():
                try:
                    mapa[row['id']] = json.loads(row['datos_json'])
                except (json.JSONDecodeError, TypeError):
                    logger.error(f"Esquema corrupto en neurona {row['id']}")
            return mapa

    def podar_experiencias(self, neurona_id, limite=50):
        """Poda transaccional atómica (Audit: Ineficiencia)."""
        with self._lock:
            self.conn.execute(f"""
                DELETE FROM experiencias 
                WHERE neurona_id = ? AND id NOT IN (
                    SELECT id FROM experiencias 
                    WHERE neurona_id = ? 
                    ORDER BY exito DESC, timestamp DESC 
                    LIMIT ?
                )
            """, (neurona_id, neurona_id, limite))
            self.conn.commit()

    def cerrar(self):
        """Cierre seguro de la base de datos (Audit: Orphan WAL prevention)."""
        with self._lock:
            if hasattr(self, 'conn') and self.conn:
                try:
                    self.conn.commit()
                    self.conn.close()
                    logger.warning("🔱 Persistencia Soberana: Conexión cerrada con éxito.")
                except Exception as e:
                    logger.error(f"Error cerrando DB: {e}")
                finally:
                    self.conn = None

    def __del__(self):
        """Garantía de cierre en recolección de basura."""
        if hasattr(self, 'conn') and self.conn:
            self.cerrar()
