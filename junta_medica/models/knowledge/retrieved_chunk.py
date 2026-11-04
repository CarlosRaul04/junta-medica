"""RetrievedChunk: un fragmento encontrado en una búsqueda, con su similitud con la consulta."""
from dataclasses import dataclass

from junta_medica.models.knowledge.chunk import Chunk


@dataclass(frozen=True)
class RetrievedChunk:
    chunk: Chunk
    similarity: float     # 0 a 1 (1 = idéntico)
