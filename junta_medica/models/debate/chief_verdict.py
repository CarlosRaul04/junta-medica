"""ChiefVerdict: el dictamen final del Médico Jefe (la segunda opinión)."""
from dataclasses import dataclass

from junta_medica.models.debate.cited_item import CitedItem


@dataclass(frozen=True)
class DiagnosisSummary:
    icd10: str
    name: str


@dataclass(frozen=True)
class ChiefVerdict:
    summary: str                                   # la segunda opinión en pocas líneas
    primary_diagnosis: DiagnosisSummary | None
    differential_diagnoses: tuple[DiagnosisSummary, ...] = ()
    recommendations: tuple[CitedItem, ...] = ()
    disagreements: tuple[str, ...] = ()            # discrepancias que quedaron sin resolver
    limitations: tuple[str, ...] = ()              # puntos concretos que las guías no cubren (no invalidan el dictamen)
    insufficient_evidence: bool = False            # RF11: las guías no cubren el caso en general (no hay segunda opinión)
