"""Paso 2: síntomas, antecedentes y alergias (se elige de la lista o se escribe uno nuevo y Enter)."""
import streamlit as st

from junta_medica.ui.forms.suggestions import field_suggestions


def clinical_step(draft: dict) -> str | None:
    """Devuelve "next", "back" o None."""
    options = field_suggestions()
    with st.form("form_clinical"):
        st.markdown("##### Cuadro clínico")
        st.caption("Escribe y pulsa Enter para agregar algo que no está en la lista.")
        symptoms = _tags("Síntomas", "symptoms", draft, options, "Ej. disnea de esfuerzo")
        history = _tags("Antecedentes", "medical_history", draft, options, "Ej. diabetes mellitus tipo 2")
        allergies = _tags("Alergias", "allergies", draft, options, "Déjalo vacío si no tiene")
        back, _, forward = st.columns([1, 3, 1])
        go_back = back.form_submit_button("← Atrás")
        go_next = forward.form_submit_button("Siguiente →", type="primary")
    if not (go_back or go_next):
        return None
    draft.update(symptoms=symptoms, medical_history=history, allergies=allergies)
    if go_next and not symptoms:
        st.error("Agrega al menos un síntoma.")
        return None
    return "next" if go_next else "back"


def _tags(label: str, field: str, draft: dict, options: dict, placeholder: str) -> list[str]:
    current = draft.get(field) or []
    choices = sorted(set(options.get(field, [])) | set(current))
    return st.multiselect(label, choices, default=current, accept_new_options=True, placeholder=placeholder)
