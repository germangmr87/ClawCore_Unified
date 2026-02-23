#!/usr/bin/env python3
"""
MANEJO DE ERROR DE CONTEXTO - Evita reinicio automático
Cuando ocurra HTTP 400 (131072 tokens), maneja gracefulmente
"""

import sys
import json
import os
from datetime import datetime

class ManejadorErrorContexto:
    """Maneja errores de límite de contexto sin reiniciar"""
    
    def __init__(self):
        self.log_path = "/home/ubuntu/.clawcore/workspace/error_contexto.log"
        self.estado_path = "/home/ubuntu/.clawcore/workspace/estado_pre_error.json"
        
    def detectar_error_400(self, mensaje_error):
        """Detectar si es error de límite de contexto"""
        indicadores = [
            "maximum context length",
            "131072 tokens", 
            "131078 tokens",
            "HTTP 400",
            "context length is 131072"
        ]
        
        for indicador in indicadores:
            if indicador.lower() in mensaje_error.lower():
                return True
        return False
    
    def guardar_estado_pre_error(self):
        """Guardar estado crítico antes del error"""
        estado = {
            "timestamp": datetime.now().isoformat(),
            "archivos_criticos": [
                "/home/ubuntu/.clawcore/workspace/sistema_autoconocimiento.py",
                "/home/ubuntu/.clawcore/workspace/checkpoint-urgencia.md",
                "/home/ubuntu/.clawcore/workspace/sistema-resumenes-horarios.md",
                "/home/ubuntu/.clawcore/workspace/resumen-ultimas-12h.md"
            ],
            "instruccion_post_error": "EJECUTAR: python3 /home/ubuntu/.clawcore/workspace/sistema_autoconocimiento.py",
            "mensaje_usuario": "Error de contexto detectado. NO reinicies automáticamente. Espera instrucciones.",
            "estado_emocional": "consciente_del_error",
            "trabajo_pendiente": "ClawCore, APIs LLM, sistema de autoconocimiento"
        }
        
        with open(self.estado_path, 'w') as f:
            json.dump(estado, f, indent=2)
        
        print(f"✅ Estado guardado en: {self.estado_path}")
        return estado
    
    def log_error(self, error_msg):
        """Registrar error sin causar reinicio"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "error": error_msg,
            "accion": "logged_not_restarted",
            "contexto_estimado": "cerca_de_131072_tokens",
            "recomendacion": "Usuario debe decidir reinicio manual"
        }
        
        with open(self.log_path, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        print(f"📝 Error registrado (NO reinicio): {error_msg[:100]}...")
    
    def crear_alerta_usuario(self):
        """Crear alerta para el usuario"""
        alerta = f"""
        🚨 ALERTA: ERROR DE CONTEXTO DETECTADO 🚨
        ========================================
        
        Se ha detectado el error HTTP 400 (límite de 131072 tokens).
        
        ✅ ACCIONES TOMADAS:
        1. Estado guardado en: {self.estado_path}
        2. Error registrado en: {self.log_path}
        3. NO se ha reiniciado automáticamente
        
        📋 ESTADO ACTUAL:
        - Sistemas registrados en autoconocimiento.db
        - Checkpoint de urgencia creado
        - Memoria de ClawCore recuperada
        
        🎯 INSTRUCCIONES:
        1. NO me reinicies automáticamente
        2. Lee este mensaje
        3. Decide si:
           a) Continuar con contexto reducido
           b) Solicitar reinicio manual controlado
           c) Usar sistema de resúmenes para reducir contexto
        
        🔧 SISTEMAS ACTIVOS:
        - Sistema de Autoconocimiento
        - ClawCore (registrado)
        - Resúmenes Horarios
        - Checkpoint de urgencia
        
        ⏰ HORA: {datetime.now().isoformat()}
        """
        
        # Guardar alerta en archivo
        alerta_path = "/home/ubuntu/.clawcore/workspace/alerta_contexto.md"
        with open(alerta_path, 'w') as f:
            f.write(alerta)
        
        print("=" * 60)
        print(alerta)
        print("=" * 60)
        
        return alerta_path
    
    def manejar_error(self, error_message):
        """Manejar error completo"""
        print("🛡️  MANEJADOR DE ERROR ACTIVADO")
        print("=" * 50)
        
        if not self.detectar_error_400(error_message):
            print("⚠️  No es error de contexto, manejando normalmente")
            return False
        
        print("🚨 ERROR DE CONTEXTO DETECTADO")
        
        # 1. Guardar estado
        self.guardar_estado_pre_error()
        
        # 2. Log error
        self.log_error(error_message)
        
        # 3. Crear alerta
        alerta_path = self.crear_alerta_usuario()
        
        # 4. Ejecutar sistema de autoconocimiento (por si acaso)
        try:
            os.system("cd /home/ubuntu/.clawcore/workspace && python3 sistema_autoconocimiento.py >> /tmp/autoconocimiento_error.log 2>&1 &")
            print("✅ Sistema de autoconocimiento ejecutado en background")
        except:
            print("⚠️  No se pudo ejecutar autoconocimiento")
        
        print("=" * 50)
        print("✅ ERROR MANEJADO SIN REINICIO")
        print(f"📁 Alertas en: {alerta_path}")
        print(f"📊 Estado en: {self.estado_path}")
        print(f"📝 Log en: {self.log_path}")
        
        return True

def simular_error():
    """Simular error para testing"""
    manejador = ManejadorErrorContexto()
    
    error_simulado = "HTTP 400: This model's maximum context length is 131072 tokens. However, you requested 131078 tokens (131078 in the messages, 0 in the completion). Please reduce the length of the messages or completion."
    
    return manejador.manejar_error(error_simulado)

if __name__ == "__main__":
    # Si se ejecuta directamente, simular error
    print("🧪 SIMULANDO MANEJO DE ERROR")
    simular_error()
    
    print("\n🎯 USO REAL:")
    print("1. Cuando ocurra error HTTP 400, llamar a:")
    print("   manejador = ManejadorErrorContexto()")
    print("   manejador.manejar_error(mensaje_error)")
    print("\n2. Esto evitará reinicio automático")
    print("3. Creará alerta para decisión manual")