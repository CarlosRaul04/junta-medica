"""
Servicios que usa la interfaz, creados UNA sola vez por servidor (st.cache_resource).

Así el modelo de embeddings y la base vectorial no se vuelven a cargar en cada clic.
"""
import streamlit as st

from junta_medica.config import environment
from junta_medica.factories.case_factory import create_case_loader, create_case_repository
from junta_medica.factories.debate_factory import create_debate_orchestrator
from junta_medica.factories.history_factory import (
    create_case_id_generator, create_consultation_service, create_csv_exporter,
)
from junta_medica.factories.llm_factory import create_models_by_role
from junta_medica.factories.pharmacology_factory import create_drug_repository
from junta_medica.factories.report_factory import create_citation_formatter, create_date_formatter
from junta_medica.factories.user_factory import create_auth_service


@st.cache_resource(show_spinner=False)
def auth_service():
    return create_auth_service()


@st.cache_resource(show_spinner=False)
def consultation_service():
    return create_consultation_service()


@st.cache_resource(show_spinner=False)
def case_loader():
    return create_case_loader()


@st.cache_resource(show_spinner=False)
def case_repository():
    return create_case_repository()


@st.cache_resource(show_spinner="Preparando la junta médica (la primera vez carga el modelo de búsqueda)…")
def debate_orchestrator():
    return create_debate_orchestrator()


@st.cache_resource(show_spinner=False)
def drug_repository():
    return create_drug_repository()


@st.cache_resource(show_spinner=False)
def citation_formatter():
    return create_citation_formatter()


@st.cache_resource(show_spinner=False)
def date_formatter():
    return create_date_formatter()


@st.cache_resource(show_spinner=False)
def csv_exporter():
    return create_csv_exporter()


def case_id_generator():
    return create_case_id_generator()


def is_mock_mode() -> bool:
    return environment.MOCK_MODE


def models_in_use() -> dict[str, str]:
    return create_models_by_role()
