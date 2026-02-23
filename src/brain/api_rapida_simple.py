#!/usr/bin/env python3
"""
API RÁPIDA SIMPLE - CLAWCORE
"""

import json
import time
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler

class Cache:
    def __init__(self):
        self.cache = {}
    
    def get(self, key):
        return self.cache.get(key)
    
    def set(self, key, value):
        if len(self.cache) > 1000:
            self.cache.clear()
        self.cache[key] = value

cache = Cache()

def query_ollama(prompt, model="qwen2.5:0.5b"):
    """Consulta Ollama rápido"""
    try:
        start = time.time()
        
        cmd = ["ollama", "run", model, prompt[:150]]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
        
        elapsed = time.time() - start
        
        if result.returncode == 0:
            return {
                "success": True,
                "response": result.stdout.strip(),
                "time_ms": int(elapsed * 1000),
                "model": model
            }
        else:
            return {
                "success": False,
                "error": result.stderr[:100],
                "time_ms": int(elapsed * 1000)
            }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timeout 2s", "time_ms": 2000}
    except Exception as e:
        return {"success": False, "error": str(e), "time_ms": 0}

class APIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {
                "status": "ok",
                "service": "ClawCore Fast API",
                "version": "0.1.0",
                "model": "qwen2.5:0.5b"
            }
            self.wfile.write(json.dumps(response).encode())
        
        elif self.path == '/benchmark':
            # Benchmark simple
            prompts = ["Hola", "¿Cómo estás?", "2+2"]
            results = []
            
            for prompt in prompts:
                result = query_ollama(prompt)
                results.append({
                    "prompt": prompt,
                    "time_ms": result["time_ms"],
                    "success": result["success"]
                })
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"benchmark": results}).encode())
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/chat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            
            prompt = data.get('prompt', '')
            
            # Verificar cache
            cached = cache.get(prompt)
            if cached:
                response = {
                    "success": True,
                    "response": cached,
                    "cached": True,
                    "time_ms": 1
                }
            else:
                # Consultar modelo
                result = query_ollama(prompt)
                if result["success"]:
                    cache.set(prompt, result["response"])
                response = result
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        
        else:
            self.send_response(404)
            self.end_headers()

def main():
    print("🚀 ClawCore Fast API iniciando...")
    print("📡 Puerto: 8080")
    print("🤖 Modelo: qwen2.5:0.5b (300MB)")
    print("🎯 Objetivo: <500ms respuestas")
    print("")
    print("Endpoints:")
    print("  GET  /health     - Estado")
    print("  GET  /benchmark  - Prueba velocidad")
    print("  POST /api/chat   - Chat rápido")
    
    server = HTTPServer(('0.0.0.0', 8080), APIHandler)
    server.serve_forever()

if __name__ == '__main__':
    main()