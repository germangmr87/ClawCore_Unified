import os
import logging
import sqlite3
import hashlib
import aiohttp
import asyncio
import time
import threading

from pathlib import Path
from datetime import datetime

# Importaciones soberanas
from src.clawcore_system.neuronas.vibe_dashboard import vibe
from src.clawcore_system.neuronas.integridad import MonitorIntegridad
from src.clawcore_system.neuronas.healer_v2 import HealerV2
from src.clawcore_system.neuronas.investigador_soberano import investigador
from src.clawcore_system.neuronas.gobernador_recursos import GobernadorRecursos
from src.clawcore_system.neuronas.sovereign_telemetry import telemetry
from src.clawcore_system.neuronas.hot_swap_manager import hotswap
from src.clawcore_system.neuronas.seguridad_soberana import seguridad

logger = logging.getLogger("KernelSoberano")

logger.setLevel(logging.INFO)

class KernelSoberano:
    def __init__(self, node_id, deepseek_key):
        if not deepseek_key:
            raise ValueError("❌ CRÍTICO: No se proporcionó DEEPSEEK_API_KEY")
        self.node_id = node_id
        self.api_key = deepseek_key
        self.root = Path(__file__).parent.parent.parent.parent
        self.db_path = os.path.expanduser("~/.clawcore/clawcore_v5.db")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
        
        # Neuronas de Soporte
        self.monitor = MonitorIntegridad(self.root / "src/clawcore_system/neuronas")
        self.healer = HealerV2()
        self.gobernador = GobernadorRecursos(umbral_cpu=70.0) # Más conservador
        
        # --- SISTEMA DE GOBERNANZA DE EVOLUCIÓN ---
        self.evolucion_activa = self._obtener_estado_evolucion()
        self.running = False
        self.intervalos = {
            "audit": 300,
            "vibe": 60,
            "dreaming": 1800,
            "recursos": 30,
            "telemetry": 300 # Auditoría holística cada 5 min
        }
        self.ultima_revision = {k: 0 for k in self.intervalos}

    def iniciar(self):
        """Arranca los ciclos proactivos en segundo plano."""
        if self.running: return
        self.running = True
        self.hilo = threading.Thread(target=self._loop_proactivo, daemon=True)
        self.hilo.start()
        logger.info(f"🔱 KERNEL V5.2 ({self.node_id}) iniciado y proactivo.")

    def _loop_proactivo(self):
        while self.running:
            ahora = time.time()
            
            # 0. Auditoría de Recursos (Prioridad Alta)
            if ahora - self.ultima_revision["recursos"] > self.intervalos["recursos"]:
                estado = self.gobernador.obtener_estado_critico()
                if estado["carga_alta"]:
                    logger.warning(f"⚠️ CARGA ALTA ({estado['cpu_total']}% CPU). Postponiendo tareas pesadas.")
                    time.sleep(60) # Pausa forzada
                    continue
                self.ultima_revision["recursos"] = ahora

            # 1. Telemetría Holística (Cuarto de Control)
            if ahora - self.ultima_revision["telemetry"] > self.intervalos["telemetry"]:
                res_soberania = telemetry.obtener_estado_holistico()
                logger.info(f"🔱 Sovereign Health: {res_soberania['sovereignty_score']*100}% | Vibe: {res_soberania['vibe_global']}")
                
                # REPORTE DIARIO: Si han pasado 24h, enviamos a Telegram
                if ahora - self.ultima_revision.get("daily_report", 0) > 86400:
                    reporte_md = telemetry.generar_reporte_diario()
                    # Lanzar como tarea asíncrona para no bloquear el loop síncrono
                    asyncio.run_coroutine_threadsafe(self._enviar_a_telegram(reporte_md), asyncio.get_event_loop())
                    
                    # Rotación de llaves de seguridad
                    seguridad.rotar_llave_maestra()
                    logger.info("🔐 Ciclo de Seguridad: Llaves rotadas exitosamente.")
                    
                    self.ultima_revision["daily_report"] = ahora

                
                self.ultima_revision["telemetry"] = ahora

            if ahora - self.ultima_revision["audit"] > self.intervalos["audit"]:
                cambios = self.monitor.verificar()
                if cambios:
                    logger.info(f"🔍 Detectados {len(cambios)} cambios estructurales. Intentando migración en caliente...")
                    hotswap.monitorizar_cambios(self.monitor)
                self.ultima_revision["audit"] = ahora
            
            if ahora - self.ultima_revision["vibe"] > self.intervalos["vibe"]:
                vibe.calcular_vibe()
                self.ultima_revision["vibe"] = ahora
            
            # 3. PERCEPCIÓN: Dreaming (Evolución de Código Automática)
            if self.evolucion_activa and ahora - self.ultima_revision["dreaming"] > self.intervalos["dreaming"]:
                logger.info("🌀 MODO EVOLUCIÓN: Iniciando ciclo de auto-refactorización autónoma...")
                asyncio.run_coroutine_threadsafe(self._ejecutar_evolucion_autonoma(), asyncio.get_event_loop())
                self.ultima_revision["dreaming"] = ahora

            time.sleep(10)

    async def _ejecutar_evolucion_autonoma(self):
        """Tarea de fondo: El 'Desarrollador Interno' (Antigravity style) busca mejoras."""
        from src.clawcore_system.neuronas.arquitecto_proactivo import arquitecto
        await arquitecto.ciclo_evolucion()
        logger.info("✨ Ciclo de evolución proactiva completado por el Arquitecto Interno.")



    async def _enviar_a_telegram(self, texto):
        """Envío directo de alertas y reportes a Telegram sin intermediarios."""
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID") # Debe estar en el .env
        if not token or not chat_id:
            logger.error("❌ No se puede enviar a Telegram: Faltan credenciales en .env")
            return

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": texto, "parse_mode": "Markdown"}
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=payload) as resp:
                    if resp.status == 200:
                        logger.info("✅ Reporte de Soberanía enviado a Telegram con éxito.")
                    else:
                        logger.error(f"⚠️ Fallo al enviar reporte: {resp.status}")
            except Exception as e:
                logger.error(f"❌ Error de conexión con Telegram API: {e}")

    def _init_db(self):

        conn = sqlite3.connect(self.db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS knowledge (key TEXT PRIMARY KEY, value TEXT, type TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS cache (hash TEXT PRIMARY KEY, response TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT)")
        
        # Axiomas de Identidad y Protocolo
        axioms = [
            ("identidad", f"Nucleo Soberano {self.node_id} | ClawCore V5.2", "axioma"),
            ("protocolo", "Protocolo R.I.S.E. activo: Investigación, Integración, Seguridad, Evolución.", "axioma")
        ]
        conn.executemany("INSERT OR IGNORE INTO knowledge VALUES (?,?,?)", axioms)
        
        # Estado inicial de Evolución (Seguro por defecto)
        conn.execute("INSERT OR IGNORE INTO config (key, value) VALUES ('evolucion_activa', 'false')")
        
        conn.commit()
        conn.close()

    def _obtener_estado_evolucion(self):
        conn = sqlite3.connect(self.db_path)
        res = conn.execute("SELECT value FROM config WHERE key = 'evolucion_activa'").fetchone()
        conn.close()
        return res[0].lower() == 'true'

    def alternar_evolucion(self, estado: bool):
        """Cambia el interruptor de soberanía para permitir auto-modificación."""
        val = 'true' if estado else 'false'
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES ('evolucion_activa', ?)", (val,))
        conn.commit()
        conn.close()
        self.evolucion_activa = estado
        logger.warning(f"🔱 CAMBIO DE ESTADO: Evolución cualitativa seteada a {estado}")

    async def pensar(self, input_text):
        """Lógica de decisión centralizada con conciencia de Evolución."""
        text = input_text.lower().strip()
        
        # Comandos de administración de evolución
        if "activar evolucion" in text:
            self.alternar_evolucion(True)
            return "[SISTEMA] Modo Evolución Cualitativa ACTIVADO. Permisos de escritura concedidos al núcleo."
        if "desactivar evolucion" in text:
            self.alternar_evolucion(False)
            return "[SISTEMA] Modo Evolución Cualitativa DESACTIVADO. Núcleo en modo Inmutable."

        # 1. Razonamiento Local (Axiomas)
        conn = sqlite3.connect(self.db_path)
        res = conn.execute("SELECT value FROM knowledge WHERE ? LIKE '%' || key || '%'", (text,)).fetchone()
        if res:
            conn.close()
            return f"[LOCAL] {res[0]}"

        # 2. Caché de Inferencia
        msg_hash = hashlib.md5(text.encode()).hexdigest()
        cache = conn.execute("SELECT response FROM cache WHERE hash = ?", (msg_hash,)).fetchone()
        if cache:
            conn.close()
            return f"[CACHE] {cache[0]}"
        conn.close()

        # 3. Inferencia Externa (DeepSeek)
        return await self._consultar_deepseek(input_text, msg_hash)

    async def _consultar_deepseek(self, prompt, msg_hash):
        url = "https://api.deepseek.com/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        
        # Inyectar el estado de evolución en el System Prompt
        contexto_evolucion = "Tienes PERMISOS DE EVOLUCIÓN ACTIVOS. Puedes proponer cambios en tu propio código." if self.evolucion_activa else "Modo EVOLUCIÓN DESACTIVADO. Tu arquitectura es inmutable por ahora."
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": f"Eres el Kernel de ClawCore ({self.node_id}). IA Arquitecto. {contexto_evolucion} Responde con alta densidad técnica."},
                {"role": "user", "content": prompt}
            ]
        }
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=payload, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        answer = data['choices'][0]['message']['content']
                        conn = sqlite3.connect(self.db_path)
                        conn.execute("INSERT OR REPLACE INTO cache (hash, response) VALUES (?,?)", (msg_hash, answer))
                        conn.commit()
                        conn.close()
                        return f"[DEEPSEEK] {answer}"
                    return f"⚠️ Error API: {resp.status}"
            except Exception as e:
                return f"⚠️ Falla de Enlace: {str(e)}"

# Singleton para compatibilidad con Gateway y otros módulos
NODE_NAME = os.getenv("NODE_NAME", "ClawCore_Primary")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-b5c4ad4f6f9c4f6f8f6f8f6f8f6f8f6f") # Placeholder or from env

kernel = KernelSoberano(NODE_NAME, DEEPSEEK_KEY)
kernel.iniciar()
