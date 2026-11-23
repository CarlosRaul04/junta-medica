"""Usuarios (solo administrador, RF15): cambiar el rol o desactivar cuentas."""
import pandas as pd
import streamlit as st

from junta_medica.config.users import ROLE_LABELS
from junta_medica.exceptions import UserAccountError
from junta_medica.ui import dependencies, session
from junta_medica.ui.components.page_header import page_header


def page() -> None:
    user = session.current_user()
    page_header("Administración", "Usuarios",
                "Los médicos ven solo sus consultas; el administrador ve todas y gestiona las cuentas.")
    if not user.role.can_manage_users:
        st.error("Solo el administrador puede ver esta pantalla.")
        return
    auth = dependencies.auth_service()
    accounts = auth.all_users()
    labels = {label: role for role, label in ROLE_LABELS.items()}
    original = pd.DataFrame([{"id": a.user_id, "Usuario": a.username, "Nombre": a.full_name,
                              "Rol": ROLE_LABELS[a.role], "Activa": a.active} for a in accounts])
    edited = st.data_editor(
        original, hide_index=True, width="stretch", disabled=["id", "Usuario", "Nombre"],
        column_config={"id": None, "Rol": st.column_config.SelectboxColumn(options=list(labels), required=True)},
    )
    st.caption("Tu propia cuenta no se puede cambiar desde aquí (así el sistema nunca se queda sin administrador).")
    if st.button("Guardar cambios", type="primary"):
        changes = 0
        for before, after in zip(original.to_dict("records"), edited.to_dict("records")):
            try:
                if before["Rol"] != after["Rol"]:
                    auth.change_role(user, before["id"], labels[after["Rol"]])
                    changes += 1
                if before["Activa"] != after["Activa"]:
                    auth.set_active(user, before["id"], bool(after["Activa"]))
                    changes += 1
            except UserAccountError as error:
                st.error(f"{before['Usuario']}: {error}")
        if changes:
            st.success(f"Se guardaron {changes} cambio(s).")
            st.rerun()
