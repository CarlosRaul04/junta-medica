"""AbstentionPolicy: decide si el sistema debe abstenerse de opinar (RF11, CP07)."""
from junta_medica.models.debate.case_evidence import CaseEvidence


class AbstentionPolicy:
    def __init__(self, abstain_without_debate: bool):
        self._enabled = abstain_without_debate

    def should_abstain(self, evidence: CaseEvidence) -> bool:
        """Sin fragmentos de guía suficientemente parecidos al caso, no hay base para una segunda opinión."""
        return self._enabled and not evidence.guidelines.sufficient_evidence
