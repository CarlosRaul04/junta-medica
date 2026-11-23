"""Paso 1: código del caso, edad, sexo y motivo de consulta."""
import streamlit as st

from junta_medica.config import cases as cases_config

SEX_OPTIONS = {"M": "Masculino", "F": "Femenino"}


def patient_step(draft: dict) -> bool | None:
    """Devuelve True al pulsar Siguiente (con lo mínimo lleno), None si no pasó nada."""
    with st.form("form_patient"):
        st.markdown("##### Identificación del caso")
        st.caption("Sin nombre, DNI, teléfono ni correo: el caso se identifica solo con un código (Ley 29733).")
        c1, c2, c3 = st.columns([1.2, 1, 1])
        case_id = c1.text_input("Código del caso", value=draft["case_id"],
                                help=f"Formato {cases_config.CASE_ID_EXAMPLE}. Se propone el siguiente libre.")
        age = c2.number_input("Edad (años)", min_value=cases_config.MIN_AGE, max_value=cases_config.MAX_AGE,
                              value=draft["age"], placeholder="Ej. 68", step=1,
                              help="Medicina Interna de adultos: 18 años o más.")
        sex = c3.segmented_control("Sexo", list(SEX_OPTIONS), format_func=SEX_OPTIONS.get,
                                   default=draft["sex"] or None)
        complaint = st.text_input("Motivo de consulta", value=draft["chief_complaint"],
                                  placeholder="Ej. Disnea progresiva y edema de miembros inferiores")
        submitted = st.form_submit_button("Siguiente →", type="primary")
    if not submitted:
        return None
    draft.update(case_id=case_id.strip().upper(), age=int(age) if age else None, sex=sex or "",
                 chief_complaint=complaint.strip())
    missing = [name for name, value in (("la edad", draft["age"]), ("el sexo", draft["sex"]),
                                        ("el motivo de consulta", draft["chief_complaint"])) if not value]
    if missing:
        st.error("Falta " + ", ".join(missing) + ".")
        return None
    return True
