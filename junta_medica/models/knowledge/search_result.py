"""SearchResult: lo que devuelve el buscador para una consulta."""
from dataclasses import dataclass

from junta_medica.models.knowledge.retrieved_chunk import RetrievedChunk


@dataclass(frozen=True)
class SearchResult:
    query: str
    chunks: tuple[RetrievedChunk, ...]
    sufficient_evidence: bool   # False -> RF11: el sistema debe abstenerse / declarar evidencia insuficiente

    @property
    def citations(self) -> list[str]:
        return [f.chunk.citation for f in self.chunks]
