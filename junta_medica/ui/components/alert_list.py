"""Alertas de seguridad de la medicación: primero las graves (destacadas, RF12), luego las demás."""
import streamlit as st

from junta_medica.config.texts import SEVERITY_LABELS
from junta_medica.services.reports.citation_formatter import CitationFormatter
from junta_medica.services.reports.result_reader import ResultReader
from junta_medica.ui.components.citation_list import sources_html
from junta_medica.ui.components.html import chip, esc, render

_TONES = {"severe": "red", "moderate": "amber", "mild": "gray", "unknown": "gray"}
_ORIGINS = {"interaction_table": "Interacción entre fármacos", "condition_rules": "Fármaco y condición del paciente",
            "agent": "Señalada por el Agente Farmacológico"}


def alert_list(result: ResultReader, citations: CitationFormatter) -> None:
    if not result.alerts:
        st.success("No se encontraron interacciones ni contraindicaciones para la medicación registrada.")
        return
    for alert in result.highlighted_alerts:
        _alert(alert, citations)
    others = result.other_alerts
    if others:
        with st.expander(f"Otras alertas ({len(others)})", expanded=not result.highlighted_alerts):
            for alert in others:
                _alert(alert, citations)


def _alert(alert: dict, citations: CitationFormatter) -> None:
    severity = alert["severity"]
    label = SEVERITY_LABELS.get(severity, severity).capitalize()
    origin = _ORIGINS.get(alert.get("origin"), "")
    render(f'<div class="jm-alert {severity}">{chip(label, _TONES.get(severity, "gray"))}'
           f'{chip(origin, "gray") if origin else ""}'
           f'<div class="jm-alert-text">{esc(alert["text"])}</div>'
           f'{sources_html(alert.get("citations", []), citations)}</div>')
