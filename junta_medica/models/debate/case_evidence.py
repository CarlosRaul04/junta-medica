"""CaseEvidence: todo lo que las herramientas SIN IA encontraron para un caso (la base del debate)."""
from dataclasses import dataclass

from junta_medica.models.cases.clinical_case import ClinicalCase
from junta_medica.models.knowledge.search_result import SearchResult
from junta_medica.models.pharmacology.condition_finding import ConditionCheckResult
from junta_medica.models.pharmacology.interaction_finding import InteractionFinding
from junta_medica.models.pharmacology.normalized_drug import NormalizedDrug


@dataclass(frozen=True)
class CaseEvidence:
    case: ClinicalCase
    drugs: tuple[NormalizedDrug, ...]
    interactions: tuple[InteractionFinding, ...]
    conditions: ConditionCheckResult
    guidelines: SearchResult              # fragmentos de guía recuperados para el caso

    @property
    def inns(self) -> list[str]:
        return [d.inn for d in self.drugs if d.inn]

    @property
    def unrecognized_drugs(self) -> list[str]:
        return [d.original_name for d in self.drugs if not d.recognized]
