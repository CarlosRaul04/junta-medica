"""Inicio de sesión y creación de cuentas (RF15). Si no hay cuentas, se crea la del administrador."""
import streamlit as st

from junta_medica.config.users import MIN_PASSWORD_LENGTH, USERNAME_RULE
from junta_medica.exceptions import UserAccountError
from junta_medica.ui import dependencies, session
from junta_medica.ui.components.html import render


def page() -> None:
    _, center, _ = st.columns([1, 1.3, 1])
    with center:
        render('<div style="text-align:center;margin:2.5rem 0 1.2rem 0">'
               '<div class="jm-brand-mark" style="margin:0 auto .7rem auto;width:3rem;height:3rem;font-size:1.3rem">JM</div>'
               '<div class="jm-title" style="font-size:1.7rem">Junta Médica IA</div>'
               '<div class="jm-subtitle" style="margin:0 auto">Segunda opinión en Medicina Interna: '
               'cuatro agentes de IA debaten tu caso con guías clínicas peruanas.</div></div>')
        auth = dependencies.auth_service()
        if not auth.has_users():
            st.info("Es la primera vez que se abre el sistema. Crea la cuenta del **administrador**.", icon="👋")
            _register(first=True)
            return
        sign_in, register = st.tabs(["Iniciar sesión", "Crear cuenta"])
        with sign_in:
            _login()
        with register:
            _register(first=False)


def _login() -> None:
    with st.form("login_form", border=False):
        username = st.text_input("Usuario", autocomplete="username")
        password = st.text_input("Contraseña", type="password", autocomplete="current-password")
        if st.form_submit_button("Ingresar", type="primary", width="stretch"):
            try:
                session.sign_in(dependencies.auth_service().login(username, password))
                st.rerun()
            except UserAccountError as error:
                st.error(str(error))


def _register(first: bool) -> None:
    with st.form("register_form", border=False):
        full_name = st.text_input("Nombre completo", placeholder="Ej. Dra. Ana Pérez")
        username = st.text_input("Usuario", help=f"Debe tener {USERNAME_RULE}.", placeholder="ej. aperez")
        password = st.text_input("Contraseña", type="password", help=f"Mínimo {MIN_PASSWORD_LENGTH} caracteres.")
        confirmation = st.text_input("Repite la contraseña", type="password")
        if not first:
            st.caption("Las cuentas nuevas son de **médico tratante**. El administrador puede cambiar el rol.")
        label = "Crear cuenta de administrador" if first else "Crear cuenta"
        if st.form_submit_button(label, type="primary", width="stretch"):
            try:
                session.sign_in(dependencies.auth_service().register(username, full_name, password, confirmation))
                st.rerun()
            except UserAccountError as error:
                st.error(str(error))
