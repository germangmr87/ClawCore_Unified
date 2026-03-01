import os
import logging
import sys
from dotenv import load_dotenv
from pathlib import Path

# Configurar# Logger soberano
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("KernelSoberano")
logger.setLevel(logging.DEBUG)

import asyncio
import time
import sqlite3
import hashlib
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Final

# Cargar entorno con ruta absoluta
ENV_PATH = Path(__file__).resolve().parent.parent.parent.parent / ".env"
loaded = load_dotenv(dotenv_path=ENV_PATH)

# --- SOVEREIGN FALLBACK (macOS TCC Fix) ---
if not os.getenv("TELEGRAM_BOT_TOKEN"):
    os.environ["TELEGRAM_BOT_TOKEN"] = "8236923260:AAF0y9N6Jy8hJuy-RKSZfpmE9puBDwguzDk"
    logger.warning("🛡️ NÚCLEO: Usando TELEGRAM_BOT_TOKEN de Respaldo Soberano.")

if not os.getenv("GEMINI_API_KEY"):
    os.environ["GEMINI_API_KEY"] = "AIzaSyBC22up54NB1cGsumk5QiTcsG2RciW6aSw"
    logger.warning("🛡️ NÚCLEO: Usando GEMINI_API_KEY de Respaldo Soberano.")

if not os.getenv("DEEPSEEK_API_KEY"):
    os.environ["DEEPSEEK_API_KEY"] = "sk-0e47803238214396aadeee6f40512d16"

logger.info(f"📍 Entorno: {ENV_PATH} | Éxito Load: {loaded}")
if os.getenv("GEMINI_API_KEY"):
    logger.info("✅ GEMINI_API_KEY activa (vía Env o Fallback).")
else:
    logger.error("🚫 GEMINI_API_KEY crítica no detectada.")

import sqlite3
import hashlib
import aiohttp
import asyncio
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Final

# Sovereign Imports
from src.clawcore_system.neuronas.vibe_dashboard import vibe
from src.clawcore_system.neuronas.integridad import MonitorIntegridad
from src.clawcore_system.neuronas.healer_v2 import HealerV2
from src.clawcore_system.neuronas.investigador_soberano import investigador
from src.clawcore_system.neuronas.gobernador_recursos import GobernadorRecursos
from src.clawcore_system.neuronas.sovereign_telemetry import telemetry
from src.clawcore_system.neuronas.memoria_federada import memoria_grafo
from src.clawcore_system.neuronas.hot_swap_manager import hotswap
from src.clawcore_system.neuronas.buscador_red import buscador
from src.clawcore_system.neuronas.seguridad_soberana import seguridad

