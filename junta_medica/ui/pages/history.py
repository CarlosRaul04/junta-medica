"""Historial de consultas (RF16): buscar, filtrar, abrir y exportar a CSV."""
import pandas as pd
import streamlit as st

from junta_medica.ui import dependencies, navigation, session
from junta_medica.ui.components.page_header import page_header

_STATUS = {"Todas": None, "Con dictamen": False, "Evidencia insuficiente": True}


def page() -> None:
    user = session.current_user()
    page_header("Historial", "Consultas anteriores",
                "Selecciona una fila para abrir su resultado. Puedes exportar la lista a Excel (CSV).")
    text_col, status_col, scope_col = st.columns([2, 2, 1.3], vertical_alignment="bottom")
    text = text_col.text_input("Buscar", placeholder="Código, CIE-10 o diagnóstico", label_visibility="collapsed")
    status = status_col.segmented_control("Estado", list(_STATUS), default="Todas", label_visibility="collapsed")
    all_users = False
    if user.role.can_see_all_history:
        all_users = scope_col.toggle("Todo el equipo", value=True)
    consultations = dependencies.consultation_service().search(user, text, _STATUS[status or "Todas"], all_users)
    if not consultations:
        st.info("No hay consultas que coincidan.")
        return

    dates = dependencies.date_formatter()
    table = pd.DataFrame([{
        "N.°": c.consultation_id, "Fecha": dates.format(c.created_at), "Caso": c.case_id,
        "CIE-10": c.primary_icd10 or "—", "Diagnóstico principal": c.primary_name,
        "Alertas graves": c.severe_alerts, "Acuerdo": c.agreement, "Trazabilidad": c.traceability,
        "Médico": c.username,
    } for c in consultations])
    if not all_users:
        table = table.drop(columns=["Médico"])
    selection = st.dataframe(
        table, hide_index=True, width="stretch", on_select="rerun", selection_mode="single-row",
        column_config={
            "N.°": st.column_config.NumberColumn(width="small"),
            "Diagnóstico principal": st.column_config.TextColumn(width="medium"),
            "Acuerdo": st.column_config.NumberColumn(format="percent", width="small"),
            "Trazabilidad": st.column_config.NumberColumn(format="percent", width="small"),
            "Alertas graves": st.column_config.NumberColumn(width="small"),
        },
    )
    rows = selection.selection.rows
    open_col, csv_col, _ = st.columns([1.4, 1.4, 3])
    if open_col.button("Abrir consulta", type="primary", disabled=not rows, icon=":material/open_in_new:",
                       width="stretch"):
        session.open_consultation(consultations[rows[0]].consultation_id)
        navigation.go("result")
    csv_col.download_button("Exportar a CSV", dependencies.csv_exporter().export(consultations),
                            file_name="historial_junta_medica.csv", mime="text/csv", icon=":material/download:",
                            width="stretch")
