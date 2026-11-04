"""CaseValidator: aplica todas las reglas y devuelve TODOS los problemas juntos (RF02)."""
from junta_medica.interfaces.validation_rule import ValidationRule
from junta_medica.models.cases.validation_result import ValidationError, ValidationResult


class CaseValidator:
    def __init__(self, rules: list[ValidationRule]):
        self._rules = rules

    def validate(self, data) -> ValidationResult:
        if not isinstance(data, dict):
            return ValidationResult((ValidationError("case", "El caso debe ser un conjunto de campos."),))
        errors: list[ValidationError] = []
        for rule in self._rules:
            errors.extend(rule.check(data))
        return ValidationResult(tuple(errors))
