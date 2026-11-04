"""
Integridad de los 18 casos simulados (data/cases/CASO-XXX.json).

Además comprueba, a nivel de herramientas (sin IA), que las interacciones y alertas marcadas como
esperadas SÍ se detectan. Si una falla, o el caso está mal escrito o falta un dato en las tablas.
"""
import csv
from collections import Counter

import pytest

from junta_medica.config import cases as config
from junta_medica.config import paths
from junta_medica.factories.case_factory import create_case_loader, create_case_repository
from junta_medica.factories.diagnosis_factory import create_icd10_repository
from junta_medica.factories.pharmacology_factory import (
    create_condition_checker, create_drug_normalizer, create_interaction_checker,
)
from junta_medica.repositories.pharmacology.condition_rule_repository import ConditionRuleRepository

REPOSITORY = create_case_repository()
FILES = REPOSITORY.list_files()
EXPECTED = {f.stem: REPOSITORY.read_expected(f) for f in FILES}
with open(paths.CATALOG_PATH, encoding="utf-8") as _file:
    DOCUMENT_IDS = {row["id"] for row in csv.DictReader(_file)}
RULE_IDS = {r.rule_id for r in ConditionRuleRepository(paths.CONDITION_RULES_PATH).read_all()}


def test_there_are_18_cases_with_the_planned_mix():
    assert len(FILES) == 18
    assert Counter(e["type"] for e in EXPECTED.values()) == {
        "common": 6, "polypharmacy": 6, "atypical": 4, "out_of_scope": 2,
    }


@pytest.mark.parametrize("file", FILES, ids=lambda f: f.stem)
def test_case_is_valid_and_file_name_matches_its_id(file):
    case = create_case_loader().from_file(file)        # lanza InvalidCaseError si no es válido
    assert case.case_id == file.stem


@pytest.mark.parametrize("file", FILES, ids=lambda f: f.stem)
def test_expected_section_is_complete_and_consistent(file):
    expected = EXPECTED[file.stem]
    assert set(config.EXPECTED_FIELDS) <= set(expected)
    assert expected["test_cases"] == config.CASE_TYPES[expected["type"]]
    assert expected["should_abstain"] == (expected["type"] == "out_of_scope")
    assert set(expected["relevant_guidelines"]) <= DOCUMENT_IDS
    assert set(expected["condition_alerts"]) <= RULE_IDS
    assert expected["primary_diagnosis"]["icd10"] and expected["primary_diagnosis"]["name"]


@pytest.mark.parametrize("file", FILES, ids=lambda f: f.stem)
def test_expected_diagnoses_exist_in_icd10(file):
    expected = EXPECTED[file.stem]
    icd10 = create_icd10_repository()
    primary = expected["primary_diagnosis"]["icd10"]
    for code in [primary] + expected["acceptable_diagnoses"]:
        assert icd10.find(code), f"{code} no existe en la CIE-10"
    assert any(primary.startswith(code) or code.startswith(primary) for code in expected["acceptable_diagnoses"]), \
        "el diagnóstico principal debe estar entre los aceptables"


@pytest.mark.parametrize("file", FILES, ids=lambda f: f.stem)
def test_tools_detect_every_expected_interaction_and_alert(file):
    case = create_case_loader().from_file(file)
    expected = EXPECTED[file.stem]
    inns = [d.inn for d in create_drug_normalizer().normalize_many(case.medication_names) if d.inn]

    detected = {i.interaction.pair: i.interaction.severity.value for i in create_interaction_checker().detect(inns)}
    for interaction in expected["interactions"]:
        pair = frozenset(interaction["drugs"])
        assert pair in detected, f"no se detectó {interaction['drugs']}"
        assert detected[pair] == interaction["severity"]

    alerts = {f.rule.rule_id for f in create_condition_checker().detect(case, inns).findings}
    assert set(expected["condition_alerts"]) <= alerts
