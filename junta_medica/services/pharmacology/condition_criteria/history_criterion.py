"""HistoryCriterion: busca alguno de los términos de la regla como palabra completa en los antecedentes."""
import re

from junta_medica.interfaces.condition_criterion import ConditionCriterion, Evaluation
from junta_medica.models.cases.clinical_case import ClinicalCase
from junta_medica.models.pharmacology.condition_rule import ConditionRule
from junta_medica.services.pharmacology.name_cleaning import remove_accents


class HistoryCriterion(ConditionCriterion):
    def __init__(self, separator: str):
        self._separator = separator

    def evaluate(self, rule: ConditionRule, case: ClinicalCase) -> Evaluation:
        terms = [remove_accents(t.strip().lower()) for t in rule.value.split(self._separator) if t.strip()]
        for history_entry in case.medical_history:
            text = remove_accents(history_entry.lower())
            if any(re.search(rf"\b{re.escape(t)}\b", text) for t in terms):
                return True, f"antecedente: {history_entry}"
        return False, "sin el antecedente"
