"""Las pantallas de la aplicación y cómo ir de una a otra (st.navigation)."""
import streamlit as st

from junta_medica.models.users.user import User

_PAGES: dict[str, st.Page] = {}


def build(user: User) -> dict[str, list[st.Page]]:
    from junta_medica.ui.pages import board_session, history, home, how_it_works, new_consultation, result, users
    _PAGES.update(
        home=st.Page(home.page, title="Inicio", icon=":material/home:", url_path="inicio", default=True),
        new=st.Page(new_consultation.page, title="Nueva consulta", icon=":material/add_circle:",
                    url_path="nueva-consulta"),
        board=st.Page(board_session.page, title="Junta en curso", icon=":material/groups:", url_path="junta",
                      visibility="hidden"),
        result=st.Page(result.page, title="Resultado", icon=":material/clinical_notes:", url_path="resultado"),
        history=st.Page(history.page, title="Historial", icon=":material/history:", url_path="historial"),
        help=st.Page(how_it_works.page, title="Cómo funciona", icon=":material/help:", url_path="como-funciona"),
        users=st.Page(users.page, title="Usuarios", icon=":material/manage_accounts:", url_path="usuarios"),
    )
    sections = {
        "Consultas": [_PAGES["home"], _PAGES["new"], _PAGES["board"], _PAGES["result"], _PAGES["history"]],
        "Ayuda": [_PAGES["help"]],
    }
    if user.role.can_manage_users:
        sections["Administración"] = [_PAGES["users"]]
    return sections


def go(name: str) -> None:
    st.switch_page(_PAGES[name])
