"""
CitationFormatter: convierte una cita técnica en un texto que entiende el médico.

    "gpc_ic:p22-23"              -> "GPC Insuficiencia cardiaca (EsSalud-IETSI 2024), pág. 22-23"
    "ft_dabigatran:p84"          -> "Ficha técnica: dabigatrán, pág. 84"
    "ddinter:DDInter48-DDInter76" -> "DDInter (base de interacciones)"
"""
import re

from junta_medica.models.knowledge.source_document import SourceDocument

_PAGE = re.compile(r"^p(\d+(?:-\d+)?)$")


class CitationFormatter:
    def __init__(self, documents: list[SourceDocument], external_sources: dict[str, str]):
        self._documents = {d.id: d for d in documents}
        self._external = external_sources     # ej. {"ddinter": "DDInter (base de interacciones)"}

    def document_label(self, document_id: str) -> str:
        document = self._documents.get(document_id)
        if not document:
            return self._external.get(document_id.lower(), document_id)
        if document_id.startswith("gpc_"):
            return f"GPC {document.condition} ({document.institution} {document.year})".replace(" )", ")")
        return document.condition

    def format(self, citation: str) -> str:
        source, _, locator = citation.partition(":")
        label = self.document_label(source)
        page = _PAGE.match(locator)
        return f"{label}, pág. {page.group(1)}" if page else label

    def source_url(self, citation: str) -> str:
        document = self._documents.get(citation.partition(":")[0])
        return document.source_url if document else ""
