"""Arma los servicios de casos clínicos con las reglas y parámetros de config/cases.py."""
from junta_medica.config import cases as config
from junta_medica.config import paths
from junta_medica.repositories.cases.case_repository import CaseRepository
from junta_medica.services.cases.case_loader import CaseLoader
from junta_medica.services.cases.case_converter import CaseConverter
from junta_medica.services.cases.validation_rules.field_rules import (
    RequiredFields,
    AllowedFields,
    IdentifierFormat,
    FieldTypes,
)
from junta_medica.services.cases.validation_rules.clinical_rules import RecognizedLabTests, AgeRange, ValidSex
from junta_medica.services.cases.validation_rules.privacy_rules import NoPersonalData
from junta_medica.services.cases.case_validator import CaseValidator


def create_case_validator() -> CaseValidator:
    return CaseValidator([
        AllowedFields(config.ALLOWED_FIELDS),
        RequiredFields(config.REQUIRED_FIELDS, config.FIELD_LABELS),
        FieldTypes(config.FIELD_TYPES, config.FIELD_LABELS),
        IdentifierFormat(config.CASE_ID_PATTERN, config.CASE_ID_EXAMPLE),
        AgeRange(config.MIN_AGE, config.MAX_AGE),
        ValidSex(),
        RecognizedLabTests(config.RECOGNIZED_LAB_TESTS),
        NoPersonalData(config.PERSONAL_DATA_PATTERNS),
    ])


def create_case_repository() -> CaseRepository:
    return CaseRepository(paths.CASES_DIR)


def create_case_loader() -> CaseLoader:
    return CaseLoader(create_case_validator(), CaseConverter(), create_case_repository())
