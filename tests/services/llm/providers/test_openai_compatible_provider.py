from types import SimpleNamespace

import pytest

from junta_medica.exceptions import LLMProviderError
from junta_medica.models.llm.llm_request import LLMRequest
from junta_medica.services.llm.providers.openai_compatible_provider import OpenAICompatibleProvider

REQUEST = LLMRequest("clinical", "Eres el agente clínico.", "Caso: ...", "modelo-x")


class FakeCompletions:
    """Imita client.chat.completions del SDK de OpenAI y guarda lo que se le envió."""

    def __init__(self, content='{"ok": true}', error=None, usage=True):
        self.sent = None
        self._content, self._error, self._usage = content, error, usage

    def create(self, **kwargs):
        self.sent = kwargs
        if self._error:
            raise self._error
        usage = SimpleNamespace(prompt_tokens=120, completion_tokens=30) if self._usage else None
        message = SimpleNamespace(content=self._content)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)], usage=usage)


def create_provider(completions, json_mode=True, merge=False):
    client = SimpleNamespace(chat=SimpleNamespace(completions=completions))
    return OpenAICompatibleProvider(client, 0.2, json_mode, merge)


def test_sends_system_and_user_messages_with_json_format():
    completions = FakeCompletions()
    raw = create_provider(completions).complete(REQUEST)
    assert raw.text == '{"ok": true}'
    assert (raw.input_tokens, raw.output_tokens) == (120, 30)
    assert [m["role"] for m in completions.sent["messages"]] == ["system", "user"]
    assert completions.sent["response_format"] == {"type": "json_object"}
    assert completions.sent["model"] == "modelo-x"


def test_without_json_mode_does_not_send_response_format():
    completions = FakeCompletions()
    create_provider(completions, json_mode=False).complete(REQUEST)
    assert "response_format" not in completions.sent


def test_merge_system_prompt_sends_a_single_user_message():
    completions = FakeCompletions()
    create_provider(completions, merge=True).complete(REQUEST)
    messages = completions.sent["messages"]
    assert len(messages) == 1 and messages[0]["role"] == "user"
    assert "Eres el agente clínico." in messages[0]["content"]


def test_missing_usage_counts_as_zero_tokens():
    raw = create_provider(FakeCompletions(usage=False)).complete(REQUEST)
    assert (raw.input_tokens, raw.output_tokens) == (0, 0)


def test_provider_error_is_wrapped():
    with pytest.raises(LLMProviderError, match="modelo-x"):
        create_provider(FakeCompletions(error=RuntimeError("401 invalid key"))).complete(REQUEST)
