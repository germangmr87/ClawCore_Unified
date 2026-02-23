import os
import json
from pathlib import Path

class VerificadorVerdad:
    """
    Sistema Anti-Alucinación.
    Verifica que las rutas y archivos mencionados por ClawCore existan realmente en el disco.
    """
    def __init__(self, root_path):
        self.root = Path(root_path).resolve()

    def validar_perimetro(self, ruta_propuesta):
        """Asegura que ClawCore no trabaje fuera del directorio del proyecto"""
        try:
            ruta_abs = Path(ruta_propuesta).resolve()
            # El "Ancla de Verdad": Debe estar dentro del root
            es_seguro = str(ruta_abs).startswith(str(self.root))
            return {
                "valido": es_seguro,
                "ruta_real": str(ruta_abs) if es_seguro else "BLOQUEADO",
                "msj": "OK" if es_seguro else "ALUCINACIÓN_DETECTADA: Intento de salir del perímetro."
            }
        except:
            return {"valido": False, "msj": "Ruta inválida"}

    def verificar_existencia(self, archivo):
        """Confirma si un archivo existe antes de que la neurona alucine sobre su contenido"""
        path_file = Path(archivo)
        if not path_file.is_absolute():
            path_file = self.root / path_file

        existe = path_file.exists()
        return {
            "existe": existe,
            "tipo": "directorio" if path_file.is_dir() else "archivo" if existe else "fantasma",
            "msj": "Verificado" if existe else "ERROR: El archivo no existe. Detener alucinación."
        }

    def generar_mapa_contexto(self):
        """Crea un mapa ligero de la estructura actual para que el sistema tenga el contexto fresco"""
        mapa = []
        for root, dirs, files in os.walk(self.root):
            # No entrar en carpetas basura o pesadas para ahorrar tokens
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
            rel_path = os.path.relpath(root, self.root)
            if rel_path == ".": rel_path = ""
            for f in files[:10]: # Solo primeros 10 archivos por carpeta para no saturar tokens
                if not f.startswith('.'):
                    mapa.append(os.path.join(rel_path, f))
        
        return {
            "root": str(self.root),
            "estructura_ligera": mapa[:50] # Límite de 50 archivos clave para ahorro máximo de tokens
        }

if __name__ == "__main__":
    v = VerificadorVerdad("/Users/german/Documents/GitHub/ClawCore_Unified")
    print(json.dumps(v.generar_mapa_contexto(), indent=4))
