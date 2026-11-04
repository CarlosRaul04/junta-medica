"""
Arma el LLMClient según el .env: proveedor simulado (MOCK_MODE=1) o uno real compatible con OpenAI.

La elección del proveedor y de los modelos es del equipo: se cambia solo en el .env (ver .env.ejemplo).
"""
from junta_medica.config import debate, environment, llm, paths
from junta_medica.exceptions import LLMConfigurationError
from junta_medica.interfaces.llm_provider import LLMProvider
from junta_medica.services.llm.cost_calculator import CostCalculator
from junta_medica.services.llm.llm_client import LLMClient
from junta_medica.services.llm.providers.mock_provider import MockLLMProvider
from junta_medica.services.llm.providers.openai_compatible_provider import OpenAICompatibleProvider

ALL_ROLES = debate.DEBATE_ROLES + [debate.CHIEF_ROLE]
NO_KEY_PLACEHOLDER = "no-key"   # Ollama/LM Studio no piden clave, pero el SDK exige un texto


def resolve_models(agent_model: str, chief_model: str, overrides: dict[str, str]) -> dict[str, str]:
    """Modelo de cada rol: el específico del rol si existe; si no, el de agentes o el del jefe."""
    defaults = {role: agent_model for role in debate.DEBATE_ROLES} | {debate.CHIEF_ROLE: chief_model}
    models = {role: overrides.get(role) or defaults[role] for role in ALL_ROLES}
    missing = [role for role, model in models.items() if not model]
    if missing:
        raise LLMConfigurationError(
            f"Falta elegir el modelo para: {', '.join(missing)}. Completa AGENT_MODEL y CHIEF_MODEL en el .env."
        )
    return models


def create_llm_provider() -> LLMProvider:
    if environment.MOCK_MODE:
        return MockLLMProvider(paths.MOCK_RESPONSES_DIR)
    if not environment.LLM_BASE_URL and not environment.LLM_API_KEY:
        raise LLMConfigurationError("Falta LLM_API_KEY (o LLM_BASE_URL para un modelo local) en el .env.")
    from openai import OpenAI  # solo se importa si se usa un proveedor real

    client = OpenAI(
        base_url=environment.LLM_BASE_URL or None,
        api_key=environment.LLM_API_KEY or NO_KEY_PLACEHOLDER,
        max_retries=llm.REQUEST_RETRIES,
        timeout=llm.REQUEST_TIMEOUT_SECONDS,
    )
    return OpenAICompatibleProvider(client, llm.TEMPERATURE, environment.LLM_JSON_MODE,
                                    environment.LLM_MERGE_SYSTEM_PROMPT)


def create_models_by_role() -> dict[str, str]:
    if environment.MOCK_MODE:
        return {role: llm.MOCK_MODEL_NAME for role in ALL_ROLES}
    return resolve_models(environment.AGENT_MODEL, environment.CHIEF_MODEL, environment.ROLE_MODEL_OVERRIDES)


def create_llm_client() -> LLMClient:
    return LLMClient(
        provider=create_llm_provider(),
        calculator=CostCalculator(llm.PRICES_USD_PER_MILLION),
        json_retries=llm.JSON_RETRIES,
        models_by_role=create_models_by_role(),
    )
