"""TextCleaner: deja solo el contenido útil de las páginas extraídas del PDF."""
import re
from collections import Counter

from junta_medica.models.knowledge.page_text import PageText


class TextCleaner:
    def __init__(self, line_patterns_to_remove: list[str], header_ratio: float, edge_lines: int):
        self._patterns = [re.compile(p) for p in line_patterns_to_remove]
        self._ratio = header_ratio
        self._edge_lines = edge_lines

    def clean(self, pages: list[PageText]) -> list[PageText]:
        repeated = self._repeated_lines(pages)
        return [PageText(p.document_id, p.number, self._clean_text(p.text, repeated)) for p in pages]

    def _repeated_lines(self, pages: list[PageText]) -> set[str]:
        """Encabezados y pies de página: líneas del BORDE de la página (primeras/últimas) que se repiten en la mayoría.

        Solo se miran los bordes para no borrar contenido que se repite dentro del texto
        (ej. "Fuerza de la recomendación: Fuerte").
        """
        if len(pages) < 3:
            return set()
        counts = Counter()
        for page in pages:
            lines = [_normalize(l) for l in page.text.splitlines() if _normalize(l)]
            counts.update(set(lines[: self._edge_lines] + lines[-self._edge_lines:]))
        min_size = self._ratio * len(pages)
        return {line for line, occurrences in counts.items() if occurrences >= min_size and len(line) < 200}

    def _clean_text(self, text: str, repeated: set[str]) -> str:
        lines = []
        for line in text.splitlines():
            if _normalize(line) in repeated or any(p.search(line) for p in self._patterns):
                continue  # (una línea repetida se borra en toda la página, pero solo se detecta en los bordes)
            lines.append(line.rstrip())
        cleaned_text = "\n".join(lines)
        cleaned_text = re.sub(r"(\w)-\n(\w)", r"\1\2", cleaned_text)       # palabras cortadas con guion al final de línea
        cleaned_text = re.sub(r"[ \t]+", " ", cleaned_text)
        cleaned_text = re.sub(r"\n\s*\n\s*\n+", "\n\n", cleaned_text)       # máximo una línea en blanco seguida
        return cleaned_text.strip()


def _normalize(line: str) -> str:
    return re.sub(r"\s+", " ", line).strip()
