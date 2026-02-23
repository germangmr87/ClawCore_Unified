import logging
from pathlib import Path
from typing import Optional

try:
    from llama_cpp import Llama  # pip install llama-cpp-python
except Exception as e:
    raise ImportError("llama-cpp-python no está instalado") from e

logger = logging.getLogger("CerebroCPP")
logger.setLevel(logging.INFO)


class CerebroCPP:
    """Wrapper ligero sobre llama‑cpp‑python.
    Usa un modelo GGUF local (ej. llama‑3‑8b‑instruct‑q4_0.gguf).
    """

    def __init__(self, model_path: Path, n_ctx: int = 2048):
        self.model_path = model_path
        self.n_ctx = n_ctx
        self._model: Optional[Llama] = None
        self._load_model()

    def _load_model(self):
        if not self.model_path.exists():
            logger.error(f"Modelo no encontrado: {self.model_path}")
            raise FileNotFoundError(self.model_path)
        logger.info(f"Cargando modelo local {self.model_path.name}")
        self._model = Llama(
            model_path=str(self.model_path),
            n_ctx=self.n_ctx,
            n_threads=4,
            verbose=False,
        )
        logger.info("Modelo cargado y listo")

    def razonar(self, prompt: str, max_tokens: int = 256, temperature: float = 0.4):
        if not self._model:
            raise RuntimeError("Modelo no inicializado")
        resp = self._model(
            f"[SYSTEM]: Eres ClawCore, razonador soberano.\n[USER]: {prompt}\n[ANSWER]:",
            max_tokens=max_tokens,
            temperature=temperature,
            stop=["[END]"],
        )
        return {
            "identidad": "DeepLocal-CPP",
            "respuesta": resp["choices"][0]["text"].strip(),
            "tokens": resp["usage"]["completion_tokens"],
            "latencia": resp["time"] / 1e9,
        }
