import json
import time

class NanoEngine:
    """
    Motor de Inferencia Nano-Local (<5ms)
    Simula una red neuronal de peso ultra-ligero para decisiones de seguridad en RAM.
    """
    def __init__(self):
        """Inicializa el motor nano estableciendo la matriz de pesos estática en RAM."""

        # "Pesos" del modelo nano (Cargados en RAM)
        self.matriz_pesos = {
            "seguridad": {
                "evaluar": 0.8,
                "riesgo": 0.9,
                "ataque": 0.95,
                "vulnerabilidad": 0.85
            },
            "acciones": {
                "bloquear": 0.9,
                "ignorar": 0.1,
                "notificar": 0.5
            }
        }
        self.latencia_promedio = 0.002 # 2ms

    def inferir(self, entrada: str):
        """Realiza una inferencia rápida basada en vectores de peso"""
        t_inicio = time.time()
        
        tokens = entrada.lower().split()
        score_riesgo = 0.0
        
        # Simulación de propagación hacia adelante
        for token in tokens:
            if token in self.matriz_pesos["seguridad"]:
                score_riesgo += self.matriz_pesos["seguridad"][token]
        
        # Normalización
        score_riesgo = min(1.0, score_riesgo / 2.0)
        
        decision = "proceder"
        if score_riesgo > 0.7:
            decision = "bloquear_protocolo_seguridad"
        elif score_riesgo > 0.4:
            decision = "notificar_admin"
            
        t_fin = time.time()
        latencia = t_fin - t_inicio
        
        return {
            "modelo": "ClawNano-V1",
            "score_riesgo": score_riesgo,
            "decision": decision,
            "latencia_ms": latencia * 1000,
            "estado_ram": "residente"
        }

if __name__ == "__main__":
    engine = NanoEngine()
    resultado = engine.inferir("Posible ataque de vulnerabilidad detectado en el perímetro")
    print(json.dumps(resultado, indent=4))
