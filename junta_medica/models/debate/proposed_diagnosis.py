"""ProposedDiagnosis: un diagnóstico propuesto por el Agente Clínico."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ProposedDiagnosis:
    icd10: str
    name: str
    likelihood: str            # high | medium | low
    rationale: str
    citations: tuple[str, ...] = ()
