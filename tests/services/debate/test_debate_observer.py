"""El orquestador avisa a un observador cada paso (para el progreso en vivo de la interfaz)."""
from junta_medica.interfaces.debate_observer import DebateObserver
from tests.services.debate.test_debate_orchestrator import AGREE, PROPOSAL, VERDICT, retriever, run  # noqa: F401


class RecordingObserver(DebateObserver):
    def __init__(self):
        self.events = []

    def evidence_collected(self, evidence):
        self.events.append("evidence")

    def agent_started(self, role, round_number):
        self.events.append(f"start:{role}:{round_number}")

    def agent_finished(self, turn):
        self.events.append(f"end:{turn.role}")

    def round_finished(self, debate_round):
        self.events.append(f"round:{debate_round.number}")

    def abstained(self, reason):
        self.events.append("abstained")


def test_observer_receives_every_step(retriever, monkeypatch):
    observer = RecordingObserver()
    script = {"clinical": [PROPOSAL], "pharmacological": [AGREE], "protocol": [AGREE], "chief": [VERDICT]}
    from junta_medica.services.debate.debate_orchestrator import DebateOrchestrator
    original = DebateOrchestrator.run
    monkeypatch.setattr(DebateOrchestrator, "run", lambda self, case: original(self, case, observer))
    run("CASO-008", retriever, script)
    assert observer.events == [
        "evidence", "start:clinical:1", "end:clinical", "start:pharmacological:1", "end:pharmacological",
        "start:protocol:1", "end:protocol", "round:1", "start:chief:0", "end:chief",
    ]
