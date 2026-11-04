"""Reglas sobre los valores clínicos básicos del caso."""
from junta_medica.models.cases.clinical_case import Sex
from junta_medica.interfaces.validation_rule import ValidationRule
from junta_medica.models.cases.validation_result import ValidationError


class AgeRange(ValidationRule):
    def __init__(self, min_age: int, max_age: int):
        self._min = min_age
        self._max = max_age

    def check(self, data: dict) -> list[ValidationError]:
        age = data.get("age")
        if not isinstance(age, int) or isinstance(age, bool) or self._min <= age <= self._max:
            return []
        return [ValidationError("age", f"La edad debe estar entre {self._min} y {self._max} años.")]


class ValidSex(ValidationRule):
    def check(self, data: dict) -> list[ValidationError]:
        sex = data.get("sex")
        values = {s.value for s in Sex}
        if not isinstance(sex, str) or not sex.strip() or sex.strip().upper() in values:
            return []
        return [ValidationError("sex", "El sexo debe ser 'F' (femenino) o 'M' (masculino).")]


class RecognizedLabTests(ValidationRule):
    """Cada resultado de laboratorio debe usar una clave conocida y tener un valor numérico."""

    def __init__(self, recognized_lab_tests: dict[str, str]):
        self._recognized = recognized_lab_tests

    def check(self, data: dict) -> list[ValidationError]:
        lab_results = data.get("lab_results")
        if not isinstance(lab_results, dict):
            return []
        errors = []
        for key, value in lab_results.items():
            field = f"lab_results.{key}"
            if key not in self._recognized:
                errors.append(ValidationError(field, f"El resultado de laboratorio '{key}' no se reconoce. "
                                                      f"Use uno de: {', '.join(self._recognized)}."))
            elif isinstance(value, bool) or not isinstance(value, (int, float)):
                errors.append(ValidationError(field, f"El valor de {self._recognized[key]} debe ser un número."))
        return errors
