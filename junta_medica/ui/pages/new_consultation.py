"""
Nueva consulta: formulario del caso en 4 pasos (o un caso de ejemplo).

Al convocar a la junta pasa a la pantalla board_session, que muestra el progreso en vivo.
"""
import streamlit as st

from junta_medica.ui import dependencies, navigation, session
from junta_medica.ui.components.page_header import page_header
from junta_medica.ui.components.step_indicator import step_indicator
from junta_medica.ui.forms.case_draft import empty_draft, from_case
from junta_medica.ui.forms.clinical_step import clinical_step
from junta_medica.ui.forms.medication_step import medication_step
from junta_medica.ui.forms.patient_step import patient_step
from junta_medica.ui.forms.review_step import review_step
from junta_medica.ui.forms.suggestions import example_cases

STEPS = ["Paciente", "Cuadro clínico", "Medicación y laboratorio", "Revisar y convocar"]


def page() -> None:
    page_header("Nueva consulta", "Pide una segunda opinión",
                "Completa el caso en 4 pasos o carga un caso de ejemplo para ver cómo funciona.")
    draft = session.draft(lambda: empty_draft(dependencies.case_id_generator().next_id()))
    step = session.wizard_step()
    if step == 0:
        _example_picker()
    step_indicator(STEPS, step)

    if step == 0:
        if patient_step(draft):
            _move(1)
    elif step == 1:
        _navigate(clinical_step(draft), step)
    elif step == 2:
        _navigate(medication_step(draft), step)
    else:
        action, case = review_step(draft)
        if action == "back":
            _move(2)
        elif action == "run":
            session.start_run(case)
            navigation.go("board")


def _example_picker() -> None:
    with st.expander("¿Solo quieres probar? Carga un caso de ejemplo", icon=":material/science:"):
        examples = example_cases()
        choice = st.selectbox("Caso de ejemplo", list(examples), index=None, placeholder="Elige un caso…",
                              label_visibility="collapsed")
        if st.button("Cargar este caso", disabled=choice is None):
            session.clear_draft()
            session.replace_draft(from_case(examples[choice]))
            _move(3)


def _navigate(action: str | None, step: int) -> None:
    if action == "next":
        _move(step + 1)
    elif action == "back":
        _move(step - 1)


def _move(step: int) -> None:
    session.go_to_step(step)
    st.rerun()
