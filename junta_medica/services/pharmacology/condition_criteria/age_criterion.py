"""AgeCriterion: compara la edad del paciente con el umbral de la regla."""
from junta_medica.interfaces.condition_criterion import ConditionCriterion, Evaluation
from junta_medica.models.cases.clinical_case import ClinicalCase
from junta_medica.models.pharmacology.condition_rule import ConditionRule
from junta_medica.services.pharmacology.condition_criteria.comparison import compare


class AgeCriterion(ConditionCriterion):
    def evaluate(self, rule: ConditionRule, case: ClinicalCase) -> Evaluation:
        return compare(case.age, rule), f"edad = {case.age} años"
