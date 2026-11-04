"""ClinicalAgent: propone el top-3 de diagnósticos (CIE-10) y el plan. Desde la ronda 2 responde a las objeciones."""
from junta_medica.models.cases.clinical_case import ClinicalCase
from junta_medica.models.debate.agent_turn import AgentTurn
from junta_medica.models.debate.clinical_proposal import ClinicalProposal
from junta_medica.models.debate.review import Review
from junta_medica.models.knowledge.retrieved_chunk import RetrievedChunk
from junta_medica.services.agents.context.case_formatter import CaseFormatter
from junta_medica.services.agents.context.debate_formatter import DebateFormatter
from junta_medica.services.agents.context.evidence_formatter import EvidenceFormatter
from junta_medica.services.agents.llm_agent import LLMAgent


class ClinicalAgent(LLMAgent):
    role = "clinical"

    def __init__(self, client, prompts, parser, cases: CaseFormatter, evidence: EvidenceFormatter,
                 debate: DebateFormatter):
        super().__init__(client, prompts, parser)
        self._cases = cases
        self._evidence = evidence
        self._debate = debate

    def propose(self, case: ClinicalCase, fragments: tuple[RetrievedChunk, ...], round_number: int,
                previous: ClinicalProposal | None = None,
                feedback: list[tuple[str, Review]] | None = None) -> AgentTurn:
        sections = [
            self._section("Caso", self._cases.full(case)),
            self._section("Fragmentos de las guías", self._evidence.fragments(fragments)),
        ]
        if previous is not None:
            sections.append(self._section("Tu propuesta anterior", self._debate.proposal(previous)))
        if feedback:
            sections.append(self._section("Objeciones y comentarios de los otros agentes", self._debate.feedback(feedback)))
            sections.append("Corrige tu propuesta o explica por qué la mantienes (campo response_to_objections).")
        citations = [f.chunk.citation for f in fragments]
        return self._ask("\n\n".join(sections), round_number, citations)