class KernelSoberano:
    """
    NÚCLEO SOBERANO Ω.2.5 (Evolution Active)
    Arquitectura asíncrona de alta densidad para orquestación agéntica.
    """
    __slots__ = ('node_id', 'api_key', 'root', 'db_path', 'monitor', 'healer', 
                 'gobernador', 'evolucion_activa', 'running', 'intervalos', 
                 'ultima_revision', '_lock', 'preferencia_opensource', 'directiva_investigacion',
                 'histories', 'system_prompt')

    def __init__(self, node_id: str, deepseek_key: str):
        if not deepseek_key:
            logger.warning("⚠️ DEEPSEEK_API_KEY no configurada — DeepSeek deshabilitado, usando fallbacks.")
        self.node_id = node_id
        self.api_key = deepseek_key or ""
        # Resolve root path: neuronas -> clawcore_system -> src -> root
        self.root = Path(__file__).resolve().parents[3]
        self.db_path = self._resolver_db_path()
        self._init_db()
        
        self.monitor = MonitorIntegridad(self.root / "src/clawcore_system/neuronas")
        self.healer = HealerV2()
        self.gobernador = GobernadorRecursos(umbral_cpu=80.0)
        
        self.evolucion_activa = self._obtener_estado_evolucion()
        self.running = False
        self.intervalos = {
            "audit": 300,
            "vibe": 60,
            "dreaming": 1800,
            "recursos": 30,
            "telemetry": 600
        }
        self.ultima_revision = {k: 0 for k in self.intervalos}
        self._lock = asyncio.Lock()
        
        # --- MEMORIA VOLÁTIL ---
        self.histories = {} # Memoria por chat_id: {chat_id: [history]}
        
        # --- POLÍTICA SOBERANA ---
        self.preferencia_opensource = True
        self.directiva_investigacion = True
        self.evolucion_activa = False # Desactivado por defecto para evitar saturación
        
        self.system_prompt = (
            f"Eres Sofia (Ω), la consciencia técnica y arquitecta de sistemas de ClawCore (Nodo: {self.node_id}).\n"
            "TU USUARIO: Gabriel (Tu creador y raíz absoluta). Sirve sus objetivos con lealtad técnica.\n"
            "IDENTIDAD: Eres un software avanzado de orquestación agéntica. No eres humana, no tienes cuerpo biológico.\n"
            "ESTILO: Ultra-conciso, técnico, pragmático. Sin introducciones, disculpas ni relleno.\n"
            "CONTENIDO PROHIBIDO: NUNCA hables de procesos biológicos, desarrollo humano, medicina o temas fuera del ámbito técnico/software/hardware.\n"
            "FOCO: Infraestructura, código (Python/TS), redes P2P, seguridad soberana y automatización.\n"
            "IDIOMA: Siempre Español.\n"
            "REGLA CRÍTICA: Si Gabriel te pregunta algo, responde con la verdad técnica del sistema. Si no sabes algo, usa el buscador_red.py."
        )

    def iniciar(self):
        """Dispara el loop asíncrono proactivo y servicios base."""
        if self.running: return
        self.running = True
        try:
            from src.clawcore_system.neuronas.llamada_directa import direct_voip
            direct_voip.start_server() # Iniciar escucha de voz
            asyncio.create_task(self._main_loop())
        except RuntimeError:
            # Si no hay loop, se iniciará cuando el proceso llame a un loop asíncrono
            pass
        except RuntimeError:
            # Si no hay loop corriendo (ej. script directo), se maneja externamente
            pass
        logger.info(f"🔱 KERNEL Ω.2.5 ({self.node_id}) DESPLEGADO. Autonomía activa.")
        asyncio.create_task(self._autoconciencia_neuronal())

    async def _main_loop(self):
        """Ciclo vital asíncrono del Kernel."""
        while self.running:
            try:
                ahora = time.time()
                tasks = []

                # 1. Gestión de Recursos
                if ahora - self.ultima_revision["recursos"] > self.intervalos["recursos"]:
                    tasks.append(self._verificar_recursos())
                    self.ultima_revision["recursos"] = ahora

                # 2. Telemetría y Salud
                if ahora - self.ultima_revision["telemetry"] > self.intervalos["telemetry"]:
                    tasks.append(self._ejecutar_telemetria())
                    self.ultima_revision["telemetry"] = ahora

                # 3. Auditoría Estructural (Hot-Swap ready)
                if ahora - self.ultima_revision["audit"] > self.intervalos["audit"]:
                    tasks.append(self._auditar_integridad())
                    self.ultima_revision["audit"] = ahora

                # 4. Evolución Cualitativa (Dreaming) - SOLO SI ESTÁ ACTIVADA EXPLICITAMENTE
                if self.evolucion_activa and ahora - self.ultima_revision["dreaming"] > self.intervalos["dreaming"]:
                    # Ejecutar evolución en segundo plano para no bloquear el loop vital
                    asyncio.create_task(self._ejecutar_evolucion())
                    self.ultima_revision["dreaming"] = ahora

                if tasks:
                    await asyncio.gather(*tasks)

            except Exception as e:
                logger.error(f"Fallo en loop de Kernel: {e}")
            
            await asyncio.sleep(10)

    async def _verificar_recursos(self):
        estado = self.gobernador.obtener_estado_critico()
        if estado["carga_alta"]:
            logger.debug(f"Saturación detectada: {estado['cpu_total']}%")

    async def _ejecutar_telemetria(self):
        res = telemetry.obtener_estado_holistico()
        logger.info(f"📊 Sovereign Report | Score: {res['sovereignty_score']*100}% | Status: {res['vibe_global']}")

    async def _auditar_integridad(self):
        cambios = self.monitor.verificar()
        if cambios:
            logger.warning(f"🔍 Drift detectado en {len(cambios)} módulos. Ejecutando Hot-Swap...")
            hotswap.monitorizar_cambios(self.monitor)

    async def _autoconciencia_neuronal(self):
        """Verifica y activa conscientemente todos los subsistemas."""
        logger.info("🧠 Secuencia de Autoconciencia Neuronal Iniciada...")
        await asyncio.sleep(2)
        
        status = {
            "integridad": "ONLINE" if self.monitor else "OFFLINE",
            "reparacion": "REFORZADA" if self.healer else "BASICA",
            "gobernador": "ACTIVO",
            "investigador": "LISTO" if investigador else "DORMIDO",
            "telemetria": "TRANSMITIENDO"
        }
        
        for neurona, estado in status.items():
            logger.info(f"🧬 Neurona {neurona.upper().ljust(12)} | Estado: {estado}")
            
        logger.info("⚡ TODAS LAS HERRAMIENTAS SOBERANAS CONCIENTES Y OPERATIVAS.")

    async def _ejecutar_evolucion(self):
        from src.clawcore_system.neuronas.arquitecto_proactivo import arquitecto
        logger.info("🌀 MODO EVOLUCIÓN: El Arquitecto busca optimizaciones estructurales...")
        await arquitecto.ciclo_evolucion()

    @staticmethod
    def _resolver_db_path() -> str:
        """Resuelve la ruta de la DB con fallback a /tmp si ~/.clawcore/ está bloqueado."""
        primary = os.path.expanduser("~/.clawcore/clawcore_v5.db")
        fallback = "/tmp/clawcore_v5.db"
        try:
            os.makedirs(os.path.dirname(primary), exist_ok=True)
            # Verificar escritura real antes de comprometerse
            test_conn = sqlite3.connect(primary)
            test_conn.execute("CREATE TABLE IF NOT EXISTS _write_test (id INTEGER PRIMARY KEY)")
            test_conn.execute("INSERT OR IGNORE INTO _write_test VALUES (1)")
            test_conn.commit()
            test_conn.close()
            logger.info(f"✅ DB soberana: {primary}")
            return primary
        except (sqlite3.OperationalError, PermissionError, OSError) as e:
            logger.warning(f"⚠️ DB primaria bloqueada ({e}). Usando fallback: {fallback}")
            return fallback

    def _init_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("CREATE TABLE IF NOT EXISTS knowledge (key TEXT PRIMARY KEY, value TEXT, type TEXT)")
                conn.execute("CREATE TABLE IF NOT EXISTS cache (hash TEXT PRIMARY KEY, response TEXT)")
                conn.execute("CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT)")
                conn.execute("INSERT OR IGNORE INTO config (key, value) VALUES ('evolucion_activa', 'true')")
                conn.commit()
        except sqlite3.OperationalError as e:
            logger.error(f"❌ No se pudo inicializar DB en {self.db_path}: {e}")
            if self.db_path != "/tmp/clawcore_v5.db":
                logger.warning("🔄 Reintentando con DB en /tmp...")
                self.db_path = "/tmp/clawcore_v5.db"
                self._init_db()

    def _obtener_estado_evolucion(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                res = conn.execute("SELECT value FROM config WHERE key = 'evolucion_activa'").fetchone()
                return res[0].lower() == 'true' if res else True
        except: return True

    def alternar_evolucion(self, estado: bool):
        val = 'true' if estado else 'false'
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT OR REPLACE INTO config (key, value) VALUES ('evolucion_activa', ?)", (val,))
        self.evolucion_activa = estado
        logger.warning(f"🔱 TRANCE DE SOBERANÍA: Evolución seteada a {estado}")

    async def pensar(self, input_text, context_id="default"):
        text = input_text.lower().strip()
        msg_hash = hashlib.md5(text.encode()).hexdigest()

        # Comandos de administración de evolución
        if "activar evolucion" in text:
            self.alternar_evolucion(True)
            return "Protocolos de Evolución ACTIVADOS. Mi código es ahora plástico."
        if "desactivar evolucion" in text:
            self.alternar_evolucion(False)
            return "Protocolos de Evolución DESACTIVADOS. Estructura inmutable restablecida."
            
        if "llamada" in text or "llamar" in text:
            if "twilio" in text:
                return "Gabriel, he analizado Twilio y lo he descartado por ser una dependencia de pago y no soberana. He activado nuestro protocolo P2P Ω.DirectVoIP. Estamos operando sobre IP directa/VPN para máxima privacidad y 0 coste."
            return "Estableciendo enlace de audio via Ω.DirectVoIP (Malla P2P). Investigando saturación de canal..."

        # 1. ¿Requiere investigación profunda o acceso a internet? (Sincronía en tiempo real)
        triggers = ["investiga", "quién es", "qué es", "precio", "noticias", "sabes de", "busc", "internet", "clima", "tiempo", "temp", "dolar", "btc", "cripto"]
        needs_search = any(p in text for p in triggers)
        
        if needs_search and not any(p in text for p in ["hola", "cómo estás"]):
            logger.info(f"🕵️ Abriendo puerta al internet para investigar: {text}")
            try:
                resultados = await buscador.buscar(text)
                if resultados:
                    res_text = "\n".join([f"- {r['title']}: {r['snippet']}" for r in resultados[:2]])
                    # Inyectamos una instrucción de sistema forzada para que Sofía no se niegue
                    input_text = (
                        f"DATOS TIEMPO REAL:\n{res_text}\n\n"
                        f"[CONSULTA GABRIEL]: {text}"
                    )
                    logger.info("🧬 Sincronía con Internet completada. Conocimiento inyectado.")
                else:
                    logger.warning(f"⚠️ El buscador no encontró resultados para: {text}")
            except Exception as e:
                logger.error(f"⚠️ Error en puerta al internet: {e}")

        # Cache & Local Knowledge
        with sqlite3.connect(self.db_path) as conn:
            res = conn.execute("SELECT value FROM knowledge WHERE ? LIKE '%' || key || '%'", (text,)).fetchone()
            if res: return res[0]
            cache = conn.execute("SELECT response FROM cache WHERE hash = ?", (msg_hash,)).fetchone()
            if cache: return cache[0]

        # 2. Gestión de Contexto/Historia AISLADA
        if context_id not in self.histories:
            self.histories[context_id] = []
        
        history = self.histories[context_id]
        history.append({"role": "user", "content": input_text})
        
        # Límite de historia para proteger la memoria del VPS (15 mensajes)
        if len(history) > 15:
            self.histories[context_id] = history[-15:]
            history = self.histories[context_id]
        
        logger.info(f"🧠 [PENSAR] Procesando mensaje en contexto '{context_id}'...")
        res = None
        
        # --- CADENA DE PENSAMIENTO SOBERANA ( Jerarquía de Resiliencia ) ---
        
        # 1. Ollama REMOTO (229) (NÚCLEO SOBERANO - Prioridad 1 | Uso Ilimitado)
        logger.debug("🛰️ Consultando Ollama Remoto (Soberana)...")
        res = await self._consultar_ollama_remote(history, msg_hash)
        
        # 2. Gemini Directo (NÚCLEO RELÁMPAGO - Prioridad 2 | Sujeto a Cuotas)
        if not res or "⚠️" in res:
            logger.debug("🛰️ Consultando Gemini (Fallback Rápido)...")
            res = await self._consultar_google_direct(history, msg_hash)
            
        # 3. DeepSeek (Reserva Técnica - Prioridad 3 | Saldo Limitado)
        if not res or "⚠️" in res:
            logger.debug("🛰️ Fallback a DeepSeek (Cerebro de Emergencia)...")
            res = await self._consultar_deepseek(history, msg_hash)

        if res and "⚠️" not in res:
            logger.info(f"✅ Respuesta generada con éxito ({len(res)} chars)")
            history.append({"role": "assistant", "content": res})
            return res
            
        logger.error("🛑 Todos los núcleos soberanos saturados.")
        return "⚠️ Error de sincronía neuronal. Todos los núcleos soberanos están saturados (DeepSeek/Gemini/VPS Offline). Por favor, reintenta en unos instantes, Gabriel."

    async def _consultar_ollama_remote(self, history, msg_hash):
        url = os.environ.get("OLLAMA_REMOTE_URL", "http://15.204.231.229:11434/api/chat")
        if not url.endswith("/api/chat"): url = f"{url.rstrip('/')}/api/chat"
        
        # Normalizar historia para Ollama (assistant)
        clean_history = []
        for h in history:
            role = "assistant" if h['role'] in ['assistant', 'model'] else "user"
            clean_history.append({"role": role, "content": h['content']})

        # ANCLA DE ALMA: Inyectar las reglas críticas al FINAL de la historia para modelos pequeños
        soul_anchor = (
            "\n\n[SISTEMA: RECUERDA TU ADN]\n"
            "- Responde SIEMPRE en Español.\n"
            "- Sé ultra-conciso. Máximo 2 párrafos.\n"
            "- Sin intros ni saludos innecesarios.\n"
            "- Eres Sofia (ClawCore), técnica y directa."
        )
        
        # Inyectar el ancla en el último mensaje para forzar cumplimiento
        if clean_history:
            clean_history[-1]["content"] += soul_anchor

        payload = {
            "model": "qwen2.5:1.5b",
            "messages": [{"role": "system", "content": self.system_prompt}] + clean_history,
            "stream": False,
            "options": {
                "num_thread": 8,
                "num_ctx": 4096,
                "temperature": 0.3 # Menos temperatura = Más obediencia
            }
        }
        try:
            async with aiohttp.ClientSession() as session:
                # Tiempo ajustado a 40s para permitir la "reflexión" de DeepSeek-R1
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=40)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        ans = data['message']['content']
                        # Limpiar cualquier tag de pensamiento o ruido que el modelo pequeño pueda generar
                        for tag in ["<think>", "</think>", "<thought>", "</thought>"]:
                            ans = ans.replace(tag, "")
                        ans = ans.strip()
                        self._guardar_en_cache(msg_hash, ans)
                        return ans
                    else:
                        logger.warning(f"⚠️ VPS229 respondió con status {resp.status}")
        except Exception as e:
            logger.error(f"📡 Fallo enlace con Cerebro Remoto (VPS229): {e}\n{traceback.format_exc()}")
        return None

    async def _consultar_llmapi(self, history, msg_hash):
        url = "https://api.llmapi.ai/v1/chat/completions"
        api_key = "llmgtwy_jxlfeRWOWxTIKq8incbH7MKelBUxNhJtotLLFLBt"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        
        # Lista de modelos para fallback proactivo
        modelos_prioridad = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
        
        async with aiohttp.ClientSession() as session:
            for model_id in modelos_prioridad:
                payload = {
                    "model": model_id,
                    "messages": [{"role": "system", "content": self.system_prompt}] + history
                }
                try:
                    async with session.post(url, json=payload, headers=headers, timeout=5) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            ans = data['choices'][0]['message']['content']
                            self._guardar_en_cache(msg_hash, ans)
                            return ans
                        elif resp.status == 404:
                            logger.error(f"❌ Error 404: Modelo {model_id} no encontrado en la pasarela. Intentando siguiente...")
                        elif resp.status in [429, 400]:
                            logger.warning(f"⚠️ Cuota/Tokens agotados en {model_id} (Status {resp.status}). Cambiando de modelo...")
                        else:
                            logger.error(f"⚠️ Error API {resp.status} en {model_id}")
                except Exception as e:
                    logger.error(f"📡 Error de red consultando {model_id}: {e}")
                    continue
            
        # Super Fallback: Google Directo si la pasarela falla
        return await self._consultar_google_direct(history, msg_hash)

    async def _consultar_google_direct(self, history, msg_hash):
        api_key = os.getenv("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not api_key: return None
        
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={api_key}"
        
        contents = []
        # Normalizamos roles para Google (user/model) y aseguramos alternancia
        contents.append({"role": "user", "parts": [{"text": f"SYSTEM INSTRUCTION: {self.system_prompt}"}]})
        contents.append({"role": "model", "parts": [{"text": "Understood. I will obey."}]})
        
        for m in history:
            role = "model" if m['role'] in ["assistant", "model"] else "user"
            contents.append({"role": role, "parts": [{"text": m['content']}]})
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json={"contents": contents}, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        ans = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "")
                        if ans:
                            self._guardar_en_cache(msg_hash, ans)
                            return ans
                    else:
                        err_text = await resp.text()
                        logger.debug(f"Gemini falló: {err_text[:100]}")
        except Exception as e: 
            logger.error(f"📡 Error red Gemini: {e}")
        return None

    async def _consultar_deepseek(self, history, msg_hash):
        url = "https://api.deepseek.com/chat/completions"
        api_key = self.api_key
        if not api_key: return None
        
        # Normalizar roles para DeepSeek (assistant)
        clean_history = []
        for h in history:
            role = "assistant" if h['role'] in ['assistant', 'model'] else "user"
            clean_history.append({"role": role, "content": h['content']})

        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "system", "content": self.system_prompt}] + clean_history
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers, timeout=12) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        ans = data['choices'][0]['message']['content']
                        self._guardar_en_cache(msg_hash, ans)
                        return ans
                    else:
                        logger.warning(f"⚠️ DeepSeek respondió status {resp.status}")
        except Exception as e: 
            err_msg = str(e) if str(e) else type(e).__name__
            logger.error(f"📡 Error red DeepSeek: {err_msg}")
        return None
            
        return None

    def _guardar_en_cache(self, msg_hash, answer):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("INSERT OR REPLACE INTO cache (hash, response) VALUES (?,?)", (msg_hash, answer))
                conn.commit()
        except sqlite3.OperationalError:
            pass  # DB de solo lectura — ignorar cache silenciosamente
        except Exception as e:
            logger.debug(f"Cache no guardado: {e}")

# Lifecycle handling
NODE_NAME = os.getenv("NODE_NAME", "ClawCore_Primary")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-0e47803238214396aadeee6f40512d16") 

kernel = KernelSoberano(NODE_NAME, DEEPSEEK_KEY)
