"""Lo que la interfaz recuerda mientras el usuario navega (st.session_state), en un solo lugar."""
import streamlit as st

from junta_medica.models.users.user import User

_USER = "current_user"
_CONSULTATION = "open_consultation_id"
_DRAFT = "case_draft"
_STEP = "wizard_step"
_PENDING_CASE = "pending_case"


def current_user() -> User | None:
    return st.session_state.get(_USER)


def sign_in(user: User) -> None:
    st.session_state[_USER] = user


def sign_out() -> None:
    st.session_state.clear()


def open_consultation(consultation_id: int) -> None:
    st.session_state[_CONSULTATION] = consultation_id


def opened_consultation() -> int | None:
    return st.session_state.get(_CONSULTATION)


def draft(default_factory) -> dict:
    """El borrador del caso clínico que se está llenando en el formulario por pasos."""
    if _DRAFT not in st.session_state:
        st.session_state[_DRAFT] = default_factory()
    return st.session_state[_DRAFT]


def replace_draft(data: dict) -> None:
    st.session_state[_DRAFT] = data


def clear_draft() -> None:
    for key in (_DRAFT, _STEP):
        st.session_state.pop(key, None)
    for key in [k for k in st.session_state if str(k).startswith("form_")]:
        del st.session_state[key]


def wizard_step() -> int:
    return st.session_state.get(_STEP, 0)


def go_to_step(step: int) -> None:
    st.session_state[_STEP] = step


def start_run(case) -> None:
    """Guarda el caso validado para convocar a la junta en la siguiente vuelta (pantalla de progreso limpia)."""
    st.session_state[_PENDING_CASE] = case


def take_pending_case():
    return st.session_state.pop(_PENDING_CASE, None)
