import pytest

from junta_medica.config import paths
from junta_medica.repositories.prompts.prompt_repository import PromptRepository

REQUIRED_KEYS = {
    "clinical": ["diagnoses", "icd10", "plan", "citations", "missing_data", "response_to_objections"],
    "pharmacological": ["stance", "objections", "severity", "additional_alerts"],
    "protocol": ["stance", "objections", "comments"],
    "chief": ["summary", "primary_diagnosis", "recommendations", "disagreements", "insufficient_evidence"],
}


@pytest.mark.parametrize("role", REQUIRED_KEYS)
def test_each_agent_has_a_prompt_that_explains_its_json(role):
    prompt = PromptRepository(paths.PROMPTS_DIR).get(role)
    for key in REQUIRED_KEYS[role]:
        assert f'"{key}"' in prompt, f"el prompt de {role} no muestra la clave {key}"


def test_missing_prompt_raises_clear_error(tmp_path):
    with pytest.raises(FileNotFoundError, match="nadie"):
        PromptRepository(tmp_path).get("nadie")
