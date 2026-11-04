"""DebateRound: una ronda del debate (propuesta del Clínico + revisiones + nivel de acuerdo)."""
from dataclasses import dataclass

from junta_medica.models.debate.agent_turn import AgentTurn


@dataclass(frozen=True)
class DebateRound:
    number: int
    proposal: AgentTurn
    reviews: tuple[AgentTurn, ...]
    agreement_level: float         # 0 a 1: proporción de agentes de acuerdo (el Clínico cuenta como de acuerdo)
    consensus: bool                # agreement_level >= CONSENSUS_THRESHOLD
