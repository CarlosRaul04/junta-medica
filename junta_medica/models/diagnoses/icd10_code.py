"""Icd10Code: un código de la Clasificación Internacional de Enfermedades (CIE-10, OPS 2018)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Icd10Code:
    code: str      # ej. "I50" (categoría) o "I50.0" (subcategoría)
    title: str     # ej. "Insuficiencia cardíaca congestiva"
    page: int      # página del PDF de la OPS donde aparece (para citarlo)

    @property
    def is_category(self) -> bool:
        """True para los códigos de 3 caracteres (I50); False para las subcategorías (I50.0)."""
        return "." not in self.code

    @property
    def category(self) -> str:
        return self.code.split(".")[0]
