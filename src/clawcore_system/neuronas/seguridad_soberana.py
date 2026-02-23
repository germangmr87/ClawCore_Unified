import subprocess
import os
import logging
import base64
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SeguridadSoberana")

class SeguridadSoberana:
    """
    PUNTO 9: SEGURIDAD DE COMUNICACIONES SOBERANA
    Gestiona el cifrado de capa de transporte (TLS) y de payload (AES-256-GCM).
    """
    def __init__(self):
        self.cert_dir = Path.home() / ".clawcore" / "seguridad"
        self.cert_dir.mkdir(exist_ok=True, parents=True)
        self.key_path = self.cert_dir / "sovereign.key"
        self.cert_path = self.cert_dir / "sovereign.crt"
        self.secret_path = self.cert_dir / "payload.secret"
        self._inicializar_llave_maestra()

    def _inicializar_llave_maestra(self):
        """Genera una llave de cifrado de payload si no existe."""
        if not self.secret_path.exists():
            key = AESGCM.generate_key(bit_length=256)
            self.secret_path.write_bytes(key)
            logger.info("🔑 Llave maestra de payload generada.")
        self.payload_key = self.secret_path.read_bytes()

    def garantizar_cifrado_local(self):
        """Genera certificados auto-firmados para HTTPS/WSS."""
        if not self.key_path.exists() or not self.cert_path.exists():
            logger.info("🔐 Generando Identidad de Seguridad SSL Soberana...")
            try:
                cmd = [
                    "openssl", "req", "-x509", "-newkey", "rsa:4096",
                    "-keyout", str(self.key_path),
                    "-out", str(self.cert_path),
                    "-days", "365", "-nodes",
                    "-subj", "/C=CL/ST=Sovereign/L=Local/O=ClawCore/CN=ClawCoreSovereign"
                ]
                subprocess.run(cmd, check=True, capture_output=True)
                logger.info(f"✅ Certificados SSL generados.")
                return True
            except Exception as e:
                logger.error(f"❌ Error en openssl: {e}")
                return False
        return True

    def encriptar_payload(self, data: str) -> str:
        """Cifra un mensaje usando AES-256-GCM (Autenticado)."""
        aesgcm = AESGCM(self.payload_key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, data.encode(), None)
        # Combinamos nonce + ciphertext y codificamos en base64
        return base64.b64encode(nonce + ciphertext).decode('utf-8')

    def desencriptar_payload(self, encrypted_data: str) -> str:
        """Descifra un mensaje cifrado con AES-256-GCM."""
        try:
            raw_data = base64.b64decode(encrypted_data)
            nonce = raw_data[:12]
            ciphertext = raw_data[12:]
            aesgcm = AESGCM(self.payload_key)
            return aesgcm.decrypt(nonce, ciphertext, None).decode('utf-8')
        except Exception as e:
            logger.error(f"❌ Fallo al desencriptar: {e}")
            return "[ERROR_CIFRADO]"

    def rotar_llave_maestra(self):
        """Genera una nueva llave de payload y sobrescribe la anterior."""
        new_key = AESGCM.generate_key(bit_length=256)
        self.secret_path.write_bytes(new_key)
        self.payload_key = new_key
        logger.warning("🔄 SEGURIDAD: Llave maestra rotada. Las comunicaciones anteriores requieren la llave antigua.")
        return True

# Singleton
seguridad = SeguridadSoberana()

if __name__ == "__main__":
    msg = "Directiva de Seguridad: Priorizar Soberanía sobre Todo."
    cifrado = seguridad.encriptar_payload(msg)
    descifrado = seguridad.desencriptar_payload(cifrado)
    print(f"Original: {msg}")
    print(f"Cifrado: {cifrado}")
    print(f"Descifrado Correcto: {msg == descifrado}")
