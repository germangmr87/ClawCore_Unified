"""
CEREBRO PROFUNDO SOBERANO V2.0
Jerarquía de backends:
  1. API externa (Gemini) — POR DEFECTO
  2. Ollama local — OPCIONAL (activable desde portal)
  3. llama-cpp-python — OPCIONAL (si el usuario descarga un GGUF)
"""
import json
import os
import logging
import requests
from pathlib import Path

logger = logging.getLogger("CerebroProfundo")
logger.setLevel(logging.INFO)

# Cargar config
_CFG_PATH = Path(__file__).parent / "cerebro_config.json"
_DEFAULTS = {
    "use_local": False,
    "local_endpoint": "http://localhost:11434/api/generate",
    "api_endpoint": "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
    "api_key_env": "GEMINI_API_KEY",
    "model_local": "llama3.2:3b",
    "model_api": "gemini-1.5-flash"
}

def _load_cfg():
    if _CFG_PATH.exists():
        try: return json.loads(_CFG_PATH.read_text())
        except: pass
    _CFG_PATH.write_text(json.dumps(_DEFAULTS, indent=4))
    return _DEFAULTS.copy()


class CerebroProfundoSoberano:
    def __init__(self):
        self.cfg = _load_cfg()
        self.activo = False
        self.backend_name = "api"  # default

        if self.cfg.get("use_local"):
            self._intentar_local()

    # ── backends locales (opcionales) ──────────────────────────
    def _intentar_local(self):
        # Intento 1: llama-cpp
        try:
            from src.clawcore_system.neuronas.cerebro_cpp import CerebroCPP
            model_path = Path(__file__).parent / "models" / f"{self.cfg['model_local']}.gguf"
            self._cpp = CerebroCPP(model_path)
            self.activo = True
            self.backend_name = "llama-cpp"
            logger.info("✅ Backend llama-cpp activo")
            return
        except Exception:
            pass

        # Intento 2: Ollama
        try:
            r = requests.get(self.cfg["local_endpoint"].replace("/generate", "/tags"), timeout=2)
            if r.status_code == 200:
                self.activo = True
                self.backend_name = "ollama"
                logger.info("✅ Backend Ollama activo")
                return
        except Exception:
            pass

        logger.info("ℹ️ Local no disponible, se usará API externa.")

    # ── razonamiento ───────────────────────────────────────────
    def razonar(self, prompt, contexto=None):
        full_prompt = self._build_prompt(prompt, contexto)

        # Si el usuario activó local Y hay backend local disponible
        if self.cfg.get("use_local") and self.activo:
            if self.backend_name == "llama-cpp":
                return self._cpp.razonar(prompt)
            if self.backend_name == "ollama":
                return self._razonar_ollama(full_prompt)

        # Por defecto → API externa (Gemini)
        return self._razonar_api(full_prompt)

    def _razonar_ollama(self, prompt):
        try:
            payload = {"model": self.cfg["model_local"], "prompt": prompt, "stream": False,
                       "options": {"temperature": 0.4, "num_predict": 128}}
            r = requests.post(self.cfg["local_endpoint"], json=payload, timeout=30)
            if r.status_code == 200:
                d = r.json()
                return {"identidad": "Ollama-Local", "respuesta": d.get("response",""),
                        "tokens": d.get("eval_count",0), "latencia": d.get("total_duration",0)/1e9}
        except Exception as e:
            logger.error(f"Ollama error: {e}")
        return self._razonar_api(prompt)  # fallback

    def _razonar_api(self, prompt):
        api_key = os.getenv(self.cfg["api_key_env"], "")
        if not api_key:
            return {"error": "API key no configurada", "fallback": True}
        url = f"{self.cfg['api_endpoint']}?key={api_key}"
        payload = {"contents": [{"role":"user","parts":[{"text": prompt}]}],
                   "generationConfig": {"temperature":0.4, "maxOutputTokens":256}}
        try:
            r = requests.post(url, json=payload, timeout=30)
            r.raise_for_status()
            d = r.json()
            text = d["candidates"][0]["content"]["parts"][0]["text"]
            return {"identidad":"Gemini-API","respuesta":text,
                    "tokens": d.get("usageMetadata",{}).get("candidatesTokenCount",0),
                    "latencia": r.elapsed.total_seconds()}
        except Exception as e:
            logger.error(f"API error: {e}")
            return {"error": str(e), "fallback": True}

    def _build_prompt(self, prompt, ctx):
        s = "Eres ClawCore V4.5, sistema soberano. Responde con eficiencia técnica."
        if ctx: s += f" Contexto: {json.dumps(ctx)}"
        return f"[SYSTEM]: {s}\n[USER]: {prompt}\n[ANSWER]:"


if __name__ == "__main__":
    brain = CerebroProfundoSoberano()
    print(f"Backend: {brain.backend_name}")
    res = brain.razonar("¿Por qué SQLite WAL es superior a pickle?")
    print(json.dumps(res, indent=2, ensure_ascii=False))
