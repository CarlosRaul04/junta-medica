"""
DebateObserver: recibe avisos de lo que va pasando en la junta médica, para mostrar el progreso en vivo
(la interfaz web lo usa; la terminal no lo necesita).
"""
from abc import ABC, abstractmethod

from junta_medica.models.debate.agent_turn import AgentTurn
from junta_medica.models.debate.case_evidence import CaseEvidence
from junta_medica.models.debate.debate_round import DebateRound


class DebateObserver(ABC):
    @abstractmethod
    def evidence_collected(self, evidence: CaseEvidence) -> None:
        """Terminaron las herramientas sin IA (medicación, interacciones, reglas y búsqueda en guías)."""

    @abstractmethod
    def agent_started(self, role: str, round_number: int) -> None:
        """Un agente empezó a trabajar (round_number = 0 para el Médico Jefe)."""

    @abstractmethod
    def agent_finished(self, turn: AgentTurn) -> None:
        ...

    @abstractmethod
    def round_finished(self, debate_round: DebateRound) -> None:
        ...

    @abstractmethod
    def abstained(self, reason: str) -> None:
        """El sistema se abstuvo sin debatir (RF11)."""
