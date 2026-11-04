"""ValidationRule: toda regla que revisa un caso clínico debe cumplir este contrato."""
from abc import ABC, abstractmethod

from junta_medica.models.cases.validation_result import ValidationError


class ValidationRule(ABC):
    @abstractmethod
    def check(self, data: dict) -> list[ValidationError]:
        """Devuelve los problemas encontrados (lista vacía si no hay ninguno).

        Cada regla revisa SOLO lo suyo y no falla si otro campo está mal o falta.
        """
