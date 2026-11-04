from junta_medica.factories.case_factory import create_case_validator


def test_valid_case_passes_all_rules(valid_case):
    assert create_case_validator().validate(valid_case).is_valid


def test_cp01_case_without_medications_is_rejected_and_reports_the_field(valid_case):
    """Caso de prueba CP01 del documento."""
    del valid_case["medications"]
    result = create_case_validator().validate(valid_case)
    assert not result.is_valid
    assert "medications" in {e.field for e in result.errors}


def test_collects_errors_from_several_rules(valid_case):
    valid_case["age"] = 15
    valid_case["sex"] = "X"
    valid_case["dni"] = "45678912"
    fields = {e.field for e in create_case_validator().validate(valid_case).errors}
    assert {"age", "sex", "dni"} <= fields


def test_input_that_is_not_a_dict():
    result = create_case_validator().validate(["no", "es", "un", "case"])
    assert not result.is_valid
