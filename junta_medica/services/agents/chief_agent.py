"""ChiefAgent: lee todo el debate y las alertas del sistema, y redacta la segunda opinión final."""
from junta_medica.models.debate.agent_turn import AgentTurn
from junta_medica.models.debate.case_evidence import CaseEvidence
from junta_medica.models.debate.debate_round import DebateRound
from junta_medica.models.debate.final_alert import FinalAlert
from junta_medica.services.agents.context.case_formatter import CaseFormatter
from junta_medica.services.agents.context.debate_formatter import DebateFormatter
from junta_medica.services.agents.llm_agent import LLMAgent

FINAL_ROUND = 0


class ChiefAgent(LLMAgent):
    role = "chief"

    def __init__(self, client, prompts, parser, cases: CaseFormatter, debate: DebateFormatter,
                 severity_labels: dict[str, str]):
        super().__init__(client, prompts, parser)
        self._cases = cases
        self._debate = debate
        self._severity = severity_labels

    def decide(self, evidence: CaseEvidence, rounds: list[DebateRound], alerts: list[FinalAlert],
               unresolved_objections: list[str], allowed_citations: list[str]) -> AgentTurn:
        sections = [
            self._section("Caso", self._cases.full(evidence.case)),
            self._section("Debate", self._debate.rounds(rounds)),
            self._section("Alertas de seguridad del sistema (siempre van en el informe)", self._alerts(alerts)),
        ]
        if unresolved_objections:
            sections.append(self._section("Objeciones graves sin resolver", "\n".join(f"- {o}" for o in unresolved_objections)))
        sections.append(self._section("Citas que puedes usar", ", ".join(allowed_citations) or "(ninguna)"))
        return self._ask("\n\n".join(sections), FINAL_ROUND, allowed_citations)

    def _alerts(self, alerts: list[FinalAlert]) -> str:
        if not alerts:
            return "- Ninguna."
        return "\n".join(f"- {self._severity[a.severity.value].upper()}: {a.text} " + " ".join(f"[{c}]" for c in a.citations)
                         for a in alerts)
