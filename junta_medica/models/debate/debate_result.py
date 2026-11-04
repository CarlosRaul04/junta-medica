"""DebateResult: el proceso completo de un caso, listo para el informe, el historial y la evaluación."""
from dataclasses import dataclass

from junta_medica.models.debate.agent_turn import AgentTurn
from junta_medica.models.debate.case_evidence import CaseEvidence
from junta_medica.models.debate.citation_check import CitationCheck
from junta_medica.models.debate.debate_round import DebateRound
from junta_medica.models.debate.final_alert import FinalAlert


@dataclass(frozen=True)
class DebateResult:
    case_id: str
    evidence: CaseEvidence
    rounds: tuple[DebateRound, ...]
    verdict: AgentTurn | None              # None si el sistema se abstuvo sin debatir
    abstained: bool                        # RF11
    abstention_reason: str
    alerts: tuple[FinalAlert, ...]
    unresolved_objections: tuple[str, ...]  # objeciones graves que siguieron en la última ronda
    citation_check: CitationCheck
    seconds: float

    @property
    def turns(self) -> list[AgentTurn]:
        turns = [t for r in self.rounds for t in (r.proposal, *r.reviews)]
        return turns + ([self.verdict] if self.verdict else [])

    @property
    def llm_calls(self) -> int:
        return sum(t.llm.attempts for t in self.turns)

    @property
    def cost_usd(self) -> float:
        return sum(t.llm.cost_usd for t in self.turns)

    @property
    def final_agreement(self) -> float:
        return self.rounds[-1].agreement_level if self.rounds else 0.0
