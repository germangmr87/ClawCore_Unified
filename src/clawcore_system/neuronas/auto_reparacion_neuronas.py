#!/usr/bin/env python3
"""
🧠 SISTEMA DE AUTO-REPARACIÓN NEURONAL V2 (AST-BASED)
Analiza y repara neuronas usando Árboles de Sintaxis Abstracta
"""

import os
import ast
import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("ClawDoctor")

class AnalizadorAST(ast.NodeVisitor):
    """Analizador sofisticado de vulnerabilidades en Python"""
    def __init__(self, contenido):
        self.vulnerabilidades = []
        self.contenido_lineas = contenido.splitlines()

    def visit_FunctionDef(self, node):
        """Analiza definiciones de funciones"""
        # Verificar si ya tiene un bloque try-except
        tiene_error_handling = any(isinstance(n, ast.Try) for n in node.body)
        
        if not tiene_error_handling and node.name != "__init__":
            self.vulnerabilidades.append({
                "linea": node.lineno,
                "tipo": "sin_manejo_errores_ast",
                "descripcion": f"Función '{node.name}' no tiene bloque try-except.",
                "gravedad": "media"
            })
            
        self.generic_visit(node)

    def visit_Call(self, node):
        """Analiza llamadas a funciones (ej: requests)"""
        # Detectar requests.get o similar
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == 'get' and (
                (isinstance(node.func.value, ast.Name) and node.func.value.id == 'requests')
            ):
                tiene_timeout = any(kw.arg == 'timeout' for kw in node.keywords)
                if not tiene_timeout:
                    self.vulnerabilidades.append({
                        "linea": node.lineno,
                        "tipo": "conexion_sin_timeout",
                        "descripcion": "Llamada a requests.get sin parámetro timeout.",
                        "gravedad": "alta"
                    })
        self.generic_visit(node)

class AutoReparacionNeuronas:
    def __init__(self, directorio_base=None):
        if directorio_base is None:
            self.directorio_base = Path(__file__).parent
        else:
            self.directorio_base = Path(directorio_base)
            
        self.vulnerabilidades_totales = []
        self.reporte_final = {
            "timestamp": datetime.now().isoformat(),
            "archivos_procesados": 0,
            "vulnerabilidades_detectadas": 0,
            "reparaciones_realizadas": 0,
            "estado": "inicializado"
        }

    def escanear_neuronas(self):
        """Escaneo profundo usando AST"""
        logger.info(f"🔍 Iniciando escaneo AST en: {self.directorio_base}")
        self.vulnerabilidades_totales = []
        archivos = list(self.directorio_base.glob("*.py"))
        
        for archivo in archivos:
            if archivo.name == "auto_reparacion_neuronas.py":
                continue
                
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                
                tree = ast.parse(contenido)
                analizador = AnalizadorAST(contenido)
                analizador.visit(tree)
                
                if analizador.vulnerabilidades:
                    self.vulnerabilidades_totales.append({
                        "archivo": str(archivo),
                        "vulnerabilidades": analizador.vulnerabilidades,
                        "gravedad": "alta" if any(v["gravedad"] == "alta" for v in analizador.vulnerabilidades) else "media"
                    })
                    
            except Exception as e:
                logger.error(f"❌ Error analizando {archivo.name}: {e}")
                
        self.reporte_final["archivos_procesados"] = len(archivos)
        self.reporte_final["vulnerabilidades_detectadas"] = sum(len(f["vulnerabilidades"]) for f in self.vulnerabilidades_totales)
        return self.vulnerabilidades_totales

    def reparar_neuronas(self):
        """Aplica reparaciones seguras basadas en los hallazgos"""
        if not self.vulnerabilidades_totales:
            return 0
            
        cambios_realizados = 0
        for item in self.vulnerabilidades_totales:
            archivo_path = Path(item["archivo"])
            vulnerabilidades = item["vulnerabilidades"]
            
            with open(archivo_path, 'r', encoding='utf-8') as f:
                lineas = f.readlines()
                
            # Aplicar de abajo hacia arriba para no alterar los números de línea
            vulnerabilidades.sort(key=lambda x: x["linea"], reverse=True)
            
            pudimos_reparar = False
            for vuln in vulnerabilidades:
                idx = vuln["linea"] - 1
                
                # Reparar timeouts (Simple y seguro)
                if vuln["tipo"] == "conexion_sin_timeout":
                    linea = lineas[idx]
                    if 'requests.get(' in linea and 'timeout=' not in linea:
                        lineas[idx] = linea.replace('requests.get(', 'requests.get(', 1).replace(')', ', timeout=10)')
                        cambios_realizados += 1
                        pudimos_reparar = True
                
                elif vuln["tipo"] == "sin_manejo_errores_ast":
                    logger.warning(f"⚠️  Sugerencia en {archivo_path.name}:{vuln['linea']}: La función requiere try-except estructural.")

            if pudimos_reparar:
                with open(archivo_path, 'w', encoding='utf-8') as f:
                    f.writelines(lineas)
                    
        self.reporte_final["reparaciones_realizadas"] = cambios_realizados
        return cambios_realizados

    def generar_reporte(self):
        """Genera metadata para el feedback loop con el sistema TS"""
        reporte_path = self.directorio_base / "salud_neuronal.json"
        with open(reporte_path, 'w') as f:
            json.dump(self.reporte_final, f, indent=4)
        return self.reporte_final

def main():
    print("🧠 CLAWCORE DOCTOR: Módulo de Auto-Reparación AST")
    print("=" * 60)
    
    # Asegurar que el directorio sea el correcto si no se encuentran archivos
    directorio_neuronas = Path(__file__).parent
    reparador = AutoReparacionNeuronas(directorio_neuronas)
    
    # 1. Escaneo
    hallazgos = reparador.escanear_neuronas()
    if not hallazgos:
        print("✅ No se detectaron vulnerabilidades estructurales en las neuronas.")
    else:
        print(f"📊 Se detectaron {reparador.reporte_final['vulnerabilidades_detectadas']} puntos de mejora.")
    
    # 2. Reparación
    reparados = reparador.reparar_neuronas()
    if reparados > 0:
        print(f"🔧 Se aplicaron {reparados} reparaciones automáticas con éxito.")
    
    # 3. Reporte de Salud (Feedback Loop)
    reporte = reparador.generar_reporte()
    print(f"💾 Reporte de salud actualizado: salud_neuronal.json")
    print("=" * 60)

if __name__ == "__main__":
    main()
