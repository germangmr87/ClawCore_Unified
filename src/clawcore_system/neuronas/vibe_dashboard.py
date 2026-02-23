"""
TELEMETRÍA VIBE V1.0 — Dashboard de Salud Emocional del Sistema
Mide éxito vs fracaso, latencia, y confianza en tiempo real.
Expone métricas vía WebSocket para consumo del portal.
"""
import json
import time
import threading
import logging
from collections import deque
from datetime import datetime

logger = logging.getLogger("VibeDashboard")
logger.setLevel(logging.INFO)


class VibeTelemetry:
    """Recolector de métricas de 'vibe' del sistema."""

    def __init__(self, window_size: int = 100):
        self.window = window_size
        self._lock = threading.Lock()
        self.decisiones = deque(maxlen=window_size)
        self.latencias = deque(maxlen=window_size)
        self.tokens_usados = 0
        self.inicio = time.time()

    def registrar_decision(self, exito: bool, latencia_ms: float, neurona: str = "", confianza: float = 0.0):
        with self._lock:
            self.decisiones.append({
                "ts": datetime.now().isoformat(),
                "exito": exito,
                "latencia_ms": latencia_ms,
                "neurona": neurona,
                "confianza": confianza
            })
            self.latencias.append(latencia_ms)

    def registrar_tokens(self, cantidad: int):
        with self._lock:
            self.tokens_usados += cantidad

    def calcular_vibe(self) -> dict:
        with self._lock:
            total = len(self.decisiones)
            if total == 0:
                return {"vibe": "NEUTRAL", "score": 0.5, "msg": "Sin datos aún"}

            exitos = sum(1 for d in self.decisiones if d["exito"])
            tasa_exito = exitos / total
            lat_media = sum(self.latencias) / len(self.latencias) if self.latencias else 0
            conf_media = sum(d["confianza"] for d in self.decisiones) / total

            # Score compuesto: 60% éxito, 25% confianza, 15% velocidad
            speed_score = max(0, 1 - (lat_media / 1000))  # penalizar > 1s
            score = (tasa_exito * 0.6) + (conf_media * 0.25) + (speed_score * 0.15)

            if score >= 0.8:
                vibe = "SEGURO"
                emoji = "😎"
            elif score >= 0.6:
                vibe = "ESTABLE"
                emoji = "🙂"
            elif score >= 0.4:
                vibe = "INCIERTO"
                emoji = "😐"
            else:
                vibe = "CONFUNDIDO"
                emoji = "😵"

            return {
                "vibe": vibe,
                "emoji": emoji,
                "score": round(score, 3),
                "tasa_exito": round(tasa_exito, 3),
                "latencia_media_ms": round(lat_media, 2),
                "confianza_media": round(conf_media, 3),
                "decisiones_ventana": total,
                "tokens_acumulados": self.tokens_usados,
                "uptime_s": round(time.time() - self.inicio, 1)
            }


# Singleton global
vibe = VibeTelemetry()


if __name__ == "__main__":
    # Simular actividad
    import random
    for i in range(50):
        vibe.registrar_decision(
            exito=random.random() > 0.2,
            latencia_ms=random.uniform(0.5, 200),
            neurona=f"NEURONA_{i % 5}",
            confianza=random.uniform(0.5, 1.0)
        )
        vibe.registrar_tokens(random.randint(10, 200))

    print(json.dumps(vibe.calcular_vibe(), indent=2, ensure_ascii=False))
