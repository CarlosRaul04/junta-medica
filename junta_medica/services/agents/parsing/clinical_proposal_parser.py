"""ClinicalProposalParser: JSON del Agente Clínico -> ClinicalProposal."""
from junta_medica.models.debate.clinical_proposal import ClinicalProposal
from junta_medica.models.debate.proposed_diagnosis import ProposedDiagnosis
from junta_medica.services.agents.parsing.field_readers import (
    read_citations, read_cited_items, read_dict, read_text, read_text_list,
)


class ClinicalProposalParser:
    def __init__(self, max_diagnoses: int, valid_likelihoods: list[str], likelihood_synonyms: dict[str, str],
                 default_likelihood: str):
        self._max = max_diagnoses
        self._valid = set(valid_likelihoods)
        self._synonyms = likelihood_synonyms
        self._default = default_likelihood

    def parse(self, data: dict) -> ClinicalProposal:
        diagnoses = [self._diagnosis(read_dict(d)) for d in (data.get("diagnoses") or []) if isinstance(d, dict)]
        return ClinicalProposal(
            diagnoses=tuple(d for d in diagnoses if d.icd10 or d.name)[: self._max],
            plan=read_cited_items(data.get("plan")),
            missing_data=read_text_list(data.get("missing_data")),
            response_to_objections=read_text_list(data.get("response_to_objections")),
        )

    def _diagnosis(self, data: dict) -> ProposedDiagnosis:
        likelihood = read_text(data.get("likelihood")).lower()
        likelihood = self._synonyms.get(likelihood, likelihood)
        return ProposedDiagnosis(
            icd10=read_text(data.get("icd10")).upper().replace(" ", ""),
            name=read_text(data.get("name")),
            likelihood=likelihood if likelihood in self._valid else self._default,
            rationale=read_text(data.get("rationale")),
            citations=read_citations(data.get("citations")),
        )
