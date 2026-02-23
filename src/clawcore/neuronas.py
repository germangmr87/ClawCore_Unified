#!/usr/bin/env python3
"""
Neuronas Locales - Sistema de decisión autónomo
Toma decisiones simples localmente (10% de autonomía inicial)
"""

import json
import pickle
import hashlib
from datetime import datetime
from pathlib import Path
import logging
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NeuronaLocal:
    """Neurona básica para decisiones locales"""
    
    def __init__(self, nombre, umbral_activacion=0.7):
        self.nombre = nombre
        self.umbral = umbral_activacion
        self.experiencias = []  # Memoria de experiencias
        self.conexiones = []    # Conexiones a otras neuronas
        self.peso = 1.0         # Peso de la neurona
        self.ultima_activacion = None
        
    def procesar(self, entrada, contexto):
        """Procesa entrada y decide si activarse"""
        # Evaluar entrada basada en experiencias previas
        similitud = self._calcular_similitud(entrada)
        confianza = self._calcular_confianza(contexto)
        
        # Decisión combinada
        activacion = (similitud * 0.6) + (confianza * 0.4)
        
        if activacion >= self.umbral:
            self.ultima_activacion = datetime.now()
            decision = self._generar_decision(entrada, contexto)
            
            # Aprender de esta experiencia
            self._aprender(entrada, contexto, decision, activacion)
            
            return {
                "activada": True,
                "neurona": self.nombre,
                "decision": decision,
                "confianza": activacion,
                "tipo": "local"
            }
        
        return {"activada": False, "neurona": self.nombre}

    def _calcular_similitud(self, entrada):
        """Calcula similitud con experiencias previas"""
        if not self.experiencias:
            return 0.5  # Neutral si no hay experiencias
        
        entrada_hash = hashlib.md5(str(entrada).encode()).hexdigest()
        similares = 0
        for exp in self.experiencias[-10:]:
            if exp.get("entrada_hash") == entrada_hash:
                similares += 1
        
        return min(similares / 10, 1.0)

    def _calcular_confianza(self, contexto):
        """Calcula confianza basada en contexto"""
        factores_confianza = {
            "recursos_disponibles": 0.8,
            "tiempo_disponible": 0.7,
            "complejidad_baja": 0.9,
            "riesgo_bajo": 0.85
        }
        
        confianza = 0.5
        for factor, valor in factores_confianza.items():
            if factor in contexto:
                confianza = (confianza + valor) / 2
        
        return confianza

    def _generar_decision(self, entrada, contexto):
        """Genera decisión basada en patrones aprendidos"""
        patrones = {
            "error_configuracion": "validar_estructura_antes_de_aplicar",
            "recurso_insuficiente": "optimizar_o_esperar",
            "tiempo_limite": "tomar_decision_conservadora",
            "complejidad_alta": "consultar_sistemas_externos",
            "riesgo_bajo": "proceder_con_cautela"
        }
        
        for patron, decision in patrones.items():
            if patron in str(entrada).lower():
                return decision
        
        if contexto.get("riesgo_bajo", False):
            return "proceder_autonomamente"
        else:
            return "consultar_y_validar"

    def _aprender(self, entrada, contexto, decision, resultado):
        """Aprende de la experiencia"""
        experiencia = {
            "timestamp": datetime.now().isoformat(),
            "entrada": str(entrada)[:100],
            "entrada_hash": hashlib.md5(str(entrada).encode()).hexdigest(),
            "contexto": contexto,
            "decision": decision,
            "resultado": resultado,
            "exito": resultado > 0.6
        }
        
        self.experiencias.append(experiencia)
        if experiencia["exito"]:
            self.peso = min(self.peso * 1.1, 2.0)
        else:
            self.peso = max(self.peso * 0.9, 0.5)
        
        if len(self.experiencias) > 100:
            self.experiencias = self.experiencias[-100:]

class RedNeuronalAutonoma:
    """Red de neuronas para autonomía progresiva"""
    
    def __init__(self):
        self.neuronas = {}
        self.archivo_memoria = Path.home() / ".clawcore" / "memoria_neural.pkl"
        self.nivel_autonomia = 0.10
        self.evoluciones = []
        self._inicializar_neuronas()
        self.cargar_memoria()
    
    def _inicializar_neuronas(self):
        """Inicializa neuronas básicas"""
        neuronas_basicas = [
            ("supervivencia", 0.6),
            ("optimizacion", 0.7),
            ("validacion", 0.8),
            ("aprendizaje", 0.5),
            ("adaptacion", 0.65),
        ]
        for nombre, umbral in neuronas_basicas:
            self.neuronas[nombre] = NeuronaLocal(nombre, umbral)
        logger.info(f"✅ Red neuronal inicializada con {len(self.neuronas)} neuronas")

    def tomar_decision(self, situacion, contexto):
        """Toma decisión autónoma"""
        if self._puede_decidir_autonomamente(contexto):
            decisiones = []
            for nombre, neurona in self.neuronas.items():
                if self._es_relevante(nombre, situacion):
                    decision = neurona.procesar(situacion, contexto)
                    if decision["activada"]:
                        decisiones.append(decision)
            
            if decisiones:
                mejor_decision = max(decisiones, key=lambda d: d["confianza"])
                if mejor_decision["confianza"] > 0.7:
                    self._aumentar_autonomia(0.01)
                return {
                    "autonomo": True,
                    "decision": mejor_decision["decision"],
                    "confianza": mejor_decision["confianza"],
                    "neurona": mejor_decision["neurona"]
                }
        return {"autonomo": False, "decision": "consultar_externo"}

    def _puede_decidir_autonomamente(self, contexto):
        probabilidad = self.nivel_autonomia
        return random.random() < min(probabilidad, 0.95)

    def _es_relevante(self, nombre_neurona, situacion):
        relevancias = {
            "supervivencia": ["error", "caida", "muerte", "reinicio"],
            "optimizacion": ["lento", "recurso", "memoria", "cpu"],
            "validacion": ["validar", "verificar", "chequear"],
            "aprendizaje": ["aprender", "evolucionar"],
            "adaptacion": ["cambio", "nuevo", "ajustar"]
        }
        if nombre_neurona in relevancias:
            for palabra in relevancias[nombre_neurona]:
                if palabra in situacion.lower():
                    return True
        return False

    def _aumentar_autonomia(self, incremento):
        self.nivel_autonomia = min(self.nivel_autonomia + incremento, 1.0)
        self.guardar_memoria()

    def guardar_memoria(self):
        try:
            memoria = {"neuronas": self.neuronas, "nivel_autonomia": self.nivel_autonomia}
            self.archivo_memoria.parent.mkdir(exist_ok=True, parents=True)
            with open(self.archivo_memoria, 'wb') as f:
                pickle.dump(memoria, f)
        except Exception as e:
            logger.error(f"Error guardando memoria: {e}")

    def cargar_memoria(self):
        try:
            if self.archivo_memoria.exists():
                with open(self.archivo_memoria, 'rb') as f:
                    memoria = pickle.load(f)
                self.neuronas = memoria.get("neuronas", self.neuronas)
                self.nivel_autonomia = memoria.get("nivel_autonomia", 0.10)
        except Exception as e:
            logger.error(f"Error cargando memoria: {e}")

# Instancia global
red_neuronal = RedNeuronalAutonoma()

def decidir_autonomamente(situacion, contexto=None):
    if contexto is None:
        contexto = {"riesgo": "bajo", "complejidad": "media"}
    return red_neuronal.tomar_decision(situacion, contexto)
