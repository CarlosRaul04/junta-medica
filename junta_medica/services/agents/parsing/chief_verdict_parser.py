"""ChiefVerdictParser: JSON del Médico Jefe -> ChiefVerdict."""
from junta_medica.models.debate.chief_verdict import ChiefVerdict, DiagnosisSummary
from junta_medica.services.agents.parsing.field_readers import (
    read_bool, read_cited_items, read_dict, read_text, read_text_list,
)


class ChiefVerdictParser:
    def __init__(self, max_differentials: int):
        self._max_differentials = max_differentials

    def parse(self, data: dict) -> ChiefVerdict:
        differentials = [self._diagnosis(d) for d in (data.get("differential_diagnoses") or []) if isinstance(d, dict)]
        return ChiefVerdict(
            summary=read_text(data.get("summary")),
            primary_diagnosis=self._diagnosis(data.get("primary_diagnosis")),
            differential_diagnoses=tuple(d for d in differentials if d)[: self._max_differentials],
            recommendations=read_cited_items(data.get("recommendations")),
            disagreements=read_text_list(data.get("disagreements")),
            insufficient_evidence=read_bool(data.get("insufficient_evidence")),
        )

    @staticmethod
    def _diagnosis(value) -> DiagnosisSummary | None:
        data = read_dict(value)
        icd10 = read_text(data.get("icd10")).upper().replace(" ", "")
        name = read_text(data.get("name"))
        return DiagnosisSummary(icd10, name) if (icd10 or name) else None
