"""LocalFileStorage: guarda archivos en una carpeta del disco (output/). En la nube se reemplaza por S3."""
from pathlib import Path

from junta_medica.interfaces.file_storage import FileStorage


class LocalFileStorage(FileStorage):
    def __init__(self, root: Path):
        self._root = root.resolve()

    def save(self, key: str, content: bytes, content_type: str) -> str:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return key

    def load(self, key: str) -> bytes | None:
        path = self._path(key)
        return path.read_bytes() if path.is_file() else None

    def _path(self, key: str) -> Path:
        path = (self._root / key).resolve()
        if self._root not in path.parents:
            raise ValueError(f"Clave de archivo no permitida: {key}")
        return path
