"""PageText: el texto extraído de una página de un PDF."""
from dataclasses import dataclass


@dataclass(frozen=True)
class PageText:
    document_id: str
    number: int          # página del PDF (1 = primera)
    text: str
