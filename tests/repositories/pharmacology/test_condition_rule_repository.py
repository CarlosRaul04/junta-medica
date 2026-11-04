"""Integridad de data/pharmacology/condition_rules.csv: cada regla debe ser trazable y evaluable."""
import csv

import pytest

from junta_medica.config import cases as cases_config
from junta_medica.config import paths
from junta_medica.factories.pharmacology_factory import create_drug_repository
from junta_medica.repositories.pharmacology.condition_rule_repository import ConditionRuleRepository
from junta_medica.models.pharmacology.condition_rule import CriterionType

RULES = ConditionRuleRepository(paths.CONDITION_RULES_PATH).read_all()


def page_count(relative_file: str) -> int:
    import pymupdf
    with pymupdf.open(paths.DOCUMENTS_DIR / relative_file) as document:
        return document.page_count


def test_unique_ids():
    ids = [r.rule_id for r in RULES]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("rule", RULES, ids=lambda r: r.rule_id)
def test_each_rule_is_traceable_and_evaluable(rule):
    assert create_drug_repository().find(rule.drug), "medicamento fuera del catálogo"
    with open(paths.CATALOG_PATH, encoding="utf-8") as file:
        documents = {f["id"]: f for f in csv.DictReader(file)}
    assert documents[rule.source]["status"] == "downloaded", "la fuente debe ser un documento descargado"
    assert 0 < rule.page <= page_count(documents[rule.source]["file"]), "la página no existe en el PDF"
    assert rule.effect and rule.recommendation
    if rule.criterion_type is CriterionType.LAB:
        assert rule.parameter in cases_config.RECOGNIZED_LAB_TESTS
    if rule.criterion_type in (CriterionType.LAB, CriterionType.AGE):
        float(rule.value)
        assert rule.operator in ("<", "<=", ">", ">=")
