"""SourceDocument: una guía (u otro documento) registrada en data/documents/catalog.csv."""
from dataclasses import dataclass

INDEXABLE_STATUS = "downloaded"


@dataclass(frozen=True)
class SourceDocument:
    id: str             # se usa en las citas (ej. "gpc_ic")
    file: str        # ruta relativa dentro de data/documents/
    condition: str
    title: str
    institution: str
    year: str
    source_url: str
    status: str         # pendiente | descargado | alternativa

    @property
    def is_indexable(self) -> bool:
        return self.status == INDEXABLE_STATUS
