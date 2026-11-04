"""Proveedor de prueba: devuelve respuestas de ejemplo guardadas en archivos JSON."""
from pathlib import Path

from junta_medica.interfaces.llm_provider import LLMProvider
from junta_medica.models.llm.llm_response import RawLLMResponse
from junta_medica.models.llm.llm_request import LLMRequest


class MockLLMProvider(LLMProvider):
    """Busca el archivo <rol>.json en la carpeta indicada (data/mock_responses/)."""

    def __init__(self, responses_folder: Path):
        self._folder = responses_folder

    def complete(self, request: LLMRequest) -> RawLLMResponse:
        file = self._folder / f"{request.role}.json"
        if not file.exists():
            raise FileNotFoundError(f"No hay respuesta simulada para el rol '{request.role}': {file}")
        return RawLLMResponse(text=file.read_text(encoding="utf-8"), is_mock=True)
