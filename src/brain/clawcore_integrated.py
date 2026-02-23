#!/usr/bin/env python3
"""
ClawCore Integrated - Núcleo + Monitor integrados
"""

import asyncio
import json
import sqlite3
import time
import logging
from typing import Dict, List
import aiohttp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar monitor (simplificado para demo)
class SimpleMonitor:
    """Monitor simplificado integrado"""
    
    def __init__(self):
        self.metrics = {
            "response_times": [],
            "errors": [],
            "costs": [],
            "api_usage": {}
        }
    
    async def track_response(self, api: str, response_time: float, cost: float = 0):
        """Registra métrica de respuesta"""
        self.metrics["response_times"].append({
            "api": api,
            "time": response_time,
            "timestamp": time.time()
        })
        
        if api not in self.metrics["api_usage"]:
            self.metrics["api_usage"][api] = 0
        self.metrics["api_usage"][api] += 1
        
        if cost > 0:
            self.metrics["costs"].append({
                "api": api,
                "cost": cost,
                "timestamp": time.time()
            })
        
        # Análisis simple
        if response_time > 5.0:
            logger.warning(f"⚠️  Respuesta lenta de {api}: {response_time:.1f}s")
        
        if cost > 0.01:
            logger.warning(f"💰 Costo alto de {api}: ${cost:.4f}")
    
    async def track_error(self, api: str, error: str):
        """Registra error"""
        self.metrics["errors"].append({
            "api": api,
            "error": error,
            "timestamp": time.time()
        })
        logger.error(f"❌ Error de {api}: {error}")
    
    def get_analysis(self) -> Dict:
        """Obtiene análisis simple"""
        if not self.metrics["response_times"]:
            return {"message": "No hay métricas aún"}
        
        # API más usada
        api_usage = self.metrics["api_usage"]
        most_used = max(api_usage.items(), key=lambda x: x[1]) if api_usage else ("none", 0)
        
        # Tiempo promedio por API
        api_times = {}
        for rt in self.metrics["response_times"]:
            api = rt["api"]
            if api not in api_times:
                api_times[api] = []
            api_times[api].append(rt["time"])
        
        avg_times = {api: sum(times)/len(times) for api, times in api_times.items()}
        
        # Costo total
        total_cost = sum(c["cost"] for c in self.metrics["costs"])
        
        # Sugerencias
        suggestions = []
        
        # Si hay API lenta
        for api, avg_time in avg_times.items():
            if avg_time > 3.0:
                suggestions.append(f"API {api} es lenta ({avg_time:.1f}s). Considerar cache.")
        
        # Si hay errores frecuentes
        error_count = len(self.metrics["errors"])
        if error_count > 3:
            suggestions.append(f"{error_count} errores recientes. Revisar conexiones API.")
        
        # Si costo alto
        if total_cost > 0.05:
            suggestions.append(f"Costo acumulado ${total_cost:.4f}. Optimizar uso de APIs premium.")
        
        return {
            "most_used_api": most_used[0],
            "usage_count": most_used[1],
            "average_response_times": avg_times,
            "total_cost": total_cost,
            "error_count": error_count,
            "suggestions": suggestions,
            "total_requests": len(self.metrics["response_times"])
        }

