import pytest

from junta_medica.services.cases.validation_rules.clinical_rules import AgeRange, ValidSex


@pytest.mark.parametrize("age, is_valid", [(18, True), (120, True), (17, False), (121, False)])
def test_age_range(valid_case, age, is_valid):
    valid_case["age"] = age
    assert (AgeRange(18, 120).check(valid_case) == []) == is_valid


@pytest.mark.parametrize("sex, is_valid", [("F", True), ("m", True), (" M ", True), ("X", False), ("hombre", False)])
def test_sex(valid_case, sex, is_valid):
    valid_case["sex"] = sex
    assert (ValidSex().check(valid_case) == []) == is_valid


def test_lab_results_with_valid_keys_and_values(valid_case):
    from junta_medica.services.cases.validation_rules.clinical_rules import RecognizedLabTests
    from junta_medica.config import cases as config
    rule = RecognizedLabTests(config.RECOGNIZED_LAB_TESTS)
    assert rule.check(valid_case) == []
    valid_case["lab_results"] = {"TFG": 30, "potassium_meq_l": "alto"}
    assert {e.field for e in rule.check(valid_case)} == {"lab_results.TFG", "lab_results.potassium_meq_l"}
