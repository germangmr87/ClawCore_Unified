import zlib
import base64
import json

class CompresorTokens:
    """
    Sistema de compresión y codificación simbólica para ahorro de tokens.
    Reduce el tamaño de los payloads mediante mapeo de keywords y compresión LZW/Zlib.
    """
    def __init__(self):
        # Mapeo de términos frecuentes a símbolos de 1-2 caracteres
        self.diccionario_mapeo = {
            "neurona": "n",
            "autonomia": "au",
            "seguridad": "s",
            "conocimiento": "k",
            "experiencia": "ex",
            "vulnerabilidad": "v",
            "continuidad": "ct",
            "proceder": "p",
            "bloquear": "b",
            "diagnostico": "dg",
            "arquitectura": "ar",
            "malla": "m",
            "hibrida": "h",
            " ClawCore": "cc"
        }
        # Invertir para descompresión
        self.diccionario_inv = {v: k for k, v in self.diccionario_mapeo.items()}

    def comprimir_texto(self, texto: str) -> str:
        """Sustituye palabras clave por símbolos cortos"""
        palabras = texto.split()
        resultado = []
        for p in palabras:
            p_limpia = p.lower().strip(",.()\"")
            found = False
            for k, v in self.diccionario_mapeo.items():
                if k in p_limpia:
                    resultado.append(v)
                    found = True
                    break
            if not found:
                resultado.append(p)
        return " ".join(resultado)

    def empaquetar(self, data: dict) -> str:
        """Comprime un JSON y lo codifica en Base85 (Nivel 6 para balance CPU/Ratio)."""
        json_str = json.dumps(data)
        comprimido = zlib.compress(json_str.encode('utf-8'), level=6)
        return base64.b85encode(comprimido).decode('utf-8')

    def desempaquetar(self, b85_str: str) -> dict:
        """Revierte el empaquetado (Audit: Reparación de b85decode)."""
        try:
            binario = base64.b85decode(b85_str.encode('utf-8'))
            descomprimido = zlib.decompress(binario)
            return json.loads(descomprimido.decode('utf-8'))
        except Exception as e:
            return {"error": f"Fallo en descompresión: {str(e)}"}


if __name__ == "__main__":
    comp = CompresorTokens()
    test_data = {
        "accion": "proceder con la neurona de seguridad y la arquitectura de malla hibrida",
        "autonomia_actual": 0.35,
        "diagnostico": "sistema estable sin vulnerabilidades detectadas"
    }
    
    # 1. Compresión de texto simple
    txt_comp = comp.comprimir_texto(test_data["accion"])
    print(f"Original: {len(test_data['accion'])} chars")
    print(f"Simbólico: {len(txt_comp)} chars -> {txt_comp}")
    
    # 2. Empaquetado Binario (Para transporte)
    pack = comp.empaquetar(test_data)
    print(f"\nPayload empaquetado (b85): {len(pack)} bytes")
    print(f"Data: {pack}")
