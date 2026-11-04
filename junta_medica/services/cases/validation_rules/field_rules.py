"""Reglas sobre la estructura del caso: qué campos hay, de qué tipo y con qué formato."""
import re

from junta_medica.interfaces.validation_rule import ValidationRule
from junta_medica.models.cases.validation_result import ValidationError


def is_empty(value) -> bool:
    return value is None or (isinstance(value, (str, list, dict)) and len(value) == 0) or (
        isinstance(value, str) and not value.strip()
    )


class RequiredFields(ValidationRule):
    """RF02: informa todos los datos faltantes."""

    def __init__(self, fields: list[str], field_labels: dict[str, str]):
        self._fields = fields
        self._labels = field_labels

    def check(self, data: dict) -> list[ValidationError]:
        return [
            ValidationError(field, f"Falta completar: {self._labels.get(field, field)}.")
            for field in self._fields
            if is_empty(data.get(field))
        ]


class AllowedFields(ValidationRule):
    """RF03: solo se aceptan los campos conocidos (evita que se cuelen nombres, DNI, etc.)."""

    def __init__(self, allowed_fields: list[str]):
        self._allowed = set(allowed_fields)

    def check(self, data: dict) -> list[ValidationError]:
        return [
            ValidationError(field, f"El campo '{field}' no está permitido en un caso clínico.")
            for field in data
            if field not in self._allowed
        ]


class FieldTypes(ValidationRule):
    """Cada campo presente debe tener el tipo correcto."""

    _DESCRIPTIONS = {
        "text": "un texto",
        "integer": "un número entero",
        "text_list": "una lista de textos",
        "medication_list": "una lista de medicamentos (texto o {\"nombre\": ..., \"dosis\": ...})",
        "dict": "un conjunto de resultados (nombre: valor)",
    }

    def __init__(self, field_types: dict[str, str], field_labels: dict[str, str]):
        self._types = field_types
        self._labels = field_labels

    def check(self, data: dict) -> list[ValidationError]:
        errors = []
        for field, kind in self._types.items():
            value = data.get(field)
            if is_empty(value) or self._has_type(value, kind):
                continue
            name = self._labels.get(field, field)
            errors.append(ValidationError(field, f"El campo {name} debe ser {self._DESCRIPTIONS[kind]}."))
        return errors

    @staticmethod
    def _has_type(value, kind: str) -> bool:
        if kind == "text":
            return isinstance(value, str)
        if kind == "integer":
            return isinstance(value, int) and not isinstance(value, bool)
        if kind == "text_list":
            return isinstance(value, list) and all(isinstance(v, str) for v in value)
        if kind == "medication_list":
            return isinstance(value, list) and all(_is_medication(v) for v in value)
        if kind == "dict":
            return isinstance(value, dict)
        raise ValueError(f"Tipo desconocido en la configuración: {kind}")


def _is_medication(value) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    return (
        isinstance(value, dict)
        and isinstance(value.get("name"), str)
        and bool(value["name"].strip())
        and isinstance(value.get("dose", ""), str)
    )


class IdentifierFormat(ValidationRule):
    """RF03: el caso se identifica con un código (ej. CASO-001), nunca con datos del paciente."""

    def __init__(self, pattern: str, example: str):
        self._pattern = re.compile(pattern)
        self._example = example

    def check(self, data: dict) -> list[ValidationError]:
        value = data.get("case_id")
        if not isinstance(value, str) or is_empty(value) or self._pattern.fullmatch(value.strip()):
            return []
        return [ValidationError("case_id", f"El código del caso debe tener el formato {self._example}.")]
