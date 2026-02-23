#!/usr/bin/env python3
"""
ClawCore Monitor - Agente que monitorea TODO y sugiere mejoras
"""

import asyncio
import json
import sqlite3
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import aiohttp
import psutil
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClawCoreMonitor:
    """Monitor inteligente que analiza TODO el sistema"""
    
    def __init__(self):
        self.monitor_db = sqlite3.connect("/tmp/clawcore_monitor.db")
        self.init_monitor_db()
        
        # Métricas a monitorear
        self.metrics = {
            "performance": [],
            "errors": [],
            "costs": [],
            "usage_patterns": [],
            "system_health": []
        }
        
        # Umbrales de alerta
        self.thresholds = {
            "response_time": 5.0,  # segundos
            "error_rate": 0.1,     # 10%
            "cost_per_request": 0.01,  # $0.01
            "memory_usage": 80,    # 80%
            "cpu_usage": 70        # 70%
        }
        
        logger.info("ClawCore Monitor inicializado")
    
    def init_monitor_db(self):
        """Inicializa base de datos de monitoreo"""
        cursor = self.monitor_db.cursor()
        
        # Tabla métricas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_type TEXT,
                value REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                context TEXT
            )
        """)
        
        # Tabla alertas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT,
                severity TEXT,
                message TEXT,
                suggestion TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                resolved BOOLEAN DEFAULT FALSE
            )
        """)
        
        # Tabla mejoras sugeridas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS improvements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                area TEXT,
                current_state TEXT,
                suggested_improvement TEXT,
                priority INTEGER,
                estimated_impact TEXT,
                implemented BOOLEAN DEFAULT FALSE,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.monitor_db.commit()
    
    async def monitor_performance(self, response_time: float, api_used: str):
        """Monitorea performance de respuestas"""
        cursor = self.monitor_db.cursor()
        cursor.execute(
            "INSERT INTO metrics (metric_type, value, context) VALUES (?, ?, ?)",
            ("response_time", response_time, api_used)
        )
        
        # Alertar si es lento
        if response_time > self.thresholds["response_time"]:
            await self.create_alert(
                alert_type="performance",
                severity="warning",
                message=f"Respuesta lenta: {response_time:.1f}s (API: {api_used})",
                suggestion=f"Considerar cambiar a API más rápida o implementar cache"
            )
        
        self.monitor_db.commit()
    
    async def monitor_errors(self, error_type: str, error_details: str):
        """Monitorea errores"""
        cursor = self.monitor_db.cursor()
        cursor.execute(
            "INSERT INTO metrics (metric_type, value, context) VALUES (?, ?, ?)",
            ("error", 1, f"{error_type}: {error_details}")
        )
        
        # Calcular tasa de error reciente
        cursor.execute("""
            SELECT COUNT(*) FROM metrics 
            WHERE metric_type = 'error' 
            AND timestamp > datetime('now', '-1 hour')
        """)
        recent_errors = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM metrics 
            WHERE metric_type = 'response_time' 
            AND timestamp > datetime('now', '-1 hour')
        """)
        total_requests = cursor.fetchone()[0]
        
        if total_requests > 0:
            error_rate = recent_errors / total_requests
            if error_rate > self.thresholds["error_rate"]:
                await self.create_alert(
                    alert_type="reliability",
                    severity="critical",
                    message=f"Alta tasa de errores: {error_rate:.1%} en última hora",
                    suggestion="Revisar conexiones API, implementar mejor fallback"
                )
        
        self.monitor_db.commit()
    
    async def monitor_costs(self, cost: float, api_used: str):
        """Monitorea costos"""
        cursor = self.monitor_db.cursor()
        cursor.execute(
            "INSERT INTO metrics (metric_type, value, context) VALUES (?, ?, ?)",
            ("cost", cost, api_used)
        )
        
        # Alertar si costo alto
        if cost > self.thresholds["cost_per_request"]:
            await self.create_alert(
                alert_type="cost",
                severity="warning",
                message=f"Costo alto por request: ${cost:.4f} (API: {api_used})",
                suggestion="Considerar usar API más barata o optimizar prompts"
            )
        
        self.monitor_db.commit()
    
    async def monitor_system_health(self):
        """Monitorea salud del sistema"""
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memoria
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Disco
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        cursor = self.monitor_db.cursor()
        cursor.execute(
            "INSERT INTO metrics (metric_type, value, context) VALUES (?, ?, ?)",
            ("cpu_usage", cpu_percent, "system")
        )
        cursor.execute(
            "INSERT INTO metrics (metric_type, value, context) VALUES (?, ?, ?)",
            ("memory_usage", memory_percent, "system")
        )
        cursor.execute(
            "INSERT INTO metrics (metric_type, value, context) VALUES (?, ?, ?)",
            ("disk_usage", disk_percent, "system")
        )
        
        # Alertas de sistema
        if cpu_percent > self.thresholds["cpu_usage"]:
            await self.create_alert(
                alert_type="system",
                severity="warning",
                message=f"CPU alta: {cpu_percent}%",
                suggestion="Optimizar procesos, considerar escalar recursos"
            )
        
        if memory_percent > self.thresholds["memory_usage"]:
            await self.create_alert(
                alert_type="system",
                severity="warning",
                message=f"Memoria alta: {memory_percent}%",
                suggestion="Limpiar cache, optimizar uso de memoria"
            )
        
        self.monitor_db.commit()
        return {
            "cpu": cpu_percent,
            "memory": memory_percent,
            "disk": disk_percent
        }
    
    async def create_alert(self, alert_type: str, severity: str, message: str, suggestion: str):
        """Crea una alerta"""
        cursor = self.monitor_db.cursor()
        cursor.execute(
            "INSERT INTO alerts (alert_type, severity, message, suggestion) VALUES (?, ?, ?, ?)",
            (alert_type, severity, message, suggestion)
        )
        self.monitor_db.commit()
        
        logger.warning(f"ALERTA [{severity}] {alert_type}: {message}")
        
        # Si es crítica, sugerir mejora automáticamente
        if severity == "critical":
            await self.suggest_improvement(
                area=alert_type,
                current_state=message,
                suggested_improvement=suggestion,
                priority=1  # Alta prioridad
            )
    
    async def suggest_improvement(self, area: str, current_state: str, 
                                 suggested_improvement: str, priority: int = 2):
        """Sugiere una mejora basada en análisis"""
        cursor = self.monitor_db.cursor()
        
        # Verificar si ya existe sugerencia similar
        cursor.execute("""
            SELECT COUNT(*) FROM improvements 
            WHERE area = ? AND suggested_improvement LIKE ? AND implemented = FALSE
        """, (area, f"%{suggested_improvement[:50]}%"))
        
        existing = cursor.fetchone()[0]
        
        if existing == 0:
            estimated_impact = self.estimate_impact(area, suggested_improvement)
            
            cursor.execute("""
                INSERT INTO improvements 
                (area, current_state, suggested_improvement, priority, estimated_impact)
                VALUES (?, ?, ?, ?, ?)
            """, (area, current_state, suggested_improvement, priority, estimated_impact))
            
            self.monitor_db.commit()
            logger.info(f"✅ Mejora sugerida: {suggested_improvement}")
    
    def estimate_impact(self, area: str, improvement: str) -> str:
        """Estima impacto de una mejora"""
        impacts = {
            "performance": "Reducción 30-50% en tiempo de respuesta",
            "cost": "Ahorro 20-80% en costos API",
            "reliability": "Aumento 25% en tasa de éxito",
            "system": "Reducción 40% en uso de recursos",
            "scalability": "Capacidad para 10x más usuarios"
        }
        return impacts.get(area, "Mejora general en experiencia")
    
    async def analyze_trends(self) -> List[Dict]:
        """Analiza tendencias y sugiere mejoras proactivas"""
        cursor = self.monitor_db.cursor()
        improvements = []
        
        # 1. Análisis de performance
        cursor.execute("""
            SELECT AVG(value), context FROM metrics 
            WHERE metric_type = 'response_time' 
            AND timestamp > datetime('now', '-24 hours')
            GROUP BY context
        """)
        
        for avg_time, api in cursor.fetchall():
            if avg_time and avg_time > 3.0:  # Más de 3 segundos
                improvements.append({
                    "area": "performance",
                    "current_state": f"API {api} tarda {avg_time:.1f}s en promedio",
                    "suggested_improvement": f"Implementar cache para respuestas de {api}",
                    "priority": 2
                })
        
        # 2. Análisis de costos
        cursor.execute("""
            SELECT SUM(value), context FROM metrics 
            WHERE metric_type = 'cost' 
            AND timestamp > datetime('now', '-24 hours')
            GROUP BY context
            ORDER BY SUM(value) DESC
        """)
        
        results = cursor.fetchall()
        if len(results) > 1:
            most_expensive = results[0]
            cheapest = results[-1]
            
            if most_expensive[0] > cheapest[0] * 5:  # 5x más caro
                improvements.append({
                    "area": "cost",
                    "current_state": f"{most_expensive[1]} cuesta ${most_expensive[0]:.4f} vs ${cheapest[0]:.4f} de {cheapest[1]}",
                    "suggested_improvement": f"Usar {cheapest[1]} más frecuentemente, reservar {most_expensive[1]} para tareas críticas",
                    "priority": 1
                })
        
        # 3. Análisis de errores
        cursor.execute("""
            SELECT context, COUNT(*) FROM metrics 
            WHERE metric_type = 'error' 
            AND timestamp > datetime('now', '-24 hours')
            GROUP BY context
            ORDER BY COUNT(*) DESC
        """)
        
        for api, error_count in cursor.fetchall():
            if error_count > 5:  # Más de 5 errores
                improvements.append({
                    "area": "reliability",
                    "current_state": f"{api} tiene {error_count} errores en 24h",
                    "suggested_improvement": f"Mejorar error handling para {api} o considerar alternativa",
                    "priority": 2
                })
        
        # Guardar mejoras sugeridas
        for imp in improvements:
            await self.suggest_improvement(**imp)
        
        return improvements
    
    async def get_dashboard_data(self) -> Dict:
        """Obtiene datos para dashboard"""
        cursor = self.monitor_db.cursor()
        
        # Métricas recientes
        cursor.execute("""
            SELECT metric_type, AVG(value) FROM metrics 
            WHERE timestamp > datetime('now', '-1 hour')
            GROUP BY metric_type
        """)
        recent_metrics = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Alertas no resueltas
        cursor.execute("""
            SELECT alert_type, severity, message, suggestion FROM alerts 
            WHERE resolved = FALSE 
            ORDER BY timestamp DESC LIMIT 10
        """)
        active_alerts = cursor.fetchall()
        
        # Mejoras pendientes
        cursor.execute("""
            SELECT area, suggested_improvement, priority FROM improvements 
            WHERE implemented = FALSE 
            ORDER BY priority DESC, timestamp DESC LIMIT 10
        """)
        pending_improvements = cursor.fetchall()
        
        # Salud del sistema
        system_health = await self.monitor_system_health()
        
        return {
            "recent_metrics": recent_metrics,
            "active_alerts": [
                {"type": a[0], "severity": a[1], "message": a[2], "suggestion": a[3]}
                for a in active_alerts
            ],
            "pending_improvements": [
                {"area": i[0], "improvement": i[1], "priority": i[2]}
                for i in pending_improvements
            ],
            "system_health": system_health,
            "timestamp": datetime.now().isoformat()
        }
    
    async def run_continuous_monitoring(self, interval_seconds: int = 60):
        """Ejecuta monitoreo continuo"""
        logger.info(f"Iniciando monitoreo continuo (intervalo: {interval_seconds}s)")
        
        while True:
            try:
                # Monitorear salud del sistema
                await self.monitor_system_health()
                
                # Analizar tendencias cada 10 minutos
                if int(time.time()) % 600 < interval_seconds:
                    improvements = await self.analyze_trends()
                    if improvements:
                        logger.info(f"Análisis de tendencias: {len(improvements)} mejoras sugeridas")
                
                # Log estado
                if int(time.time()) % 300 < interval_seconds:  # Cada 5 minutos
                    data = await self.get_dashboard_data()
                    logger.info(f"Estado monitor: {len(data['active_alerts'])} alertas, {len(data['pending_improvements'])} mejoras")
                
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Error en monitoreo continuo: {e}")
                await asyncio.sleep(interval_seconds)

async def main():
    """Demo del monitor"""
    print("🔍 ClawCore Monitor - Demo")
    print("=" * 40)
    
    monitor = ClawCoreMonitor()
    
    # Simular métricas
    print("\n📊 Simulando métricas...")
    await monitor.monitor_performance(2.5, "DeepSeek")
    await monitor.monitor_performance(6.2, "OpenAI")  # Lento → alerta
    await monitor.monitor_costs(0.005, "DeepSeek")
    await monitor.monitor_costs(0.015, "OpenAI")  # Caro → alerta
    await monitor.monitor_errors("API timeout", "DeepSeek no respondió")
    
    # Obtener dashboard
    print("\n📈 Dashboard data:")
    data = await monitor.get_dashboard_data()
    print(f"  Alertas activas: {len(data['active_alerts'])}")
    print(f"  Mejoras pendientes: {len(data['pending_improvements'])}")
    print(f"  CPU: {data['system_health']['cpu']}%")
    print(f"  Memoria: {data['system_health']['memory']}%")
    
    # Analizar tendencias
    print("\n🧠 Analizando tendencias...")
    improvements = await monitor.analyze_trends()
    print(f"  Mejoras sugeridas: {len(improvements)}")
    
    for imp in improvements[:3]:  # Mostrar primeras 3
        print(f"  • {imp['area']}: {imp['suggested_improvement']}")
    
    print("\n✅ Monitor demo completado")
    print("\n🚀 Para ejecutar monitoreo continuo:")
    print("   asyncio.run(monitor.run_continuous_monitoring())")

if __name__ == "__main__":
    asyncio.run(main())