"""SilentDebateObserver: no hace nada con los avisos (se usa cuando nadie mira el progreso, ej. la terminal)."""
from junta_medica.interfaces.debate_observer import DebateObserver


class SilentDebateObserver(DebateObserver):
    def evidence_collected(self, evidence) -> None:
        pass

    def agent_started(self, role: str, round_number: int) -> None:
        pass

    def agent_finished(self, turn) -> None:
        pass

    def round_finished(self, debate_round) -> None:
        pass

    def abstained(self, reason: str) -> None:
        pass
