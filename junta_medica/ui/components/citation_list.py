"""Muestra citas técnicas ("gpc_ic:p23") como fuentes legibles ("GPC Insuficiencia cardiaca …, pág. 23")."""
from junta_medica.services.reports.citation_formatter import CitationFormatter
from junta_medica.ui.components.html import esc


def sources_html(citations: list[str], formatter: CitationFormatter) -> str:
    if not citations:
        return ""
    readable = " · ".join(esc(formatter.format(c)) for c in citations)
    return f'<div class="jm-source">📄 {readable}</div>'
