from junta_medica.models.cases.clinical_case import ClinicalCase, Medication, Sex
from junta_medica.services.pharmacology.condition_criteria.history_criterion import HistoryCriterion
from junta_medica.services.pharmacology.condition_criteria.age_criterion import AgeCriterion
from junta_medica.services.pharmacology.condition_criteria.lab_criterion import LabCriterion
from junta_medica.models.pharmacology.condition_rule import ConditionRule, CriterionType
from junta_medica.models.pharmacology.severity import Severity


def rule(kind, parameter, operator, value):
    return ConditionRule("RX", "x", kind, parameter, operator, value, Severity.SEVERE, "e", "r", "gpc_x", 1)


def case(age=70, medical_history=(), lab_results=None):
    return ClinicalCase("CASO-001", age, Sex.FEMALE, "m", ("s",), (Medication("x"),), medical_history, (), lab_results or {})


def test_lab_criterion_met_not_met_and_missing():
    r = rule(CriterionType.LAB, "egfr_ml_min", "<", "30")
    assert LabCriterion().evaluate(r, case(lab_results={"egfr_ml_min": 25})) == (True, "egfr_ml_min = 25")
    assert LabCriterion().evaluate(r, case(lab_results={"egfr_ml_min": 45}))[0] is False
    assert LabCriterion().evaluate(r, case()) is None


def test_exact_threshold_respects_operator():
    assert LabCriterion().evaluate(rule(CriterionType.LAB, "potassium_meq_l", ">=", "5"), case(lab_results={"potassium_meq_l": 5.0}))[0]
    assert not LabCriterion().evaluate(rule(CriterionType.LAB, "potassium_meq_l", ">", "6"), case(lab_results={"potassium_meq_l": 6.0}))[0]


def test_age():
    r = rule(CriterionType.AGE, "age", ">", "60")
    assert AgeCriterion().evaluate(r, case(age=61))[0] and not AgeCriterion().evaluate(r, case(age=60))[0]


def test_history_ignores_accents_and_matches_whole_words():
    r = rule(CriterionType.HISTORY, "ic", "contains", "insuficiencia cardiaca|icc")
    criterion = HistoryCriterion("|")
    assert criterion.evaluate(r, case(medical_history=("Insuficiencia cardíaca con FEVI reducida",)))[0]
    assert criterion.evaluate(r, case(medical_history=("ICC",)))[0]
    assert not criterion.evaluate(r, case(medical_history=("hipertensión arterial",)))[0]
    assert not criterion.evaluate(r, case(medical_history=("lectura de ficción",)))[0]  # "ficcion" contiene "icc": no debe calzar
