"""
El borrador del caso clínico mientras se llena el formulario por pasos.

Tiene la misma forma que la sección "case" de los JSON de data/cases/, así un caso de ejemplo
se puede cargar en el formulario y el validador recibe exactamente lo que espera.
"""
import copy


def empty_draft(case_id: str) -> dict:
    return {
        "case_id": case_id, "age": None, "sex": "", "chief_complaint": "",
        "symptoms": [], "medical_history": [], "allergies": [],
        "medications": [], "lab_results": {},
    }


def from_case(case: dict) -> dict:
    """Un caso de ejemplo -> borrador (medicamentos siempre como {name, dose})."""
    draft = copy.deepcopy(case)
    draft["medications"] = [m if isinstance(m, dict) else {"name": str(m), "dose": ""}
                            for m in case.get("medications", [])]
    for key in ("medical_history", "allergies"):
        draft.setdefault(key, [])
    draft.setdefault("lab_results", {})
    return draft


def to_case(draft: dict) -> dict:
    """Borrador -> diccionario para el validador (quita filas vacías)."""
    case = copy.deepcopy(draft)
    case["case_id"] = (case.get("case_id") or "").strip().upper()
    case["chief_complaint"] = (case.get("chief_complaint") or "").strip()
    case["medications"] = [
        {"name": m["name"].strip(), "dose": (m.get("dose") or "").strip()}
        for m in case.get("medications", []) if (m.get("name") or "").strip()
    ]
    return case
