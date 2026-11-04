"""VectorStore: guarda fragmentos con sus vectores y busca los más parecidos (implementaciones: ChromaDB, memoria)."""
from abc import ABC, abstractmethod

from junta_medica.models.knowledge.chunk import Chunk
from junta_medica.models.knowledge.retrieved_chunk import RetrievedChunk


class VectorStore(ABC):
    @abstractmethod
    def clear(self) -> None:
        """Borra todo el contenido (antes de reindexar)."""

    @abstractmethod
    def add(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        ...

    @abstractmethod
    def search(self, vector: list[float], limit: int,
               document_ids: list[str] | None = None) -> list[RetrievedChunk]:
        """Los `cantidad` fragmentos más parecidos, opcionalmente solo de ciertos documentos."""

    @abstractmethod
    def count(self) -> int:
        ...
