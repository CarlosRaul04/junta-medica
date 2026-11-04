"""ProtocolAgent: revisa si la propuesta cumple las guías, con fragmentos buscados para ESA propuesta."""
from junta_medica.models.cases.clinical_case import ClinicalCase
from junta_medica.models.debate.agent_turn import AgentTurn
from junta_medica.models.debate.clinical_proposal import ClinicalProposal
from junta_medica.models.knowledge.retrieved_chunk import RetrievedChunk
from junta_medica.services.agents.context.case_formatter import CaseFormatter
from junta_medica.services.agents.context.debate_formatter import DebateFormatter
from junta_medica.services.agents.context.evidence_formatter import EvidenceFormatter
from junta_medica.services.agents.llm_agent import LLMAgent


class ProtocolAgent(LLMAgent):
    role = "protocol"

    def __init__(self, client, prompts, parser, cases: CaseFormatter, evidence: EvidenceFormatter,
                 debate: DebateFormatter):
        super().__init__(client, prompts, parser)
        self._cases = cases
        self._evidence = evidence
        self._debate = debate

    def review(self, case: ClinicalCase, proposal: ClinicalProposal, fragments: tuple[RetrievedChunk, ...],
               round_number: int) -> AgentTurn:
        message = "\n\n".join([
            self._section("Resumen del caso", self._cases.summary(case)),
            self._section("Propuesta del Agente Clínico", self._debate.proposal(proposal)),
            self._section("Fragmentos de las guías sobre esta propuesta", self._evidence.fragments(fragments)),
        ])
        return self._ask(message, round_number, [f.chunk.citation for f in fragments])
