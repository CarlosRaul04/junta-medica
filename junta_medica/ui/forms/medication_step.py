"""
Paso 3: medicación activa y laboratorio.

Cada medicamento es una fila (nombre + dosis + quitar). El nombre se elige del catálogo o se escribe
libre (genérico o comercial); el laboratorio pide solo los resultados que se tengan.
"""
import re

import streamlit as st

from junta_medica.config.cases import RECOGNIZED_LAB_TESTS
from junta_medica.ui.forms.suggestions import drug_names

_ROWS = "form_medication_rows"
_BRANDS = re.compile(r"\s*\(.*\)$")     # "dabigatrán (Pradaxa)" -> "dabigatrán"


def medication_step(draft: dict) -> str | None:
    """Devuelve "next", "back" o None."""
    rows = _rows(draft)
    st.markdown("##### Medicación activa")
    st.caption("Elige de la lista o escribe el nombre (genérico o comercial) y pulsa Enter.")
    catalog = drug_names()
    for row_id in list(rows):
        name_col, dose_col, remove_col = st.columns([3, 2.4, 0.5], vertical_alignment="bottom")
        key = f"form_med_name_{row_id}"
        current = st.session_state.get(key)
        options = catalog if current in (None, *catalog) else [current, *catalog]
        start = {} if key in st.session_state else {"index": None}     # fila nueva: vacía
        name_col.selectbox("Medicamento", options, key=key, **start,
                           accept_new_options=True, placeholder="Ej. enalapril o Pradaxa",
                           label_visibility="visible" if row_id == rows[0] else "collapsed")
        dose_col.text_input("Dosis y frecuencia", key=f"form_med_dose_{row_id}", placeholder="Ej. 20 mg cada 12 h",
                            label_visibility="visible" if row_id == rows[0] else "collapsed")
        if remove_col.button("", key=f"form_med_remove_{row_id}", icon=":material/delete:", help="Quitar",
                             disabled=len(rows) == 1):
            rows.remove(row_id)
            st.rerun()
    if st.button("Agregar otro medicamento", icon=":material/add:"):
        rows.append(max(rows) + 1)
        st.rerun()

    st.markdown("##### Laboratorio y signos vitales")
    labels = {label: key for key, label in RECOGNIZED_LAB_TESTS.items()}
    chosen = st.multiselect("Elige solo los resultados que tienes", list(labels),
                            default=[RECOGNIZED_LAB_TESTS[k] for k in draft["lab_results"]],
                            placeholder="Ej. Potasio sérico, TFG estimada…", key="form_lab_choice")
    values = {}
    columns = st.columns(3)
    for index, label in enumerate(chosen):
        key = labels[label]
        values[key] = columns[index % 3].number_input(label, value=draft["lab_results"].get(key), step=0.1,
                                                      format="%.2f", placeholder="Valor", key=f"form_lab_{key}")

    st.write("")
    back, _, forward = st.columns([1, 3, 1])
    go_back = back.button("← Atrás", width="stretch")
    go_next = forward.button("Siguiente →", type="primary", width="stretch")
    if not (go_back or go_next):
        return None
    medications = _medications(rows)
    st.session_state.pop(_ROWS, None)     # al volver a este paso, las filas se rearman desde el borrador
    empty = [label for label in chosen if values.get(labels[label]) is None]
    draft.update(medications=medications, lab_results={k: v for k, v in values.items() if v is not None})
    if go_next and empty:
        st.error("Escribe el valor de: " + ", ".join(empty) + " (o quítalo de la lista).")
        return None
    if go_next and not medications:
        st.error("Registra al menos un medicamento: la junta revisa la medicación activa.")
        return None
    return "next" if go_next else "back"


def _rows(draft: dict) -> list[int]:
    """Las filas del formulario; la primera vez se llenan con lo que tenga el borrador."""
    if _ROWS not in st.session_state:
        meds = draft["medications"] or [{"name": "", "dose": ""}]
        for index, med in enumerate(meds):
            st.session_state[f"form_med_name_{index}"] = med["name"] or None
            st.session_state[f"form_med_dose_{index}"] = med.get("dose", "")
        st.session_state[_ROWS] = list(range(len(meds)))
    return st.session_state[_ROWS]


def _medications(rows: list[int]) -> list[dict]:
    medications = []
    for row_id in rows:
        name = _BRANDS.sub("", st.session_state.get(f"form_med_name_{row_id}") or "").strip()
        if name:
            medications.append({"name": name, "dose": (st.session_state.get(f"form_med_dose_{row_id}") or "").strip()})
    return medications
