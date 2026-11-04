"""Interaction: un par de medicamentos que interactúan, según la tabla (DDInter)."""
from dataclasses import dataclass

from junta_medica.models.pharmacology.severity import Severity


@dataclass(frozen=True)
class Interaction:
    drug_a: str   # DCI (orden alfabético: drug_a < drug_b)
    drug_b: str
    severity: Severity
    source: str          # ej. "DDInter"
    source_id: str       # identificador en la fuente (ej. "DDInter1951-DDInter906")

    @property
    def pair(self) -> frozenset[str]:
        return frozenset((self.drug_a, self.drug_b))

    @property
    def citation(self) -> str:
        return f"{self.source.lower()}:{self.source_id}"
