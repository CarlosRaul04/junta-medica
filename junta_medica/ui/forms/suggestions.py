"""Opciones sugeridas para los campos de texto (sacadas de los casos de ejemplo y del catálogo de fármacos)."""
import streamlit as st

from junta_medica.ui import dependencies


@st.cache_data(show_spinner=False)
def field_suggestions() -> dict[str, list[str]]:
    repository = dependencies.case_repository()
    found = {"symptoms": set(), "medical_history": set(), "allergies": set()}
    for path in repository.list_files():
        case = repository.read_clinical_data(path)
        for field, values in found.items():
            values.update(v for v in case.get(field, []) if isinstance(v, str))
    return {field: sorted(values) for field, values in found.items()}


@st.cache_data(show_spinner=False)
def example_cases() -> dict[str, dict]:
    """"CASO-008 · Debilidad marcada y palpitaciones (77 años, M)" -> datos del caso."""
    repository = dependencies.case_repository()
    examples = {}
    for path in repository.list_files():
        case = repository.read_clinical_data(path)
        label = f"{case['case_id']} · {case['chief_complaint']} ({case['age']} años, {case['sex']})"
        examples[label] = case
    return examples


@st.cache_data(show_spinner=False)
def drug_names() -> list[str]:
    """Nombres genéricos del catálogo y sus marcas, ej. "dabigatrán (Pradaxa)"."""
    names = []
    for drug in dependencies.drug_repository().all():
        brands = ", ".join(drug.brands)
        names.append(f"{drug.inn} ({brands})" if brands else drug.inn)
    return sorted(names)
