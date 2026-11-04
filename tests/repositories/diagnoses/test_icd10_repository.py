"""CIE-10: la tabla generada (data/references/icd10.csv) y la búsqueda de códigos."""
import pytest

from junta_medica.factories.diagnosis_factory import create_icd10_repository
from junta_medica.models.diagnoses.icd10_code import Icd10Code
from junta_medica.repositories.diagnoses.icd10_repository import Icd10Repository

# Diagnósticos de las 6 enfermedades del alcance (y algunos diferenciales frecuentes)
SCOPE_CODES = ["I10", "I11.0", "I50.0", "I50.9", "I48.0", "I48.9", "E11", "E11.9", "E11.2",
               "N18.3", "N18.5", "J18.9", "J15.9", "J13", "I21.9", "J44.1", "E87.5"]


@pytest.mark.parametrize("code", SCOPE_CODES)
def test_scope_codes_exist_with_title(code):
    found = create_icd10_repository().find(code)
    assert found is not None and found.title


def test_table_size_is_complete():
    assert len(create_icd10_repository()) > 10_000


def test_finds_code_written_in_different_ways(tmp_path):
    repository = Icd10Repository(tmp_path / "icd10.csv")
    repository.save_all([Icd10Code("I50.0", "Insuficiencia cardíaca congestiva", 469)])
    for written in ("I50.0", "i50.0", "I500", " I50.0 "):
        assert repository.find(written).title == "Insuficiencia cardíaca congestiva"
    assert repository.find("I99.9") is None


def test_category_properties():
    assert Icd10Code("I50", "x", 1).is_category
    sub = Icd10Code("I50.0", "x", 1)
    assert not sub.is_category and sub.category == "I50"
