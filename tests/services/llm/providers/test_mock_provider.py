import pytest

from junta_medica.config import debate, paths
from junta_medica.services.llm.json_parser import parse_json
from junta_medica.services.llm.providers.mock_provider import MockLLMProvider
from junta_medica.models.llm.llm_request import LLMRequest


@pytest.mark.parametrize("role", debate.DEBATE_ROLES + [debate.CHIEF_ROLE])
def test_valid_mock_response_exists_for_each_role(role):
    provider = MockLLMProvider(paths.MOCK_RESPONSES_DIR)
    raw = provider.complete(LLMRequest(role, "", "", "model"))
    assert raw.is_mock
    assert isinstance(parse_json(raw.text), dict)


def test_unknown_role_raises_error():
    provider = MockLLMProvider(paths.MOCK_RESPONSES_DIR)
    with pytest.raises(FileNotFoundError):
        provider.complete(LLMRequest("rol_inexistente", "", "", "model"))
