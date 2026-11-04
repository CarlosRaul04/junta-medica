"""Chunk: un trozo de una guía que se guarda en la base vectorial y se puede citar."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    chunk_id: str    # ej. "gpc_ic-007"
    document_id: str    # ej. "gpc_ic"
    text: str
    start_page: int
    end_page: int
    section_type: str    # recomendaciones | flujogramas
    title: str = ""     # ej. "Pregunta 7. En adultos con ICC ..."

    @property
    def citation(self) -> str:
        """Ej. "gpc_ic:p23" o "gpc_ic:p23-24"."""
        pages = str(self.start_page) if self.start_page == self.end_page else f"{self.start_page}-{self.end_page}"
        return f"{self.document_id}:p{pages}"
