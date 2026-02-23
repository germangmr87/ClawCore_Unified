"""
MOTOR SOBERANO V5 — Ciclo de Procesamiento Ultra-Eficiente
Optimizado para entornos con recursos limitados (Computadora host).
Implementa: Reducción de carga CPU, Caché de Memoria Throttled y Async Flow.
"""

import asyncio
import logging
import sqlite3
import hashlib
import time
import os
from pathlib import Path
from datetime import datetime
from collections import deque

# Importaciones soberanas (Carga diferida para ahorrar RAM)
import sys
ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))

logger = logging.getLogger("MotorSoberanoV5")
logger.setLevel(logging.INFO)

class MotorProcesoClawCore:
    def __init__(self, db_path=None):
        self.root = ROOT
        self.db_path = db_path or os.path.expanduser("~/.clawcore/clawcore_v5.db")
        self.memory_cache = deque(maxlen=50) # Cache LRU en RAM limitada
        self.throttling_delay = 0.5 # Delay base para control de CPU (ms)
        self._init_db_optimized()
        
    def _init_db_optimized(self):
        """Inicializa SQLite con parámetros de alto rendimiento para poco disco/CPU."""
        conn = sqlite3.connect(self.db_path)
        # Modo WAL para permitir lectura/escritura concurrente sin bloqueos
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=-2000") # Limita cache a 2MB RAM
        
        conn.execute("CREATE TABLE IF NOT EXISTS synapses (hash TEXT PRIMARY KEY, input TEXT, output TEXT, hits INTEGER, last_used TEXT)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_hits ON synapses(hits)")
        conn.commit()
        conn.close()

    async def ejecutar_ciclo(self, entrada: str):
        """
        NUEVO CICLO DE PROCESAMIENTO:
        1. Normalizar (CPU Min)
        2. Fast-Lookup (Local Hit)
        3. Inferencia Throttled (Solo si falla local)
        4. Auto-Destilación (Aprendizaje)
        """
        start_time = time.time()
        entrada_norm = entrada.lower().strip()
        h = hashlib.md5(entrada_norm.encode()).hexdigest()

        # --- ETAPA 1: RAM HIT (O(1)) ---
        for entry in self.memory_cache:
            if entry['hash'] == h:
                logger.info("💎 RAM HIT: Respuesta entregada instantáneamente.")
                return entry['output']

        # --- ETAPA 2: LOCAL DISK HIT (O(log n)) ---
        res_local = self._consultar_sinapsis(h)
        if res_local:
            # Mover a RAM cache para siguiente uso
            self.memory_cache.append({'hash': h, 'output': res_local})
            logger.info("⚡ DISK HIT: Sinapsis recuperada de SQLite.")
            return res_local

        # --- ETAPA 3: INFERENCIA EXTERNA (CONTROLADA) ---
        # Si no está en motor local, usamos el Orquestador con control de tokens
        logger.info("🧠 MISS Local: Escalando a Inferencia Externa...")
        resultado = await self._escalar_inferencia(entrada_norm)
        
        # --- ETAPA 4: DESTILACIÓN SOBERANA ---
        if resultado:
            self._destilar(h, entrada_norm, resultado)
            self.memory_cache.append({'hash': h, 'output': resultado})

        return resultado

    def _consultar_sinapsis(self, h):
        conn = sqlite3.connect(self.db_path)
        res = conn.execute("SELECT output FROM synapses WHERE hash = ?", (h,)).fetchone()
        if res:
            conn.execute("UPDATE synapses SET hits = hits + 1, last_used = ? WHERE hash = ?", 
                         (datetime.now().isoformat(), h))
            conn.commit()
        conn.close()
        return res[0] if res else None

    async def _escalar_inferencia(self, prompt):
        """Llamada a motor externo (DeepSeek/GPT) con ahorro de tokens."""
        # Integración con el sistema de gateway existente
        from src.clawcore_system.neuronas.kernel_soberano import kernel
        # Control de throttling para no saturar la CPU en ráfagas
        await asyncio.sleep(self.throttling_delay)
        return await kernel.pensar(prompt)

    def _destilar(self, h, entrada, salida):
        """Almacena el conocimiento aprendido permanentemente."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("INSERT OR REPLACE INTO synapses VALUES (?,?,?,?,?)", 
                         (h, entrada, salida, 1, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            logger.info(f"🧬 Sinapsis destilada: {h[:8]} guardada en cerebro local.")
        except Exception as e:
            logger.error(f"⚠️ Error en destilación: {e}")

# Singleton para el Motor
motor = MotorProcesoClawCore()

if __name__ == "__main__":
    # Prueba de eficiencia
    async def test():
        print("🔱 Probando Motor Proceso Soberano V5...")
        resp = await motor.ejecutar_ciclo("¿cuál es tu objetivo?")
        print(f"Respuesta 1: {resp}")
        
        # El segundo llamado debería ser instantáneo (RAM Hit)
        start = time.time()
        resp2 = await motor.ejecutar_ciclo("¿cuál es tu objetivo?")
        elapsed = (time.time() - start) * 1000
        print(f"Respuesta 2 (Instant): {resp2}")
        print(f"⏱️ Tiempo RAM Hit: {elapsed:.4f}ms")

    asyncio.run(test())
