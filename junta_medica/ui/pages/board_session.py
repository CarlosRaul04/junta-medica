"""
La junta trabajando (pantalla oculta del menú): convoca a los agentes, muestra el progreso en vivo,
guarda la consulta con su informe PDF y abre el resultado.
"""
import streamlit as st

from junta_medica.config.debate import MAX_ROUNDS
from junta_medica.exceptions import LLMConfigurationError, LLMProviderError, OutdatedIndexError
from junta_medica.ui import dependencies, navigation, session
from junta_medica.ui.components.page_header import page_header
from junta_medica.ui.components.progress_tracker import ProgressTracker

_ERROR_HINTS = {
    LLMConfigurationError: "Revisa el archivo .env (LLM_API_KEY, AGENT_MODEL, CHIEF_MODEL) o usa MOCK_MODE=1.",
    LLMProviderError: "El proveedor de IA rechazó la consulta (límite diario, modelo no disponible o clave inválida). "
                      "Prueba más tarde o cambia de modelo en el .env.",
    OutdatedIndexError: "Ejecuta en la terminal: python -m scripts.index_guidelines",
}


def page() -> None:
    case = session.take_pending_case()
    if case is None:
        navigation.go("new")
        return
    page_header("La junta está trabajando", f"{case.case_id} · {case.chief_complaint}",
                "No cierres esta pestaña. Cada agente aparece aquí cuando empieza y cuando termina.")
    orchestrator = dependencies.debate_orchestrator()
    tracker = ProgressTracker(MAX_ROUNDS)
    try:
        result = orchestrator.run(case, tracker)
    except tuple(_ERROR_HINTS) as error:
        tracker.fail("La junta no pudo terminar")
        st.error(f"{error}\n\n{_ERROR_HINTS[type(error)]}")
        if st.button("← Volver a revisar el caso", type="primary"):
            navigation.go("new")
        return
    tracker.finish(result.insufficient_evidence)
    with st.spinner("Guardando la consulta y generando el informe PDF…"):
        consultation = dependencies.consultation_service().record(result, session.current_user())
    session.clear_draft()
    session.open_consultation(consultation.consultation_id)
    navigation.go("result")
