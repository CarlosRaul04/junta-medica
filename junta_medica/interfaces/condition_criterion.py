"""ConditionCriterion: cómo se evalúa un tipo de criterio (laboratorio, edad, antecedente) contra un caso."""
from abc import ABC, abstractmethod

from junta_medica.models.cases.clinical_case import ClinicalCase
from junta_medica.models.pharmacology.condition_rule import ConditionRule

# None           -> no se puede evaluar (falta el dato)
# (False, texto) -> el caso NO cumple la condición de riesgo
# (True, texto)  -> el caso SÍ la cumple (texto = lo observado, ej. "egfr_ml_min = 25")
Evaluation = tuple[bool, str] | None


class ConditionCriterion(ABC):
    @abstractmethod
    def evaluate(self, rule: ConditionRule, case: ClinicalCase) -> Evaluation:
        ...
