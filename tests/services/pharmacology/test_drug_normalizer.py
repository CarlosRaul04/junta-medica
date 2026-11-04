import pytest

from junta_medica.factories.pharmacology_factory import create_drug_normalizer
from junta_medica.models.pharmacology.normalized_drug import NormalizationMethod as M


@pytest.fixture(scope="module")
def normalizer():
    return create_drug_normalizer()


@pytest.mark.parametrize("name, inn, method", [
    ("warfarina", "warfarina", M.EXACT),
    ("Losartán potásico 50 mg", "losartán", M.EXACT),
    ("losartan", "losartán", M.EXACT),
    ("Panadol", "paracetamol", M.BRAND),
    ("acetaminofén", "paracetamol", M.SYNONYM),
    ("AAS", "ácido acetilsalicílico", M.SYNONYM),
    ("Warfarin", "warfarina", M.SYNONYM),
    ("Amoxicilina + ácido clavulánico", "amoxicilina/ácido clavulánico", M.EXACT),
    ("amoxicilina", "amoxicilina", M.EXACT),
    ("insulina glargina", "insulina", M.SYNONYM),
])
def test_recognizes_known_names(normalizer, name, inn, method):
    result = normalizer.normalize(name)
    assert (result.inn, result.method) == (inn, method)


@pytest.mark.parametrize("misspelled, inn", [("amoxicilna", "amoxicilina"), ("metformna", "metformina"), ("espironolactna", "espironolactona")])
def test_fixes_typos_and_asks_for_confirmation(normalizer, misspelled, inn):
    result = normalizer.normalize(misspelled)
    assert result.inn == inn and result.needs_confirmation


def test_does_not_confuse_similar_drugs(normalizer):
    assert normalizer.normalize("valsartan").inn == "valsartán"
    assert normalizer.normalize("telmisartán").inn is None   # parecido, pero no está en el catálogo


@pytest.mark.parametrize("name", ["xyz123", "remedio casero", "AB"])
def test_unknown_names_are_unrecognized(normalizer, name):
    result = normalizer.normalize(name)
    assert not result.recognized and result.method is M.UNRECOGNIZED


def test_normalize_many_keeps_order(normalizer):
    assert [r.inn for r in normalizer.normalize_many(["Panadol", "Coumadin"])] == ["paracetamol", "warfarina"]
