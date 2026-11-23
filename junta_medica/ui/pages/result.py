"""Resultado de una consulta: dictamen, indicadores y pestañas con alertas, recomendaciones, debate y fuentes."""
import streamlit as st

from junta_medica.config.texts import SEX_LABELS
from junta_medica.exceptions import AccessDeniedError
from junta_medica.ui import dependencies, navigation, session
from junta_medica.ui.components.alert_list import alert_list
from junta_medica.ui.components.case_summary import case_summary
from junta_medica.ui.components.debate_view import debate_view
from junta_medica.ui.components.disclaimer import disclaimer
from junta_medica.ui.components.metric_tile import Metric, metric_row
from junta_medica.ui.components.page_header import page_header
from junta_medica.ui.components.recommendation_list import recommendation_list
from junta_medica.ui.components.sources_view import sources_view
from junta_medica.ui.components.verdict_hero import verdict_hero


def page() -> None:
    consultation_id = session.opened_consultation()
    if consultation_id is None:
        page_header("Resultado", "Ninguna consulta abierta", "Abre una desde el historial o crea una nueva.")
        left, right, _ = st.columns([1, 1, 3])
        if left.button("Nueva consulta", type="primary", width="stretch"):
            session.clear_draft()
            navigation.go("new")
        if right.button("Ir al historial", width="stretch"):
            navigation.go("history")
        return

    user = session.current_user()
    service = dependencies.consultation_service()
    try:
        consultation = service.get(user, consultation_id)
    except AccessDeniedError as error:
        st.error(str(error))
        return
    result = service.load_result(consultation)
    if result is None:
        st.error("No se encontró el archivo con el resultado completo de esta consulta.")
        return

    case = result.case
    dates = dependencies.date_formatter()
    page_header(f"Consulta N.° {consultation.consultation_id} · {dates.format(consultation.created_at)}",
                f"{result.case_id} · {case.get('chief_complaint', '')}",
                f"{case.get('age')} años, {SEX_LABELS.get(case.get('sex'), '')} · solicitada por "
                f"{consultation.username}")
    _actions(service, consultation, user)
    if result.unrecognized_drugs:
        st.warning("No se reconocieron estos medicamentos, así que no se revisaron sus interacciones: "
                   + ", ".join(result.unrecognized_drugs) + ". Revisa cómo están escritos.", icon="💊")
    verdict_hero(result)
    metric_row([
        Metric("Acuerdo final", f"{result.agreement:.0%}" if result.rounds else "—", "umbral de consenso: 67 %"),
        Metric("Rondas de debate", str(len(result.rounds)), "máximo 3"),
        Metric("Alertas graves", str(len(result.highlighted_alerts)), "de la medicación"),
        Metric("Trazabilidad", f"{result.traceability:.0%}", "afirmaciones con cita válida"),
        Metric("Tiempo", f"{result.seconds:.0f} s", f"{result.llm_calls} llamadas a la IA"),
    ])
    st.write("")
    citations = dependencies.citation_formatter()
    tabs = st.tabs([f"Alertas de medicación ({len(result.alerts)})", "Recomendaciones", "Debate de la junta",
                    "Fuentes y trazabilidad", "Datos del caso"])
    with tabs[0]:
        alert_list(result, citations)
    with tabs[1]:
        recommendation_list(result, citations)
    with tabs[2]:
        debate_view(result, citations)
    with tabs[3]:
        sources_view(result, citations)
    with tabs[4]:
        case_summary(case, result.unrecognized_drugs)
    disclaimer()


def _actions(service, consultation, user) -> None:
    pdf, new, _ = st.columns([1.3, 1.2, 3])
    report = service.load_report(consultation, user.full_name)
    if report:
        pdf.download_button("Descargar informe PDF", report, file_name=f"{consultation.case_id}_informe.pdf",
                            mime="application/pdf", type="primary", icon=":material/download:", width="stretch")
    if new.button("Nueva consulta", icon=":material/add_circle:", width="stretch"):
        session.clear_draft()
        navigation.go("new")