class ClawCoreIntegrated:
    """ClawCore con monitor integrado"""
    
    def __init__(self):
        # APIs (igual que antes)
        self.apis = [
            {
                "name": "DeepSeek",
                "base_url": "https://api.deepseek.com",
                "api_key": None,
                "model": "deepseek-chat",
                "cost_per_1k": 0.00014,
                "priority": 1
            },
            {
                "name": "LLMAPI",
                "base_url": "https://internal.llmapi.ai/v1",
                "api_key": "llmgtwy_jxlfeRWOWxTIKq8incbH7MKelBUxNhJtotLLFLBt",
                "model": "gpt-4o-mini",
                "cost_per_1k": 0.00015,
                "priority": 2
            }
        ]
        
        # Monitor integrado
        self.monitor = SimpleMonitor()
        
        # Memoria
        self.db = sqlite3.connect("/tmp/clawcore_integrated.db")
        self.init_db()
        
        logger.info("ClawCore Integrated inicializado")
    
    def init_db(self):
        cursor = self.db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                message TEXT,
                response TEXT,
                api_used TEXT,
                response_time REAL,
                cost REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.db.commit()
    
    async def call_api(self, api_config: Dict, messages: List[Dict]) -> str:
        """Llama a API con tracking"""
        start_time = time.time()
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_config['api_key']}" if api_config['api_key'] else ""
            }
            
            payload = {
                "model": api_config["model"],
                "messages": messages,
                "max_tokens": 500,
                "stream": False
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{api_config['base_url']}/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=15  # Timeout más corto
                ) as response:
                    
                    elapsed = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                        
                        # Calcular costo
                        tokens = len(content) / 4
                        cost = tokens * api_config["cost_per_1k"]
                        
                        # Trackear respuesta
                        await self.monitor.track_response(
                            api=api_config["name"],
                            response_time=elapsed,
                            cost=cost
                        )
                        
                        return content, elapsed, cost
                    else:
                        error_text = await response.text()
                        await self.monitor.track_error(
                            api=api_config["name"],
                            error=f"HTTP {response.status}: {error_text[:100]}"
                        )
                        return None, elapsed, 0
                        
        except Exception as e:
            elapsed = time.time() - start_time
            await self.monitor.track_error(
                api=api_config["name"],
                error=str(e)
            )
            return None, elapsed, 0
    
    async def get_response(self, user_id: str, message: str) -> str:
        """Obtiene respuesta con monitoreo completo"""
        start_time = time.time()
        
        # Guardar mensaje
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO conversations (user_id, message) VALUES (?, ?)",
            (user_id, message)
        )
        msg_id = cursor.lastrowid
        
        # Intentar APIs en orden
        messages = [{"role": "user", "content": message}]
        
        for api in sorted(self.apis, key=lambda x: x["priority"]):
            logger.info(f"Intentando {api['name']}...")
            
            response, elapsed, cost = await self.call_api(api, messages)
            
            if response:
                # Guardar respuesta completa
                cursor.execute("""
                    UPDATE conversations 
                    SET response = ?, api_used = ?, response_time = ?, cost = ?
                    WHERE id = ?
                """, (response, api["name"], elapsed, cost, msg_id))
                self.db.commit()
                
                logger.info(f"✅ {api['name']} respondió en {elapsed:.1f}s (${cost:.4f})")
                
                # Análisis periódico
                if len(self.monitor.metrics["response_times"]) % 5 == 0:
                    analysis = self.monitor.get_analysis()
                    logger.info(f"📊 Análisis: {analysis}")
                
                return response
        
        # Si todas fallan
        error_msg = "❌ No se pudo obtener respuesta"
        cursor.execute(
            "UPDATE conversations SET response = ? WHERE id = ?",
            (error_msg, msg_id)
        )
        self.db.commit()
        
        return error_msg
    
    def get_stats(self) -> Dict:
        """Obtiene estadísticas completas"""
        cursor = self.db.cursor()
        
        # Stats de base de datos
        cursor.execute("SELECT COUNT(*) FROM conversations")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM conversations WHERE response IS NOT NULL")
        successful = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(response_time) FROM conversations WHERE response_time IS NOT NULL")
        avg_time = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT SUM(cost) FROM conversations WHERE cost IS NOT NULL")
        total_cost = cursor.fetchone()[0] or 0
        
        # Stats del monitor
        monitor_stats = self.monitor.get_analysis()
        
        return {
            "database": {
                "total_messages": total,
                "successful_responses": successful,
                "success_rate": (successful / total * 100) if total > 0 else 0,
                "avg_response_time": avg_time,
                "total_cost": total_cost
            },
            "monitor": monitor_stats,
            "suggestions": monitor_stats.get("suggestions", [])
        }
    
    def close(self):
        self.db.close()

async def main():
    """Demo integrada"""
    print("🚀 ClawCore Integrated - Demo")
    print("=" * 40)
    
    core = ClawCoreIntegrated()
    
    # Test 1: Respuesta simple
    print("\n🧪 Test 1: Respuesta con monitoreo")
    response = await core.get_response("user123", "Hola, ¿cómo funciona el monitoreo?")
    print(f"Respuesta: {response[:150]}...")
    
    # Test 2: Otra respuesta
    print("\n🧪 Test 2: Otra respuesta")
    response = await core.get_response("user123", "Explícame qué métricas monitorea")
    print(f"Respuesta: {response[:150]}...")
    
    # Test 3: Stats completas
    print("\n📊 Test 3: Estadísticas con análisis")
    stats = core.get_stats()
    
    print(f"  Total mensajes: {stats['database']['total_messages']}")
    print(f"  Tasa éxito: {stats['database']['success_rate']:.1f}%")
    print(f"  Tiempo promedio: {stats['database']['avg_response_time']:.1f}s")
    print(f"  Costo total: ${stats['database']['total_cost']:.4f}")
    
    print(f"\n  API más usada: {stats['monitor'].get('most_used_api', 'N/A')}")
    print(f"  Total requests: {stats['monitor'].get('total_requests', 0)}")
    
    if stats['suggestions']:
        print("\n  💡 Sugerencias del monitor:")
        for suggestion in stats['suggestions']:
            print(f"    • {suggestion}")
    
    core.close()
    print("\n✅ Demo integrada completada")

if __name__ == "__main__":
    asyncio.run(main())