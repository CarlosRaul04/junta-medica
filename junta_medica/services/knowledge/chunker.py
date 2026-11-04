"""
Chunker: parte el texto de una sección en fragmentos citables.

1. Divide en BLOQUES donde empieza cada pregunta clínica ("Pregunta 7. ..."): un bloque = una pregunta con sus recomendaciones.
2. Si un bloque es más largo que el máximo, lo subdivide por párrafos con solapamiento,
   y antepone el título de la pregunta a cada trozo para no perder el contexto.
3. Cada fragmento guarda las páginas del PDF de donde salió (para la cita).
"""
import re

from junta_medica.models.knowledge.chunk import Chunk
from junta_medica.models.knowledge.page_text import PageText


class Chunker:
    def __init__(self, block_start_pattern: str, max_size: int, overlap: int, min_size: int):
        self._pattern = re.compile(block_start_pattern, re.MULTILINE)
        self._max_size = max_size
        self._overlap = overlap
        self._min_size = min_size

    def chunk(self, pages: list[PageText], section_type: str) -> list[Chunk]:
        """Devuelve fragmentos sin id (chunk_id vacío): el indexador los numera."""
        if not pages:
            return []
        text, page_starts = self._join_pages(pages)
        chunks = []
        for start, end in self._block_bounds(text):
            raw_text = text[start:end]
            start += len(raw_text) - len(raw_text.lstrip())   # la posición real empieza en el primer carácter visible
            block = raw_text.strip()
            title = self._title(block)
            for piece_start, piece_end, piece in self._split_block(block, title):
                if len(piece) < self._min_size:
                    continue
                chunks.append(Chunk(
                    chunk_id="", document_id=pages[0].document_id, text=piece,
                    start_page=self._page_at(start + piece_start, page_starts, pages),
                    end_page=self._page_at(start + max(piece_start, piece_end - 1), page_starts, pages),
                    section_type=section_type, title=title,
                ))
        return chunks

    @staticmethod
    def _join_pages(pages: list[PageText]) -> tuple[str, list[int]]:
        parts, starts, position = [], [], 0
        for page in pages:
            starts.append(position)
            parts.append(page.text)
            position += len(page.text) + 2
        return "\n\n".join(parts), starts

    def _block_bounds(self, text: str) -> list[tuple[int, int]]:
        # m.start() puede caer en los saltos de línea previos (el patrón admite espacios iniciales):
        # se corre al primer carácter visible para no asignar la pregunta a la página anterior
        cuts = [m.start() + len(m.group()) - len(m.group().lstrip()) for m in self._pattern.finditer(text)]
        if not cuts or cuts[0] > 0:
            cuts.insert(0, 0)            # texto antes de la primera pregunta (o sección sin preguntas)
        cuts.append(len(text))
        return [(a, b) for a, b in zip(cuts, cuts[1:]) if b > a]

    def _title(self, block: str) -> str:
        first_line = block.splitlines()[0].strip() if block else ""
        return first_line[:200] if self._pattern.match(first_line) else ""

    def _split_block(self, block: str, title: str) -> list[tuple[int, int, str]]:
        """(posición inicial, posición final, texto) de cada trozo del bloque."""
        if len(block) <= self._max_size:
            return [(0, len(block), block)]
        paragraphs = [(m.start(), m.end()) for m in re.finditer(r"\S[\s\S]*?(?=\n\s*\n|\Z)", block)]
        pieces, current = [], []
        for paragraph in paragraphs:
            if current and paragraph[1] - current[0][0] > self._max_size:
                pieces.append(self._build_piece(block, current, title, is_first=not pieces))
                current = [p for p in current if current[-1][1] - p[0] <= self._overlap]  # solapamiento
            current.append(paragraph)
        if current:
            pieces.append(self._build_piece(block, current, title, is_first=not pieces))
        return pieces

    def _build_piece(self, block: str, paragraphs: list[tuple[int, int]], title: str, is_first: bool):
        piece_start, piece_end = paragraphs[0][0], paragraphs[-1][1]
        text = block[piece_start:piece_end].strip()[: self._max_size]
        if title and not is_first:
            text = f"{title} (continuación)\n{text}"
        return piece_start, piece_end, text

    @staticmethod
    def _page_at(position: int, starts: list[int], pages: list[PageText]) -> int:
        idx = 0
        for i, start in enumerate(starts):
            if start <= position:
                idx = i
        return pages[idx].number
