#!/usr/bin/env python3
"""
ClawCore MVP - Núcleo minimalista en 1 archivo
"""

import asyncio
import json
import sqlite3
import logging
from typing import Dict, List
import aiohttp
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClawCore:
    """Núcleo minimalista - Todo en 1 clase"""
    
    def __init__(self):
        # APIs gratuitas/baratas primero
        self.apis = [
            {
                "name": "DeepSeek",
                "base_url": "https://api.deepseek.com",
                "api_key": None,  # Gratuita
                "model": "deepseek-chat",
                "cost_per_1k": 0.00014,
                "priority": 1
            },
            {
                "name": "OpenRouter",
                "base_url": "https://openrouter.ai/api/v1",
                "api_key": None,  # Configurar después
                "model": "openai/gpt-3.5-turbo",
                "cost_per_1k": 0.00015,
                "priority": 2
            },
            {
                "name": "LLMAPI",
                "base_url": "https://internal.llmapi.ai/v1",
                "api_key": "llmgtwy_jxlfeRWOWxTIKq8incbH7MKelBUxNhJtotLLFLBt",
                "model": "gpt-4o-mini",
                "cost_per_1k": 0.00015,
                "priority": 3
            }
        ]
        
        # Memoria SQLite simple
        self.init_memory()
        
        # Stats
        self.stats = {
            "total_requests": 0,
            "successful": 0,
            "failed": 0,
            "total_cost": 0.0
        }
    
    def init_memory(self):
        """Inicializa base de datos SQLite"""
        self.db = sqlite3.connect("/tmp/clawcore_memory.db")
        cursor = self.db.cursor()
        
        # Tabla conversaciones
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                message TEXT,
                response TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                api_used TEXT,
                cost REAL DEFAULT 0.0
            )
        """)
        
        # Tabla embeddings (simplificada)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT,
                embedding BLOB,
                metadata TEXT
            )
        """)
        
        self.db.commit()
        logger.info("Memoria SQLite inicializada")
    
    async def call_api(self, api_config: Dict, messages: List[Dict]) -> str:
        """Llama a una API LLM"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_config['api_key']}" if api_config['api_key'] else ""
            }
            
            payload = {
                "model": api_config["model"],
                "messages": messages,
                "max_tokens": 1000,
                "stream": False
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{api_config['base_url']}/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=30
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                        
                        # Calcular costo aproximado
                        tokens = len(content) / 4  # Aproximación
                        cost = tokens * api_config["cost_per_1k"]
                        self.stats["total_cost"] += cost
                        
                        return content
                    else:
                        logger.error(f"API {api_config['name']} error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"API {api_config['name']} exception: {e}")
            return None
    
    async def get_response(self, user_id: str, message: str) -> str:
        """Obtiene respuesta inteligente"""
        self.stats["total_requests"] += 1
        
        # Guardar mensaje en memoria
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO conversations (user_id, message) VALUES (?, ?)",
            (user_id, message)
        )
        self.db.commit()
        
        # Intentar APIs en orden de prioridad (más barata primero)
        messages = [{"role": "user", "content": message}]
        
        for api in sorted(self.apis, key=lambda x: x["priority"]):
            logger.info(f"Intentando API: {api['name']}")
            response = await self.call_api(api, messages)
            
            if response:
                self.stats["successful"] += 1
                
                # Guardar respuesta en memoria
                cursor.execute(
                    "UPDATE conversations SET response = ?, api_used = ? WHERE id = ?",
                    (response, api["name"], cursor.lastrowid)
                )
                self.db.commit()
                
                logger.info(f"✅ {api['name']} respondió")
                return response
        
        # Si todas fallan
        self.stats["failed"] += 1
        return "❌ No se pudo obtener respuesta de ninguna API"
    
    def get_conversation_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Obtiene historial de conversación"""
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT message, response, timestamp FROM conversations WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
            (user_id, limit)
        )
        
        history = []
        for message, response, timestamp in cursor.fetchall():
            history.append({
                "message": message,
                "response": response,
                "timestamp": timestamp
            })
        
        return history
    
    def get_stats(self) -> Dict:
        """Obtiene estadísticas"""
        cursor = self.db.cursor()
        cursor.execute("SELECT COUNT(*) FROM conversations")
        total_messages = cursor.fetchone()[0]
        
        return {
            **self.stats,
            "total_messages": total_messages,
            "avg_cost_per_request": self.stats["total_cost"] / self.stats["total_requests"] if self.stats["total_requests"] > 0 else 0,
            "success_rate": (self.stats["successful"] / self.stats["total_requests"] * 100) if self.stats["total_requests"] > 0 else 0
        }
    
    def close(self):
        """Cierra conexiones"""
        self.db.close()

# Ejemplo de uso
async def main():
    """Demo de ClawCore MVP"""
    print("🚀 ClawCore MVP - Demo")
    print("=" * 40)
    
    core = ClawCore()
    
    # Test 1: Respuesta simple
    print("\n🧪 Test 1: Respuesta simple")
    response = await core.get_response("user123", "Hola, ¿cómo estás?")
    print(f"Respuesta: {response[:100]}...")
    
    # Test 2: Historial
    print("\n📜 Test 2: Historial")
    history = core.get_conversation_history("user123")
    print(f"Mensajes en historial: {len(history)}")
    
    # Test 3: Stats
    print("\n📊 Test 3: Estadísticas")
    stats = core.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    core.close()
    print("\n✅ Demo completada")

if __name__ == "__main__":
    asyncio.run(main())