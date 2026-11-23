"""Ficha del caso clínico tal como se registró (para el resultado y el paso de revisión)."""
import streamlit as st

from junta_medica.config.cases import RECOGNIZED_LAB_TESTS
from junta_medica.config.texts import SEX_LABELS
from junta_medica.ui.components.html import chip, esc, render



def case_summary(case: dict, unrecognized_drugs: list[str] | None = None) -> None:
    meds = [f"{m['name']} {m.get('dose', '')}".strip() if isinstance(m, dict) else str(m)
            for m in case.get("medications") or []]
    labs = case.get("lab_results") or {}
    lab_text = "<br>".join(f"{esc(RECOGNIZED_LAB_TESTS.get(k, k))}: <b>{v:g}</b>" for k, v in labs.items())
    rows = [
        ("Paciente", esc(f"{case.get('age', '—')} años · {SEX_LABELS.get(case.get('sex'), case.get('sex', '—'))}")),
        ("Motivo de consulta", esc(case.get("chief_complaint") or "—")),
        ("Síntomas", _chips(case.get("symptoms"))),
        ("Antecedentes", _chips(case.get("medical_history"))),
        ("Alergias", _chips(case.get("allergies"), "Ninguna registrada")),
        ("Medicación activa", _chips(meds)),
        ("Laboratorio y signos", lab_text or "Sin resultados registrados"),
    ]
    body = "".join(f'<tr><td style="width:12rem;color:var(--jm-gray);font-weight:600;vertical-align:top;'
                   f'padding:.45rem .6rem .45rem 0">{label}</td><td style="padding:.45rem 0">{value}</td></tr>'
                   for label, value in rows)
    render(f'<div class="jm-card"><table style="width:100%;border-collapse:collapse">{body}</table></div>')
    if unrecognized_drugs:
        st.warning("No reconocidos en el catálogo (no se revisan sus interacciones): " + ", ".join(unrecognized_drugs))


def _chips(items, empty: str = "—") -> str:
    return "".join(chip(i) for i in items or []) or esc(empty)
