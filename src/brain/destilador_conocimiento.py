#!/usr/bin/env python3
"""
DESTILADOR DE CONOCIMIENTO - Auto-Axiomas
Convierte soluciones de nube en lógica local permanente
"""

import json
import re
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

class DestiladorConocimiento:
    """Sistema que destila conocimiento de interacciones en axiomas locales"""
    
    def __init__(self):
        self.axiomas_dir = Path("~/.clawcore/clawcore/axiomas").expanduser()
        self.axiomas_dir.mkdir(exist_ok=True)
        
        self.axiomas_file = self.axiomas_dir / "axiomas_locales.json"
        self.historial_file = self.axiomas_dir / "historial_destilacion.json"
        
        # Cargar axiomas existentes
        self.axiomas = self._cargar_axiomas()
        
        # Patrones para destilar conocimiento
        self.patrones_destilacion = {
            "codigo": r'(def|class|import|from|async|await|return|yield)',
            "configuracion": r'(config|settings|env|\.json|\.yaml|\.toml)',
            "comando": r'(sudo|apt|pip|npm|git|ssh|curl|wget)',
            "solucion": r'(solution|fix|workaround|resolved|solved)',
            "error": r'(error|exception|traceback|failed|crash)'
        }
    
    def _cargar_axiomas(self) -> Dict[str, Any]:
        """Cargar axiomas existentes"""
        if self.axiomas_file.exists():
            try:
                with open(self.axiomas_file, 'r') as f:
                    return json.load(f)
            except:
                return {"axiomas": [], "contador": 0, "ultima_actualizacion": None}
        return {"axiomas": [], "contador": 0, "ultima_actualizacion": None}
    
    def _guardar_axiomas(self):
        """Guardar axiomas actualizados"""
        self.axiomas["ultima_actualizacion"] = datetime.now().isoformat()
        with open(self.axiomas_file, 'w') as f:
            json.dump(self.axiomas, f, indent=2)
    
    def destilar_interaccion(self, pregunta: str, respuesta: str, metadata: Dict = None) -> Dict[str, Any]:
        """Destilar una interacción en axiomas locales"""
        print(f"🧠 Destilando conocimiento de interacción...")
        
        # Analizar contenido
        conocimiento = self._analizar_contenido(respuesta)
        
        # Extraer axiomas
        axiomas_extraidos = self._extraer_axiomas(pregunta, respuesta, conocimiento)
        
        # Guardar axiomas
        for axioma in axiomas_extraidos:
            self._agregar_axioma(axioma)
        
        # Registrar en historial
        self._registrar_destilacion(pregunta, axiomas_extraidos, metadata)
        
        return {
            "destilado": True,
            "axiomas_extraidos": len(axiomas_extraidos),
            "total_axiomas": self.axiomas["contador"],
            "timestamp": datetime.now().isoformat()
        }
    
    def _analizar_contenido(self, contenido: str) -> Dict[str, Any]:
        """Analizar contenido para extraer conocimiento"""
        conocimiento = {
            "tipo": "desconocido",
            "patrones": [],
            "complejidad": 0,
            "acciones": []
        }
        
        # Detectar tipo de contenido
        contenido_lower = contenido.lower()
        
        if any(palabra in contenido_lower for palabra in ["código", "programa", "script", "función"]):
            conocimiento["tipo"] = "codigo"
        elif any(palabra in contenido_lower for palabra in ["config", "settings", "ajuste", "parámetro"]):
            conocimiento["tipo"] = "configuracion"
        elif any(palabra in contenido_lower for palabra in ["comando", "terminal", "bash", "shell"]):
            conocimiento["tipo"] = "comando"
        elif any(palabra in contenido_lower for palabra in ["solución", "resolver", "arreglar", "corregir"]):
            conocimiento["tipo"] = "solucion"
        
        # Detectar patrones
        for patron_nombre, patron_regex in self.patrones_destilacion.items():
            if re.search(patron_regex, contenido, re.IGNORECASE):
                conocimiento["patrones"].append(patron_nombre)
        
        # Calcular complejidad (simple heurística)
        lineas = contenido.split('\n')
        conocimiento["complejidad"] = min(len(lineas) // 10, 10)  # 0-10
        
        # Extraer acciones (verbos)
        verbos = re.findall(r'\b([A-Z][a-z]+)\b', contenido[:500])
        conocimiento["acciones"] = list(set(verbos[:5]))
        
        return conocimiento
    
    def _extraer_axiomas(self, pregunta: str, respuesta: str, conocimiento: Dict) -> List[Dict[str, Any]]:
        """Extraer axiomas específicos del contenido"""
        axiomas = []
        
        # Axioma 1: Relación pregunta-respuesta
        axioma_base = {
            "id": hashlib.md5(f"{pregunta[:50]}".encode()).hexdigest()[:8],
            "pregunta": pregunta[:100] + "..." if len(pregunta) > 100 else pregunta,
            "respuesta": respuesta[:200] + "..." if len(respuesta) > 200 else respuesta,
            "tipo": conocimiento["tipo"],
            "patrones": conocimiento["patrones"],
            "complejidad": conocimiento["complejidad"],
            "timestamp": datetime.now().isoformat()
        }
        axiomas.append(axioma_base)
        
        # Extraer comandos específicos (código entre ```)
        codigo_bloques = re.findall(r'```(?:bash|sh)?\n([^`]+)```', respuesta, re.DOTALL)
        for i, codigo in enumerate(codigo_bloques[:3]):
            if "sudo" in codigo or "apt" in codigo or "pip" in codigo:
                axioma_comando = {
                    "id": f"cmd_{hashlib.md5(codigo.encode()).hexdigest()[:6]}",
                    "tipo": "comando",
                    "contenido": codigo.strip(),
                    "contexto": f"Extraído de respuesta a: {pregunta[:50]}...",
                    "timestamp": datetime.now().isoformat()
                }
                axiomas.append(axioma_comando)
        
        # Extraer configuraciones JSON/YAML
        json_bloques = re.findall(r'```(?:json|yaml)?\n([^`]+)```', respuesta, re.DOTALL)
        for i, config in enumerate(json_bloques[:2]):
            if "{" in config or ":" in config:
                axioma_config = {
                    "id": f"config_{hashlib.md5(config.encode()).hexdigest()[:6]}",
                    "tipo": "configuracion",
                    "contenido": config.strip(),
                    "timestamp": datetime.now().isoformat()
                }
                axiomas.append(axioma_config)
        
        return axiomas
    
    def _agregar_axioma(self, axioma: Dict[str, Any]):
        """Agregar axioma a la base de conocimiento"""
        # Verificar si ya existe (por id)
        axiomas_existentes = [a.get("id") for a in self.axiomas.get("axiomas", [])]
        
        if axioma["id"] not in axiomas_existentes:
            self.axiomas["axiomas"].append(axioma)
            self.axiomas["contador"] += 1
            print(f"  ✅ Axioma agregado: {axioma['id']} ({axioma['tipo']})")
    
    def _registrar_destilacion(self, pregunta: str, axiomas: List[Dict], metadata: Dict = None):
        """Registrar proceso de destilación en historial"""
        registro = {
            "pregunta": pregunta[:150],
            "axiomas_extraidos": len(axiomas),
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        historial = []
        if self.historial_file.exists():
            try:
                with open(self.historial_file, 'r') as f:
                    historial = json.load(f)
            except:
                historial = []
        
        historial.append(registro)
        
        # Mantener solo últimos 100 registros
        if len(historial) > 100:
            historial = historial[-100:]
        
        with open(self.historial_file, 'w') as f:
            json.dump(historial, f, indent=2)
    
    def consultar_axioma(self, consulta: str) -> List[Dict[str, Any]]:
        """Consultar axiomas relevantes para una consulta"""
        consulta_lower = consulta.lower()
        resultados = []
        
        for axioma in self.axiomas.get("axiomas", []):
            # Búsqueda simple por contenido
            contenido = f"{axioma.get('pregunta', '')} {axioma.get('respuesta', '')} {axioma.get('contenido', '')}".lower()
            
            if consulta_lower in contenido:
                resultados.append(axioma)
            elif any(palabra in contenido for palabra in consulta_lower.split()[:3]):
                resultados.append(axioma)
        
        return resultados[:5]  # Máximo 5 resultados
    
    def estadisticas(self) -> Dict[str, Any]:
        """Obtener estadísticas del destilador"""
        return {
            "total_axiomas": self.axiomas.get("contador", 0),
            "ultima_actualizacion": self.axiomas.get("ultima_actualizacion"),
            "tipos_distribucion": self._calcular_distribucion_tipos(),
            "estado": "operativo"
        }
    
    def _calcular_distribucion_tipos(self) -> Dict[str, int]:
        """Calcular distribución de tipos de axiomas"""
        distribucion = {}
        for axioma in self.axiomas.get("axiomas", []):
            tipo = axioma.get("tipo", "desconocido")
            distribucion[tipo] = distribucion.get(tipo, 0) + 1
        return distribucion

def main():
    """Prueba del destilador de conocimiento"""
    print("🧠 PRUEBA DESTILADOR DE CONOCIMIENTO - Auto-Axiomas")
    print("=" * 60)
    
    destilador = DestiladorConocimiento()
    
    # Ejemplo de interacción para destilar
    ejemplo_pregunta = "¿Cómo configurar ClawCore Gateway para acceso externo?"
    ejemplo_respuesta = """Para configurar ClawCore Gateway para acceso externo:

1. Editar el archivo de configuración:
```json
{
  "gateway": {
    "mode": "local",
    "port": 18789
  }
}
```

2. Reiniciar el servicio:
```bash
sudo systemctl restart clawcore-gateway
```

3. Verificar que está escuchando:
```bash
sudo ss -tlnp | grep :18789
```

Solución: Gateway configurado para acceso local."""
    
    # Destilar la interacción
    resultado = destilador.destilar_interaccion(
        ejemplo_pregunta, 
        ejemplo_respuesta,
        {"fuente": "ejemplo", "importancia": "alta"}
    )
    
    print(f"\n📊 Resultado destilación:")
    print(f"   • Axiomas extraídos: {resultado['axiomas_extraidos']}")
    print(f"   • Total axiomas: {resultado['total_axiomas']}")
    
    # Consultar axiomas relacionados
    print(f"\n🔍 Consultando axiomas para 'configurar gateway':")
    axiomas = destilador.consultar_axioma("configurar gateway")
    for i, axioma in enumerate(axiomas, 1):
        print(f"   {i}. [{axioma['tipo']}] {axioma.get('pregunta', axioma.get('contenido', ''))[:60]}...")
    
    # Estadísticas
    stats = destilador.estadisticas()
    print(f"\n📈 Estadísticas destilador:")
    print(f"   • Total axiomas: {stats['total_axiomas']}")
    print(f"   • Estado: {stats['estado']}")
    
    print("\n" + "=" * 60)
    print("✅ Destilador de conocimiento operativo")
    print("   Cada interacción ahora genera conocimiento local permanente")

if __name__ == "__main__":
    main()