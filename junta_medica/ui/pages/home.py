"""Inicio: qué hace el sistema en 3 pasos, botón para empezar y las últimas consultas del usuario."""
import streamlit as st

from junta_medica.ui import dependencies, navigation, session
from junta_medica.ui.components.html import chip, esc, render
from junta_medica.ui.components.metric_tile import Metric, metric_row
from junta_medica.ui.components.page_header import page_header

STEPS = [
    ("1", "Registra el caso", "Edad, síntomas, antecedentes, medicación y laboratorio. Sin datos personales."),
    ("2", "La junta debate", "Un Agente Clínico propone; el Farmacológico y el de Protocolo revisan con las guías. "
                             "Hasta 3 rondas."),
    ("3", "Recibe la segunda opinión", "Diagnóstico con CIE-10, alertas de medicación, recomendaciones con su "
                                      "fuente e informe PDF."),
]


def page() -> None:
    user = session.current_user()
    names = [w for w in user.full_name.split() if not w.endswith(".")]   # sin "Dr." ni "Dra."
    first_name = names[0] if names else user.username
    page_header("Inicio", f"Hola, {first_name}",
                "Pide una segunda opinión para un caso de Medicina Interna. La decisión final siempre es tuya.")

    columns = st.columns(3)
    for column, (number, title, text) in zip(columns, STEPS):
        with column:
            render(f'<div class="jm-card" style="min-height:9.5rem"><div class="jm-eyebrow">Paso {number}</div>'
                   f'<h4>{esc(title)}</h4><p>{esc(text)}</p></div>')
    left, right, _ = st.columns([1.3, 1.3, 3])
    if left.button("Nueva consulta", type="primary", icon=":material/add_circle:", width="stretch"):
        session.clear_draft()
        navigation.go("new")
    if right.button("Cómo funciona", icon=":material/help:", width="stretch"):
        navigation.go("help")

    consultations = dependencies.consultation_service().search(user)
    st.markdown("### Tus consultas")
    if not consultations:
        st.info("Todavía no tienes consultas. Empieza con **Nueva consulta**; puedes usar un caso de ejemplo.",
                icon="📋")
        return
    metric_row([
        Metric("Consultas", str(len(consultations))),
        Metric("Con alertas graves", str(sum(1 for c in consultations if c.severe_alerts))),
        Metric("Evidencia insuficiente", str(sum(1 for c in consultations if c.insufficient_evidence))),
        Metric("Trazabilidad promedio",
               f"{sum(c.traceability for c in consultations) / len(consultations):.0%}", "meta: 90 %"),
    ])
    st.write("")
    dates = dependencies.date_formatter()
    for consultation in consultations[:5]:
        _row(consultation, dates)
    if len(consultations) > 5 and st.button("Ver todo el historial →"):
        navigation.go("history")


def _row(c, dates) -> None:
    info, action = st.columns([5, 1], vertical_alignment="center")
    status = chip("Evidencia insuficiente", "amber") if c.insufficient_evidence else chip(c.primary_icd10, "teal")
    alerts = chip(f"{c.severe_alerts} alerta(s) grave(s)", "red") if c.severe_alerts else ""
    with info:
        render(f'<div style="padding:.35rem 0"><b>{esc(c.case_id)}</b> · {esc(c.primary_name)}<br>'
               f'<span class="jm-muted">{esc(dates.format(c.created_at))}</span> {status}{alerts}</div>')
    if action.button("Abrir", key=f"open_{c.consultation_id}", width="stretch"):
        session.open_consultation(c.consultation_id)
        navigation.go("result")
