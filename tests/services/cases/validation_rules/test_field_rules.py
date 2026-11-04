from junta_medica.services.cases.validation_rules.field_rules import (
    RequiredFields,
    AllowedFields,
    IdentifierFormat,
    FieldTypes,
)
from junta_medica.config import cases as config


def test_complete_case_has_no_missing_fields(valid_case):
    rule = RequiredFields(config.REQUIRED_FIELDS, config.FIELD_LABELS)
    assert rule.check(valid_case) == []


def test_reports_all_missing_fields(valid_case):
    del valid_case["medications"]
    valid_case["symptoms"] = []
    valid_case["chief_complaint"] = "   "
    errors = RequiredFields(config.REQUIRED_FIELDS, config.FIELD_LABELS).check(valid_case)
    assert {e.field for e in errors} == {"medications", "symptoms", "chief_complaint"}
    assert "Falta completar: medicación." in [e.message for e in errors]


def test_rejects_unknown_fields(valid_case):
    valid_case["name"] = "Juan Pérez"
    errors = AllowedFields(config.ALLOWED_FIELDS).check(valid_case)
    assert [e.field for e in errors] == ["name"]


def test_detects_wrong_types(valid_case):
    valid_case["age"] = "68"
    valid_case["symptoms"] = "cefalea"
    valid_case["medications"] = [{"dose": "10 mg"}]
    errors = FieldTypes(config.FIELD_TYPES, config.FIELD_LABELS).check(valid_case)
    assert {e.field for e in errors} == {"age", "symptoms", "medications"}


def test_boolean_age_is_not_an_integer(valid_case):
    valid_case["age"] = True
    errors = FieldTypes(config.FIELD_TYPES, config.FIELD_LABELS).check(valid_case)
    assert [e.field for e in errors] == ["age"]


def test_case_id_format(valid_case):
    rule = IdentifierFormat(config.CASE_ID_PATTERN, config.CASE_ID_EXAMPLE)
    assert rule.check(valid_case) == []
    valid_case["case_id"] = "paciente-juan"
    assert [e.field for e in rule.check(valid_case)] == ["case_id"]
