"""AgentTurn: una intervención de un agente. Guarda qué dijo y cuánto costó (trazabilidad por agente, RF14)."""
from dataclasses import dataclass

from junta_medica.models.debate.chief_verdict import ChiefVerdict
from junta_medica.models.debate.clinical_proposal import ClinicalProposal
from junta_medica.models.debate.review import Review
from junta_medica.models.llm.llm_response import LLMResponse


@dataclass(frozen=True)
class AgentTurn:
    role: str                      # clinical | pharmacological | protocol | chief
    round_number: int              # 0 = dictamen final del jefe
    output: ClinicalProposal | Review | ChiefVerdict
    llm: LLMResponse               # modelo, tokens, costo, tiempo, intentos y JSON original
    context_citations: tuple[str, ...] = ()   # citas que este agente tenía disponibles
