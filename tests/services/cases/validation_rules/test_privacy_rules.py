import pytest

from junta_medica.services.cases.validation_rules.privacy_rules import NoPersonalData
from junta_medica.config import cases as config


@pytest.fixture
def rule():
    return NoPersonalData(config.PERSONAL_DATA_PATTERNS)


def test_case_without_personal_data(rule, valid_case):
    assert rule.check(valid_case) == []


@pytest.mark.parametrize("text", ["DNI 45678912", "llamar al 987654321", "correo juan@mail.com"])
def test_detects_personal_data_in_texts(rule, valid_case, text):
    valid_case["medical_history"].append(text)
    errors = rule.check(valid_case)
    assert errors and errors[0].field == "medical_history[1]"


def test_checks_nested_texts(rule, valid_case):
    valid_case["medications"][0]["dose"] = "según indicación al 987654321"
    assert [e.field for e in rule.check(valid_case)] == ["medications[0].dose"]


def test_normal_clinical_values_are_not_personal_data(rule, valid_case):
    valid_case["symptoms"] = ["PA 160/95 mmHg", "glucosa 126 mg/dL", "FC 110 lpm"]
    assert rule.check(valid_case) == []
