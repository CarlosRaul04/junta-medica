"""ValidationResult: lo que devuelve el validador. Incluye ValidationError (cada problema encontrado)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationError:
    field: str      # campo con el problema (ej. "medicacion", "sintomas[1]")
    message: str    # explicación en español claro, para mostrar al usuario


@dataclass(frozen=True)
class ValidationResult:
    errors: tuple[ValidationError, ...] = ()

    @property
    def is_valid(self) -> bool:
        return not self.errors

    @property
    def messages(self) -> list[str]:
        return [error.message for error in self.errors]
