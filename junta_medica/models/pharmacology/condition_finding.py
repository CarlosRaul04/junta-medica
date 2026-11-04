"""ConditionFinding y ConditionCheckResult: lo que encontró el verificador de reglas fármaco–condición en un caso."""
from dataclasses import dataclass

from junta_medica.models.pharmacology.condition_rule import ConditionRule


@dataclass(frozen=True)
class ConditionFinding:
    rule: ConditionRule
    observed_value: str      # lo que se encontró en el caso (ej. "egfr_ml_min = 25")
    highlighted: bool


@dataclass(frozen=True)
class ConditionCheckResult:
    findings: tuple[ConditionFinding, ...] = ()
    # reglas que no se pudieron evaluar porque falta el dato (ej. metformina sin TFG): el agente puede pedirlo
    not_evaluable: tuple[ConditionRule, ...] = ()
