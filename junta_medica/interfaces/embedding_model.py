"""EmbeddingModel: convierte textos en vectores para la búsqueda semántica (implementaciones: e5 local, falso de pruebas)."""
from abc import ABC, abstractmethod


class EmbeddingModel(ABC):
    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Vectores de los fragmentos que se guardan en la base."""

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        """Vector de una pregunta/búsqueda."""
