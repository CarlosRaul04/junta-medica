import json

import pytest

from junta_medica.exceptions import InvalidCaseError
from junta_medica.repositories.cases.case_repository import CaseRepository


def test_reads_case_section_and_expected_separately(tmp_path, valid_case):
    file = tmp_path / "CASO-001.json"
    file.write_text(json.dumps({"case": valid_case, "expected": {"icd10_diagnosis": "I10"}}), encoding="utf-8")
    repository = CaseRepository(tmp_path)
    assert repository.read_clinical_data(file) == valid_case
    assert repository.read_expected(file) == {"icd10_diagnosis": "I10"}
    assert repository.list_files() == [file]


def test_file_without_case_section_or_invalid_json(tmp_path):
    without_section = tmp_path / "CASO-001.json"
    without_section.write_text("{}", encoding="utf-8")
    broken = tmp_path / "CASO-002.json"
    broken.write_text("{ no es json", encoding="utf-8")
    for file in (without_section, broken):
        with pytest.raises(InvalidCaseError):
            CaseRepository(tmp_path).read_clinical_data(file)
