import sys
import json
import random
import logging
from pathlib import Path
from typing import List, Dict

# NÚCLEO SOBERANO: Gestión dinámica de rutas
root_dir = Path(__file__).parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))
if str(root_dir / "src/clawcore_system/neuronas") not in sys.path:
    sys.path.append(str(root_dir / "src/clawcore_system/neuronas"))

# Importaciones soberanas absolutas (Audit: Estructura de Paquete)
from src.clawcore_system.neuronas.neuronas_locales import RedNeuronalAutonoma
from src.clawcore_system.neuronas.descubridor_herramientas import DescubridorHerramientas
from src.clawcore_system.neuronas.gobernador_recursos import GobernadorRecursos
from src.clawcore_system.neuronas.simulador_decisiones import simulador
from src.clawcore_system.neuronas.claw_gpt_mini import claw_mini


logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("OrquestadorSoberano")


class OrquestadorSoberano:
    """
    SISTEMA DE ORQUESTACIÓN AGÉNTICA V4
    Implementa: Tool Discovery, Self-Healing, Load Prediction y Wisdom Scaling.
    """
    def __init__(self):
        self.red = RedNeuronalAutonoma()
        self.root = Path(__file__).parent.parent.parent.parent
        self.descubridor = DescubridorHerramientas(self.root)
        self.descubridor.escanear_proyecto() 
        self.gobernador = GobernadorRecursos() # PUNTO 4: Monitoreo Eficiente
        self.wisdom_index = 0.40 

    def detener(self):
        """Apagado controlado del orquestador (Audit: Orphan Process Prevention)."""
        logger.warning("🔱 Apagando Orquestador Soberano...")
        self.red.detener()

    def ejecutar_objetivo(self, objetivo: str, intentos=0):
        """
        Ejecuta un objetivo con capacidad de PUNTO 2: Self-Healing (Recursivo)
        """
        if intentos > 2:
            logger.error(f"❌ Abortando objetivo '{objetivo}' tras 3 intentos fallidos.")
            return {"error": "Limite de auto-correccion excedido"}

        # PUNTO 4: Gobernanza de hardware (Throttling agéntico)
        self.red.nivel_autonomia = self.gobernador.aplicar_throttling_agéntico(self.red.nivel_autonomia)

        logger.info(f"🔱 ORQUESTANDO OBJETIVO: {objetivo} (Intento {intentos+1})")
        
        # 0. INTENTO DE INFERENCIA MINI (0 TOKENS)
        res_mini = claw_mini.generar(objetivo)
        if res_mini["resultado"] and res_mini["confianza"] > 0.8:
            logger.info("💎 ClawGPT Mini resolvió el objetivo localmente (0 tokens).")
            return {
                "objetivo": objetivo,
                "status": "CLAW_GPT_MINI_SOLVED",
                "resultado": res_mini["resultado"],
                "ahorro": "100%",
                "confianza": res_mini["confianza"]
            }

        # PUNTO 4: Pre-Throttling (Predicción de Carga)

        prediccion_carga = self._predecir_carga(objetivo)
        if prediccion_carga > 80:
            logger.warning(f"⚠️ Carga proyectada alta ({prediccion_carga}%). Throttling preventivo activo.")

        # 1. Planificación dinámica con Tool Discovery
        herramientas = self.descubridor.obtener_herramientas_para_tarea(objetivo)
        plan = self._generar_plan_dinamico(objetivo, herramientas)
        
        resultados = {}
        exito_total = True

        # 2. Ejecución paralela delegada
        for paso in plan:
            neurona = paso["neurona"]
            tarea = paso["tarea"]
            
            # EVALUACIÓN DE RIESGO SOBERANO
            evaluacion = simulador.evaluar_accion(neurona, tarea, {"objetivo": objetivo})
            if evaluacion.get("requiere_humano"):
                logger.warning(f"🚨 TAREA BLOQUEADA por riego {evaluacion['riesgo']}: {tarea}. Requiere aprobación en Dashboard.")
                exito_total = False
                resultados[neurona] = {"status": "BLOCKED_BY_SIMULATOR", "evaluacion": evaluacion}
                continue

            logger.info(f"➡️ Delegando a {neurona}: {tarea}")
            
            if neurona in self.red.neuronas:
                res = self.red.neuronas[neurona].procesar(tarea, {"objetivo": objetivo})
                
                if not res["activada"] or "error" in res.get("decision", "").lower():
                    logger.warning(f"💥 Fallo detectado en {neurona}. Iniciando Auto-Corrección...")
                    exito_total = False
                    break
                
                resultados[neurona] = res
            else:
                logger.error(f"❌ Neurona {neurona} no encontrada.")
                exito_total = False
                break

        # PUNTO 2: Lógica de Self-Healing
        if not exito_total:
            return self.ejecutar_objetivo(objetivo, intentos + 1)

        # PUNTO 10: Wisdom Scaling (Actualización de sabiduría basada en éxito)
        self.wisdom_index = min(1.0, self.wisdom_index + 0.02)
        
        # Persistencia Crítica (Audit: Siniestro/Amnesia)
        self.red.guardar_memoria()
        
        final_res = self._sintetizar_final(objetivo, resultados)
        
        # APRENDIZAJE: Destilar éxito para ClawGPT Mini
        claw_mini.destilar(objetivo, str(final_res["resumen"]))
        
        return final_res



    def _predecir_carga(self, objetivo):
        """PUNTO 4: Predicción de Carga (Heurística)"""
        puntos = len(objetivo.split()) * 5
        if "código" in objetivo.lower() or "implementar" in objetivo.lower():
            puntos += 30
        return min(puntos, 100)

    def _generar_plan_dinamico(self, objetivo, herramientas):
        """Usa Tool Discovery para mapear el plan"""
        plan = []
        # Si el descubridor encontró herramientas, las incluimos en el plan
        if herramientas:
            top_tool = herramientas[0]
            plan.append({"tarea": f"Utilizar herramienta {top_tool['herramienta']} para {objetivo}", "neurona": "NEURONA_CODIFICACION_ES"})
        
        # Plan base si no hay herramientas específicas
        plan.append({"tarea": f"Analizar lógica de {objetivo}", "neurona": "NEURONA_RAZONAMIENTO_ES"})
        plan.append({"tarea": f"Validar resultados finales", "neurona": "NEURONA_SEGURIDAD_ES"})
        return plan

    def _sintetizar_final(self, objetivo, resultados):
        return {
            "objetivo": objetivo,
            "status": "SINTONIA_NOMINAL",
            "wisdom_scaling": f"{self.wisdom_index:.2%}",
            "autonomia": f"{self.red.nivel_autonomia:.2%}",
            "resumen": f"Objetivo cumplido mediante enjambre soberano. Sabiduría incrementada."
        }

if __name__ == "__main__":
    import signal
    orq = OrquestadorSoberano()

    def shutdown_handler(sig, frame):
        print("\n🔱 Captada señal de terminación. Ejecutando apagado soberano...")
        orq.detener()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    res = orq.ejecutar_objetivo("Optimizar sistema de seguridad local")
    print(json.dumps(res, indent=4))
