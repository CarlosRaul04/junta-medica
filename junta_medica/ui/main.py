"""Punto de entrada de la interfaz: página, estilos, inicio de sesión, barra lateral y menú."""
from pathlib import Path

import streamlit as st

from junta_medica.config.users import ROLE_LABELS
from junta_medica.ui import dependencies, navigation, session, theme
from junta_medica.ui.components.html import esc, render
from junta_medica.ui.pages import login

ASSETS = Path(__file__).parent / "assets"


def main() -> None:
    st.set_page_config(page_title="Junta Médica IA", page_icon=str(ASSETS / "icon.svg"), layout="wide")
    theme.apply()
    user = session.current_user()
    if user is None:
        login.page()
        return
    pages = navigation.build(user)
    _sidebar(user)
    st.navigation(pages).run()


def _sidebar(user) -> None:
    st.logo(str(ASSETS / "logo.svg"), size="large", icon_image=str(ASSETS / "icon.svg"))
    with st.sidebar:
        render(f'<div style="font-size:.9rem"><b>{esc(user.full_name)}</b><br>'
               f'<span style="opacity:.75">{esc(ROLE_LABELS[user.role])} · @{esc(user.username)}</span></div>')
        if dependencies.is_mock_mode():
            st.caption("🧪 Modo simulado (sin IA real)")
        if st.button("Cerrar sesión", icon=":material/logout:", width="stretch"):
            session.sign_out()
            st.rerun()
