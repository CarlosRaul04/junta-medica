"""LLMAgent: lo común a los 4 agentes con IA (pedir al LLMClient, leer la respuesta y registrar la intervención)."""
from junta_medica.models.debate.agent_turn import AgentTurn
from junta_medica.repositories.prompts.prompt_repository import PromptRepository
from junta_medica.services.llm.llm_client import LLMClient


class LLMAgent:
    role: str = ""

    def __init__(self, client: LLMClient, prompts: PromptRepository, parser):
        self._client = client
        self._prompts = prompts
        self._parser = parser

    def _ask(self, message: str, round_number: int, context_citations: list[str]) -> AgentTurn:
        response = self._client.ask(self.role, self._prompts.get(self.role), message)
        return AgentTurn(
            role=self.role,
            round_number=round_number,
            output=self._parser.parse(response.data),
            llm=response,
            context_citations=tuple(dict.fromkeys(context_citations)),   # sin repetidos, en orden
        )

    @staticmethod
    def _section(title: str, body: str) -> str:
        return f"## {title}\n{body}"
