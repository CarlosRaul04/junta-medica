import pytest

from junta_medica.exceptions import LLMConfigurationError
from junta_medica.factories.llm_factory import resolve_models


def test_agents_use_agent_model_and_chief_uses_chief_model():
    models = resolve_models("modelo-agentes", "modelo-jefe", {})
    assert models == {"clinical": "modelo-agentes", "pharmacological": "modelo-agentes",
                      "protocol": "modelo-agentes", "chief": "modelo-jefe"}


def test_role_override_wins():
    models = resolve_models("modelo-agentes", "modelo-jefe", {"protocol": "otro"})
    assert models["protocol"] == "otro"
    assert models["clinical"] == "modelo-agentes"


def test_missing_model_raises_clear_error():
    with pytest.raises(LLMConfigurationError, match="chief"):
        resolve_models("modelo-agentes", "", {})
