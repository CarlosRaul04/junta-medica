"""Paso 4: revisar el caso completo, ver errores de validación (RF02) y convocar a la junta."""
import streamlit as st

from junta_medica.exceptions import InvalidCaseError
from junta_medica.ui import dependencies
from junta_medica.ui.components.case_summary import case_summary
from junta_medica.ui.forms.case_draft import to_case


def review_step(draft: dict):
    """Devuelve ("back", None), ("run", ClinicalCase) o (None, None)."""
    case_data = to_case(draft)
    st.markdown(f"##### Revisa el caso {case_data['case_id']} antes de convocar a la junta")
    case_summary(case_data)
    case, errors = None, []
    try:
        case = dependencies.case_loader().from_dict(case_data)
    except InvalidCaseError as error:
        errors = [e.message for e in error.errors]
    if errors:
        st.error("Corrige esto antes de continuar:\n\n" + "\n".join(f"- {m}" for m in errors))
    else:
        st.info("La junta tarda 1 a 3 minutos con un modelo real: hace unas 4 a 10 consultas a la IA. "
                "Puedes ver en vivo qué hace cada agente.", icon="⏱️")
    back, _, forward = st.columns([1, 2.4, 1.6])
    if back.button("← Atrás", width="stretch"):
        return "back", None
    if forward.button("Convocar a la junta médica", type="primary", width="stretch", disabled=bool(errors),
                      icon=":material/groups:"):
        return "run", case
    return None, None
