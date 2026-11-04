import re

import pytest

from junta_medica.factories.pharmacology_factory import create_drug_repository
from junta_medica.repositories.pharmacology.drug_repository import DrugRepository


def test_real_catalog_loads_completely():
    catalog = create_drug_repository()
    assert len(catalog) == 45
    assert catalog.find("warfarina").atc == "B01AA03"


def test_all_drugs_have_minimum_data():
    for drug in create_drug_repository().all():
        assert drug.inn and drug.drug_class and drug.english_names
        assert re.fullmatch(r"[A-Z]\d{2}[A-Z]{0,2}\d{0,2}", drug.atc), drug.inn


def test_lists_are_split_and_dash_means_empty():
    naproxen = create_drug_repository().find("naproxeno")
    assert naproxen.guidelines == ()
    assert create_drug_repository().find("ibuprofeno").brands == ("Advil", "Motrin")


def test_duplicate_inn_is_an_error(tmp_path):
    path = tmp_path / "drugs.csv"
    path.write_text("inn,drug_class,atc,synonyms,brands,english_names,guidelines\nx,g,A01,,,X,\nx,g,A01,,,X,\n", encoding="utf-8")
    with pytest.raises(ValueError):
        DrugRepository(path, "|", "—")
