"""LLMProvider: cualquier proveedor de IA (OpenAI, simulado, otro) debe cumplir este contrato."""
from abc import ABC, abstractmethod

from junta_medica.models.llm.llm_response import RawLLMResponse
from junta_medica.models.llm.llm_request import LLMRequest


class LLMProvider(ABC):
    @abstractmethod
    def complete(self, request: LLMRequest) -> RawLLMResponse:
        """Envía la solicitud al modelo y devuelve el texto tal cual llegó."""
