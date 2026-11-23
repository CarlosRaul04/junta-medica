"""FileStorage: guarda archivos (resultados JSON, informes PDF) (implementaciones: disco local; luego AWS S3)."""
from abc import ABC, abstractmethod


class FileStorage(ABC):
    @abstractmethod
    def save(self, key: str, content: bytes, content_type: str) -> str:
        """Guarda el archivo con esa clave (ej. "debates/CASO-008_20261123-180000.json") y devuelve la clave."""

    @abstractmethod
    def load(self, key: str) -> bytes | None:
        """None si no existe."""
