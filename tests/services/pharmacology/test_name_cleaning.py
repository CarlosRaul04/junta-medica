import pytest

from junta_medica.config import pharmacology as config
from junta_medica.services.pharmacology.name_cleaning import clean_drug_name


@pytest.mark.parametrize("raw_name, expected", [
    ("Losartán Potásico 50 mg", "losartan"),
    ("  ENALAPRIL  ", "enalapril"),
    ("Amoxicilina + Ácido clavulánico 875/125 mg", "amoxicilina/acido clavulanico"),
    ("amoxicilina/ácido clavulánico", "amoxicilina/acido clavulanico"),
    ("Metformina (liberación prolongada) 850 mg", "metformina"),
    ("insulina glargina 100 UI/ml", "insulina glargina"),
])
def test_clean_drug_name(raw_name, expected):
    assert clean_drug_name(raw_name, config.SALTS_TO_IGNORE) == expected
