import pytest

from junta_medica.services.llm.llm_client import LLMClient
from junta_medica.services.llm.cost_calculator import CostCalculator
from junta_medica.exceptions import InvalidResponseError
from junta_medica.interfaces.llm_provider import LLMProvider
from junta_medica.models.llm.llm_response import RawLLMResponse


class FakeLLMProvider(LLMProvider):
    """Devuelve, en orden, los textos que se le indiquen."""

    def __init__(self, texts):
        self._textos = list(texts)
        self.calls = 0

    def complete(self, request):
        self.calls += 1
        return RawLLMResponse(text=self._textos.pop(0), input_tokens=100, output_tokens=10)


def create_client(provider, retries=2):
    return LLMClient(provider, CostCalculator({"m": (1.0, 5.0)}), retries, {"clinical": "m"})


def test_valid_response_on_first_attempt():
    response = create_client(FakeLLMProvider(['{"ok": true}'])).ask("clinical", "role", "case")
    assert response.data == {"ok": True}
    assert response.attempts == 1
    assert response.cost_usd == pytest.approx((100 * 1.0 + 10 * 5.0) / 1_000_000)


def test_retries_on_invalid_json_and_adds_tokens():
    provider = FakeLLMProvider(["no es json", '{"ok": true}'])
    response = create_client(provider).ask("clinical", "role", "case")
    assert response.attempts == 2
    assert response.input_tokens == 200


def test_fails_after_exhausting_retries():
    provider = FakeLLMProvider(["mal", "mal", "mal"])
    with pytest.raises(InvalidResponseError):
        create_client(provider, retries=2).ask("clinical", "role", "case")
    assert provider.calls == 3


def test_uses_the_model_of_the_role():
    provider = FakeLLMProvider(['{"ok": true}'])
    response = create_client(provider).ask("clinical", "role", "case")
    assert response.model == "m"


def test_unknown_role_raises_error():
    with pytest.raises(KeyError):
        create_client(FakeLLMProvider([])).ask("chief", "role", "case")
