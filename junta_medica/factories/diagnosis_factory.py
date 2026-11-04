"""Arma el repositorio de códigos CIE-10."""
from junta_medica.config import paths
from junta_medica.repositories.diagnoses.icd10_repository import Icd10Repository


def create_icd10_repository() -> Icd10Repository:
    return Icd10Repository(paths.ICD10_PATH)
