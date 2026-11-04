"""LabCriterion: compara un resultado de laboratorio del caso con el umbral de la regla."""
from junta_medica.interfaces.condition_criterion import ConditionCriterion, Evaluation
from junta_medica.models.cases.clinical_case import ClinicalCase
from junta_medica.models.pharmacology.condition_rule import ConditionRule
from junta_medica.services.pharmacology.condition_criteria.comparison import compare


class LabCriterion(ConditionCriterion):
    def evaluate(self, rule: ConditionRule, case: ClinicalCase) -> Evaluation:
        value = case.lab_results.get(rule.parameter)
        if value is None:
            return None   # falta el dato
        return compare(value, rule), f"{rule.parameter} = {value}"
