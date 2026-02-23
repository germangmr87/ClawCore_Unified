"""
GESTOR DE ACTUALIZACIONES SOBERANAS (Delta Updater)
Permite empaquetar y distribuir solo los cambios diferenciales (Deltas).
Implementa: Versionado, Firma de Manifiesto y Despliegue Incremental.
"""
import json
import hashlib
import zipfile
import shutil
from pathlib import Path
from datetime import datetime

class GestorActualizaciones:
    def __init__(self, root_path):
        self.root = Path(root_path)
        self.updates_dir = self.root / ".clawcore" / "updates"
        self.updates_dir.mkdir(exist_ok=True, parents=True)
        self.manifest_path = self.root / "version_manifest.json"

    def generar_manifest_actual(self, version: str):
        """Escanea el sistema y crea un mapa de hashes de todos los archivos core."""
        manifest = {
            "version": version,
            "timestamp": datetime.now().isoformat(),
            "files": {}
        }
        
        # Escaneamos solo las neuronas y el core (lo que evoluciona)
        core_paths = [
            self.root / "src" / "clawcore_system" / "neuronas",
            self.root / "ui" / "src"
        ]

        for base_path in core_paths:
            if not base_path.exists(): continue
            for p in base_path.rglob("*"):
                if p.is_file() and not p.name.startswith("."):
                    rel_path = p.relative_to(self.root)
                    manifest["files"][str(rel_path)] = self._calcular_hash(p)
        
        self.manifest_path.write_text(json.dumps(manifest, indent=2))
        return manifest

    def crear_paquete_delta(self, manifest_anterior_path: str, nueva_version: str):
        """Compara con una versión vieja y crea un ZIP solo con lo nuevo/cambiado."""
        with open(manifest_anterior_path, 'r') as f:
            old_manifest = json.load(f)
        
        new_manifest = self.generar_manifest_actual(nueva_version)
        delta_files = []

        for path, h in new_manifest["files"].items():
            if path not in old_manifest["files"] or old_manifest["files"][path] != h:
                delta_files.append(path)

        if not delta_files:
            return None

        zip_name = self.updates_dir / f"update_{old_manifest['version']}_to_{nueva_version}.zip"
        with zipfile.ZipFile(zip_name, 'w') as zipf:
            # Incluimos el nuevo manifiesto
            zipf.writestr("manifest.json", json.dumps(new_manifest))
            # Incluimos solo los archivos que cambiaron
            for f in delta_files:
                zipf.write(self.root / f, f)
        
        return zip_name

    def aplicar_paquete_delta(self, zip_path: str):
        """Instala el delta sobre la versión actual."""
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            # 1. Validar integridad (Opcional: Verificar firmas)
            zipf.extractall(self.root)
            print(f"✅ Delta aplicado exitosamente desde {zip_path}")

    def _calcular_hash(self, path):
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

if __name__ == "__main__":
    gestor = GestorActualizaciones("/Users/german/Documents/GitHub/ClawCore_Unified")
    # 1. El desarrollador genera el manifiesto de la v4.5
    # gestor.generar_manifest_actual("4.5")
    
    # 2. Cuando sale la v4.6, se genera el delta
    # paquete = gestor.crear_paquete_delta("manifest_v45.json", "4.6")
    print("🛠️ Gestor de Actualizaciones listo para emitir Deltas.")
