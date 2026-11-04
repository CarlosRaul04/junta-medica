"""DocumentRepository: los documentos registrados en data/documents/catalog.csv."""
import csv
from pathlib import Path

from junta_medica.models.knowledge.source_document import SourceDocument


class DocumentRepository:
    def __init__(self, catalog_path: Path):
        with open(catalog_path, encoding="utf-8", newline="") as file:
            self._documents = [
                SourceDocument(
                    id=f["id"].strip(), file=f["file"].strip(), condition=f["condition"].strip(),
                    title=f["title"].strip(), institution=f["institution"].strip(), year=f["year"].strip(),
                    source_url=f["source_url"].strip(), status=f["status"].strip(),
                )
                for f in csv.DictReader(file)
            ]

    def all(self) -> list[SourceDocument]:
        return list(self._documents)

    def indexable(self) -> list[SourceDocument]:
        return [d for d in self._documents if d.is_indexable]

    def find(self, document_id: str) -> SourceDocument | None:
        return next((d for d in self._documents if d.id == document_id), None)
