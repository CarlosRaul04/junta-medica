import json

import pytest

from junta_medica.exceptions import InvalidCaseError
from junta_medica.factories.case_factory import create_case_loader
from junta_medica.config import paths


def test_loads_from_dict(valid_case):
    assert create_case_loader().from_dict(valid_case).case_id == "CASO-001"


def test_invalid_case_raises_error_with_all_problems(valid_case):
    del valid_case["medications"]
    del valid_case["symptoms"]
    with pytest.raises(InvalidCaseError) as error:
        create_case_loader().from_dict(valid_case)
    assert {e.field for e in error.value.errors} == {"medications", "symptoms"}


def test_loads_from_file(tmp_path, valid_case):
    file = tmp_path / "CASO-001.json"
    file.write_text(json.dumps({"case": valid_case, "expected": {}}), encoding="utf-8")
    assert create_case_loader().from_file(file).age == 68


def test_file_without_case_section(tmp_path, valid_case):
    file = tmp_path / "malo.json"
    file.write_text(json.dumps(valid_case), encoding="utf-8")
    with pytest.raises(InvalidCaseError):
        create_case_loader().from_file(file)


def test_file_that_is_not_json(tmp_path):
    file = tmp_path / "roto.json"
    file.write_text("{ esto no es json", encoding="utf-8")
    with pytest.raises(InvalidCaseError):
        create_case_loader().from_file(file)


def test_project_template_is_a_valid_case():
    """Si alguien cambia las reglas, la plantilla debe seguir siendo válida."""
    case = create_case_loader().from_file(paths.TEMPLATES_DIR / "clinical_case.json")
    assert case.case_id == "CASO-000"
    assert case.medication_names == ["warfarina", "ibuprofeno", "bisoprolol", "omeprazol"]
