"""DocumentSection: un rango de páginas de un documento que sí se indexa (ej. lista de recomendaciones)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentSection:
    document_id: str
    kind: str            # recomendaciones | flujogramas
    start_page: int   # página del PDF (1 = primera)
    end_page: int      # inclusive
