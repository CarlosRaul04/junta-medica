"""
OpenAICompatibleProvider: proveedor real para cualquier API compatible con OpenAI (Chat Completions).

Sirve para OpenAI, OpenRouter, Groq, Google Gemini, Ollama, LM Studio... Solo cambia la URL y la clave,
que vienen ya puestas en el cliente que se le inyecta (lo arma factories/llm_factory.py).
"""
from junta_medica.exceptions import LLMProviderError
from junta_medica.interfaces.llm_provider import LLMProvider
from junta_medica.models.llm.llm_request import LLMRequest
from junta_medica.models.llm.llm_response import RawLLMResponse


class OpenAICompatibleProvider(LLMProvider):
    def __init__(self, client, temperature: float, json_mode: bool, merge_system_prompt: bool):
        self._client = client                     # openai.OpenAI(base_url=..., api_key=...)
        self._temperature = temperature
        self._json_mode = json_mode
        self._merge_system_prompt = merge_system_prompt

    def complete(self, request: LLMRequest) -> RawLLMResponse:
        options = {"response_format": {"type": "json_object"}} if self._json_mode else {}
        try:
            response = self._client.chat.completions.create(
                model=request.model,
                messages=self._messages(request),
                temperature=self._temperature,
                **options,
            )
        except Exception as error:  # el SDK ya reintentó los 429/5xx; aquí llega el error definitivo
            raise LLMProviderError(f"Error del proveedor con el modelo '{request.model}': {error}") from error

        if not response.choices:
            raise LLMProviderError(f"El modelo '{request.model}' devolvió una respuesta vacía.")
        usage = response.usage
        return RawLLMResponse(
            text=response.choices[0].message.content or "",
            input_tokens=getattr(usage, "prompt_tokens", 0) or 0,
            output_tokens=getattr(usage, "completion_tokens", 0) or 0,
        )

    def _messages(self, request: LLMRequest) -> list[dict]:
        if self._merge_system_prompt:
            return [{"role": "user", "content": f"{request.instructions}\n\n---\n\n{request.message}"}]
        return [
            {"role": "system", "content": request.instructions},
            {"role": "user", "content": request.message},
        ]
