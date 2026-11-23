"""Fila de indicadores (acuerdo, rondas, alertas, trazabilidad, tiempo)."""
from dataclasses import dataclass

import streamlit as st

from junta_medica.ui.components.html import esc, render


@dataclass(frozen=True)
class Metric:
    label: str
    value: str
    help: str = ""


def metric_row(metrics: list[Metric]) -> None:
    for column, metric in zip(st.columns(len(metrics)), metrics):
        with column:
            help_html = f'<div class="jm-metric-help">{esc(metric.help)}</div>' if metric.help else ""
            render(f'<div class="jm-metric"><div class="jm-metric-label">{esc(metric.label)}</div>'
                   f'<div class="jm-metric-value">{esc(metric.value)}</div>{help_html}</div>')
