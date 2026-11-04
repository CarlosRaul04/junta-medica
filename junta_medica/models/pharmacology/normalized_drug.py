"""NormalizedDrug: resultado de traducir lo que escribió el usuario a una DCI del catálogo."""
from dataclasses import dataclass
from enum import Enum


class NormalizationMethod(str, Enum):
    EXACT = "exact"                # escrito igual que la DCI
    SYNONYM = "synonym"            # otra forma de escribirlo (sin tilde, en inglés, con la sal)
    BRAND = "brand"                  # nombre comercial
    APPROXIMATE = "approximate"        # parecido (error de tipeo): conviene confirmarlo con el usuario
    UNRECOGNIZED = "unrecognized"  # no está en el catálogo


@dataclass(frozen=True)
class NormalizedDrug:
    original_name: str
    inn: str | None
    method: NormalizationMethod
    similarity: float = 1.0

    @property
    def recognized(self) -> bool:
        return self.inn is not None

    @property
    def needs_confirmation(self) -> bool:
        return self.method is NormalizationMethod.APPROXIMATE
