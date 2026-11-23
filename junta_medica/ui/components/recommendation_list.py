"""Recomendaciones del Médico Jefe, cada una con su fuente, y discrepancias que quedaron abiertas."""
import streamlit as st

from junta_medica.services.reports.citation_formatter import CitationFormatter
from junta_medica.services.reports.result_reader import ResultReader
from junta_medica.ui.components.citation_list import sources_html
from junta_medica.ui.components.html import esc, render


def recommendation_list(result: ResultReader, citations: CitationFormatter) -> None:
    if not result.recommendations:
        st.info("El Médico Jefe no dejó recomendaciones para este caso.")
    for number, item in enumerate(result.recommendations, start=1):
        render(f'<div class="jm-card"><h4>{number}. {esc(item.get("text", ""))}</h4>'
               f'{sources_html(item.get("citations", []), citations) or "<p>Sin cita a las guías.</p>"}</div>')
    if result.disagreements:
        st.markdown("**Discrepancias que la junta no resolvió**")
        for item in result.disagreements:
            st.warning(item, icon="⚠️")
    missing = (result.last_proposal or {}).get("missing_data") or []
    if missing:
        st.markdown("**Datos que ayudarían a decidir mejor**")
        for item in missing:
            st.markdown(f"- {item}")
