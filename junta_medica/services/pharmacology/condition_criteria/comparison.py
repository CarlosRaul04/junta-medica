"""Compara un valor del paciente con el umbral de la regla, usando el operador de la regla."""
import operator

from junta_medica.models.pharmacology.condition_rule import ConditionRule

_OPERATORS = {"<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge}


def compare(observed_value: float, rule: ConditionRule) -> bool:
    if rule.operator not in _OPERATORS:
        raise ValueError(f"Operador no válido en la regla {rule.rule_id}: {rule.operator}")
    return _OPERATORS[rule.operator](observed_value, float(rule.value))
