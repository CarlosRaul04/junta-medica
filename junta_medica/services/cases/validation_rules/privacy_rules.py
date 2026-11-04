"""RF03 / RNF05: el caso no puede contener datos personales identificables."""
import re
from collections.abc import Iterator

from junta_medica.interfaces.validation_rule import ValidationRule
from junta_medica.models.cases.validation_result import ValidationError


class NoPersonalData(ValidationRule):
    """Busca en todos los textos del caso patrones como DNI, teléfono o correo."""

    def __init__(self, patterns: dict[str, str]):
        self._patterns = {kind: re.compile(pattern) for kind, pattern in patterns.items()}

    def check(self, data: dict) -> list[ValidationError]:
        errors = []
        for path, text in _iter_texts(data):
            for kind, pattern in self._patterns.items():
                if pattern.search(text):
                    errors.append(ValidationError(
                        path,
                        f"Parece haber un dato personal ({kind}) en '{path}'. "
                        "Use solo datos simulados o anonimizados.",
                    ))
        return errors


def _iter_texts(value, path: str = "") -> Iterator[tuple[str, str]]:
    """Devuelve (ruta, texto) de cada texto dentro de diccionarios y listas anidadas."""
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, content in value.items():
            yield from _iter_texts(content, f"{path}.{key}" if path else str(key))
    elif isinstance(value, list):
        for idx, content in enumerate(value):
            yield from _iter_texts(content, f"{path}[{idx}]")
