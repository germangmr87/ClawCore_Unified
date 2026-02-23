import sys
import time
import threading
import random
import logging
from pathlib import Path

# NÚCLEO SOBERANO: Gestión dinámica de rutas
root_dir = Path(__file__).resolve().parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.clawcore_system.neuronas.neuronas_locales import decidir_autonomamente, red_neuronal
from src.clawcore_system.neuronas.gobernador_recursos import GobernadorRecursos



# Configuración del Benchmark
TOTAL_REQUESTS = 500
CONCURRENCY = 10  # Hilos simultáneos
SIMULATED_LOAD_TIME = 0.05 # s

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("Benchmark")

class NeuralBenchmark:
    def __init__(self):
        self.gobernador = GobernadorRecursos()
        self.tiempos = []
        self.exitos = 0
        self.errores = 0
        self.hits_cache = 0
        self._lock = threading.Lock()

    def _simular_peticion(self, id_hilo):
        """Simula una carga de trabajo neuronal."""
        situaciones = [
            "Analizar vulnerabilidad en puerto 80",
            "Optimizar uso de memoria ram",
            "Validar integridad de archivos de sistema",
            "Error critico en base de datos",
            "Actualizar pesos de aprendizaje"
        ]
        
        for i in range(TOTAL_REQUESTS // CONCURRENCY):
            start = time.perf_counter()
            situacion = random.choice(situaciones)
            
            # 50% de probabilidad de generar situaciones repetidas para probar O(1) Cache
            if i % 2 == 0:
                situacion = situaciones[0]
            
            try:
                # El contexto cambia ligeramente para forzar decisiones frescas o hits
                contexto = {
                    "riesgo": random.choice(["bajo", "medio", "alto"]),
                    "recursos_disponibles": True,
                    "complejidad": "baja"
                }
                
                resultado = decidir_autonomamente(situacion, contexto)
                
                with self._lock:
                    end = time.perf_counter()
                    self.tiempos.append(end - start)
                    self.exitos += 1
                    # Nota: El núcleo reporta autonomía pero no hits de cache directamente aquí, 
                    # lo inferimos por el tiempo < 0.001s
                    if (end - start) < 0.005:
                        self.hits_cache += 1
            except Exception as e:
                with self._lock:
                    self.errores += 1
            
            # Pequeña pausa para no saturar el kernel de mac
            time.sleep(0.01)

    def ejecutar(self):
        print(f"🚀 INICIANDO BENCHMARK DE CARGA AGÉNTICA (V4.5.1)")
        print(f"• Peticiones totales: {TOTAL_REQUESTS}")
        print(f"• Concurrencia: {CONCURRENCY} hilos")
        print("-" * 50)
        
        estado_previo = self.gobernador.obtener_estado_critico()
        start_bench = time.perf_counter()
        
        hilos = []
        for i in range(CONCURRENCY):
            t = threading.Thread(target=self._simular_peticion, args=(i,))
            hilos.append(t)
            t.start()
            
        for t in hilos:
            t.join()
            
        end_bench = time.perf_counter()
        duracion_total = end_bench - start_bench
        
        estado_post = self.gobernador.obtener_estado_critico()
        
        # Análisis de Resultados
        avg_time = sum(self.tiempos) / len(self.tiempos) if self.tiempos else 0
        throughput = self.exitos / duracion_total
        
        print("\n📊 RESULTADOS DEL ANALISIS DE CARGA:")
        print(f"   • Tiempo Total: {duracion_total:.2f}s")
        print(f"   • Latencia Media: {avg_time*1000:.2f}ms")
        print(f"   • Rendimiento (Throughput): {throughput:.1f} req/sec")
        print(f"   • Cache-Hit Efficiency (Inferida): {(self.hits_cache/self.exitos)*100:.1f}%")
        print(f"   • Tasa de Error: {(self.errores/TOTAL_REQUESTS)*100:.2f}%")
        
        print("\n📈 IMPACTO EN RECURSOS (Vía Gobernador):")
        print(f"   • CPU Post-Carga: {estado_post['cpu_total']}% (Delta: {estado_post['cpu_total'] - estado_previo['cpu_total']:.1f}%)")
        print(f"   • RAM en Uso: {estado_post['ram_uso_pct']}%")
        
        if self.errores == 0 and avg_time < 0.05:
            print("\n🔱 VERDICTO: SISTEMA ALTAMENTE ESCALABLE. Listo para enjambre masivo.")
        else:
            print("\n⚠️ VERDICTO: Cuello de botella detectado. Revisar IO de SQLite.")

if __name__ == "__main__":
    bench = NeuralBenchmark()
    bench.ejecutar()
