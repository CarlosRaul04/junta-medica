"""PDFReader: extrae el texto de un rango de páginas de un PDF (con PyMuPDF)."""
from pathlib import Path

from junta_medica.models.knowledge.page_text import PageText


class PDFReader:
    def count_pages(self, path: Path) -> int:
        import pymupdf
        with pymupdf.open(path) as document:
            return document.page_count

    def read_pages(self, path: Path, document_id: str, start: int, end: int) -> list[PageText]:
        """inicio y fin son páginas del PDF contando desde 1, inclusive."""
        import pymupdf  # se importa aquí para no exigir la librería a quien no lee PDFs
        with pymupdf.open(path) as document:
            return [
                PageText(document_id, number, document[number - 1].get_text("text"))
                for number in range(start, min(end, document.page_count) + 1)
            ]
