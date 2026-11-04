"""PharmacologicalAgent: revisa la seguridad de la medicación con los hallazgos de la tabla y las reglas."""
from junta_medica.models.debate.agent_turn import AgentTurn
from junta_medica.models.debate.case_evidence import CaseEvidence
from junta_medica.models.debate.clinical_proposal import ClinicalProposal
from junta_medica.services.agents.context.case_formatter import CaseFormatter
from junta_medica.services.agents.context.debate_formatter import DebateFormatter
from junta_medica.services.agents.context.evidence_formatter import EvidenceFormatter
from junta_medica.services.agents.llm_agent import LLMAgent


class PharmacologicalAgent(LLMAgent):
    role = "pharmacological"

    def __init__(self, client, prompts, parser, cases: CaseFormatter, evidence: EvidenceFormatter,
                 debate: DebateFormatter):
        super().__init__(client, prompts, parser)
        self._cases = cases
        self._evidence = evidence
        self._debate = debate

    def review(self, evidence: CaseEvidence, proposal: ClinicalProposal, round_number: int) -> AgentTurn:
        message = "\n\n".join([
            self._section("Paciente", self._cases.clinical_profile(evidence.case)),
            self._section("Medicación (nombre escrito -> nombre genérico)", self._evidence.drugs(evidence.drugs)),
            self._section("Interacciones de la tabla", self._evidence.interactions(evidence.interactions)),
            self._section("Reglas fármaco–condición", self._evidence.conditions(evidence.conditions)),
            self._section("Propuesta del Agente Clínico", self._debate.proposal(proposal)),
        ])
        citations = [f.interaction.citation for f in evidence.interactions]
        citations += [f.rule.citation for f in evidence.conditions.findings]
        return self._ask(message, round_number, citations)
