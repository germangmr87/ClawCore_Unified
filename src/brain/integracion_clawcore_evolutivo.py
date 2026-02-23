#!/usr/bin/env python3
"""
INTEGRACIÓN CLAWCORE EVOLUTIVO - Versión segura
Conecta sistema neuronal + Ollama + ChromaDB sin riesgos
"""

import os
import sys
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClawCoreEvolutivo:
    """Integración segura de todos los componentes"""
    
    def __init__(self):
        self.base_dir = Path.home() / ".clawcore" / "clawcore"
        self.sistemas_dir = Path.home() / ".clawcore" / "workspace" / "systems"
        
        # Verificar que todo existe
        self._verificar_instalacion()
        
        # Componentes (se cargan solo si existen)
        self.neuronas = None
        self.chromadb = None
        self.ollama = None
        
    def _verificar_instalacion(self):
        """Verifica que todo esté instalado de forma segura"""
        logger.info("🔍 Verificando instalación...")
        
        # 1. Directorio ClawCore
        if not self.base_dir.exists():
            logger.error(f"❌ Directorio ClawCore no existe: {self.base_dir}")
            return False
        
        # 2. Sistema neuronal
        neurona_file = self.sistemas_dir / "neuronas_locales.py"
        if not neurona_file.exists():
            logger.error(f"❌ Sistema neuronal no encontrado: {neurona_file}")
            return False
        
        # 3. Ollama (verificar comando)
        ollama_check = os.system("which ollama > /dev/null 2>&1")
        if ollama_check != 0:
            logger.warning("⚠️  Ollama no instalado (instalar con: curl -fsSL https://ollama.com/install.sh | sh)")
        
        # 4. ChromaDB (verificar Python)
        try:
            import chromadb
            logger.info("✅ ChromaDB disponible")
        except ImportError:
            logger.warning("⚠️  ChromaDB no instalado (instalar con: pip install chromadb sentence-transformers)")
        
        logger.info("✅ Verificación completada")
        return True
    
    def cargar_sistema_neuronal(self):
        """Carga el sistema neuronal existente de forma segura"""
        try:
            # Agregar ruta al sistema
            sys.path.append(str(self.sistemas_dir))
            
            # Importar módulo
            from neuronas_locales import RedNeuronalAutonoma
            
            self.neuronas = RedNeuronalAutonoma()
            logger.info(f"✅ Sistema neuronal cargado: {self.neuronas.nivel_autonomia:.1%} autonomía")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cargando sistema neuronal: {e}")
            return False
    
    def probar_ollama(self):
        """Prueba Ollama de forma segura"""
        try:
            # Verificar si ollama está corriendo
            import subprocess
            
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logger.info("✅ Ollama funcionando")
                logger.info(f"📋 Modelos: {result.stdout.strip()}")
                return True
            else:
                logger.warning(f"⚠️  Ollama no responde: {result.stderr}")
                return False
                
        except FileNotFoundError:
            logger.warning("⚠️  Ollama no instalado")
            return False
        except Exception as e:
            logger.error(f"❌ Error probando Ollama: {e}")
            return False
    
    def probar_chromadb(self):
        """Prueba ChromaDB de forma segura"""
        try:
            import chromadb
            
            # Prueba básica
            client = chromadb.Client()
            test_collection = client.create_collection("test_clawcore")
            
            # Agregar documento de prueba
            test_collection.add(
                documents=["Este es un documento de prueba para ClawCore Evolutivo"],
                metadatas=[{"tipo": "prueba", "fecha": "2026-02-15"}],
                ids=["test_id_1"]
            )
            
            # Buscar
            results = test_collection.query(
                query_texts=["documento prueba"],
                n_results=1
            )
            
            logger.info("✅ ChromaDB funcionando correctamente")
            logger.info(f"📊 Prueba RAG: {len(results['documents'][0])} documento encontrado")
            
            # Limpiar
            client.delete_collection("test_clawcore")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error probando ChromaDB: {e}")
            return False
    
    def crear_integracion_basica(self):
        """Crea integración básica entre componentes"""
        logger.info("🔗 Creando integración básica...")
        
        integracion = {
            "estado": "inicializado",
            "componentes": {
                "neuronas": self.neuronas is not None,
                "ollama": False,  # Se verifica después
                "chromadb": False  # Se verifica después
            },
            "autonomia_inicial": 0.10,
            "configuracion": {
                "modelo_primario": "ollama/llama3.2:3b",
                "modelo_respaldo": "google/gemini-2.5-flash",
                "rag_habilitado": True,
                "aprendizaje_automatico": True
            }
        }
        
        # Verificar Ollama
        integracion["componentes"]["ollama"] = self.probar_ollama()
        
        # Verificar ChromaDB
        integracion["componentes"]["chromadb"] = self.probar_chromadb()
        
        # Guardar configuración
        config_file = self.base_dir / "integracion_config.json"
        with open(config_file, 'w') as f:
            json.dump(integracion, f, indent=2)
        
        logger.info(f"✅ Integración guardada: {config_file}")
        return integracion
    
    def generar_reporte(self):
        """Genera reporte del estado actual"""
        logger.info("📊 Generando reporte del sistema...")
        
        reporte = {
            "timestamp": "2026-02-15T20:05:00Z",
            "sistema": "ClawCore Evolutivo",
            "vps": "127.0.0.1",
            "estado": "instalacion_en_progreso",
            "componentes": {},
            "recomendaciones": []
        }
        
        # Verificar cada componente
        componentes = [
            ("ClawCore", self._verificar_clawcore),
            ("Sistema Neuronal", self.cargar_sistema_neuronal),
            ("Ollama", self.probar_ollama),
            ("ChromaDB", self.probar_chromadb),
            ("Python", self._verificar_python)
        ]
        
        for nombre, funcion in componentes:
            try:
                resultado = funcion() if callable(funcion) else funcion
                reporte["componentes"][nombre] = {
                    "estado": "✅" if resultado else "❌",
                    "detalles": str(resultado) if not isinstance(resultado, bool) else ""
                }
            except Exception as e:
                reporte["componentes"][nombre] = {
                    "estado": "❌",
                    "detalles": f"Error: {str(e)}"
                }
        
        # Generar recomendaciones
        if not reporte["componentes"].get("Ollama", {}).get("estado") == "✅":
            reporte["recomendaciones"].append("Instalar Ollama: curl -fsSL https://ollama.com/install.sh | sh")
        
        if not reporte["componentes"].get("ChromaDB", {}).get("estado") == "✅":
            reporte["recomendaciones"].append("Instalar ChromaDB: pip install chromadb sentence-transformers")
        
        # Guardar reporte
        reporte_file = self.base_dir / "reporte_instalacion.json"
        with open(reporte_file, 'w') as f:
            json.dump(reporte, f, indent=2)
        
        logger.info(f"✅ Reporte guardado: {reporte_file}")
        return reporte
    
    def _verificar_clawcore(self):
        """Verifica ClawCore"""
        try:
            import subprocess
            result = subprocess.run(
                ["clawcore", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return f"Versión: {result.stdout.strip()}" if result.returncode == 0 else "No encontrado"
        except:
            return "No encontrado"
    
    def _verificar_python(self):
        """Verifica Python y dependencias"""
        try:
            import sys
            return f"Python {sys.version}"
        except:
            return "Error"

def main():
    """Función principal - Ejecución segura"""
    print("=" * 60)
    print("🚀 CLAWCORE EVOLUTIVO - INSTALACIÓN SEGURA")
    print("=" * 60)
    
    try:
        # Inicializar
        clawcore = ClawCoreEvolutivo()
        
        # Cargar sistema neuronal (si existe)
        if clawcore.cargar_sistema_neuronal():
            print("🧠 Sistema neuronal: ✅ CARGADO")
        else:
            print("🧠 Sistema neuronal: ⚠️  NO CARGADO (verificar archivo)")
        
        # Probar componentes
        print("\n🔍 Probando componentes...")
        
        ollama_ok = clawcore.probar_ollama()
        print(f"🤖 Ollama: {'✅ FUNCIONANDO' if ollama_ok else '⚠️  NO INSTALADO'}")
        
        chromadb_ok = clawcore.probar_chromadb()
        print(f"📚 ChromaDB: {'✅ FUNCIONANDO' if chromadb_ok else '⚠️  NO INSTALADO'}")
        
        # Crear integración básica
        print("\n🔗 Creando integración...")
        integracion = clawcore.crear_integracion_basica()
        
        # Generar reporte
        print("\n📊 Generando reporte...")
        reporte = clawcore.generar_reporte()
        
        print("\n" + "=" * 60)
        print("🎯 INSTALACIÓN COMPLETADA (FASE SEGURA)")
        print("=" * 60)
        
        # Resumen
        print(f"\n📍 VPS: 127.0.0.1")
        print(f"📁 Directorio: ~/.clawcore/clawcore/")
        
        componentes_ok = sum(1 for c in integracion["componentes"].values() if c)
        print(f"🔧 Componentes listos: {componentes_ok}/{len(integracion['componentes'])}")
        
        if reporte["recomendaciones"]:
            print(f"\n⚠️  RECOMENDACIONES:")
            for rec in reporte["recomendaciones"]:
                print(f"   • {rec}")
        
        print(f"\n🚀 Próximo paso: Ejecutar pruebas completas")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        print("⚠️  La instalación encontró un problema.")
        print("💡 Solución: Verificar logs y corregir manualmente")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())