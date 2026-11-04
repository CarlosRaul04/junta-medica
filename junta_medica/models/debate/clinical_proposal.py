"""ClinicalProposal: la propuesta del Agente Clínico en una ronda (diagnósticos y plan)."""
from dataclasses import dataclass

from junta_medica.models.debate.cited_item import CitedItem
from junta_medica.models.debate.proposed_diagnosis import ProposedDiagnosis


@dataclass(frozen=True)
class ClinicalProposal:
    diagnoses: tuple[ProposedDiagnosis, ...]          # top-3, del más al menos probable
    plan: tuple[CitedItem, ...]
    missing_data: tuple[str, ...] = ()                # datos que faltan para decidir mejor
    response_to_objections: tuple[str, ...] = ()      # desde la ronda 2: qué cambió y por qué
