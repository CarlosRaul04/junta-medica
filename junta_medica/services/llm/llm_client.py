"""
LLMClient: el único punto por el que los agentes hablan con la IA.

Se encarga de: elegir el modelo de cada rol, pedir JSON, reintentar si llega mal, medir tiempo y calcular costo.
No sabe qué proveedor hay detrás (se le inyecta uno).
"""
import time

from junta_medica.services.llm.cost_calculator import CostCalculator
from junta_medica.exceptions import InvalidResponseError
from junta_medica.services.llm.json_parser import parse_json
from junta_medica.interfaces.llm_provider import LLMProvider
from junta_medica.models.llm.llm_response import LLMResponse
from junta_medica.models.llm.llm_request import LLMRequest

JSON_INSTRUCTION = "\n\nResponde ÚNICAMENTE con un objeto JSON válido."


class LLMClient:
    def __init__(self, provider: LLMProvider, calculator: CostCalculator, json_retries: int,
                 models_by_role: dict[str, str]):
        self._provider = provider
        self._calculator = calculator
        self._retries = json_retries
        self._models = models_by_role

    def model_for(self, role: str) -> str:
        if role not in self._models:
            raise KeyError(f"No hay modelo configurado para el rol '{role}'.")
        return self._models[role]

    def ask(self, role: str, instructions: str, message: str) -> LLMResponse:
        model = self.model_for(role)
        request = LLMRequest(role, instructions + JSON_INSTRUCTION, message, model)
        input_tokens = output_tokens = 0
        start = time.perf_counter()
        last_error: InvalidResponseError | None = None

        for attempt in range(1, self._retries + 2):
            raw = self._provider.complete(request)
            input_tokens += raw.input_tokens
            output_tokens += raw.output_tokens
            try:
                data = parse_json(raw.text)
            except InvalidResponseError as error:
                last_error = error
                continue
            return LLMResponse(
                role=role,
                model=model,
                data=data,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=self._calculator.calculate(model, input_tokens, output_tokens),
                seconds=time.perf_counter() - start,
                attempts=attempt,
                is_mock=raw.is_mock,
            )

        raise InvalidResponseError(
            f"El modelo {model} no devolvió JSON válido tras {self._retries + 1} intentos: {last_error}"
        )
