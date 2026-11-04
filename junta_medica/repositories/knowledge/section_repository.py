"""SectionRepository: qué páginas de cada documento se indexan (data/documents/sections.csv)."""
import csv
from pathlib import Path

from junta_medica.models.knowledge.document_section import DocumentSection


class SectionRepository:
    def __init__(self, path: Path):
        with open(path, encoding="utf-8", newline="") as file:
            self._sections = [
                DocumentSection(f["document_id"].strip(), f["type"].strip(), int(f["start_page"]), int(f["end_page"]))
                for f in csv.DictReader(file)
            ]

    def all(self) -> list[DocumentSection]:
        return list(self._sections)

    def for_document(self, document_id: str) -> list[DocumentSection]:
        return [s for s in self._sections if s.document_id == document_id]
